/**
 * MEMORA Voice Assistant - Phase 7
 * Uses browser's built-in Web Speech API (SpeechSynthesis + SpeechRecognition)
 * No external APIs or paid services required
 */

// ============================================================
// VOICE ASSISTANT STATE
// ============================================================

const VoiceAssistant = {
    isListening: false,
    isSpeaking: false,
    recognition: null,
    synthesis: window.speechSynthesis,
    isSupported: {
        tts: 'speechSynthesis' in window,
        stt: 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window
    },
    remindersData: []  // Will be populated by reminders.js
};

// Initialize speech recognition if supported
if (VoiceAssistant.isSupported.stt) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    VoiceAssistant.recognition = new SpeechRecognition();
    
    // Configuration
    VoiceAssistant.recognition.continuous = false;
    VoiceAssistant.recognition.interimResults = false;
    VoiceAssistant.recognition.language = 'en-US';
}

// ============================================================
// TEXT-TO-SPEECH FUNCTION
// ============================================================

function speak(text) {
    return new Promise((resolve, reject) => {
        if (!VoiceAssistant.isSupported.tts) {
            console.warn('Text-to-speech not supported in this browser');
            reject('TTS not supported');
            return;
        }

        // Cancel any ongoing speech
        VoiceAssistant.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        
        // Settings optimized for elderly listeners
        utterance.rate = 0.9;        // Slightly slower for clarity
        utterance.pitch = 1.0;       // Normal pitch
        utterance.volume = 1.0;      // Full volume
        utterance.lang = 'en-US';

        // Update state
        utterance.onstart = () => {
            VoiceAssistant.isSpeaking = true;
            updateVoiceUI();
        };

        utterance.onend = () => {
            VoiceAssistant.isSpeaking = false;
            updateVoiceUI();
            resolve();
        };

        utterance.onerror = (event) => {
            console.error('Speech error:', event.error);
            VoiceAssistant.isSpeaking = false;
            updateVoiceUI();
            reject(event.error);
        };

        // Speak the text
        VoiceAssistant.synthesis.speak(utterance);
    });
}

// ============================================================
// SPEECH-TO-TEXT FUNCTION
// ============================================================

function listenForQuery() {
    if (!VoiceAssistant.isSupported.stt) {
        console.warn('Speech recognition not supported');
        showVoiceMessage('Voice input is not supported in your browser. Please use Chrome or Edge.');
        return;
    }

    if (VoiceAssistant.isListening) {
        stopListening();
        return;
    }

    // Start listening
    VoiceAssistant.isListening = true;
    updateVoiceUI();

    VoiceAssistant.recognition.onstart = () => {
        console.log('Listening started...');
    };

    VoiceAssistant.recognition.onresult = (event) => {
        let transcript = '';
        
        // Collect all results
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }

        console.log('Heard:', transcript);

        // Process the query
        processVoiceQuery(transcript.toLowerCase());
    };

    VoiceAssistant.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        VoiceAssistant.isListening = false;
        updateVoiceUI();

        // Handle specific errors gracefully
        if (event.error === 'no-speech') {
            speak('I did not hear anything. Please try again.');
        } else if (event.error !== 'aborted') {
            speak('Sorry, there was an issue with voice recognition.');
        }
    };

    VoiceAssistant.recognition.onend = () => {
        VoiceAssistant.isListening = false;
        updateVoiceUI();
    };

    try {
        VoiceAssistant.recognition.start();
    } catch (error) {
        console.error('Error starting recognition:', error);
        VoiceAssistant.isListening = false;
        updateVoiceUI();
    }
}

function stopListening() {
    if (VoiceAssistant.recognition && VoiceAssistant.isListening) {
        VoiceAssistant.recognition.abort();
        VoiceAssistant.isListening = false;
        updateVoiceUI();
    }
}

// ============================================================
// VOICE QUERY PROCESSING (Intent Matching)
// ============================================================

