# Football Intelligence Backend

Professional Flask backend for the Football Intelligence application.

## Overview

The backend provides:
- REST API endpoints for competitions, teams, and players
- StatsBomb API integration with caching
- Report generation orchestration
- Seamless frontend integration

## Quick Start

### 1. Installation

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configuration

Create a `.env` file in the project root (optional, has defaults):

```env
DEBUG=False
PORT=5000
STATSBOMB_API_USER=ustunrobot@gmail.com
STATSBOMB_API_PASSWORD=waQMIar2
```

### 3. Run the Application

```bash
# From the app_backend directory
python app.py

# Or from the project root
python football_analytics/app_backend/app.py
```

Expected output:
```
╔═══════════════════════════════════════════════════════════╗
║     Football Intelligence Application                     ║
║                                                           ║
║  Server running on: http://127.0.0.1:5000               ║
║  Opening browser in 2 seconds...                         ║
║                                                           ║
║  Press Ctrl+C to stop the application                    ║
╚═══════════════════════════════════════════════════════════╝
```

Browser automatically opens to `http://localhost:5000`

## API Endpoints

### Competitions

**GET /api/competitions**

Fetch all available competitions from StatsBomb API.

Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": 5,
      "league": "EFL League Two",
      "season": "2024/25",
      "season_id": 318,
      "country": "England",
      "year": 2024
    },
    {
      "id": 5,
      "league": "EFL League Two",
      "season": "2025/26",
      "season_id": 351,
      "country": "England",
      "year": 2025
    }
  ],
  "count": 2
}
```

### Teams

**GET /api/teams/{competition_id}**

Fetch teams in a competition. Uses latest season by default.

Query Parameters:
- `season_id` (optional): Specific season ID

Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": 123,
      "name": "Manchester United"
    },
    {
      "id": 124,
      "name": "Liverpool"
    }
  ],
  "count": 2
}
```

### Players

**GET /api/players/{team_id}**

Fetch players in a team.

Query Parameters (Required):
- `competition_id`: Competition ID
- `season_id`: Season ID

Response:
```json
{
  "status": "success",
  "data": [
    {
      "id": 456,
      "name": "Marcus Rashford",
      "number": 10
    },
    {
      "id": 457,
      "name": "Bruno Fernandes",
      "number": 18
    }
  ],
  "count": 2
}
```

### Health

**GET /api/health**

Check if the API is running.

Response:
```json
{
  "status": "ok",
  "message": "Football Intelligence API is running"
}
```

## Architecture

```
app_backend/
├── app.py                      # Flask application
├── statsbomb_service.py        # StatsBomb API integration
├── __init__.py                 # Package marker
└── README.md                   # This file
```

### Key Components

#### StatsBombService
```python
from app_backend.statsbomb_service import get_service

service = get_service()
competitions = service.get_competitions()
teams = service.get_teams(competition_id, season_id)
players = service.get_players(competition_id, season_id, team_id)
```

Features:
- Automatic caching of results
- Error handling and logging
- Uses default StatsBomb credentials
- Pandas DataFrame manipulation for data transformation

#### Flask App
- Serves frontend (index.html, styles.css, app.js)
- Provides REST API endpoints
- CORS enabled for localhost
- Comprehensive error handling
- Automatic browser opening on startup

## Credentials

The application uses the following StatsBomb API credentials (from data_loader.py):

```python
{
    "user": "ustunrobot@gmail.com",
    "passwd": "waQMIar2",
}
```

These are embedded in the code and automatically used by `StatsBombService`.

## Caching

The service automatically caches:
- **Competitions**: Cached indefinitely per session
- **Teams**: Cached by `competition_id_season_id`
- **Players**: Cached by `competition_id_season_id_team_id`

Clear cache:
```python
service = get_service()
service.clear_cache()
```

## Error Handling

All endpoints return JSON with status:

Success:
```json
{
  "status": "success",
  "data": [...],
  "count": 10
}
```

Error:
```json
{
  "status": "error",
  "message": "Detailed error message"
}
```

HTTP status codes:
- `200`: Success
- `400`: Bad request (missing parameters)
- `404`: Not found
- `500`: Server error

## Logging

Logs are output to console with format:
```
YYYY-MM-DD HH:MM:SS - module_name - LOG_LEVEL - message
```

Example:
```
2024-01-15 10:30:45,123 - app - INFO - Starting Flask server on 127.0.0.1:5000
2024-01-15 10:30:47,456 - app - INFO - Fetching competitions...
2024-01-15 10:30:48,789 - app_backend.statsbomb_service - INFO - ✓ Fetched 50 competitions
```

## Development

### Running Tests

```bash
# To add later - pytest tests/
```

### Debug Mode

Set `DEBUG=True` in `.env` to enable Flask debug mode:
```env
DEBUG=True
```

This enables:
- Auto-reload on code changes
- Enhanced error messages
- Python debugger access

### Testing API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Get competitions
curl http://localhost:5000/api/competitions

# Get teams (competition_id=5)
curl http://localhost:5000/api/teams/5

# Get players (team_id=123, competition_id=5, season_id=318)
curl "http://localhost:5000/api/players/123?competition_id=5&season_id=318"
```

## Performance

- **Initial API load**: 2-5 seconds (fetches 50+ competitions from StatsBomb)
- **Teams fetch**: < 1 second
- **Players fetch**: 2-5 seconds (fetches match events)
- **Subsequent calls**: < 100ms (using cache)

## Troubleshooting

### "Failed to connect to StatsBomb API"

**Cause**: Invalid credentials or StatsBomb API down  
**Solution**:
1. Verify credentials in `statsbomb_service.py`
2. Check internet connection
3. Try StatsBomb website to ensure API is up

### "No competitions returned"

**Cause**: API response issue or credentials expired  
**Solution**:
1. Clear cache: `service.clear_cache()`
2. Check API credentials
3. Test with `statsbombpy` directly

### "Port 5000 already in use"

**Solution**:
1. Kill existing process on port 5000
2. Or change PORT in `.env`:
   ```env
   PORT=5001
   ```

### "ModuleNotFoundError"

**Solution**:
```bash
# Ensure in correct directory and venv activated
cd /home/baris/statsbomb
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## Next Steps

1. **Implement Report Generation**
   - Create `/api/reports/opposition` endpoint
   - Create `/api/reports/player` endpoint
   - Integrate with section0-7 code

2. **Add Database**
   - SQLite for local caching
   - Store competitions, teams, players
   - Track report generation history

3. **Implement Status/Download**
   - `/api/status/{task_id}` for progress
   - `/api/reports/{task_id}/download` for PDF download
   - Background task processing

4. **Authentication** (Optional)
   - User login/logout
   - API key validation
   - Rate limiting

## File Structure

```
football_analytics/
├── app_backend/              # ← Backend code
│   ├── app.py               # Flask application
│   ├── statsbomb_service.py # API integration
│   ├── __init__.py
│   └── README.md
│
├── app_frontend/            # Frontend code
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── config.py
│
└── opposition_report/       # Report generation
    ├── section0.py
    ├── section1.py
    └── ... (sections 1-7)
```

## Support

For issues:
1. Check console logs for error messages
2. Verify StatsBomb API is accessible
3. Clear cache and restart application
4. Check network connectivity
5. Review error responses in browser DevTools

## License

Part of Football Intelligence platform. All rights reserved.
