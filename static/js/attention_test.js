/**
 * MEMORA Attention Test
 * Find the odd one out as quickly as possible
 */

// ============================================================
// GAME CONFIG
// ============================================================

const GAME_CONFIG = {
    difficulty: 'medium',  // default fallback
    roundsPerDifficulty: {
        easy: 6,
        medium: 8,
        hard: 10
    },
    shapesPerRound: {
        easy: 8,
        medium: 12,
        hard: 16
    }
};

const SHAPES = ['🔵', '🔵', '🟦', '🔵'];
const COLORS = ['blue', 'blue', 'red', 'blue'];

// ============================================================
// GAME STATE
// ============================================================

let gameState = {
    round: 0,
    totalRounds: GAME_CONFIG.roundsPerDifficulty[GAME_CONFIG.difficulty],
    correct: 0,
    incorrect: 0,
    reactionTimes: [],
    roundStartTime: null,
    gameActive: true,
    shapes: [],
    targetIndex: -1,
    answered: false,
    difficulty: 'medium',
    usedDifficulty: null
};

// ============================================================
// INITIALIZATION
// ============================================================

document.addEventListener('DOMContentLoaded', async () => {
    // Fetch adaptive difficulty before starting game
    await fetchDifficultyAndInit();
});

// ============================================================
// ADAPTIVE DIFFICULTY FUNCTIONS
// ============================================================

async function fetchDifficultyAndInit() {
    try {
        if (!USER_ID || USER_ID === 'null') {
            console.warn('USER_ID not set, using default difficulty');
            startNextRound();
            return;
        }
        
        const response = await fetch(`/api/difficulty/${USER_ID}`, { credentials: 'include' });
        
        if (!response.ok) {
            console.warn('Failed to fetch difficulty, using default');
            startNextRound();
            return;
        }
        
        const data = await response.json();
        const difficulty = data.difficulty || 'medium';
        
        // Update game state with fetched difficulty
        gameState.difficulty = difficulty;
        gameState.usedDifficulty = difficulty;
        gameState.totalRounds = GAME_CONFIG.roundsPerDifficulty[difficulty];
        GAME_CONFIG.difficulty = difficulty;
        
        // Update difficulty badge on page
        const badge = document.getElementById('difficulty-badge');
        if (badge) {
            const emojis = {
                'easy': '🟢 Easy',
                'medium': '🟡 Medium',
                'hard': '🔴 Hard'
            };
            badge.textContent = emojis[difficulty] || '🟡 Medium';
        }
        
        // Start game with adaptive difficulty
        startNextRound();
        
    } catch (error) {
        console.error('Error fetching difficulty:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Could not load your difficulty level. Using default.');
        }
        startNextRound();  // Fall back to default
    }
}

function startNextRound() {
    gameState.round++;
    gameState.answered = false;
    gameState.roundStartTime = null;
    
    if (gameState.round > gameState.totalRounds) {
        completeGame();
        return;
    }
    
    generateRound();
    renderRound();
}

// ============================================================
// ROUND GENERATION
// ============================================================

function generateRound() {
    const shapesCount = GAME_CONFIG.shapesPerRound[GAME_CONFIG.difficulty];
    const roundDifficulty = Math.floor((gameState.round - 1) / 3);  // Increases every 3 rounds
    
    // Generate shapes array with one odd one out
    gameState.shapes = [];
    gameState.targetIndex = Math.floor(Math.random() * shapesCount);
    
    for (let i = 0; i < shapesCount; i++) {
        if (i === gameState.targetIndex) {
            // Odd one out - different shape
            gameState.shapes.push({
                emoji: '🟥',
                color: 'red',
                isTarget: true
            });
        } else {
            // Normal shape
            gameState.shapes.push({
                emoji: '🔵',
                color: 'blue',
                isTarget: false
            });
        }
    }
    
    // Shuffle array
    gameState.shapes.sort(() => Math.random() - 0.5);
}

// ============================================================
// RENDERING
// ============================================================

function renderRound() {
    const grid = document.getElementById('attention-grid');
    
    const shapesCount = gameState.shapes.length;
    const gridSize = Math.ceil(Math.sqrt(shapesCount));
    
    grid.style.gridTemplateColumns = `repeat(${gridSize}, 1fr)`;
    grid.innerHTML = gameState.shapes.map((shape, idx) => `
        <button class="attention-button" 
                onclick="respondToShape(${idx})"
                data-index="${idx}"
                data-target="${shape.isTarget}">
            <span class="shape-emoji">${shape.emoji}</span>
        </button>
    `).join('');
    
    // Update display
    updateStats();
    
    // Start timer for this round
    gameState.roundStartTime = Date.now();
}

