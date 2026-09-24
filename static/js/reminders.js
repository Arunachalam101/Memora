/**
 * MEMORA Reminders Module
 * Handles all reminder CRUD operations and UI updates
 */

// ============================================================
// CONSTANTS & HELPERS
// ============================================================

const REMINDER_TYPES = {
    medicine: { icon: '💊', label: 'Medicine', color: '#4A90D9' },
    appointment: { icon: '📅', label: 'Appointment', color: '#27AE60' },
    activity: { icon: '🎯', label: 'Activity', color: '#F39C12' }
};

function getTypeInfo(type) {
    return REMINDER_TYPES[type] || { icon: '📝', label: type, color: '#7F8C8D' };
}

// Use ErrorHandler from error_handler.js
function showError(message) {
    if (typeof ErrorHandler !== 'undefined') {
        ErrorHandler.showError(message);
    } else {
        console.error(message);
    }
}

function showSuccess(message) {
    if (typeof ErrorHandler !== 'undefined') {
        ErrorHandler.showSuccess(message);
    } else {
        console.log(message);
    }
}

// ============================================================
// REMINDER API CALLS
// ============================================================

/**
 * Fetch all reminders for the logged-in user
 */
async function fetchReminders() {
    try {
        const result = await ErrorHandler.fetchWithErrorHandling(
            '/api/reminders',
            {},
            'Something went wrong loading reminders. Please try again.'
        );
        return result || [];
    } catch (error) {
        return [];
    }
}

/**
 * Create a new reminder
 */
async function createReminder(title, type, time) {
    try {
        const response = await fetch('/api/reminders', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ title, type, time })
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        showSuccess(`Reminder "${title}" created`);
        return await response.json();
    } catch (error) {
        showError(`Failed to create reminder: ${error.message}`);
        return null;
    }
}

/**
 * Update a reminder
 */
async function updateReminder(id, updates) {
    try {
        const response = await fetch(`/api/reminders/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(updates)
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            return null;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        showError(`Failed to update reminder: ${error.message}`);
        return null;
    }
}

/**
 * Delete a reminder
 */
async function deleteReminder(id) {
    try {
        const response = await fetch(`/api/reminders/${id}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            return false;
        }
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || `HTTP ${response.status}`);
        }
        
        showSuccess('Reminder deleted');
        return true;
    } catch (error) {
        showError(`Failed to delete reminder: ${error.message}`);
        return false;
    }
}

// ============================================================
// UI RENDERING - PATIENT HOME PAGE
// ============================================================

/**
 * Render reminders list for patient home page
 */
async function renderPatientReminders() {
    const container = document.getElementById('reminders-container');
    if (!container) return;
    
    container.innerHTML = '<p class="loading">Loading reminders...</p>';
    
    const reminders = await fetchReminders();
    
    // Expose reminders data to voice assistant
    if (window.VoiceAPI) {
        window.VoiceAPI.updateRemindersData(reminders);
    }
    
    if (reminders.length === 0) {
        container.innerHTML = '<p class="empty-state">No reminders yet. Check back later!</p>';
        return;
    }
    
    const remindersHTML = reminders.map(reminder => {
        const typeInfo = getTypeInfo(reminder.type);
        const doneClass = reminder.is_done ? 'reminder-done' : '';
        return `
            <div class="reminder-card ${doneClass}" data-id="${reminder.id}">
                <div class="reminder-icon" style="color: ${typeInfo.color}">
                    ${typeInfo.icon}
                </div>
                <div class="reminder-content">
                    <h3 class="reminder-title">${reminder.title}</h3>
                    <p class="reminder-meta">
                        <span class="reminder-time">🕐 ${reminder.time}</span>
                        <span class="reminder-type">${typeInfo.label}</span>
                    </p>
                </div>
                <div class="reminder-actions">
                    <button class="btn btn-sm ${reminder.is_done ? 'btn-done' : 'btn-todo'}" 
                            onclick="markReminderDone(${reminder.id}, ${!reminder.is_done})">
                        ${reminder.is_done ? '✓ Done' : '○ Mark Done'}
                    </button>
                </div>
            </div>
        `;
    }).join('');
    
    container.innerHTML = remindersHTML;
}

/**
 * Mark a reminder as done/undone
 */
async function markReminderDone(id, isDone) {
    const updated = await updateReminder(id, { is_done: isDone });
    if (updated) {
        await renderPatientReminders();
        
        // Trigger voice greeting after update if voice API available
        if (window.VoiceAPI) {
            // Re-fetch to get updated reminders
            const reminders = await fetchReminders();
            window.VoiceAPI.updateRemindersData(reminders);
        }
    }
}

