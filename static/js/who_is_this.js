/**
 * MEMORA Who Is This? Game - Phase 10B
 * Patient sees person's name and selects correct photo from options
 */

// ============================================================
// GAME CONFIG
// ============================================================

const GAME_CONFIG = {
    TOTAL_QUESTIONS: 5,
    POINTS_PER_CORRECT: 20,
    MAX_SCORE: 100,
    MIN_PEOPLE_REQUIRED: 2,
    DIFFICULTY_CHOICES: {
        easy: 2,
        medium: 3,
        hard: 4
    }
};

// ============================================================
// GAME STATE
// ============================================================

let gameState = {
    people: [],
    questions: [],
    currentQuestionIndex: 0,
    correctAnswers: 0,
    startTime: null,
    difficulty: 'medium',
    gameActive: false,
    answers: []
};

let timerInterval;

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    if (!USER_ID || USER_ID === 'null') {
        showError('Not logged in', 'Please log in to play the game.');
        return;
    }
    
    try {
        // Fetch difficulty
        await fetchDifficulty();
        
        // Load memory people
        await loadMemoryPeople();
        
        // Initialize game
        if (gameState.people.length < GAME_CONFIG.MIN_PEOPLE_REQUIRED) {
            showError('Not enough memories', 'Ask your caregiver to add more familiar people to your Memory Album.');
            return;
        }
        
        generateQuestions();
        gameState.gameActive = true;
        gameState.startTime = Date.now();
        startTimer();  // Start the timer
        
        // Show game
        document.getElementById('error-state').style.display = 'none';
        document.getElementById('game-state').style.display = 'block';
        
        // Apply translations
        if (typeof I18N !== 'undefined') {
            I18N.applyTranslations();
        }
        
        // Display first question
        displayQuestion();
        
    } catch (error) {
        console.error('Game initialization error:', error);
        showError('Failed to start game', error.message || 'Please try again.');
    }
});

// ============================================================
// DIFFICULTY & DATA LOADING
// ============================================================

async function fetchDifficulty() {
    try {
        const response = await fetch(`/api/difficulty/${USER_ID}`, { credentials: 'include' });
        if (!response.ok) {
            console.warn('Failed to fetch difficulty, using default');
            return;
        }
        
        const data = await response.json();
        gameState.difficulty = data.difficulty || 'medium';
        
        // Update difficulty badge
        const emojis = {
            'easy': '🟢 Easy',
            'medium': '🟡 Medium',
            'hard': '🔴 Hard'
        };
        document.getElementById('difficulty-badge').textContent = emojis[gameState.difficulty] || '🟡 Medium';
        
    } catch (error) {
        console.error('Error fetching difficulty:', error);
    }
}

async function loadMemoryPeople() {
    try {
        const response = await fetch(`/api/memory/people?patient_id=${USER_ID}`, { credentials: 'include' });
        
        if (response.status === 401) {
            throw new Error('Unauthorized');
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to load people');
        }
        
        const data = await response.json();
        
        // Filter only active people
        gameState.people = (Array.isArray(data) ? data : [])
            .filter(person => person.is_active !== false);
        
        console.log(`Loaded ${gameState.people.length} active people`);
        
    } catch (error) {
        console.error('Error loading memory people:', error);
        throw new Error('Failed to load your memories. ' + error.message);
    }
}

// ============================================================
// TIMER
// ============================================================