function updateStats() {
    document.getElementById('round-count').textContent = `${gameState.round}/${gameState.totalRounds}`;
    document.getElementById('correct-count').textContent = gameState.correct;
    
    if (gameState.reactionTimes.length > 0) {
        const avgTime = Math.floor(
            gameState.reactionTimes.reduce((a, b) => a + b, 0) / gameState.reactionTimes.length
        );
        document.getElementById('avg-reaction').textContent = avgTime + 'ms';
    }
}

// ============================================================
// GAME LOGIC
// ============================================================

function respondToShape(index) {
    if (!gameState.gameActive || gameState.answered) return;
    
    gameState.answered = true;
    
    const reactionTime = Date.now() - gameState.roundStartTime;
    gameState.reactionTimes.push(reactionTime);
    
    const shape = gameState.shapes[index];
    const isCorrect = shape.isTarget;
    
    if (isCorrect) {
        gameState.correct++;
        showFeedback(index, true);
    } else {
        gameState.incorrect++;
        showFeedback(index, false);
        
        // Show where the target was
        const targetButton = document.querySelector('[data-target="true"]');
        if (targetButton) {
            targetButton.classList.add('feedback-target');
            setTimeout(() => targetButton.classList.remove('feedback-target'), 500);
        }
    }
    
    updateStats();
    setTimeout(startNextRound, 800);
}

function showFeedback(index, isCorrect) {
    const button = document.querySelector(`[data-index="${index}"]`);
    if (isCorrect) {
        button.classList.add('feedback-correct');
        setTimeout(() => button.classList.remove('feedback-correct'), 500);
    } else {
        button.classList.add('feedback-incorrect');
        setTimeout(() => button.classList.remove('feedback-incorrect'), 500);
    }
}

// ============================================================
// COMPLETION
// ============================================================

async function completeGame() {
    gameState.gameActive = false;
    
    const totalRounds = gameState.totalRounds;
    const correct = gameState.correct;
    const accuracy = (correct / totalRounds) * 100;
    
    // Calculate average reaction time
    const avgReactionTime = gameState.reactionTimes.reduce((a, b) => a + b, 0) / gameState.reactionTimes.length;
    
    // Calculate score:
    // Base score: 1000
    // Deduct 10 points per incorrect answer
    // Deduct 1 point per 10ms reaction time
    // Bonus: add 50 if accuracy > 90%
    let score = 1000;
    score -= gameState.incorrect * 10;
    score -= Math.floor(avgReactionTime / 10);
    if (accuracy > 90) score += 50;
    score = Math.max(score, 100);  // Minimum score of 100
    
    // Log game result with the difficulty that was actually used
    const result = await logGameResult({
        game_type: 'attention_test',
        score: Math.floor(score),
        accuracy: parseFloat(accuracy.toFixed(1)),
        time_taken: parseFloat((avgReactionTime / 1000).toFixed(2)),
        difficulty: gameState.usedDifficulty || GAME_CONFIG.difficulty
    });
    
    if (result) {
        showCompletion(score, accuracy, avgReactionTime);
    }
}

function showCompletion(score, accuracy, avgReactionTime) {
    document.getElementById('final-score').textContent = Math.floor(score);
    document.getElementById('final-accuracy').textContent = accuracy.toFixed(1) + '%';
    document.getElementById('final-avg-reaction').textContent = Math.floor(avgReactionTime) + 'ms';
    
    document.getElementById('completion-screen').style.display = 'flex';
}

// ============================================================
// API
// ============================================================

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
            if (typeof ErrorHandler !== 'undefined') {
                ErrorHandler.showError('Failed to save game result. You can still continue playing.');
            }
            return false;
        }
        
        const result = await response.json();
        console.log('Game logged:', result);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showSuccess('Game saved successfully!');
        }
        return true;
    } catch (error) {
        console.error('Error logging game:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Failed to save game result. Please check your connection.');
        }
        return false;
    }
}

// ============================================================
// NAVIGATION
// ============================================================

function goToGamesHub() {
    window.location.href = '/games';
}
