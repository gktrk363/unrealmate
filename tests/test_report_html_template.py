# ═══════════════════════════════════════════════════════════════════════════════
#  UnrealMate - Test Report Html Template
#  Author: G & E ZYNTH
#  © 2026 G & E ZYNTH - Crafted with passion for Unreal Engine developers
# ═══════════════════════════════════════════════════════════════════════════════

"""HTML template helper stability tests for report domain."""

from __future__ import annotations

from pathlib import Path

from unrealmate.adapters.report.report_html_template import render_report_html_document


def test_html_template_render_is_stable_for_same_input() -> None:
    payload = {
        "uproject_files": 1,
        "cpp_source_files": 2,
        "blueprint_assets": 3,
        "scene_maps": 4,
    }
    config = {
        "performance": {
            "cache_enabled": True,
            "parallel_processing": True,
            "max_workers": 8,
        },
        "git": {"auto_lfs": False},
    }

    first = render_report_html_document(
        project_name="TemplateGame",
        project_path=Path("/tmp/template-game"),
        generated_at_iso="2026-04-03T13:14:15",
        stats_payload=payload,
        python_script_count=5,
        config_snapshot=config,
    )
    second = render_report_html_document(
        project_name="TemplateGame",
        project_path=Path("/tmp/template-game"),
        generated_at_iso="2026-04-03T13:14:15",
        stats_payload=payload,
        python_script_count=5,
        config_snapshot=config,
    )

    assert first == second
    assert "<html" in first.lower()
    assert "TemplateGame - Project Report" in first
    assert "Python scripts</td><td>5" in first
    assert "Cache enabled</td><td>True" in first