async function processVoiceQuery(query) {
    console.log('Processing query:', query);

    try {
        // Intent: Memory Companion Query (Phase 10C)
        if (isMemoryCompanionQuery(query)) {
            await handleMemoryCompanionQuery(query);
            return;
        }

        // Intent: Current time
        if (query.includes('time') && !query.includes('reminder')) {
            const now = new Date();
            const timeStr = now.toLocaleTimeString('en-US', {
                hour: 'numeric',
                minute: '2-digit',
                hour12: true
            });
            await speak(`The time is ${timeStr}.`);
            return;
        }

        // Intent: Today's date
        if (query.includes('date') || query.includes('today') || query.includes('what day')) {
            const today = new Date();
            const dateStr = today.toLocaleDateString('en-US', {
                weekday: 'long',
                month: 'long',
                day: 'numeric',
                year: 'numeric'
            });
            await speak(`Today is ${dateStr}.`);
            return;
        }

        // Intent: Next reminder
        if (query.includes('reminder') || query.includes('next') || query.includes('task')) {
            respondToReminderQuery();
            return;
        }

        // Intent: Mood query (Phase 10D)
        if (isMoodQuery(query)) {
            await handleMoodQuery(query);
            return;
        }

        // Intent: Greeting
        if (query.includes('how are you') || query.includes('hello') || query.includes('hi there')) {
            const greeting = 'I am Memora, your voice assistant. I am here to help you stay on track with your tasks and reminders.';
            await speak(greeting);
            return;
        }

        // Intent: No match
        await speak('Sorry, I did not understand. Please try asking about the time, date, or your reminders.');

    } catch (error) {
        console.error('Error processing query:', error);
    }
}

// ============================================================
// MEMORY COMPANION QUERY DETECTION & HANDLING (Phase 10C)
// ============================================================

function isMemoryCompanionQuery(query) {
    /**
     * Detect if query is a memory companion query.
     * Examples: "Who is Anil?", "where is home?", "tell me about Anil"
     */
    const keywords = ['who is', "who's", 'where is', 'tell me about', 'describe', 
                      'how is', 'what about', 'who am i'];
    return keywords.some(kw => query.toLowerCase().includes(kw));
}

async function handleMemoryCompanionQuery(query) {
    /**
     * Handle memory companion query via API.
     * Searches patient's memory and speaks the result.
     */
    try {
        console.log('Handling memory companion query:', query);
        
        // Show listening indicator
        showVoiceMessage('Searching your memories...');
        
        // Call the API
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
            const errorMsg = errorData.error || 'Could not search memories';
            console.error('Memory search error:', errorMsg);
            await speak('I had trouble searching your memory. Please try again later.');
            return;
        }
        
        const data = await response.json();
        
        if (!data.success) {
            console.error('Memory search failed:', data.error);
            await speak(data.response || 'I could not find that information.');
            return;
        }
        
        // Speak the response
        const responseText = data.response;
        console.log('Memory companion response:', responseText);
        await speak(responseText);
        
    } catch (error) {
        console.error('Error handling memory companion query:', error);
        await speak('I had trouble searching your memory. Please try again.');
    }
}

// ============================================================
// REMINDER QUERY HANDLER
// ============================================================

async function respondToReminderQuery() {
    try {
        // If reminders data is not yet available, fetch it
        if (!VoiceAssistant.remindersData || VoiceAssistant.remindersData.length === 0) {
            // Try to fetch from API
            const response = await fetch(`/api/reminders/${USER_ID}`, { credentials: 'include' });
            if (response.ok) {
                VoiceAssistant.remindersData = await response.json();
            }
        }

        // Find active reminders
        const activeReminders = VoiceAssistant.remindersData.filter(r => r.is_active);

        if (activeReminders.length === 0) {
            await speak('You have no more reminders today.');
            return;
        }

        // Get the first reminder
        const nextReminder = activeReminders[0];
        const reminderText = `Your next reminder is: ${nextReminder.title} at ${nextReminder.time}.`;
        await speak(reminderText);

    } catch (error) {
        console.error('Error responding to reminder query:', error);
        await speak('I had trouble retrieving your reminders. Please try again later.');
    }
}

// ============================================================
// AUTO-SPEAK REMINDERS GREETING (On Page Load)
// ============================================================

