from dataclasses import dataclass, field
from typing import Optional, List

@dataclass
class Metric:
    value: float
    value_pg: float
    percentile: float
    percentile_order: int
    percentile_total: int
    sample_size: int
    average: float
    z_score: float
    label: str = ""
    label2: str = ""
    bar_label_low: str = ""
    bar_label_high: str = ""
    show_as_percentage: bool = False
    reverse: bool = False
    heatmap: Optional[List[List[float]]] = field(default=None)  # 20x30 grid (4m x 4m cells)
    value_trend: Optional[List[float]] = field(default=None)  # Per-match history: one value per match
    secondary_z_score: Optional[float] = field(default=None)  # For metrics with a secondary z-score (e.g., HI Distance)

    @classmethod
    def default(cls):
        """Create a default Metric with zero values."""
        return cls(
            value=0.0,
            value_pg=0.0,
            percentile=0.0,
            percentile_order=0,
            percentile_total=0,
            sample_size=0,
            average=0.0,
            z_score=0.0,
            label="",
            label2="",
            bar_label_low="Low",
            bar_label_high="High",
            show_as_percentage=False,
            reverse=False,
            heatmap=None,
            value_trend=None
        )

    @classmethod
    def create_empty_heatmap(cls) -> List[List[float]]:
        """
        Create an empty heatmap grid for pitch tracking.

        Returns a 20x30 grid representing a 120m x 80m pitch divided into 4m x 4m cells:
        - 20 rows (height: 80m / 4m)
        - 30 columns (width: 120m / 4m)
        """
        return [[0.0 for _ in range(30)] for _ in range(20)]
