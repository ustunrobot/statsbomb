# Football Intelligence Frontend

Professional browser-based interface for generating Opposition and Player Reports using StatsBomb data.

## Overview

The frontend is a single-page application (SPA) built with vanilla HTML, CSS, and JavaScript. It communicates with a Python Flask backend via REST API.

## Features

✅ **Competition Selection** - Choose from available league/season combinations  
✅ **Team Selection** - Filter teams based on selected competition  
✅ **Player Selection** - Optional player-specific report generation  
✅ **Real-time Progress** - Live progress updates during report generation  
✅ **Report Generation** - Two report types: Opposition & Player  
✅ **PDF Download** - Direct download of generated reports  
✅ **Responsive Design** - Works on desktop, tablet, and mobile  
✅ **Error Handling** - Clear error messages and recovery options  

## File Structure

```
app_frontend/
├── index.html          # Main HTML page
├── styles.css          # Complete stylesheet with responsive design
├── app.js              # Frontend JavaScript logic
├── README.md           # This file
└── assets/            # (optional) Images, icons, logos
    └── logo.png
```

## Architecture

### Index HTML
- Semantic structure with accessible form controls
- Multiple panels for different application states:
  - **Selection Panel**: Initial form for user input
  - **Status Panel**: Progress display during report generation
  - **Result Panel**: Success state with download link
  - **Error Panel**: Error display and recovery options
- Responsive layout for all screen sizes
- Accessibility features (ARIA labels, keyboard navigation)

### CSS Styling
- CSS Variables for consistent theming
- Mobile-first responsive design
- Dark mode support (auto-detected from system preference)
- Professional animations and transitions
- Accessible color contrast ratios
- Supports older browsers (with graceful degradation)

### JavaScript Logic
- **State Management**: Centralized `appState` object
- **API Integration**: `apiCall()` function with error handling
- **Data Loading**: Asynchronous data fetching and caching
- **Event Handling**: DOM event listeners and handlers
- **Status Polling**: Continuous status updates during report generation
- **Error Recovery**: User-friendly error handling with recovery options

## API Integration

### Expected Endpoints

The frontend expects these API endpoints on the backend:

```
GET  /api/competitions              # List available competitions
GET  /api/teams/<competition_id>   # List teams in competition
GET  /api/players/<team_id>        # List players in team
POST /api/reports/opposition        # Generate opposition report
POST /api/reports/player            # Generate player report
GET  /api/status/<task_id>          # Check report generation status
GET  /api/reports/<task_id>/download # Download generated PDF
```

### Data Formats

#### Competition Object
```json
{
  "id": 5,
  "league": "Premier League",
  "season": "2023/24",
  "year": 2023
}
```

#### Team Object
```json
{
  "id": 123,
  "name": "Manchester United",
  "country": "England",
  "competition_id": 5
}
```

#### Player Object
```json
{
  "id": 456,
  "name": "Marcus Rashford",
  "number": 10,
  "position": "Forward",
  "team_id": 123
}
```

#### API Responses

**Success Response**
```json
{
  "status": "success",
  "data": [...],
  "message": "Operation completed"
}
```

**Error Response**
```json
{
  "status": "error",
  "message": "Detailed error message"
}
```

**Report Generation Response**
```json
{
  "status": "success",
  "task_id": "uuid-string",
  "message": "Report generation started"
}
```

**Status Response (While Generating)**
```json
{
  "status": "generating",
  "progress": 45,
  "message": "Processing match data..."
}
```

**Status Response (Complete)**
```json
{
  "status": "complete",
  "filepath": "/path/to/report.pdf",
  "report_type": "opposition"
}
```

## Development

### Local Testing

1. **Start the backend server**
   ```bash
   python app.py
   ```
   This will start Flask on `http://localhost:5000`

2. **Frontend auto-opens in browser**
   The application automatically opens your default browser to `http://localhost:5000`

3. **Test the workflow**
   - Select a competition
   - Select a team
   - Choose report type
   - Click "Generate Report"
   - Monitor progress
   - Download PDF

