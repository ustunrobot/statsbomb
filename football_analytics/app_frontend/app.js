/**
 * Football Intelligence Application - Frontend JavaScript
 * Handles API calls, UI state management, and report generation
 */

// ============================================================================
// Configuration
// ============================================================================

// Detect API base URL dynamically
const API_BASE_URL = window.location.origin + '/api';
const POLL_INTERVAL = 2000; // 2 seconds
const REQUEST_TIMEOUT = 300000; // 5 minutes

console.log('API Base URL:', API_BASE_URL);

// ============================================================================
// State Management
// ============================================================================

const appState = {
    competitions: [],
    teams: [],
    players: [],
    selectedCompetition: null,
    selectedSeasonId: null,
    selectedTeam: null,
    selectedPlayer: null,
    reportType: 'opposition',
    currentTaskId: null,
    isGenerating: false,
};

// ============================================================================
// DOM Elements
// ============================================================================

const elements = {
    // Selectors
    competitionSelect: document.getElementById('competitionSelect'),
    teamSelect: document.getElementById('teamSelect'),
    playerSelect: document.getElementById('playerSelect'),
    reportTypeRadios: document.querySelectorAll('input[name="reportType"]'),

    // Buttons
    generateBtn: document.getElementById('generateBtn'),
    downloadFullSeasonBtn: document.getElementById('downloadFullSeasonBtn'),
    downloadWeeklyBtn: document.getElementById('downloadWeeklyBtn'),
    generateAnotherBtn: document.getElementById('generateAnotherBtn'),
    dismissErrorBtn: document.getElementById('dismissErrorBtn'),

    // Panels
    selectionPanel: document.querySelector('.selection-panel'),
    statusPanel: document.getElementById('statusPanel'),
    resultPanel: document.getElementById('resultPanel'),
    errorPanel: document.getElementById('errorPanel'),

    // Status elements
    statusPanelTitle: document.querySelector('.status-panel h2'),
    statusTitle: document.getElementById('statusTitle'),
    statusMessage: document.getElementById('statusMessage'),
    progressBar: document.getElementById('progressBar'),
    progressFill: document.getElementById('progressFill'),
    progressText: document.getElementById('progressText'),
    statusDetails: document.getElementById('statusDetails'),
    statusDetail1: document.getElementById('statusDetail1'),
    statusDetail2: document.getElementById('statusDetail2'),

    // Result elements
    resultTitle: document.getElementById('resultTitle'),
    resultSubtitle: document.getElementById('resultSubtitle'),
    downloadLink: document.getElementById('downloadLink'),
    resultMessage: document.getElementById('resultMessage'),

    // Error elements
    errorTitle: document.getElementById('errorTitle'),
    errorMessage: document.getElementById('errorMessage'),

    // Footer
    versionInfo: document.getElementById('versionInfo'),

    // Initial load
    initialLoadSpinner: document.getElementById('initialLoadSpinner'),
};

// ============================================================================
// Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    console.log('Football Intelligence App Initializing...');
    initializeApp();
});

async function initializeApp() {
    try {
        // Load competitions on startup
        await loadCompetitions();

        // Attach event listeners
        attachEventListeners();

        // Hide initial load spinner
        hideInitialLoadSpinner();

        console.log('✓ Application initialized successfully');
    } catch (error) {
        console.error('✗ Initialization failed:', error);
        showError('Initialization Error', 'Failed to initialize the application. Please refresh the page.');
    }
}