// ============================================================
// UI RENDERING - CAREGIVER DASHBOARD
// ============================================================

/**
 * Initialize caregiver dashboard reminder management
 */
async function initCaregiverReminders() {
    const formContainer = document.getElementById('add-reminder-form');
    const listContainer = document.getElementById('manage-reminders-list');
    
    if (!formContainer || !listContainer) return;
    
    // Render form
    formContainer.innerHTML = `
        <form id="reminder-form" class="reminder-form">
            <h3>Add New Reminder</h3>
            
            <div class="form-group">
                <label for="reminder-title">Title</label>
                <input type="text" id="reminder-title" name="title" class="form-input" 
                       placeholder="e.g., Take blood pressure medication" required>
            </div>
            
            <div class="form-row">
                <div class="form-group">
                    <label for="reminder-type">Type</label>
                    <select id="reminder-type" name="type" class="form-input" required>
                        <option value="">Select type...</option>
                        <option value="medicine">💊 Medicine</option>
                        <option value="appointment">📅 Appointment</option>
                        <option value="activity">🎯 Activity</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="reminder-time">Time</label>
                    <input type="time" id="reminder-time" name="time" class="form-input" required>
                </div>
            </div>
            
            <button type="submit" class="btn btn-primary btn-large">Add Reminder</button>
        </form>
    `;
    
    // Attach form submit handler
    document.getElementById('reminder-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);
        const reminder = await createReminder(
            formData.get('title'),
            formData.get('type'),
            formData.get('time')
        );
        if (reminder) {
            e.target.reset();
            await renderCaregiverReminders();
        }
    });
    
    // Render existing reminders list
    await renderCaregiverReminders();
}

/**
 * Render reminders list for caregiver dashboard
 */
async function renderCaregiverReminders() {
    const container = document.getElementById('manage-reminders-list');
    if (!container) return;
    
    const reminders = await fetchReminders();
    
    if (reminders.length === 0) {
        container.innerHTML = '<p class="empty-state">No reminders created yet.</p>';
        return;
    }
    
    const remindersHTML = `
        <table class="reminders-table">
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Title</th>
                    <th>Type</th>
                    <th>Status</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
                ${reminders.map(reminder => {
                    const typeInfo = getTypeInfo(reminder.type);
                    return `
                        <tr class="reminder-row ${reminder.is_done ? 'done' : ''}">
                            <td class="time">${reminder.time}</td>
                            <td class="title">${reminder.title}</td>
                            <td class="type">
                                <span class="type-badge" style="background-color: ${typeInfo.color}">
                                    ${typeInfo.icon} ${typeInfo.label}
                                </span>
                            </td>
                            <td class="status">
                                <span class="status-badge ${reminder.is_done ? 'status-done' : 'status-pending'}">
                                    ${reminder.is_done ? 'Done' : 'Pending'}
                                </span>
                            </td>
                            <td class="actions">
                                <button class="btn btn-sm btn-secondary" 
                                        onclick="editReminder(${reminder.id})">Edit</button>
                                <button class="btn btn-sm btn-danger" 
                                        onclick="confirmDelete(${reminder.id})">Delete</button>
                            </td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
    `;
    
    container.innerHTML = remindersHTML;
}

/**
 * Edit a reminder (simple prompt-based for MVP)
 */
async function editReminder(id) {
    const reminders = await fetchReminders();
    const reminder = reminders.find(r => r.id === id);
    if (!reminder) return;
    
    const newTitle = prompt('Edit title:', reminder.title);
    if (newTitle === null) return;
    
    const updated = await updateReminder(id, { title: newTitle });
    if (updated) {
        await renderCaregiverReminders();
    }
}

/**
 * Confirm and delete a reminder
 */
async function confirmDelete(id) {
    if (confirm('Are you sure you want to delete this reminder?')) {
        const success = await deleteReminder(id);
        if (success) {
            await renderCaregiverReminders();
        }
    }
}

// ============================================================
// INITIALIZATION
// ============================================================

/**
 * Initialize reminders based on current page
 */
document.addEventListener('DOMContentLoaded', () => {
    // Patient home page
    if (document.getElementById('reminders-container')) {
        renderPatientReminders();
    }
    
    // Caregiver dashboard
    if (document.getElementById('add-reminder-form')) {
        initCaregiverReminders();
    }
});