async function speakRemindersGreeting() {
    try {
        // Wait a moment for reminders to load
        await new Promise(resolve => setTimeout(resolve, 500));

        // Build greeting message
        let greeting = 'Good morning. ';

        if (!VoiceAssistant.remindersData || VoiceAssistant.remindersData.length === 0) {
            greeting += 'You have no reminders today.';
        } else {
            const activeReminders = VoiceAssistant.remindersData.filter(r => r.is_active);

            if (activeReminders.length === 0) {
                greeting += 'You have no reminders scheduled for today.';
            } else if (activeReminders.length === 1) {
                greeting += `You have 1 reminder today: ${activeReminders[0].title} at ${activeReminders[0].time}.`;
            } else {
                greeting += `You have ${activeReminders.length} reminders today: `;
                const reminderTexts = activeReminders.map(r => `${r.title} at ${r.time}`);
                greeting += reminderTexts.join(', ') + '.';
            }
        }

        // Try to speak (may be blocked by autoplay policy)
        try {
            await speak(greeting);
        } catch (error) {
            console.log('Auto-speak blocked (common on first load). User can click "Read my reminders" button.');
        }

    } catch (error) {
        console.error('Error speaking greeting:', error);
    }
}

// ============================================================
// UI STATE UPDATES
// ============================================================

function updateVoiceUI() {
    const askBtn = document.getElementById('voice-ask-button');
    const readBtn = document.getElementById('voice-read-button');
    const statusDiv = document.getElementById('voice-status');

    if (!askBtn) return;  // Voice UI not initialized yet

    if (VoiceAssistant.isListening) {
        askBtn.classList.add('listening');
        askBtn.textContent = '🎤 Listening...';
        askBtn.disabled = true;
        if (statusDiv) statusDiv.textContent = '🎙️ Listening...';
    } else if (VoiceAssistant.isSpeaking) {
        if (readBtn) readBtn.disabled = true;
        askBtn.disabled = true;
        if (statusDiv) statusDiv.textContent = '🔊 Speaking...';
    } else {
        askBtn.classList.remove('listening');
        askBtn.textContent = '🎤 Ask Memora';
        askBtn.disabled = false;
        if (readBtn) readBtn.disabled = false;
        if (statusDiv) statusDiv.textContent = '';
    }
}

// ============================================================
// UI MESSAGE HELPER
// ============================================================

function showVoiceMessage(message) {
    const statusDiv = document.getElementById('voice-status');
    if (statusDiv) {
        statusDiv.textContent = message;
        setTimeout(() => {
            statusDiv.textContent = '';
        }, 4000);
    }
}

// ============================================================
// MOOD QUERY HANDLER (Phase 10D)
// ============================================================

function isMoodQuery(query) {
    /**
     * Detect if query is asking about mood/feelings
     */
    const moodKeywords = [
        'mood', 'feeling', 'how am i', 'how do i feel', 'feel',
        'happy', 'sad', 'okay', 'stressed', 'upset', 'emotional'
    ];
    
    return moodKeywords.some(keyword => query.includes(keyword));
}

async function handleMoodQuery(query) {
    /**
     * Handle mood-related questions
     */
    try {
        // Fetch today's mood
        const response = await fetch('/api/mood/today', { credentials: 'include' });
        if (!response.ok) {
            await speak('I was unable to retrieve your mood. Please record it on the mood tracker page.');
            return;
        }

        const data = await response.json();
        
        if (!data.has_entry || !data.entry) {
            await speak('You have not recorded a mood today. Please visit the mood tracker to record how you are feeling.');
            return;
        }

        // Format mood response
        const mood = data.entry.mood;
        const moodLabel = getMoodLabel(mood);
        const timestamp = new Date(data.entry.timestamp);
        const timeStr = timestamp.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });

        let response_text = `Your mood today is ${moodLabel}, recorded at ${timeStr}.`;
        
        if (data.entry.note) {
            response_text += ` You noted: ${data.entry.note}`;
        }

        await speak(response_text);

    } catch (error) {
        console.error('Error handling mood query:', error);
        await speak('I had trouble retrieving your mood information. Please try again later.');
    }
}

function getMoodLabel(mood) {
    /**
     * Convert mood value to readable label
     */
    const labels = {
        'very_happy': 'very happy',
        'happy': 'happy',
        'okay': 'okay',
        'sad': 'sad',
        'very_sad': 'very sad'
    };
    
    return labels[mood] || mood;
}

// ============================================================
// PUBLIC API
// ============================================================

// Export functions for use in HTML
window.VoiceAPI = {
    speak,
    listenForQuery,
    stopListening,
    speakRemindersGreeting,
    updateRemindersData: (data) => {
        VoiceAssistant.remindersData = data;
    },
    isSupported: () => VoiceAssistant.isSupported
};

// Log support status
console.log('Voice Assistant initialized. TTS supported:', VoiceAssistant.isSupported.tts, 'STT supported:', VoiceAssistant.isSupported.stt);