### Browser Console

Open browser Developer Tools (F12) to see:
- API call logs
- State updates
- Error messages
- Performance metrics

Example console output:
```
⚽ Football Intelligence Application
API Base URL: http://localhost:5000/api
Status: Ready
Loading competitions...
✓ Loaded 10 competitions
✓ Report generation completed
```

### Customization

#### Colors
Modify CSS variables in `styles.css`:
```css
:root {
    --primary-color: #1e40af;      /* Blue */
    --secondary-color: #06b6d4;    /* Cyan */
    --success-color: #10b981;      /* Green */
    --error-color: #ef4444;        /* Red */
}
```

#### Fonts
```css
:root {
    --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}
```

#### Spacing
```css
:root {
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
}
```

#### Animations
```css
:root {
    --transition: all 0.3s ease;
}
```

## Deployment

### In PyInstaller Executable

When deploying with PyInstaller:

1. **Frontend files are bundled** as static assets
2. **Flask serves the files** automatically
3. **No separate HTTP server needed**
4. **Single-file executable includes everything**

### Directory Structure for PyInstaller

```
football_intelligence_app/
├── app.py                    # Flask entry point
├── frontend/                 # Static files directory
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── assets/
└── ... backend files
```

## Browser Compatibility

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ 90+ | ✅ 90+ |
| Firefox | ✅ 88+ | ✅ 88+ |
| Safari | ✅ 14+ | ✅ 14+ |
| Edge | ✅ 90+ | ✅ 90+ |

## Accessibility

- ✅ WCAG 2.1 Level AA compliant
- ✅ Keyboard navigation support
- ✅ Screen reader friendly
- ✅ High contrast mode support
- ✅ Reduced motion support

## Performance

- **Initial Load**: ~1-2 seconds (with cached assets)
- **API Calls**: Typically under 500ms
- **Report Generation**: 30-300 seconds (depends on data size)
- **File Size**:
  - HTML: ~12KB
  - CSS: ~20KB
  - JS: ~18KB
  - **Total: ~50KB (uncompressed)**

## Troubleshooting

### Backend Connection Error
**Problem**: "Failed to initialize the application"  
**Solution**: Ensure Flask backend is running on `http://localhost:5000`

### Dropdown Not Populating
**Problem**: Teams/Players dropdowns remain empty  
**Solution**: Check network tab in browser dev tools to verify API calls are succeeding

### Report Stuck Generating
**Problem**: Progress bar stuck at 0%  
**Solution**: 
- Check browser console for errors
- Verify backend server is responding
- Try refreshing the page and starting over

### Slow Performance
**Problem**: Selections/button clicks are slow  
**Solution**:
- Check internet connection
- Verify backend server performance
- Check browser for resource-heavy extensions

## API Configuration

The frontend expects the backend on `http://localhost:5000`. To change this:

Edit `app.js`:
```javascript
const API_BASE_URL = 'http://your-backend:5000/api';
```

## Support for Multiple Languages

The frontend is currently in English. To add language support:

1. Create language files:
   ```
   i18n/
   ├── en.json
   ├── es.json
   ├── fr.json
   └── de.json
   ```

2. Implement i18n library (e.g., i18next)

3. Replace text with i18n keys:
   ```javascript
   // Before
   'Please select a team'
   
   // After
   i18n.t('errors.selectTeam')
   ```

## Future Enhancements

- [ ] Dark mode toggle button
- [ ] Report templates selection
- [ ] Batch report generation
- [ ] Report history/archive
- [ ] User authentication
- [ ] Internationalization (i18n)
- [ ] Advanced filters (date range, player position, etc.)
- [ ] Real-time collaboration
- [ ] Email report delivery
- [ ] Team comparison reports

## License

This application is part of the Football Intelligence platform. All rights reserved.

## Support

For issues or questions:
1. Check browser console (F12)
2. Verify backend is running
3. Try refreshing the page
4. Contact support@footballintelligence.app
