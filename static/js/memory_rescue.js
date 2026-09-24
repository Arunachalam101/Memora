/**
 * MEMORA Memory Rescue - Phase 10C
 * View-only UI for searching and retrieving memory information
 * Integrates with existing Voice Assistant for speech input/output
 */

// ============================================================
// MEMORY RESCUE STATE
// ============================================================

const MemoryRescue = {
    currentQuery: '',
    currentResults: null,
    isSearching: false
};

// ============================================================
// DOM INITIALIZATION (When page loads)
// ============================================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Memory Rescue page initialized');
    
    // Reuse Voice Assistant from voice_assistant.js
    if (typeof VoiceAssistant === 'undefined') {
        console.error('Voice Assistant not loaded. Make sure voice_assistant.js is included.');
        return;
    }
    
    // Attach event listeners
    const voiceButton = document.getElementById('memory-voice-button');
    if (voiceButton) {
        voiceButton.addEventListener('click', handleMemoryVoiceClick);
    }
    
    const speakButton = document.getElementById('memory-speak-button');
    if (speakButton) {
        speakButton.addEventListener('click', handleMemorySpeakClick);
    }
    
    // Apply i18n translations
    applyTranslations();
});

// ============================================================
// VOICE INPUT HANDLER
// ============================================================

function handleMemoryVoiceClick() {
    console.log('Memory voice button clicked');
    
    if (!VoiceAssistant.isSupported.stt) {
        showMemoryError('Voice input is not supported in your browser. Please use Chrome or Edge.');
        return;
    }
    
    if (VoiceAssistant.isListening) {
        stopMemoryListening();
        return;
    }
    
    startMemoryListening();
}

function startMemoryListening() {
    VoiceAssistant.isListening = true;
    updateMemoryVoiceUI();
    
    const statusSpan = document.getElementById('memory-voice-status');
    if (statusSpan) {
        statusSpan.textContent = '🔴 Listening...';
    }
    
    VoiceAssistant.recognition.onstart = () => {
        console.log('Memory: Listening started');
    };
    
    VoiceAssistant.recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        
        if (event.isFinal) {
            console.log('Memory: Captured query:', transcript);
            handleMemoryQuery(transcript);
        }
    };
    
    VoiceAssistant.recognition.onerror = (event) => {
        console.error('Memory: Recognition error:', event.error);
        if (event.error === 'no-speech') {
            showMemoryError('I didn\'t hear anything. Please try again.');
        } else if (event.error === 'network') {
            showMemoryError('Connection error. Please check your internet.');
        } else {
            showMemoryError('Voice input error: ' + event.error);
        }
        stopMemoryListening();
    };
    
    VoiceAssistant.recognition.onend = () => {
        VoiceAssistant.isListening = false;
        updateMemoryVoiceUI();
    };
    
    try {
        VoiceAssistant.recognition.start();
    } catch (e) {
        console.error('Error starting recognition:', e);
        showMemoryError('Could not start voice input. Please try again.');
        stopMemoryListening();
    }
}

function stopMemoryListening() {
    if (VoiceAssistant.recognition && VoiceAssistant.isListening) {
        VoiceAssistant.recognition.stop();
    }
    VoiceAssistant.isListening = false;
    updateMemoryVoiceUI();
    
    const statusSpan = document.getElementById('memory-voice-status');
    if (statusSpan) {
        statusSpan.textContent = '';
    }
}

// ============================================================
// MEMORY QUERY PROCESSING
// ============================================================

async function handleMemoryQuery(query) {
    console.log('Handling memory query:', query);
    
    if (!query || query.trim() === '') {
        showMemoryError('No query detected. Please try again.');
        return;
    }
    
    query = query.trim();
    MemoryRescue.currentQuery = query;
    MemoryRescue.isSearching = true;
    
    // Display the query
    const queryDisplay = document.getElementById('memory-query-display');
    const queryText = document.getElementById('memory-query-text');
    if (queryDisplay && queryText) {
        queryText.textContent = query;
        queryDisplay.style.display = 'block';
    }
    
    try {
        // Call the search API
        const response = await fetch('/api/memory/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ query: query })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            showMemoryError(errorData.error || 'Search failed');
            return;
        }
        
        const data = await response.json();
        
        if (!data.success) {
            showMemoryError(data.error || 'Search failed');
            return;
        }
        
        // Store results
        MemoryRescue.currentResults = data.results;
        
        // Display response
        displayMemoryResponse(data.response, data.results);
        
        // Speak the response
        await speakMemoryResponse(data.response);
        
    } catch (error) {
        console.error('Error searching memory:', error);
        showMemoryError('Connection error. Please try again.');
    } finally {
        MemoryRescue.isSearching = false;
        updateMemoryVoiceUI();
    }
}

// ============================================================
// RESPONSE DISPLAY
// ============================================================

