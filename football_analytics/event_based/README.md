# Event-Based Analytics Pipeline

A modular, scalable pipeline for processing StatsBomb match events and accumulating KPI metrics through specialized layers.

## Architecture

```
event_based/
├── data_provider.py          # Collects & deduplicates match files
├── event_processor.py        # Routes events through KPI layers
├── kpi/
│   ├── __init__.py
│   ├── xg_layer.py          # Expected goals metrics
│   ├── dribbling_layer.py   # Dribbling & ball-carrying
│   └── ... (extensible for more KPI layers)
└── example_usage.py         # Sample pipeline execution
```

## How It Works

### 1. DataProvider
**Responsibility:** Identifies and loads match event files

```python
from football_analytics.event_based import DataProvider

provider = DataProvider()
matches = provider.get_matches(
    seasons=['25-26', '26-27'],  # Seasons to include
)

# Returns list of (filename, events_dict) tuples
for filename, events_dict in matches:
    print(f"{filename}: {len(events_dict)} events")
```

**Features:**
- Scans all team directories for match files
- Deduplicates files (same match in both team folders → processed once)
- Filters out 360frames files
- Returns events in chronological order (Week 1, 2, 3, ...)

### 2. EventProcessor
**Responsibility:** Orchestrates event-by-event processing through KPI layers

```python
from football_analytics.event_based import EventProcessor

processor = EventProcessor()

# Process events (routes through all registered KPI layers)
results = processor.process_event_file(events_dict, filename)

# Returns KPI accumulator for all teams in the match
# Structure: { team_id: { 'team_name': str, 'xg': {...}, 'dribbling': {...} } }
```

### 3. KPI Layers
**Responsibility:** Process specific event types and accumulate metrics

Each KPI layer is independent and follows the same pattern:

```python
class MyKPILayer:
    def __init__(self):
        self.layer_name = "my_kpi"
    
    def process_event_row(self, event_row: Dict, accumulator):
        """Process a single event and update accumulator."""
        team_id = self._get_team_id(event_row)
        team = accumulator.get_team(team_id)
        
        if "my_kpi" not in team:
            team["my_kpi"] = {/* initialization */}
        
        # Process event and update team["my_kpi"]
```

## Example: Full Pipeline

```python
from football_analytics.event_based import DataProvider, EventProcessor

# Step 1: Collect matches
provider = DataProvider()
matches = provider.get_matches(seasons=['25-26'])

# Step 2: Process events
processor = EventProcessor()
all_results = {}

for filename, events_dict in matches:
    results = processor.process_event_file(events_dict, filename)
    all_results[filename] = results

# Step 3: Access results
for match_file, kpi_results in all_results.items():
    for team_id, team_data in kpi_results.items():
        xg = team_data['xg']
        print(f"{team_data['team_name']}: xGF={xg['xgf']:.2f}, Goals={xg['goals']}")
```

## KPI Layers

### XG Layer (`xg_layer.py`)
Tracks expected goals and shot metrics.

**Metrics per team:**
- `xgf`: Expected goals for
- `xga`: Expected goals against
- `xgf_open_play`: xG from open play
- `xgf_set_piece`: xG from set pieces
- `xgf_free_kick`: xG from free kicks
- `goals`: Actual goals scored
- `shots`: Total shot attempts
- `shots_on_target`: Shots on target

**Example output:**
```python
team_data['xg'] = {
    'xgf': 1.234,
    'xga': 0.567,
    'xgf_open_play': 0.890,
    'xgf_set_piece': 0.344,
    'xgf_free_kick': 0.0,
    'goals': 2,
    'shots': 12,
    'shots_on_target': 5
}
```

### Dribbling Layer (`dribbling_layer.py`)
Template for tracking dribbling metrics (extensible).

**Metrics per team:**
- `dribbles`: Total dribble attempts
- `dribbles_completed`: Successful dribbles
- `dribbles_failed`: Failed dribbles
- `dribbles_success_rate`: Success percentage

## Adding New KPI Layers

1. Create a new file in `kpi/` folder (e.g., `passing_layer.py`)
2. Implement the layer class with `process_event_row()` method
3. Register it in `EventProcessor._register_default_layers()` or manually via `processor.register_layer()`

```python
# In event_processor.py
def _register_default_layers(self):
    self.register_layer(XGLayer())
    self.register_layer(DribblingLayer())
    self.register_layer(PassingLayer())  # Your new layer
```

## File Structure

Each match file is identified by its filename (deduplication key):
```
Week1_Accrington Stanley_vs_Gillingham.json
Week2_Barnet_vs_Fleetwood Town.json
...
```

Teams are stored in subdirectories:
```
data/teams/
├── Accrington Stanley/
│   ├── 25-26/
│   │   ├── Week1_Accrington Stanley_vs_Gillingham.json
│   │   ├── Week2_Barnet_vs_Accrington Stanley.json
│   │   └── ...
│   └── 26-27/
└── Barnet/
    ├── 25-26/
    └── 26-27/
```

## Notes

- **Deduplication:** Same match appears in both team folders with identical filenames. Processing ensures each file is loaded and processed exactly once.
- **Data Quality:** Events are processed sequentially; errors in individual events don't stop pipeline.
- **Extensibility:** New KPI layers can be added independently without modifying existing code.
- **Performance:** Processes events in order; suitable for sequential, single-threaded analysis.

## Testing

Run the example to verify setup:

```bash
python -c "
from football_analytics.event_based import DataProvider, EventProcessor

provider = DataProvider()
processor = EventProcessor()

matches = provider.get_matches(seasons=['26-27'])
for filename, events_dict in matches[:2]:
    results = processor.process_event_file(events_dict, filename)
    print(f'✓ {filename}')
"
```
