/**
 * Phase 10D: Mood Tracking
 * Mood page state management and API integration
 */

const MoodState = {
    currentMood: null,
    currentNote: '',
    todayEntry: null,
    historyEntries: [],
    isSubmitting: false
};

// Mood emoji mapping
const MOOD_EMOJIS = {
    'very_happy': '😊',
    'happy': '🙂',
    'okay': '😐',
    'sad': '😟',
    'very_sad': '😔'
};

const MOOD_LABELS = {
    'very_happy': 'Very Happy',
    'happy': 'Happy',
    'okay': 'Okay',
    'sad': 'Sad',
    'very_sad': 'Very Sad'
};

/**
 * Initialize mood page on load
 */
async function initMoodPage() {
    console.log('[Mood] Initializing mood page...');
    
    // Add event listeners to mood buttons
    const moodButtons = document.querySelectorAll('.mood-button');
    moodButtons.forEach(button => {
        button.addEventListener('click', () => handleMoodSelect(button.dataset.mood));
    });
    
    // Add event listener to save button
    const saveMoodBtn = document.getElementById('save-mood-btn');
    if (saveMoodBtn) {
        saveMoodBtn.addEventListener('click', () => {
            if (MoodState.currentMood) {
                submitMood(MoodState.currentMood, MoodState.currentNote);
            }
        });
    }
    
    // Add event listener to clear button
    const clearMoodBtn = document.getElementById('clear-mood-btn');
    if (clearMoodBtn) {
        clearMoodBtn.addEventListener('click', clearMoodSelection);
    }
    
    // Load today's mood
    await loadTodaysMood();
    
    // Load mood history
    await loadMoodHistory();
    
    console.log('[Mood] Page initialized');
}

/**
 * Handle mood button click
 */
function handleMoodSelect(mood) {
    console.log('[Mood] Selected mood:', mood);
    
    MoodState.currentMood = mood;
    
    // Update button states
    const moodButtons = document.querySelectorAll('.mood-button');
    moodButtons.forEach(button => {
        button.classList.remove('selected');
        if (button.dataset.mood === mood) {
            button.classList.add('selected');
        }
    });
    
    // Show note section and submit button
    const noteSection = document.getElementById('note-section');
    const submitSection = document.getElementById('submit-section');
    if (noteSection) noteSection.style.display = 'block';
    if (submitSection) submitSection.style.display = 'block';
    
    // Hide confirmation and today's mood sections
    const confirmationSection = document.getElementById('confirmation-section');
    const todaysMoodSection = document.getElementById('todays-mood-section');
    if (confirmationSection) confirmationSection.style.display = 'none';
    if (todaysMoodSection) todaysMoodSection.style.display = 'none';
    
    // Focus on note textarea
    setTimeout(() => {
        const noteTextarea = document.getElementById('mood-note');
        if (noteTextarea) noteTextarea.focus();
    }, 100);
}

/**
 * Clear mood selection
 */
function clearMoodSelection() {
    console.log('[Mood] Clearing mood selection');
    
    MoodState.currentMood = null;
    MoodState.currentNote = '';
    
    // Remove selected state from all buttons
    const moodButtons = document.querySelectorAll('.mood-button');
    moodButtons.forEach(button => {
        button.classList.remove('selected');
    });
    
    // Clear note textarea
    const noteTextarea = document.getElementById('mood-note');
    if (noteTextarea) noteTextarea.value = '';
    
    // Hide sections
    const noteSection = document.getElementById('note-section');
    const submitSection = document.getElementById('submit-section');
    if (noteSection) noteSection.style.display = 'none';
    if (submitSection) submitSection.style.display = 'none';
}

/**
 * Submit mood to API
 */
async function submitMood(mood, note) {
    if (!mood) {
        showMoodError(i18n.get('mood_error'));
        return;
    }
    
    if (MoodState.isSubmitting) {
        console.log('[Mood] Already submitting...');
        return;
    }
    
    MoodState.isSubmitting = true;
    
    try {
        const response = await fetch('/api/mood/entries', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                mood: mood,
                note: note || null
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            showMoodError(error.error || i18n.get('mood_error'));
            MoodState.isSubmitting = false;
            return;
        }
        
        const data = await response.json();
        console.log('[Mood] Mood entry created:', data);
        
        MoodState.todayEntry = data;
        showMoodSuccess(note ? i18n.get('mood_saved_with_note') : i18n.get('mood_saved'));
        
        // Update UI
        updateMoodUI();
        
        // Reload history
        await loadMoodHistory();
        
    } catch (error) {
        console.error('[Mood] Error submitting mood:', error);
        showMoodError(i18n.get('mood_error'));
    } finally {
        MoodState.isSubmitting = false;
    }
}

/**
 * Load today's mood from API
 */
async function loadTodaysMood() {
    try {
        const response = await fetch('/api/mood/today', { credentials: 'include' });
        if (!response.ok) {
            console.log('[Mood] No mood recorded for today');
            return;
        }
        
        const data = await response.json();
        if (data.has_entry && data.entry) {
            MoodState.todayEntry = data.entry;
            console.log('[Mood] Today\'s mood loaded:', data.entry);
        }
    } catch (error) {
        console.error('[Mood] Error loading today\'s mood:', error);
    }
}

