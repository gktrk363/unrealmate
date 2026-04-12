# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Report Dashboard Adapter
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""Lifecycle adapter for report dashboard runtime."""

from __future__ import annotations

import errno
import socket
import threading
import time
import webbrowser
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen
from typing import Callable

from unrealmate.adapters.report.report_core import (
    ReportCoreCollector,
    format_report_details,
    sort_signals,
    warning_code_for,
)
from unrealmate.contracts.report_dashboard import (
    DashboardDataSnapshot,
    DashboardError,
    DashboardStartRequest,
    DashboardStartResult,
    DashboardStatus,
    DashboardWarning,
)
from unrealmate.core.team_dashboard import TeamDashboard


@dataclass
class _DashboardRuntime:
    server: object
    thread: threading.Thread
    status: DashboardStatus


class ReportDashboardAdapter:
    """Wrap dashboard startup/shutdown into structured lifecycle results."""

    def __init__(
        self,
        collector: ReportCoreCollector | None = None,
        now_provider: Callable[[], datetime] | None = None,
        browser_open: Callable[[str], bool] | None = None,
    ) -> None:
        self._collector = collector or ReportCoreCollector()
        self._now_provider = now_provider or datetime.now
        self._browser_open = browser_open or webbrowser.open
        self._runtimes: dict[tuple[str, int], _DashboardRuntime] = {}
        self._runtime_lock = threading.Lock()

    def start(self, request: DashboardStartRequest) -> DashboardStartResult:
        snapshot, snapshot_warnings = self._collect_snapshot(request.project_path)

        bind_error = self._probe_socket_bind_error(request.host, request.port)
        if bind_error is not None:
            bind_startup_status = self._startup_status_for_bind_error(
                bind_error,
                host=request.host,
                port=request.port,
            )
            return self._error_result(
                request=request,
                snapshot=snapshot,
                warnings=snapshot_warnings,
                startup_status=bind_startup_status,
                error=self._build_bind_error(
                    request,
                    bind_error,
                    startup_status=bind_startup_status,
                ),
            )

        dashboard = TeamDashboard(
            project_path=str(request.project_path),
            port=request.port,
            report_core_snapshot=snapshot.to_payload() if snapshot else None,
        )
        app = dashboard._create_app()
        if app is None:
            return self._error_result(
                request=request,
                snapshot=snapshot,
                warnings=snapshot_warnings,
                startup_status="dependency_missing",
                error=DashboardError(
                    code="report_dashboard_dependency_missing",
                    message="Dashboard dependencies are missing. Install Flask to continue.",
                    source=str(request.project_path),
                ),
            )

        try:
            from werkzeug.serving import make_server
        except Exception as exc:
            return self._error_result(
                request=request,
                snapshot=snapshot,
                warnings=snapshot_warnings,
                startup_status="dependency_missing",
                error=DashboardError(
                    code="report_dashboard_dependency_missing",
                    message=f"Dashboard runtime dependency is unavailable: {exc}",
                    source="werkzeug.serving",
                ),
            )

        try:
            server = make_server(request.host, request.port, app)
        except OSError as exc:
            bind_startup_status = self._startup_status_for_bind_error(
                exc,
                host=request.host,
                port=request.port,
            )
            return self._error_result(
                request=request,
                snapshot=snapshot,
                warnings=snapshot_warnings,
                startup_status=bind_startup_status,
                error=self._build_bind_error(
                    request,
                    exc,
                    startup_status=bind_startup_status,
                ),
            )
        except Exception as exc:
            return self._error_result(
                request=request,
                snapshot=snapshot,
                warnings=snapshot_warnings,
                startup_status="startup_failed",
                error=DashboardError(
                    code="report_dashboard_startup_failed",
                    message=f"Dashboard server failed to initialize: {exc}",
                    source=f"{request.host}:{request.port}",
                    details=format_report_details(
                        operation="make_server",
                        error_type=type(exc).__name__,
                        error=str(exc),
                    ),
                ),
            )

        thread = threading.Thread(
            target=server.serve_forever,
            name=f"report-dashboard-{request.port}",
            daemon=True,
        )
        thread.start()

        if not self._wait_until_health_ready(
            host=request.host,
            port=request.port,
            timeout_seconds=request.startup_timeout_seconds,
        ):
            self._shutdown_runtime_server(
                server=server,
                thread=thread,
                timeout_seconds=1.0,
            )
            return self._error_result(
                request=request,
                snapshot=snapshot,
                warnings=snapshot_warnings,
                startup_status="startup_timeout",
                error=DashboardError(
                    code="report_dashboard_startup_timeout",
                    message=(
                        "Dashboard server did not become ready before timeout "
                        f"({request.startup_timeout_seconds:.2f}s)."
                    ),
                    source=f"{request.host}:{request.port}",
                    details="Retry with a larger --startup-timeout if this machine starts the dashboard slowly.",
                ),
            )

        url = f"http://{request.host}:{request.port}"
        browser_opened = False
        warnings = list(snapshot_warnings)
        if request.auto_open_browser:
            try:
                browser_opened = bool(self._browser_open(url))
                if not browser_opened:
                    warnings.append(
                        DashboardWarning(
                            code="report_dashboard_browser_open_failed",
                            message="Dashboard started, but no browser was opened automatically. Open the local dashboard manually or use --no-open in headless environments.",
                            source=url,
                            details=format_report_details(
                                operation="browser_open",
                                reason="open_returned_false",
                            ),
                        )
                    )
            except Exception as exc:
                warnings.append(
                    DashboardWarning(
                        code="report_dashboard_browser_open_failed",
                        message=(
                            "Dashboard started, but the browser could not be opened automatically. "
                            f"Open the local dashboard manually or use --no-open in headless environments: {exc}"
                        ),
                        source=url,
                        details=format_report_details(
                            operation="browser_open",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                )

        status = DashboardStatus(
            state="running",
            host=request.host,
            port=request.port,
            startup_status="started",
            url=url,
            thread_name=thread.name,
            browser_opened=browser_opened,
            started_at_iso=self._now_provider().isoformat(),
        )
        with self._runtime_lock:
            self._runtimes[(request.host, request.port)] = _DashboardRuntime(
                server=server,
                thread=thread,
                status=status,
            )

        return DashboardStartResult(
            project_path=request.project_path,
            startup_status="started",
            url=url,
            status=status,
            snapshot=snapshot,
            warnings=sort_signals(warnings),
            errors=[],
        )

    def stop(self, host: str, port: int) -> DashboardStatus:
        runtime_key = (host, port)
        with self._runtime_lock:
            runtime = self._runtimes.get(runtime_key)
        url = f"http://{host}:{port}"
        if runtime is None:
            return DashboardStatus(
                state="stopped",
                host=host,
                port=port,
                startup_status="stopped",
                url=url,
                shutdown_status="not_running",
                browser_opened=False,
            )

        shutdown_status = self._shutdown_runtime_server(
            server=runtime.server,
            thread=runtime.thread,
            timeout_seconds=2.0,
        )
        if shutdown_status == "clean":
            with self._runtime_lock:
                self._runtimes.pop(runtime_key, None)
        else:
            with self._runtime_lock:
                # Keep runtime handle for retry on timeout/failed shutdown
                # while the server thread is still alive.
                if runtime.thread.is_alive():
                    self._runtimes[runtime_key] = runtime
                else:
                    self._runtimes.pop(runtime_key, None)

        state = "stopped" if shutdown_status in {"clean", "not_running"} else "failed"
        return DashboardStatus(
            state=state,
            host=host,
            port=port,
            startup_status="stopped",
            url=url,
            shutdown_status=shutdown_status,
            thread_name=runtime.thread.name,
            browser_opened=runtime.status.browser_opened,
            started_at_iso=runtime.status.started_at_iso,
        )

    def _collect_snapshot(
        self,
        project_path: Path,
    ) -> tuple[DashboardDataSnapshot | None, list[DashboardWarning]]:
        try:
            core_snapshot = self._collector.collect(project_path=project_path)
        except Exception as exc:
            return (
                None,
                [
                    DashboardWarning(
                        code="report_dashboard_snapshot_unavailable",
                        message=f"Canonical report snapshot is unavailable: {exc}",
                        source=str(project_path.resolve()),
                        details=format_report_details(
                            operation="collect_snapshot",
                            error_type=type(exc).__name__,
                            error=str(exc),
                        ),
                    )
                ],
            )

        mapped_warnings = [
            DashboardWarning(
                code=warning_code_for("dashboard", signal.reason),
                message=signal.message,
                source=signal.source,
                details=signal.details,
            )
            for signal in core_snapshot.warnings
        ]
        return (
            DashboardDataSnapshot(
                project_name=core_snapshot.project_name,
                project_path=core_snapshot.project_path,
                generated_at_iso=core_snapshot.generated_at_iso,
                stats=core_snapshot.stats.to_payload(),
                config_snapshot=core_snapshot.config_snapshot,
            ),
            sort_signals(mapped_warnings),
        )

    def _error_result(
        self,
        request: DashboardStartRequest,
        snapshot: DashboardDataSnapshot | None,
        warnings: list[DashboardWarning],
        startup_status: str,
        error: DashboardError,
    ) -> DashboardStartResult:
        return DashboardStartResult(
            project_path=request.project_path,
            startup_status=startup_status,
            url=f"http://{request.host}:{request.port}",
            status=DashboardStatus(
                state="failed",
                host=request.host,
                port=request.port,
                startup_status=startup_status,
                url=f"http://{request.host}:{request.port}",
            ),
            snapshot=snapshot,
            warnings=sort_signals(warnings),
            errors=sort_signals([error]),
        )

    @staticmethod
    def _probe_socket_bind_error(host: str, port: int) -> OSError | None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind((host, port))
            except OSError as exc:
                return exc
        return None

    @staticmethod
    def _startup_status_for_bind_error(
        exc: OSError,
        host: str | None = None,
        port: int | None = None,
    ) -> str:
        error_codes = {
            exc.errno,
            getattr(exc, "winerror", None),
        }
        if errno.EADDRINUSE in error_codes or 10048 in error_codes:
            return "port_in_use"
        if (
            (errno.EACCES in error_codes or 10013 in error_codes)
            and host is not None
            and port is not None
            and ReportDashboardAdapter._port_accepts_connections(host, port)
        ):
            return "port_in_use"
        return "startup_failed"

    @classmethod
    def _build_bind_error(
        cls,
        request: DashboardStartRequest,
        exc: OSError,
        startup_status: str,
    ) -> DashboardError:
        address = f"{request.host}:{request.port}"
        if startup_status == "port_in_use":
            return DashboardError(
                code="report_dashboard_port_in_use",
                message=f"Dashboard could not start because {address} is already in use.",
                source=address,
                details="Stop the existing listener or retry with --port <free-port>.",
            )
        return DashboardError(
            code="report_dashboard_startup_failed",
            message=f"Dashboard could not bind to {address}: {exc}",
            source=address,
            details=cls._bind_error_suggestion(exc),
        )

    @staticmethod
    def _bind_error_suggestion(exc: OSError) -> str:
        error_codes = {
            exc.errno,
            getattr(exc, "winerror", None),
        }
        if errno.EADDRNOTAVAIL in error_codes or 10049 in error_codes:
            return "The requested host is not available on this machine. Retry with --host 127.0.0.1 or another local interface."
        if errno.EACCES in error_codes or 10013 in error_codes:
            return "The operating system denied access to this address. Retry with a port above 1024 or check local permissions."
        return "Check the selected --host/--port values and retry."

    @staticmethod
    def _port_accepts_connections(host: str, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.2)
            try:
                return sock.connect_ex((host, port)) == 0
            except OSError:
                return False

    @staticmethod
    def _wait_until_health_ready(host: str, port: int, timeout_seconds: float) -> bool:
        deadline = time.monotonic() + max(timeout_seconds, 0.1)
        health_url = f"http://{host}:{port}/api/health"
        while time.monotonic() < deadline:
            try:
                with urlopen(health_url, timeout=0.2) as response:
                    status_code = getattr(response, "status", 200)
                    if status_code == 200:
                        return True
            except Exception:
                time.sleep(0.05)
        return False

    @staticmethod
    def _shutdown_runtime_server(
        server: object,
        thread: threading.Thread,
        timeout_seconds: float,
    ) -> str:
        try:
            shutdown = getattr(server, "shutdown")
            server_close = getattr(server, "server_close")
            shutdown()
            server_close()
        except Exception:
            return "failed"

        thread.join(timeout=max(timeout_seconds, 0.1))
        if thread.is_alive():
            return "timeout"
        return "clean"