function startTimer() {
    timerInterval = setInterval(() => {
        updateTimer();
    }, 100);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function updateTimer() {
    const elapsed = Math.floor((Date.now() - gameState.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('time-count').textContent = 
        `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// ============================================================
// GAME LOGIC
// ============================================================

function generateQuestions() {
    /**
     * Generate TOTAL_QUESTIONS questions with random people
     * Each question: correct person's name shown, must select photo
     */
    gameState.questions = [];
    
    for (let i = 0; i < GAME_CONFIG.TOTAL_QUESTIONS; i++) {
        // Pick random person as correct answer
        const correctPerson = gameState.people[Math.floor(Math.random() * gameState.people.length)];
        
        // Determine number of choices based on difficulty
        const numChoices = Math.min(
            GAME_CONFIG.DIFFICULTY_CHOICES[gameState.difficulty] || 3,
            gameState.people.length
        );
        
        // Get other people as wrong answers
        let otherPeople = gameState.people.filter(p => p.id !== correctPerson.id);
        
        // If we need more wrong answers and have repetition, allow it
        while (otherPeople.length < numChoices - 1 && gameState.people.length < numChoices) {
            otherPeople = otherPeople.concat(gameState.people.filter(p => p.id !== correctPerson.id));
        }
        
        // Shuffle and take only what we need
        otherPeople = shuffle(otherPeople).slice(0, numChoices - 1);
        
        // Create answer options with correct person
        let options = [correctPerson, ...otherPeople];
        options = shuffle(options);  // Randomize order
        
        gameState.questions.push({
            correctPerson: correctPerson,
            options: options,
            answered: false,
            correct: false
        });
    }
}

function displayQuestion() {
    if (gameState.currentQuestionIndex >= GAME_CONFIG.TOTAL_QUESTIONS) {
        endGame();
        return;
    }
    
    const question = gameState.questions[gameState.currentQuestionIndex];
    
    // Update progress
    document.getElementById('question-count').textContent = 
        `${gameState.currentQuestionIndex + 1}/${GAME_CONFIG.TOTAL_QUESTIONS}`;
    document.getElementById('correct-count').textContent = gameState.correctAnswers;
    
    // Display question text (name and relationship)
    const questionText = document.getElementById('question-text');
    questionText.textContent = question.correctPerson.name;
    
    const relationshipText = document.getElementById('question-relationship');
    relationshipText.textContent = question.correctPerson.relationship ? 
        `(${question.correctPerson.relationship})` : '';
    
    // Create photo option buttons
    const optionsDiv = document.getElementById('game-options');
    optionsDiv.innerHTML = '';
    
    question.options.forEach((person) => {
        const btn = document.createElement('button');
        btn.className = 'game-photo-option-btn';
        
        // Create image or placeholder
        if (person.photo) {
            const img = document.createElement('img');
            img.src = person.photo;
            img.alt = person.name;
            btn.appendChild(img);
        } else {
            const placeholder = document.createElement('div');
            placeholder.className = 'photo-placeholder';
            placeholder.textContent = '📷';
            btn.appendChild(placeholder);
        }
        
        btn.onclick = () => selectAnswer(person.id);
        optionsDiv.appendChild(btn);
    });
}

function selectAnswer(personId) {
    if (!gameState.gameActive) return;
    
    const question = gameState.questions[gameState.currentQuestionIndex];
    const isCorrect = personId === question.correctPerson.id;
    
    question.answered = true;
    question.correct = isCorrect;
    
    if (isCorrect) {
        gameState.correctAnswers++;
    }
    
    gameState.answers.push(isCorrect);
    
    // Disable buttons
    document.querySelectorAll('.game-photo-option-btn').forEach(btn => {
        btn.disabled = true;
    });
    
    // Move to next question after brief delay
    setTimeout(() => {
        gameState.currentQuestionIndex++;
        displayQuestion();
    }, 500);
}

async function endGame() {
    gameState.gameActive = false;
    stopTimer();
    
    // Calculate results
    const elapsedSeconds = (Date.now() - gameState.startTime) / 1000;
    const score = gameState.correctAnswers * GAME_CONFIG.POINTS_PER_CORRECT;
    const accuracy = (gameState.correctAnswers / GAME_CONFIG.TOTAL_QUESTIONS) * 100;
    
    // Log game result
    try {
        const result = await logGameResult({
            game_type: 'who_is_this',
            score: Math.floor(score),
            accuracy: parseFloat(accuracy.toFixed(1)),
            time_taken: parseFloat(elapsedSeconds.toFixed(1)),
            difficulty: gameState.difficulty
        });
        
        if (!result) {
            console.warn('Failed to log game result, but showing completion screen');
        }
    } catch (error) {
        console.error('Error logging game:', error);
    }
    
    showCompletion(score, accuracy, elapsedSeconds);
}

function showCompletion(score, accuracy, timeTaken) {
    const minutes = Math.floor(timeTaken / 60);
    const seconds = Math.floor(timeTaken % 60);
    
    document.getElementById('final-score').textContent = Math.floor(score);
    document.getElementById('final-accuracy').textContent = accuracy.toFixed(1) + '%';
    document.getElementById('final-correct').textContent = `${gameState.correctAnswers}/5`;
    document.getElementById('final-time').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
    document.getElementById('game-state').style.display = 'none';
    document.getElementById('completion-screen').style.display = 'flex';
}

// ============================================================
// ERROR HANDLING
// ============================================================

function showError(title, message) {
    document.getElementById('error-title').textContent = title;
    document.getElementById('error-message').textContent = message;
    document.getElementById('error-state').style.display = 'flex';
    document.getElementById('game-state').style.display = 'none';
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function shuffle(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

async function logGameResult(data) {
    try {
        const response = await fetch('/api/games/log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(data)
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            return false;
        }
        
        if (!response.ok) {
            const error = await response.json();
            console.error('Failed to log game result:', error);
            return false;
        }
        
        console.log('Game logged successfully');
        return true;
    } catch (error) {
        console.error('Error logging game:', error);
        return false;
    }
}
