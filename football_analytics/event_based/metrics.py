from dataclasses import dataclass

@dataclass
class Metric:
    value: float
    value_pg: float
    percentile: float
    percentile_order: int
    percentile_total: int
    sample_size: int

    @classmethod
    def default(cls):
        """Create a default Metric with zero values."""
        return cls(
            value=0.0,
            value_pg=0.0,
            percentile=0.0,
            percentile_order=0,
            percentile_total=0,
            sample_size=0
        )