function attachEventListeners() {
    // Competition selection
    elements.competitionSelect.addEventListener('change', async (e) => {
        const selectedValue = e.target.value;
        appState.selectedTeam = null;
        appState.selectedPlayer = null;

        elements.teamSelect.value = '';
        elements.playerSelect.value = '';

        if (selectedValue) {
            // Parse competition data from JSON
            const competitionData = JSON.parse(selectedValue);
            appState.selectedCompetition = competitionData.id;
            appState.selectedSeasonId = competitionData.season_id;

            await loadTeams(appState.selectedCompetition, appState.selectedSeasonId);
        } else {
            appState.selectedCompetition = null;
            appState.selectedSeasonId = null;
            appState.teams = [];
            updateTeamSelect();
        }

        updateGenerateButton();
    });

    // Team selection
    elements.teamSelect.addEventListener('change', async (e) => {
        appState.selectedTeam = e.target.value;
        appState.selectedPlayer = null;
        elements.playerSelect.value = '';

        console.log(`Team selected: ${appState.selectedTeam}`);
        console.log(`Current appState:`, {
            competition: appState.selectedCompetition,
            seasonId: appState.selectedSeasonId,
            team: appState.selectedTeam
        });

        if (appState.selectedTeam) {
            if (!appState.selectedCompetition || !appState.selectedSeasonId) {
                console.error('ERROR: Competition or Season ID not set!', appState);
                showError('Selection Error', 'Please select a competition first');
                return;
            }
            await loadPlayers(appState.selectedTeam, appState.selectedCompetition, appState.selectedSeasonId);
        } else {
            appState.players = [];
            updatePlayerSelect();
        }

        updateGenerateButton();
    });

    // Player selection
    elements.playerSelect.addEventListener('change', (e) => {
        appState.selectedPlayer = e.target.value;
        updateGenerateButton();
    });

    // Report type selection
    elements.reportTypeRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            appState.reportType = e.target.value;
            updateGenerateButton();
        });
    });

    // Generate button
    elements.generateBtn.addEventListener('click', () => {
        generateReport();
    });

    // Download Full Season button
    elements.downloadFullSeasonBtn.addEventListener('click', () => {
        downloadFullSeason();
    });

    // Download Weekly Data button
    elements.downloadWeeklyBtn.addEventListener('click', () => {
        downloadWeeklyData();
    });

    // Generate another button
    elements.generateAnotherBtn.addEventListener('click', () => {
        resetUI();
    });

    // Dismiss error button
    elements.dismissErrorBtn.addEventListener('click', () => {
        hideError();
    });
}

// ============================================================================
// API Calls
// ============================================================================

async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const fullUrl = `${API_BASE_URL}${endpoint}`;
        console.log(`[API] ${method} ${fullUrl}`);

        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            },
        };

        if (body) {
            options.body = JSON.stringify(body);
        }

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

        const response = await fetch(fullUrl, {
            ...options,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        console.log(`[API] Response: ${response.status} ${response.statusText}`);

        const data = await response.json();
        console.log(`[API] Data:`, data);

        if (!response.ok) {
            const errorMsg = data.message || `${response.status} ${response.statusText}`;
            throw new Error(errorMsg);
        }

        return data;
    } catch (error) {
        console.error(`✗ API call failed (${endpoint}):`, error);
        throw error;
    }
}

// ============================================================================
// Data Loading Functions
// ============================================================================

