/**
 * MEMORA Caregiver Dashboard - Phase 6
 * Displays patient progress charts and activity data
 */

// ============================================================
// STATE & CONFIGURATION
// ============================================================

let dashboardState = {
    currentPatientId: null,
    allPatients: [],
    progressData: [],
    charts: {
        accuracy: null,
        score: null
    }
};

const COLORS = {
    memory_match: '#4A90D9',   // Primary blue
    attention_test: '#27AE60', // Success green
    gridLines: '#E0E0E0'
};

const CHART_OPTIONS = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
        mode: 'index',
        intersect: false
    },
    plugins: {
        legend: {
            display: true,
            position: 'top',
            labels: {
                font: { size: 12, weight: 'bold' },
                color: '#2C3E50',
                padding: 15
            }
        },
        title: {
            display: false
        }
    },
    scales: {
        x: {
            grid: { color: COLORS.gridLines },
            ticks: { font: { size: 11 } }
        },
        y: {
            grid: { color: COLORS.gridLines },
            ticks: { font: { size: 11 } }
        }
    }
};

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    await initDashboard();
});

async function initDashboard() {
    try {
        // Fetch all patients from the system
        await fetchAllPatients();
        
        // Set default patient (first in list, or prompt)
        if (dashboardState.allPatients.length > 0) {
            selectPatient(dashboardState.allPatients[0].id);
        } else {
            showNoPatients();
        }
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
    }
}

// ============================================================
// PATIENT SELECTION
// ============================================================

async function fetchAllPatients() {
    try {
        const response = await fetch(`/api/users/patients`, { credentials: 'include' });
        if (!response.ok) {
            console.error('Failed to fetch patients');
            if (typeof ErrorHandler !== 'undefined') {
                ErrorHandler.showError('Failed to load patients list. Please refresh the page.');
            }
            return;
        }
        
        const patients = await response.json();
        dashboardState.allPatients = patients;
        
        // Populate dropdown
        const select = document.getElementById('patient-select');
        if (!select) {
            console.warn('Patient select element not found');
            return;
        }
        
        select.innerHTML = '';
        
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = patient.name;
            select.appendChild(option);
        });
        
        // Add change listener
        select.addEventListener('change', (e) => {
            if (e.target.value) {
                selectPatient(parseInt(e.target.value));
            }
        });
        
        // Set default value
        if (patients.length > 0) {
            select.value = patients[0].id;
        }
    } catch (error) {
        console.error('Error fetching patients:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Failed to load patient data. Please try again.');
        }
    }
}

async function selectPatient(patientId) {
    dashboardState.currentPatientId = patientId;
    
    try {
        // Show loading state in the charts container message area (not by replacing the canvas)
        const chartMessageElement = document.getElementById('chart-message');
        if (chartMessageElement) {
            chartMessageElement.innerHTML = '<p style="text-align: center; padding: 20px; color: #666;">Loading patient data...</p>';
            chartMessageElement.style.display = 'block';
        }
        
        const fetchOptions = { credentials: 'include' };
        
        // Fetch progress, difficulty, mood data, and safety alerts for this patient
        const progressResponse = await fetch(`/api/progress/${patientId}`, fetchOptions);
        const progressData = progressResponse.ok ? await progressResponse.json() : [];
        
        const difficultyResponse = await fetch(`/api/difficulty/${patientId}`, fetchOptions);
        const difficultyData = difficultyResponse.ok ? await difficultyResponse.json() : { difficulty: 'medium' };
        
        const moodResponse = await fetch(`/api/mood/today?patient_id=${patientId}`, fetchOptions);
        const moodData = moodResponse.ok ? await moodResponse.json() : { has_entry: false, entry: null };
        
        const safetyResponse = await fetch(`/api/safety/alerts?patient_id=${patientId}`, fetchOptions);
        const safetyAlertsData = safetyResponse.ok ? await safetyResponse.json() : { success: false, alerts: [] };
        
        dashboardState.progressData = progressData || [];
        
        // Render overview, charts, table, and safety alerts
        updatePatientOverview(patientId, difficultyData);
        updatePatientMood(moodData);
        updateCharts(dashboardState.progressData);
        updateActivityTable(dashboardState.progressData);
        updateSafetyAlerts(safetyAlertsData.alerts || []);
    } catch (error) {
        console.error('Failed to load patient data:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Failed to load patient data. Please try again.');
        }
    }
}

function showNoPatients() {
    document.getElementById('patient-select').innerHTML = '<option>No patients found</option>';
    document.getElementById('chart-message').textContent = '❌ No patients in the system yet.';
    document.getElementById('chart-message').style.display = 'block';
}