/**
 * Load mood history from API
 */
async function loadMoodHistory() {
    try {
        const response = await fetch('/api/mood/history?days=14&limit=50', { credentials: 'include' });
        if (!response.ok) {
            console.log('[Mood] Failed to load mood history');
            return;
        }
        
        const data = await response.json();
        MoodState.historyEntries = data.entries || [];
        console.log('[Mood] History loaded:', MoodState.historyEntries.length, 'entries');
        
        renderMoodHistory(MoodState.historyEntries);
    } catch (error) {
        console.error('[Mood] Error loading mood history:', error);
    }
}

/**
 * Render mood history in UI
 */
function renderMoodHistory(entries) {
    const historyContainer = document.getElementById('mood-history');
    const noHistoryMessage = document.getElementById('no-history-message');
    
    if (!historyContainer) return;
    
    if (entries.length === 0) {
        historyContainer.innerHTML = '';
        if (noHistoryMessage) noHistoryMessage.style.display = 'block';
        return;
    }
    
    if (noHistoryMessage) noHistoryMessage.style.display = 'none';
    
    historyContainer.innerHTML = entries.map((entry, index) => {
        const date = new Date(entry.timestamp);
        const dateStr = formatMoodDate(date);
        const timeStr = formatMoodTime(date);
        const emoji = MOOD_EMOJIS[entry.mood] || '😐';
        const label = MOOD_LABELS[entry.mood] || entry.mood;
        
        let html = `
            <div class="mood-card">
                <div class="mood-card-header">
                    <span class="mood-card-emoji">${emoji}</span>
                    <div>
                        <div class="mood-card-date">${label}</div>
                        <div class="mood-card-time">${dateStr} at ${timeStr}</div>
                    </div>
                </div>
        `;
        
        if (entry.note) {
            html += `<div class="mood-card-note">${escapeHtml(entry.note)}</div>`;
        }
        
        html += `</div>`;
        
        return html;
    }).join('');
}

/**
 * Update mood UI after successful submission
 */
function updateMoodUI() {
    if (!MoodState.todayEntry) return;
    
    const emoji = MOOD_EMOJIS[MoodState.todayEntry.mood] || '😐';
    const label = MOOD_LABELS[MoodState.todayEntry.mood] || MoodState.todayEntry.mood;
    
    // Update mood display
    const moodDisplay = document.getElementById('mood-display');
    if (moodDisplay) moodDisplay.textContent = emoji;
    
    const moodValue = document.getElementById('mood-value');
    if (moodValue) moodValue.textContent = label;
    
    const moodTime = document.getElementById('mood-time');
    if (moodTime) {
        const date = new Date(MoodState.todayEntry.timestamp);
        moodTime.textContent = formatMoodDate(date) + ' at ' + formatMoodTime(date);
    }
    
    const moodNoteDisplay = document.getElementById('mood-note-display');
    if (moodNoteDisplay) {
        if (MoodState.todayEntry.note) {
            moodNoteDisplay.textContent = MoodState.todayEntry.note;
        } else {
            moodNoteDisplay.textContent = '';
        }
    }
    
    // Show sections
    const todaysMoodSection = document.getElementById('todays-mood-section');
    const confirmationSection = document.getElementById('confirmation-section');
    const noteSection = document.getElementById('note-section');
    const submitSection = document.getElementById('submit-section');
    
    if (todaysMoodSection) todaysMoodSection.style.display = 'block';
    if (confirmationSection) confirmationSection.style.display = 'block';
    if (noteSection) noteSection.style.display = 'none';
    if (submitSection) submitSection.style.display = 'none';
    
    // Clear buttons and note
    clearMoodSelection();
}

/**
 * Format date for mood display
 */
function formatMoodDate(date) {
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);
    
    const isToday = date.toDateString() === today.toDateString();
    const isYesterday = date.toDateString() === yesterday.toDateString();
    
    if (isToday) {
        return i18n.get('mood_today_label') || 'Today';
    } else if (isYesterday) {
        return 'Yesterday';
    } else {
        return date.toLocaleDateString('en-US', { 
            weekday: 'short', 
            month: 'short', 
            day: 'numeric'
        });
    }
}

/**
 * Format time for mood display
 */
function formatMoodTime(date) {
    return date.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true
    });
}

/**
 * Show mood error message
 */
function showMoodError(message) {
    console.error('[Mood] Error:', message);
    alert(message);
}

/**
 * Show mood success message
 */
function showMoodSuccess(message) {
    console.log('[Mood] Success:', message);
    // Message is shown in the confirmation-section which is already displayed
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * i18n wrapper for translation keys
 */
const i18n = {
    get: function(key) {
        // This relies on the global i18n.js from the application
        if (typeof window.getTranslation === 'function') {
            return window.getTranslation(key);
        }
        return key;
    }
};

// Initialize page when DOM is ready
document.addEventListener('DOMContentLoaded', initMoodPage);