async function loadCompetitions() {
    try {
        console.log('Loading competitions...');

        const response = await apiCall('/competitions');

        console.log('Competitions response:', response);

        if (response && response.status === 'success') {
            appState.competitions = response.data || [];
            console.log(`✓ Loaded ${appState.competitions.length} competitions`);
            updateCompetitionSelect();
        } else {
            const errorMsg = response?.message || 'Unknown error';
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error('Error loading competitions:', error);
        showError('Load Error', `Failed to load competitions: ${error.message}`);
    }
}

async function loadTeams(competitionId, seasonId) {
    try {
        console.log(`Loading teams for competition ${competitionId}, season ${seasonId}...`);

        const endpoint = `/teams/${competitionId}?season_id=${seasonId}`;
        const response = await apiCall(endpoint);

        if (response.status === 'success') {
            appState.teams = response.data || [];
            console.log(`✓ Loaded ${appState.teams.length} teams`);
            updateTeamSelect();
        } else {
            throw new Error(response.message || 'Failed to load teams');
        }
    } catch (error) {
        console.error('Error loading teams:', error);
        showError('Load Error', 'Failed to load teams. Please try again.');
    }
}

async function generateOppositionReportWithProgress(requestBody) {
    return new Promise((resolve, reject) => {
        // Use fetch with streaming response instead of EventSource
        fetch(`${API_BASE_URL}/reports/opposition`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        }).then(response => {
            if (!response.ok) {
                reject(new Error(`HTTP ${response.status}: ${response.statusText}`));
                return;
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let finalResponse = null;

            const processStream = async () => {
                try {
                    while (true) {
                        const { done, value } = await reader.read();
                        if (done) break;

                        const text = decoder.decode(value, { stream: true });
                        const lines = text.split('\n');

                        for (const line of lines) {
                            if (line.startsWith('data: ')) {
                                try {
                                    const data = JSON.parse(line.substring(6));

                                    if (data.status === 'progress') {
                                        const percent = data.percent || 0;
                                        const message = data.message || 'Generating report...';
                                        updateStatusDisplay(message, percent);
                                        console.log(`Progress: ${message} (${percent}%)`);

                                    } else if (data.status === 'success') {
                                        console.log(`✓ Opposition report generated:`, data);
                                        finalResponse = data;
                                        resolve(data);

                                    } else if (data.status === 'error') {
                                        console.error('Report generation error:', data.message);
                                        reject(new Error(data.message));
                                    }
                                } catch (parseError) {
                                    // Silently ignore parse errors for non-JSON lines
                                }
                            }
                        }
                    }

                    // Ensure we have a final response
                    if (finalResponse) {
                        resolve(finalResponse);
                    } else {
                        reject(new Error('Report generation stream ended without success'));
                    }
                } catch (error) {
                    console.error('Stream reading error:', error);
                    reject(error);
                }
            };

            processStream();
        }).catch(error => {
            console.error('Fetch error:', error);
            reject(error);
        });
    });
}

async function downloadTeamEventsWithProgress(competitionId, seasonId, teamName) {
    return new Promise((resolve, reject) => {
        const eventSource = new EventSource(
            `${API_BASE_URL}/reports/team-events?competition_id=${competitionId}&season_id=${seasonId}&team_name=${encodeURIComponent(teamName)}`
        );

        let finalResponse = null;

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.status === 'progress') {
                    // Update progress bar based on files downloaded
                    const percent = data.percent || 0;
                    const current = data.current || 0;
                    const total = data.total || 0;

                    const message = total > 0
                        ? `Downloading match data for ${teamName}... (${current}/${total})`
                        : `Downloading match data for ${teamName}...`;

                    // Scale progress: 30-100% for event downloads
                    const scaledProgress = 30 + (percent * 0.7);
                    updateStatusDisplay(message, scaledProgress);

                    console.log(`Progress: ${current}/${total} (${percent}%)`);

                } else if (data.status === 'success') {
                    console.log(`✓ Event files downloaded:`, data);
                    finalResponse = data;
                    eventSource.close();
                    resolve(data);

                } else if (data.status === 'error') {
                    console.error('Event stream error:', data.message);
                    eventSource.close();
                    reject(new Error(data.message));
                }
            } catch (error) {
                console.error('Error parsing event data:', error);
            }
        };

        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            eventSource.close();

            if (finalResponse) {
                resolve(finalResponse);
            } else {
                reject(new Error('Connection lost while downloading events'));
            }
        };
    });
}

async function loadPlayers(teamId, competitionId, seasonId) {
    try {
        console.log(`Loading players for team ${teamId} (comp: ${competitionId}, season: ${seasonId})...`);

        if (!competitionId || !seasonId) {
            throw new Error(`Missing parameters: competition_id=${competitionId}, season_id=${seasonId}`);
        }

        const endpoint = `/players/${teamId}?competition_id=${competitionId}&season_id=${seasonId}`;
        console.log(`API Endpoint: ${endpoint}`);
        const response = await apiCall(endpoint);

        if (response.status === 'success') {
            appState.players = response.data || [];
            console.log(`✓ Loaded ${appState.players.length} players`);
            updatePlayerSelect();
        } else {
            throw new Error(response.message || 'Failed to load players');
        }
    } catch (error) {
        console.error('Error loading players:', error);
        showError('Load Error', 'Failed to load players. Please try again.');
    }
}

// ============================================================================
// UI Update Functions
// ============================================================================

function updateCompetitionSelect() {
    elements.competitionSelect.innerHTML = '<option value="">Choose a competition...</option>';

    appState.competitions.forEach(competition => {
        const option = document.createElement('option');
        // Store competition_id, season_id, season_name, and league_name in the value
        option.value = JSON.stringify({
            id: competition.id,
            season_id: competition.season_id,
            season: competition.season,
            league: competition.league
        });
        option.textContent = `${competition.league} - ${competition.season}`;
        elements.competitionSelect.appendChild(option);
    });
}

function updateTeamSelect() {
    const isDisabled = appState.teams.length === 0;

    elements.teamSelect.disabled = isDisabled;
    elements.teamSelect.innerHTML = '<option value="">Choose a team...</option>';

    appState.teams.forEach(team => {
        const option = document.createElement('option');
        option.value = team.id;
        option.textContent = team.name;
        elements.teamSelect.appendChild(option);
    });
}