// ============================================================
// OVERVIEW SECTION
// ============================================================

function updatePatientOverview(patientId, difficultyData) {
    const patient = dashboardState.allPatients.find(p => p.id === patientId);
    const progressData = dashboardState.progressData;
    
    // Update patient name
    document.getElementById('overview-name').textContent = patient ? patient.name : '-';
    
    // Update current difficulty
    const diffEmojis = {
        'easy': '🟢 Easy',
        'medium': '🟡 Medium',
        'hard': '🔴 Hard'
    };
    const currentDifficulty = difficultyData?.difficulty || 'medium';
    document.getElementById('overview-difficulty').textContent = 
        diffEmojis[currentDifficulty] || '🟡 Medium';
    
    // Update total games played
    document.getElementById('overview-total-games').textContent = progressData.length;
    
    // Calculate average accuracy
    if (progressData.length > 0) {
        const avgAccuracy = progressData.reduce((sum, log) => sum + log.accuracy, 0) / progressData.length;
        document.getElementById('overview-avg-accuracy').textContent = avgAccuracy.toFixed(1) + '%';
    } else {
        document.getElementById('overview-avg-accuracy').textContent = '-';
    }
}

function updatePatientMood(moodData) {
    const moodEmojis = {
        'very_happy': '😊',
        'happy': '🙂',
        'okay': '😐',
        'sad': '😟',
        'very_sad': '😔'
    };
    
    const moodLabels = {
        'very_happy': 'Very Happy',
        'happy': 'Happy',
        'okay': 'Okay',
        'sad': 'Sad',
        'very_sad': 'Very Sad'
    };
    
    const moodDisplay = document.getElementById('overview-mood');
    const moodTimeDisplay = document.getElementById('overview-mood-time');
    
    if (moodData && moodData.has_entry && moodData.entry) {
        const mood = moodData.entry.mood;
        const emoji = moodEmojis[mood] || '😐';
        const label = moodLabels[mood] || mood;
        
        moodDisplay.textContent = emoji + ' ' + label;
        
        // Format timestamp
        const date = new Date(moodData.entry.timestamp);
        const timeStr = date.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true
        });
        
        moodTimeDisplay.textContent = timeStr;
    } else {
        moodDisplay.textContent = '-';
        moodTimeDisplay.textContent = '-';
    }
}

// ============================================================
// CHARTS SECTION
// ============================================================

function updateCharts(progressData) {
    if (progressData.length < 2) {
        // Show message instead of charts
        document.querySelector('.charts-container').style.display = 'none';
        document.getElementById('chart-message').style.display = 'block';
        return;
    }
    
    // Show charts
    document.querySelector('.charts-container').style.display = 'grid';
    document.getElementById('chart-message').style.display = 'none';
    
    // Prepare data by game type
    const memoryData = progressData.filter(log => log.game_type === 'memory_match');
    const attentionData = progressData.filter(log => log.game_type === 'attention_test');
    
    // Format labels (date/time)
    const labels = progressData.map(log => formatDateTime(log.timestamp));
    
    // Initialize accuracy chart
    initAccuracyChart(labels, memoryData, attentionData);
    
    // Initialize score chart
    initScoreChart(labels, memoryData, attentionData);
}

function initAccuracyChart(labels, memoryData, attentionData) {
    const ctx = document.getElementById('accuracy-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (dashboardState.charts.accuracy) {
        dashboardState.charts.accuracy.destroy();
    }
    
    // Prepare datasets
    const progressData = dashboardState.progressData;
    
    dashboardState.charts.accuracy = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Memory Match',
                    data: progressData.map(log => 
                        log.game_type === 'memory_match' ? log.accuracy : null
                    ),
                    borderColor: COLORS.memory_match,
                    backgroundColor: COLORS.memory_match + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.memory_match
                },
                {
                    label: 'Attention Test',
                    data: progressData.map(log => 
                        log.game_type === 'attention_test' ? log.accuracy : null
                    ),
                    borderColor: COLORS.attention_test,
                    backgroundColor: COLORS.attention_test + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.attention_test
                }
            ]
        },
        options: {
            ...CHART_OPTIONS,
            scales: {
                ...CHART_OPTIONS.scales,
                y: {
                    ...CHART_OPTIONS.scales.y,
                    min: 0,
                    max: 100,
                    ticks: {
                        ...CHART_OPTIONS.scales.y.ticks,
                        callback: (value) => value + '%'
                    }
                }
            }
        }
    });
}

