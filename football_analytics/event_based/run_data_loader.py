#!/usr/bin/env python3
"""Demo script for data provider."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from football_analytics.event_based.data_provider import DataProvider

if __name__ == "__main__":
    provider = DataProvider()
    matches = provider.get_matches()
    print(f"Loaded {len(matches)} matches")
    for filename, data in matches[:5]:
        print(f"  - {filename}: {len(data)} events")