function updatePlayerSelect() {
    const isDisabled = appState.players.length === 0;

    elements.playerSelect.disabled = isDisabled;
    elements.playerSelect.innerHTML = '<option value="">-- Full Team Report --</option>';

    appState.players.forEach(player => {
        const option = document.createElement('option');
        option.value = player.id;
        option.textContent = player.name;
        elements.playerSelect.appendChild(option);
    });
}

function updateGenerateButton() {
    const isGenerateEnabled = appState.selectedCompetition && appState.selectedTeam;
    const isDownloadEnabled = appState.selectedCompetition;

    elements.generateBtn.disabled = !isGenerateEnabled;
    elements.downloadFullSeasonBtn.disabled = !isDownloadEnabled;
    elements.downloadWeeklyBtn.disabled = !isDownloadEnabled;
}

// ============================================================================
// Report Generation
// ============================================================================

async function generateReport() {
    if (!appState.selectedCompetition || !appState.selectedTeam) {
        showError('Missing Selection', 'Please select a competition and team.');
        return;
    }

    if (appState.isGenerating) {
        return;
    }

    try {
        appState.isGenerating = true;

        // Get selected team details
        const team = appState.teams.find(t => t.id === parseInt(appState.selectedTeam));

        if (!team) {
            throw new Error('Invalid team selection');
        }

        // Get competition data from the selected dropdown value
        const selectedCompetitionValue = elements.competitionSelect.value;
        const competition = JSON.parse(selectedCompetitionValue);

        if (!competition || !competition.id || !competition.season || !competition.league) {
            throw new Error('Invalid competition selection');
        }

        // Show status panel
        showStatus();

        // Reset progress titles for report generation
        elements.statusPanelTitle.textContent = 'Generation Status';
        elements.statusTitle.textContent = 'Generating Report...';

        updateStatusDisplay(`Downloading statistics for ${team.name}...`, 10, true);

        // Handle opposition reports separately
        if (appState.reportType === 'opposition') {
            const requestBody = {
                competition_id: parseInt(appState.selectedCompetition),
                season_id: parseInt(appState.selectedSeasonId),
                team_id: parseInt(appState.selectedTeam),
                team_name: team.name,
                season_name: competition.season,
                league_name: competition.league
            };

            console.log(`Sending opposition report request:`, requestBody);

            try {
                const response = await generateOppositionReportWithProgress(requestBody);
                appState.isGenerating = false;

                if (response.status !== 'success') {
                    throw new Error(response.message || 'Failed to generate opposition report');
                }

                console.log(`✓ Opposition report generated:`, response);
                updateStatusDisplay(`✓ Opposition report generated for ${team.name}!`, 100);

                // Open report in new tab using API endpoint
                try {
                    window.open(`${API_BASE_URL}/reports/opposition-html`, '_blank');
                } catch (error) {
                    console.error('Failed to open report in new tab:', error);
                }

                showResult(
                    response.report_filepath,
                    null,
                    [],
                    0,
                    'opposition'
                );
            } catch (error) {
                throw error;
            }
        } else {
            // Handle player stats reports
            const requestBody = {
                competition_id: parseInt(appState.selectedCompetition),
                season_id: parseInt(appState.selectedSeasonId),
                team_name: team.name,
                season_name: competition.season,
                league_name: competition.league,
                report_type: "player",
                player_id: appState.selectedPlayer ? parseInt(appState.selectedPlayer) : null,
            };

            console.log(`Sending player stats report request:`, requestBody);

            // Send request to generate reports (team stats + player stats)
            updateStatusDisplay(`Downloading statistics for ${team.name}...`, 20);
            const response = await apiCall('/reports/player-stats', 'POST', requestBody);

            if (response.status !== 'success') {
                throw new Error(response.message || 'Failed to generate report');
            }

            // Now generate match data for the team with progress tracking
            updateStatusDisplay(`Downloading match data for ${team.name}... (0/0)`, 30);
            console.log(`Generating event files for team ${team.name}...`);

            try {
                const eventsResponse = await downloadTeamEventsWithProgress(
                    parseInt(appState.selectedCompetition),
                    parseInt(appState.selectedSeasonId),
                    team.name
                );

                appState.isGenerating = false;

                if (eventsResponse.status === 'success') {
                    console.log(`✓ All files generated:`, response, eventsResponse);
                    updateStatusDisplay(`✓ Download complete for ${team.name}!`, 100);

                    // Show success with all files
                    showResult(
                        response.team_stats_filepath,
                        response.player_stats_filepath,
                        eventsResponse.event_files,
                        eventsResponse.count
                    );
                } else {
                    // Show partial success with stats but no events
                    console.warn('Events generation failed, showing stats only');
                    updateStatusDisplay(`✓ Download complete for ${team.name}! (events unavailable)`, 100);
                    showResult(
                        response.team_stats_filepath,
                        response.player_stats_filepath,
                        [],
                        0
                    );
                }
            } catch (error) {
                console.error('Error downloading events:', error);
                appState.isGenerating = false;
                // Show partial success with stats
                updateStatusDisplay(`✓ Download complete (events failed)`, 100);
                showResult(
                    response.team_stats_filepath,
                    response.player_stats_filepath,
                    [],
                    0
                );
            }
        }
    } catch (error) {
        console.error('Error generating report:', error);
        appState.isGenerating = false;
        showError('Generation Error', error.message || 'Failed to generate report. Please try again.');
    }
}