function initScoreChart(labels, memoryData, attentionData) {
    const ctx = document.getElementById('score-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (dashboardState.charts.score) {
        dashboardState.charts.score.destroy();
    }
    
    // Prepare datasets
    const progressData = dashboardState.progressData;
    
    dashboardState.charts.score = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Memory Match',
                    data: progressData.map(log => 
                        log.game_type === 'memory_match' ? log.score : null
                    ),
                    borderColor: COLORS.memory_match,
                    backgroundColor: COLORS.memory_match + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.memory_match
                },
                {
                    label: 'Attention Test',
                    data: progressData.map(log => 
                        log.game_type === 'attention_test' ? log.score : null
                    ),
                    borderColor: COLORS.attention_test,
                    backgroundColor: COLORS.attention_test + '20',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.3,
                    spanGaps: true,
                    pointRadius: 4,
                    pointHoverRadius: 6,
                    pointBackgroundColor: COLORS.attention_test
                }
            ]
        },
        options: {
            ...CHART_OPTIONS,
            scales: {
                ...CHART_OPTIONS.scales,
                y: {
                    ...CHART_OPTIONS.scales.y,
                    ticks: {
                        ...CHART_OPTIONS.scales.y.ticks,
                        callback: (value) => value.toString()
                    }
                }
            }
        }
    });
}

// ============================================================
// RECENT ACTIVITY TABLE
// ============================================================

function updateActivityTable(progressData) {
    const tbody = document.getElementById('activity-table-body');
    if (!tbody) {
        console.warn('Activity table body element not found');
        return;
    }
    
    tbody.innerHTML = '';
    
    if (progressData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center">No game activity yet.</td></tr>';
        return;
    }
    
    // Show most recent 10 sessions, most recent first
    const recentSessions = progressData.slice().reverse().slice(0, 10);
    
    recentSessions.forEach(log => {
        const row = document.createElement('tr');
        
        const gameEmojis = {
            'memory_match': '🧠 Memory Match',
            'attention_test': '👁️ Attention Test'
        };
        
        const diffEmojis = {
            'easy': '🟢 Easy',
            'medium': '🟡 Medium',
            'hard': '🔴 Hard'
        };
        
        row.innerHTML = `
            <td>${formatDateTime(log.timestamp)}</td>
            <td>${gameEmojis[log.game_type] || log.game_type}</td>
            <td><strong>${log.score}</strong></td>
            <td>${log.accuracy.toFixed(1)}%</td>
            <td>${diffEmojis[log.difficulty] || log.difficulty}</td>
        `;
        tableBody.appendChild(row);
    });
}

// ============================================================
// SAFETY ALERTS SECTION (Phase 10E)
// ============================================================

function updateSafetyAlerts(alerts) {
    const container = document.getElementById('safety-alerts-container');
    if (!container) return;
    
    if (!alerts || alerts.length === 0) {
        container.innerHTML = `
            <div class="no-alerts-message">
                <p data-i18n-key="safety_no_active_alerts">🛡️ No active safety alerts</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    for (const alert of alerts) {
        const createdDate = new Date(alert.created_at);
        const formattedTime = createdDate.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        
        const alertClass = alert.status === 'active' ? 'alert-item active' : 'alert-item resolved';
        const statusText = alert.status === 'active' ? '🔴 Active' : '✅ Resolved';
        const buttonHtml = alert.status === 'active' 
            ? `<button class="btn-resolve" onclick="resolveAlertFromDashboard(${alert.id})">Resolve</button>`
            : '';
        
        html += `
            <div class="${alertClass}">
                <div class="alert-header">
                    <span class="alert-type">⚠️ Emergency Alert</span>
                    <span class="alert-status">${statusText}</span>
                </div>
                <div class="alert-body">
                    <p class="alert-time">Time: ${formattedTime}</p>
                    <p class="alert-message">${alert.message ? escapeHtmlInDashboard(alert.message) : 'Emergency alert'}</p>
                </div>
                <div class="alert-actions">
                    ${buttonHtml}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function resolveAlertFromDashboard(alertId) {
    if (confirm('Mark this alert as resolved?')) {
        fetch(`/api/safety/alerts/${alertId}/resolve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload alerts for the currently selected patient
                fetch(`/api/safety/alerts?patient_id=${dashboardState.currentPatientId}`, { credentials: 'include' })
                    .then(r => r.json())
                    .then(d => updateSafetyAlerts(d.alerts || []))
                    .catch(e => console.error('Error reloading alerts:', e));
            }
        })
        .catch(error => console.error('Error resolving alert:', error));
    }
}

function escapeHtmlInDashboard(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function formatDateTime(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch {
        return isoString;
    }
}