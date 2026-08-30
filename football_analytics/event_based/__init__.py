"""Event-based analytics pipeline: Data provider + Event processor + KPI layers."""

from .data_provider import DataProvider
from .event_processor import EventProcessor, KPIAccumulator

__all__ = ["DataProvider", "EventProcessor", "KPIAccumulator"]