async function downloadFullSeason() {
    if (!appState.selectedCompetition) {
        showError('Missing Selection', 'Please select a competition.');
        return;
    }

    if (appState.isGenerating) {
        return;
    }

    // Show confirmation dialog
    const confirmed = confirm(
        `⚠️ This operation will download statistics and match data for ALL ${appState.teams.length} teams in the selected season.\n\n` +
        `This may take several minutes to complete.\n\n` +
        `Continue?`
    );

    if (!confirmed) {
        console.log('Download cancelled by user');
        return;
    }

    if (appState.teams.length === 0) {
        showError('No Teams Available', 'No teams found for the selected competition.');
        return;
    }

    try {
        appState.isGenerating = true;

        // Show status panel
        showStatus();

        // Update progress titles for download
        elements.statusPanelTitle.textContent = 'Download Status';
        elements.statusTitle.textContent = 'Downloading full season data...';

        updateStatusDisplay(`Downloading full season statistics...`, 5, false);

        console.log(`Downloading full season statistics...`);

        // Download season stats once (for all teams)
        try {
            const statsResponse = await apiCall('/reports/generate', 'POST', {
                competition_id: parseInt(appState.selectedCompetition),
                season_id: parseInt(appState.selectedSeasonId),
            });

            if (statsResponse.status === 'success') {
                console.log(`✓ Season statistics files downloaded`);
                updateStatusDisplay(`Downloading match data for ${appState.teams.length} teams...`, 10, false);
            } else {
                console.warn(`✗ Season statistics download failed`);
            }
        } catch (error) {
            console.error(`Error downloading season stats: ${error.message}`);
        }

        updateTeamProgressBar(0, appState.teams.length);

        console.log(`Downloading match data for all ${appState.teams.length} teams...`);

        let totalEventFiles = 0;
        let successCount = 0;
        let failureCount = 0;

        // Download match events for each team
        for (let i = 0; i < appState.teams.length; i++) {
            const team = appState.teams[i];
            const teamProgress = ((i) / appState.teams.length) * 100;

            try {
                updateStatusDisplay(
                    `[${i + 1}/${appState.teams.length}] ${team.name}: Downloading match data...`,
                    10 + (teamProgress * 0.85),
                    false
                );
                updateTeamProgressBar(i, appState.teams.length);

                console.log(`[${i + 1}/${appState.teams.length}] Downloading match events for ${team.name}...`);

                const eventsResponse = await downloadTeamEventsWithProgress(
                    parseInt(appState.selectedCompetition),
                    parseInt(appState.selectedSeasonId),
                    team.name
                );

                if (eventsResponse.status === 'success') {
                    totalEventFiles += eventsResponse.count;
                    successCount++;
                    console.log(`✓ ${team.name}: ${eventsResponse.count} event files downloaded`);
                } else {
                    failureCount++;
                    console.warn(`✗ ${team.name}: Events download failed`);
                }
            } catch (error) {
                failureCount++;
                console.error(`✗ ${team.name}: ${error.message}`);
            }

            // Update team progress
            updateTeamProgressBar(i + 1, appState.teams.length);
        }

        appState.isGenerating = false;
        updateStatusDisplay(`✓ Full season download complete!`, 100, false);
        updateTeamProgressBar(appState.teams.length, appState.teams.length);

        // Show summary result
        showResult(
            '',
            '',
            [],
            totalEventFiles
        );

        // Update result panel titles and message for download
        elements.resultTitle.textContent = 'Download Complete';
        elements.resultSubtitle.textContent = 'Full season data downloaded successfully!';

        // Update result message with summary
        const resultMessage = `📊 Teams Match Data: ${successCount}/${appState.teams.length}
📋 Season Statistics: 1 set (all teams combined)
📅 Season Matches: 1 file (all competition matches)
📹 Total Match Data Files: ${totalEventFiles}

${failureCount > 0 ? `⚠️ ${failureCount} team(s) had download issues\n` : ''}All files have been saved to data_temp folder and are ready for analysis.`;

        elements.resultMessage.textContent = resultMessage;

    } catch (error) {
        console.error('Error in downloadFullSeason:', error);
        appState.isGenerating = false;
        showError('Download Error', error.message || 'Failed to download full season data.');
    }
}

