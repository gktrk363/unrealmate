"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        UnrealMate - Project Health                           ║
║                                                                              ║
║  Author: gktrk363                                                            ║
║  Purpose: Project health monitoring and quality metrics                      ║
║  Created: 2026-02-06                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝

Calculates project health score based on various metrics.

© 2026 gktrk363 - Crafted with passion for Unreal Engine developers
"""

from typing import Dict

class HealthScoreCalculator:
    """
    Calculates a 0-100 score for the project health.
    """
    def __init__(self):
        self.metrics = {}

    def calculate(self, metrics: Dict[str, float]) -> int:
        """
        Calculates weighted average of provided metrics.
        metrics: dict of 'metric_name': score (0-100)
        """
        if not metrics:
            return 0
        
        total_weight = 0
        total_score = 0
        
        # Example weights
        weights = {
            "test_coverage": 0.4,
            "lint_score": 0.3,
            "asset_optimization": 0.3
        }

        for name, score in metrics.items():
            weight = weights.get(name, 0.1)
            total_score += score * weight
            total_weight += weight
            
        if total_weight == 0:
            return 0
            
        return int(total_score / total_weight)

class CodeQualityMetrics:
    """
    Aggregates code quality metrics.
    """
    def get_test_coverage(self) -> float:
        # Placeholder for actual coverage report parsing
        return 56.0 # Mock current value

    def get_lint_score(self) -> float:
        # Placeholder for lint output parsing
        return 95.0
