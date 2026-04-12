"""Rendered HTML regression coverage for the active report dashboard UI."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from unrealmate.core.team_dashboard import (
    ActivityEvent,
    BuildStatus,
    ProjectHealth,
    TeamDashboard,
    TeamMember,
)


pytest.importorskip("flask")


class _FakeDashboardDataProvider:
    def __init__(
        self,
        *,
        health: ProjectHealth,
        builds: list[BuildStatus],
        team: list[TeamMember],
        activity: list[ActivityEvent],
    ) -> None:
        self._health = health
        self._builds = builds
        self._team = team
        self._activity = activity

    def get_project_health(self) -> ProjectHealth:
        return self._health

    def get_build_history(self, limit: int = 10) -> list[BuildStatus]:
        return self._builds[:limit]

    def get_team_members(self) -> list[TeamMember]:
        return self._team

    def get_recent_activity(self, limit: int = 20) -> list[ActivityEvent]:
        return self._activity[:limit]


def _build_dashboard(
    tmp_path: Path,
    *,
    report_core_snapshot: dict | None,
    health: ProjectHealth,
    builds: list[BuildStatus],
    team: list[TeamMember],
    activity: list[ActivityEvent],
):
    project = tmp_path / "DashboardUiProject"
    project.mkdir(parents=True, exist_ok=True)
    dashboard = TeamDashboard(
        project_path=str(project),
        report_core_snapshot=report_core_snapshot,
    )
    dashboard.data_provider = _FakeDashboardDataProvider(
        health=health,
        builds=builds,
        team=team,
        activity=activity,
    )
    app = dashboard._create_app()
    assert app is not None
    return app.test_client()


def test_team_dashboard_root_page_surfaces_experimental_secondary_artifact_truth(
    tmp_path: Path,
) -> None:
    health = ProjectHealth(
        overall_score=82,
        build_health=88,
        code_quality=79,
        test_coverage=74,
        asset_health=86,
        last_updated=datetime(2026, 4, 9, 15, 30, 0),
        issues=["Recent build failures detected"],
    )
    builds = [
        BuildStatus(
            status="success",
            started_at=datetime(2026, 4, 9, 15, 0, 0),
            finished_at=datetime(2026, 4, 9, 15, 4, 30),
            configuration="Development",
            platform="Win64",
            error_count=0,
            warning_count=2,
        )
    ]
    team = [
        TeamMember(
            name="Ayla Stone",
            email="ayla@example.com",
            role="Developer",
            last_activity=datetime(2026, 4, 9, 14, 45, 0),
            recent_commits=5,
        )
    ]
    activity = [
        ActivityEvent(
            id="abc12345",
            type="commit",
            title="Refine dashboard summary copy",
            description="",
            author="Ayla Stone",
            timestamp=datetime(2026, 4, 9, 14, 40, 0),
        )
    ]
    snapshot = {
        "project_name": "DashboardUiProject",
        "project_path": str((tmp_path / "DashboardUiProject").resolve()),
        "generated_at_iso": "2026-04-09T15:32:00",
        "stats": {
            "uproject_files": 1,
            "cpp_source_files": 14,
            "blueprint_assets": 27,
            "scene_maps": 4,
        },
    }

    client = _build_dashboard(
        tmp_path,
        report_core_snapshot=snapshot,
        health=health,
        builds=builds,
        team=team,
        activity=activity,
    )

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Project Dashboard" in html
    assert "Experimental" in html
    assert "CLI-launched secondary surface" in html
    assert "Use report json" in html
    assert "stable local report artifacts." in html
    assert "Generated from local report data" in html
    assert "UProject files" in html
    assert "C++ source" in html
    assert "Blueprint assets" in html
    assert "Scene maps" in html
    assert "Powered by UnrealMate CLI" in html


def test_team_dashboard_root_page_has_truthful_empty_states(tmp_path: Path) -> None:
    health = ProjectHealth(
        overall_score=71,
        build_health=73,
        code_quality=70,
        test_coverage=68,
        asset_health=74,
        last_updated=datetime(2026, 4, 9, 16, 0, 0),
        issues=[],
    )

    client = _build_dashboard(
        tmp_path,
        report_core_snapshot=None,
        health=health,
        builds=[],
        team=[],
        activity=[],
    )

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "Local report snapshot is unavailable for this run" in html
    assert "No recent build logs were found in this project." in html
    assert "No team activity was detected from local git history." in html
    assert "No recent git activity was found for this project yet." in html


def test_team_dashboard_root_page_is_local_first_and_self_contained(tmp_path: Path) -> None:
    health = ProjectHealth(
        overall_score=64,
        build_health=61,
        code_quality=67,
        test_coverage=59,
        asset_health=70,
        last_updated=datetime(2026, 4, 9, 16, 10, 0),
        issues=["Test coverage below threshold"],
    )

    client = _build_dashboard(
        tmp_path,
        report_core_snapshot=None,
        health=health,
        builds=[],
        team=[],
        activity=[],
    )

    response = client.get("/")
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "fonts.googleapis.com" not in html
    assert "Auto-refresh every 30s" in html
    assert "Secondary visual surface for local project data" in html