function updateTeamProgressBar(current, total) {
    const percent = total > 0 ? (current / total) * 100 : 0;
    // Create or update a second progress bar element
    let teamProgressContainer = document.getElementById('teamProgressContainer');

    if (!teamProgressContainer) {
        // Create team progress container
        teamProgressContainer = document.createElement('div');
        teamProgressContainer.id = 'teamProgressContainer';
        teamProgressContainer.className = 'progress-bar-container';
        teamProgressContainer.style.marginTop = 'var(--spacing-lg)';

        const teamProgressBar = document.createElement('div');
        teamProgressBar.id = 'teamProgressBar';
        teamProgressBar.className = 'progress-bar';

        const teamProgressFill = document.createElement('div');
        teamProgressFill.id = 'teamProgressFill';
        teamProgressFill.className = 'progress-fill';

        const teamProgressText = document.createElement('p');
        teamProgressText.id = 'teamProgressText';
        teamProgressText.className = 'progress-text';
        teamProgressText.textContent = `Teams: 0/${total}`;

        teamProgressBar.appendChild(teamProgressFill);
        teamProgressContainer.appendChild(teamProgressBar);
        teamProgressContainer.appendChild(teamProgressText);

        // Insert after main progress container
        const mainProgressContainer = document.querySelector('.progress-bar-container');
        if (mainProgressContainer && mainProgressContainer.parentNode) {
            mainProgressContainer.parentNode.insertBefore(teamProgressContainer, mainProgressContainer.nextSibling);
        }
    }

    const teamProgressFill = document.getElementById('teamProgressFill');
    const teamProgressText = document.getElementById('teamProgressText');

    if (teamProgressFill) {
        teamProgressFill.style.width = percent + '%';
    }
    if (teamProgressText) {
        teamProgressText.textContent = `Teams: ${current}/${total}`;
    }
}

async function downloadWeeklyData() {
    if (!appState.selectedCompetition) {
        showError('Missing Selection', 'Please select a competition.');
        return;
    }

    // Prompt user for week number
    const weekNumber = prompt('Enter week number to download:', '1');

    if (weekNumber === null) {
        return; // User cancelled
    }

    const week = parseInt(weekNumber);
    if (isNaN(week) || week < 1) {
        showError('Invalid Input', 'Please enter a valid week number (1 or greater).');
        return;
    }

    if (appState.isGenerating) {
        return;
    }

    try {
        appState.isGenerating = true;

        // Show status panel
        showStatus();

        // Update progress titles for download
        elements.statusPanelTitle.textContent = 'Download Status';
        elements.statusTitle.textContent = `Downloading week ${week} data...`;

        updateStatusDisplay(`Downloading season statistics...`, 5, false);

        console.log(`Downloading season statistics for week ${week}...`);

        // Download season stats once (for all teams)
        try {
            const statsResponse = await apiCall('/reports/generate', 'POST', {
                competition_id: parseInt(appState.selectedCompetition),
                season_id: parseInt(appState.selectedSeasonId),
            });

            if (statsResponse.status === 'success') {
                console.log(`✓ Season statistics files downloaded`);
                updateStatusDisplay(`Downloading week ${week} match data...`, 10, false);
            } else {
                console.warn(`✗ Season statistics download failed`);
            }
        } catch (error) {
            console.error(`Error downloading season stats: ${error.message}`);
        }

        console.log(`Downloading match data for week ${week}...`);

        const weekResponse = await downloadWeekEventsWithProgress(
            parseInt(appState.selectedCompetition),
            parseInt(appState.selectedSeasonId),
            week
        );

        appState.isGenerating = false;

        if (weekResponse.status === 'success') {
            console.log(`✓ Week ${week} downloaded:`, weekResponse);
            updateStatusDisplay(`✓ Week ${week} download complete!`, 100, false);

            showResult(
                '',
                '',
                weekResponse.event_files,
                weekResponse.count
            );

            // Update result panel titles and message for download
            elements.resultTitle.textContent = 'Download Complete';
            elements.resultSubtitle.textContent = `Week ${week} data downloaded successfully!`;

            // Update result message
            const resultMessage = `📋 Season Statistics: 1 set (all teams combined)
📅 Season Matches: 1 file (all competition matches)
📹 Match Data Files: ${weekResponse.count}

All files have been saved to data_temp folder organized by team.`;

            elements.resultMessage.textContent = resultMessage;
        } else {
            throw new Error('Download failed');
        }
    } catch (error) {
        console.error('Error in downloadWeeklyData:', error);
        appState.isGenerating = false;
        showError('Download Error', error.message || 'Failed to download weekly data.');
    }
}

