# Football Analytics Library

Professional football analytics platform built on StatsBomb event data. Modular architecture supports easy extension with new metrics.

## Project Structure

```
football_analytics/
├── data/
│   ├── teams/              # StatsBomb JSON event files (by team folder)
│   └── outputs/            # Generated CSV reports
├── metrics/
│   ├── base.py             # BaseMetric abstract class
│   ├── in_possession/
│   │   ├── style_of_play.py           # Possession patterns & zones
│   │   └── buildup_tactical.py        # Defensive-to-attack transitions
│   └── out_of_possession/
│       └── style_of_defense.py        # [SCAFFOLD] Defensive analysis
├── pipelines/
│   └── match_pipeline.py   # Orchestration & CLI
├── utils/
│   ├── statsbomb_loader.py # Data loading & normalization
│   ├── pitch_zones.py      # Zone definitions & helpers
│   └── sequence_builder.py # Possession sequence grouping
├── tests/
│   ├── test_style_of_play.py
│   └── test_buildup_tactical.py
├── notebooks/
│   └── exploration.ipynb   # Jupyter for ad-hoc analysis
├── requirements.txt
└── README.md
```

## Installation

```bash
cd football_analytics
pip install -r requirements.txt
```

## Usage

### Command-line Interface

#### Single Match
```bash
python -m pipelines.match_pipeline single-match --match data/teams/Arsenal/Week1_match.json
```

#### Team Season
```bash
python -m pipelines.match_pipeline team-season --team Arsenal
```

#### Full League
```bash
python -m pipelines.match_pipeline full-league
# Or specific teams:
python -m pipelines.match_pipeline full-league --teams Arsenal Chelsea Liverpool
```

### Python API

```python
from utils.statsbomb_loader import load_match_events
from metrics.in_possession.style_of_play import StyleOfPlay

# Load match
events_df = load_match_events('data/teams/Arsenal/match.json')

# Compute metrics
metrics = StyleOfPlay(events_df, 'Arsenal')
results = metrics.compute()

print(results)
```

## Pitch Coordinate System

StatsBomb uses a 120m (length) × 80m (width) pitch with origin at bottom-left.

- **X-axis**: 0 (own goal line) → 120 (opponent goal line)
- **Y-axis**: 0 (left sideline) → 80 (right sideline)

### Pitch Zones
- **Buildup zone** (Defensive third): x < 40
- **Middle third**: 40 ≤ x ≤ 80
- **Final third** (Attacking): x > 80

### Lanes
- **Left**: y < 20
- **Central**: 20 ≤ y ≤ 60
- **Right**: y > 60

See `utils/pitch_zones.py` for zone helper functions.

## Metrics

### In Possession

#### StyleOfPlay (Module A1)
Quantifies overall possession patterns:

- **PZDI**: Possession Zone Distribution — % of touches in each third
- **PVLI**: Pass Verticality & Length — how forward/direct are passes
- **SDBF**: Sequence Depth Before Final Third — buildup patience
- **CPPR**: Carry-to-Pass Progression Ratio — dribble vs pass progression
- **CSS**: Consecutive Pass Sequences — how many 5+/10+/15+ pass chains
- **TEMPO**: Ball Release Tempo — decision-making speed (seconds)

All metrics prefixed `sop_`.

#### BuildupTactical (Module A2)
Deep analysis of defensive-to-attack transitions:

- **INIT**: Initiation Structure — who starts buildup (GK/CB/FB/DM)
- **GK_DIST**: Goalkeeper Distribution — pass types under different press levels
- **GK_ROLE**: Goalkeeper Role — classify passes (short/medium/long/bypass)
- **ESCAPE**: Press Escape — methods for escaping high press
- **NETWORK**: Passing Network — key position-to-position connections
- **BUILDUP_STYLE**: Direct vs Patient Buildup — classification by event count
- **WIDTH**: Buildup Width — lateral distribution and compactness

All metrics prefixed `bt_`.

### Out of Possession

#### StyleOfDefense (Module B1)
[SCAFFOLD - Placeholder for future implementation]

Planned defensive metrics:
- Defensive line height and press trigger detection
- PPDA (Passes Per Defensive Action)
- Compactness and block shape
- Transition press response time

## Testing

Run pytest:
```bash
pytest tests/ -v
```

Tests cover:
- Normal cases with realistic data
- Edge cases (empty zones, missing events)
- Specific metric logic (sequence counting, etc.)

## Data Format

Events are stored as JSON files (one per match) in team folders:

```
data/teams/Arsenal/
├── Week1_Arsenal_vs_Chelsea.json
├── Week2_Liverpool_vs_Arsenal.json
└── ...
```

Each JSON is a dictionary of event UUIDs → event objects. `statsbomb_loader.py` normalizes this into a flat DataFrame with:

- **Core**: id, index, timestamp, period, minute, second, team, player, position, type_name
- **Location**: x, y (from location [x, y] array)
- **Pass**: pass_length, pass_angle, pass_end_x, pass_end_y, pass_recipient_name, pass_height_name, pass_type_name
- **Carry**: carry_end_x, carry_end_y
- **Goalkeeper**: gk_end_x, gk_end_y, gk_type_name, gk_position_name

## Architecture Notes

### Modularity
Each metric module (StyleOfPlay, BuildupTactical) is independent. New metrics:

1. Create new file under `metrics/{in_possession|out_of_possession}/`
2. Inherit from `BaseMetric`
3. Implement `compute() → dict`
4. Register in `pipelines/match_pipeline.py`

### Type Hints & Documentation
All public methods have:
- Type hints on parameters and return values
- Docstrings explaining what metric measures
- Football interpretation (high/low tactical meaning)

### Constants
All thresholds are named module-level constants (no magic numbers):
```python
BUILDUP_X_THRESHOLD = 40.0
PROGRESSIVE_PASS_THRESHOLD = 9.14
```

### Error Handling
Pipeline gracefully continues on per-module failures:
```python
try:
    sop = StyleOfPlay(events_df, team)
    result.update(sop.compute())
except Exception as e:
    print(f"Warning: StyleOfPlay failed: {e}")
```

## Outputs

Metrics are saved to `data/outputs/league_metrics_{timestamp}.csv` with one row per match:

| team | match_id | sop_pzdi_def_pct | sop_pzdi_mid_pct | ... | bt_buildup_width_std | ... |
|------|----------|-----------------|-----------------|-----|----------------------|-----|
| Arsenal | 123456 | 35.2 | 40.1 | ... | 12.4 | ... |
| Chelsea | 123457 | 28.5 | 45.3 | ... | 14.1 | ... |

## Future Work

1. **StyleOfDefense**: Implement defensive metrics (PPDA, press triggers, compactness)
2. **Advanced Possession**: Off-ball runs, overload analysis, press resistance
3. **Set Pieces**: Corner/free kick efficiency, defensive set piece organization
4. **Transition**: Direct play, counter-attack speed, transition success rates
5. **Player-level**: Per-player metrics beyond team aggregates
6. **Visualizations**: Heatmaps, pass maps, defensive shapes

## References

- StatsBomb Events Specification: https://statsbomb.com/
- Football Analytics principles: https://www.pinnergold.com/
- Expected Threat model: https://github.com/kasmircak/xT