function displayMemoryResponse(responseText, results) {
    // Show response section
    const responseSection = document.getElementById('memory-response-section');
    if (responseSection) {
        responseSection.style.display = 'block';
    }
    
    // Display response text
    const responseDisplay = document.getElementById('memory-response-text');
    if (responseDisplay) {
        responseDisplay.textContent = responseText;
    }
    
    // Show results section if there are results
    if (!results || (!results.people?.length && !results.places?.length && !results.memories?.length)) {
        const resultsSection = document.getElementById('memory-results-section');
        if (resultsSection) {
            resultsSection.style.display = 'none';
        }
        return;
    }
    
    const resultsSection = document.getElementById('memory-results-section');
    if (resultsSection) {
        resultsSection.style.display = 'block';
    }
    
    // Display people results
    if (results.people && results.people.length > 0) {
        displayMemoryCategory('people', results.people, 'memory-people');
    } else {
        hideMemoryCategory('memory-people');
    }
    
    // Display places results
    if (results.places && results.places.length > 0) {
        displayMemoryCategory('places', results.places, 'memory-places');
    } else {
        hideMemoryCategory('memory-places');
    }
    
    // Display memories results
    if (results.memories && results.memories.length > 0) {
        displayMemoryCategory('memories', results.memories, 'memory-memories');
    } else {
        hideMemoryCategory('memory-memories');
    }
}

function displayMemoryCategory(type, items, prefix) {
    const resultsDiv = document.getElementById(`${prefix}-results`);
    const listDiv = document.getElementById(`${prefix}-list`);
    
    if (!resultsDiv || !listDiv) return;
    
    resultsDiv.style.display = 'block';
    listDiv.innerHTML = '';
    
    items.forEach(item => {
        const card = createMemoryItemCard(type, item);
        listDiv.appendChild(card);
    });
}

function hideMemoryCategory(prefix) {
    const resultsDiv = document.getElementById(`${prefix}-results`);
    if (resultsDiv) {
        resultsDiv.style.display = 'none';
    }
}

function createMemoryItemCard(type, item) {
    const col = document.createElement('div');
    col.className = 'col-md-6';
    
    let content = '';
    
    if (type === 'people') {
        content = `
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title">${item.name}</h6>
                    <p class="card-text small"><strong>Relationship:</strong> ${item.relationship}</p>
                    ${item.description ? `<p class="card-text small">${item.description}</p>` : ''}
                    ${item.photo ? `<img src="${item.photo}" class="img-thumbnail mt-2" style="max-width: 150px;">` : ''}
                </div>
            </div>
        `;
    } else if (type === 'places') {
        content = `
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title">${item.name}</h6>
                    ${item.description ? `<p class="card-text small">${item.description}</p>` : ''}
                    ${item.photo ? `<img src="${item.photo}" class="img-thumbnail mt-2" style="max-width: 150px;">` : ''}
                </div>
            </div>
        `;
    } else if (type === 'memories') {
        content = `
            <div class="card h-100">
                <div class="card-body">
                    <h6 class="card-title">${item.title}</h6>
                    ${item.description ? `<p class="card-text small">${item.description}</p>` : ''}
                    ${item.memory_date ? `<p class="card-text small"><strong>Date:</strong> ${item.memory_date}</p>` : ''}
                    ${item.photo ? `<img src="${item.photo}" class="img-thumbnail mt-2" style="max-width: 150px;">` : ''}
                </div>
            </div>
        `;
    }
    
    col.innerHTML = content;
    return col;
}

// ============================================================
// SPEECH OUTPUT
// ============================================================

async function speakMemoryResponse(responseText) {
    try {
        await speak(responseText);
    } catch (error) {
        console.error('Error speaking response:', error);
    }
}

function handleMemorySpeakClick() {
    const responseText = document.getElementById('memory-response-text')?.textContent;
    if (responseText) {
        speakMemoryResponse(responseText);
    }
}

// ============================================================
// ERROR HANDLING
// ============================================================

function showMemoryError(message) {
    const errorContainer = document.getElementById('memory-error-container');
    if (!errorContainer) return;
    
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    errorContainer.innerHTML = '';
    errorContainer.appendChild(alert);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// ============================================================
// UI UPDATES
// ============================================================

function updateMemoryVoiceUI() {
    const button = document.getElementById('memory-voice-button');
    if (!button) return;
    
    if (VoiceAssistant.isListening) {
        button.textContent = '⏹️ Stop';
        button.classList.add('active');
    } else if (MemoryRescue.isSearching) {
        button.textContent = '⏳ Searching...';
        button.disabled = true;
    } else {
        button.textContent = '🎤 Ask Memora';
        button.classList.remove('active');
        button.disabled = false;
    }
}

// ============================================================
// i18n INTEGRATION
// ============================================================

// Ensure translations are applied when the page loads
// This reuses the applyTranslations() function from i18n.js
if (typeof applyTranslations === 'undefined') {
    console.warn('i18n.js not loaded. Translations may not work.');
}