async function downloadWeekEventsWithProgress(competitionId, seasonId, weekNo) {
    return new Promise((resolve, reject) => {
        const eventSource = new EventSource(
            `${API_BASE_URL}/reports/week-events?competition_id=${competitionId}&season_id=${seasonId}&week_no=${weekNo}`
        );

        let finalResponse = null;

        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                if (data.status === 'progress') {
                    // Update progress bar based on files downloaded
                    const percent = data.percent || 0;
                    const current = data.current || 0;
                    const total = data.total || 0;

                    const message = total > 0
                        ? `Downloading week ${weekNo} data... (${current}/${total})`
                        : `Downloading week ${weekNo} data...`;

                    // Scale progress: 30-100% for event downloads
                    const scaledProgress = 30 + (percent * 0.7);
                    updateStatusDisplay(message, scaledProgress);

                    console.log(`Progress: ${current}/${total} (${percent}%)`);

                } else if (data.status === 'success') {
                    console.log(`✓ Week events downloaded:`, data);
                    finalResponse = data;
                    eventSource.close();
                    resolve(data);

                } else if (data.status === 'error') {
                    console.error('Event stream error:', data.message);
                    eventSource.close();
                    reject(new Error(data.message));
                }
            } catch (error) {
                console.error('Error parsing event data:', error);
            }
        };

        eventSource.onerror = (error) => {
            console.error('EventSource error:', error);
            eventSource.close();

            if (finalResponse) {
                resolve(finalResponse);
            } else {
                reject(new Error('Connection lost while downloading events'));
            }
        };
    });
}

async function pollReportStatus() {
    const taskId = appState.currentTaskId;

    try {
        const response = await apiCall(`/status/${taskId}`);

        if (response.status === 'complete') {
            console.log('✓ Report generation completed');
            appState.isGenerating = false;
            showResult(taskId);
        } else if (response.status === 'error') {
            console.error('✗ Report generation failed:', response.message);
            appState.isGenerating = false;
            hideStatus();
            showError('Generation Error', response.message || 'Failed to generate report.');
        } else {
            // Still generating, continue polling
            updateStatusDisplay(response.message || 'Generating Report...', response.progress || 0);

            // Continue polling
            setTimeout(() => {
                if (appState.currentTaskId === taskId && appState.isGenerating) {
                    pollReportStatus();
                }
            }, POLL_INTERVAL);
        }
    } catch (error) {
        console.error('Error polling status:', error);

        // Continue polling even if there's a temporary error
        if (appState.currentTaskId === taskId && appState.isGenerating) {
            setTimeout(() => {
                pollReportStatus();
            }, POLL_INTERVAL);
        }
    }
}

// ============================================================================
// UI Display Functions
// ============================================================================

function showStatus() {
    hidePanel(elements.selectionPanel);
    hidePanel(elements.resultPanel);
    hidePanel(elements.errorPanel);
    showPanel(elements.statusPanel);
}

function hideStatus() {
    hidePanel(elements.statusPanel);
}

function updateStatusDisplay(message, progress, showDetails = true) {
    elements.statusMessage.textContent = message;

    // Update progress bar
    const progressPercent = Math.min(Math.max(progress || 0, 0), 100);
    elements.progressFill.style.width = progressPercent + '%';
    elements.progressText.textContent = Math.round(progressPercent) + '%';

    // Update status details only if requested
    const statusDetailsDiv = document.getElementById('statusDetails');

    if (showDetails) {
        // Show status details for report generation
        if (statusDetailsDiv) {
            statusDetailsDiv.classList.remove('hidden');
        }
        elements.statusDetail1.textContent = `Report Type: ${appState.reportType === 'opposition' ? 'Opposition' : 'Player'}`;
        elements.statusDetail2.textContent = `Team: ${appState.teams.find(t => t.id === parseInt(appState.selectedTeam))?.name || 'Unknown'}`;
    } else {
        // Hide status details for downloads
        if (statusDetailsDiv) {
            statusDetailsDiv.classList.add('hidden');
        }
        // Clear all text
        elements.statusDetail1.textContent = '';
        elements.statusDetail2.textContent = '';
    }
}

function showResult(filepath1, filepath2, eventFiles = [], eventCount = 0, reportType = 'player-stats') {
    hidePanel(elements.selectionPanel);
    hidePanel(elements.statusPanel);
    hidePanel(elements.errorPanel);
    showPanel(elements.resultPanel);

    // Update result message
    const team = appState.teams.find(t => t.id === parseInt(appState.selectedTeam));

    let resultText = '';
    let downloadText = '';

    if (reportType === 'opposition') {
        resultText = `✅ Opposition report generated successfully!

📋 Opposition Intelligence Report for ${team.name} has been created.`;
        downloadText = 'View Opposition Report';
    } else {
        resultText = `✅ Data download finished!

📊 Team Statistics: 1 file
👥 Player Statistics: 1 file`;

        if (eventCount > 0) {
            resultText += `
📹 Match Data: ${eventCount} files`;
        }

        resultText += `

All files have been saved to data_temp folder and are ready for analysis.`;
        downloadText = 'Download Files';
    }

    elements.resultMessage.textContent = resultText;

    // Update download link
    if (filepath1) {
        elements.downloadLink.href = filepath1;
        elements.downloadLink.textContent = downloadText;
        elements.downloadLink.style.display = 'inline-block';
    }
}

function showError(title, message) {
    hidePanel(elements.selectionPanel);
    hidePanel(elements.statusPanel);
    hidePanel(elements.resultPanel);
    showPanel(elements.errorPanel);

    elements.errorTitle.textContent = title;
    elements.errorMessage.textContent = message;
}

function hideError() {
    hidePanel(elements.errorPanel);
    showPanel(elements.selectionPanel);
}

function openReportInNewTab(htmlContent) {
    const newTab = window.open();
    if (newTab) {
        newTab.document.write(htmlContent);
        newTab.document.close();
        newTab.document.title = 'Opposition Intelligence Report';
    } else {
        console.error('Failed to open new tab. Browser may have blocked popup.');
        showError('Tab Blocked', 'Unable to open new tab. Please check your browser popup settings.');
    }
}

function resetUI() {
    appState.isGenerating = false;
    appState.currentTaskId = null;

    hidePanel(elements.statusPanel);
    hidePanel(elements.resultPanel);
    hidePanel(elements.errorPanel);
    showPanel(elements.selectionPanel);

    // Reset progress bar
    elements.progressFill.style.width = '0%';
    elements.progressText.textContent = '0%';
}

function showPanel(panel) {
    if (panel) {
        panel.style.display = 'block';
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
}

function hidePanel(panel) {
    if (panel) {
        panel.style.display = 'none';
    }
}

function hideInitialLoadSpinner() {
    elements.initialLoadSpinner.classList.add('hidden');
}

// ============================================================================
// Utility Functions
// ============================================================================

function formatDate(date) {
    return new Date(date).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
}

// ============================================================================
// Error Handling
// ============================================================================

window.addEventListener('error', (event) => {
    console.error('Unhandled error:', event.error);
});

window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled rejection:', event.reason);
    showError('Unexpected Error', 'An unexpected error occurred. Please refresh the page.');
});

// ============================================================================
// Logging
// ============================================================================

console.log('%c⚽ Football Intelligence Application', 'font-size: 16px; font-weight: bold; color: #1e40af;');
console.log('%cAPI Base URL: ' + API_BASE_URL, 'color: #6b7280;');
console.log('%cStatus: Ready', 'color: #10b981; font-weight: bold;');
