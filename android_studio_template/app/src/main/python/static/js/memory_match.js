/**
 * MEMORA Memory Match Game
 * Classic card-flip memory game with scoring
 */

// ============================================================
// GAME CONFIG
// ============================================================

const GAME_CONFIG = {
    difficulty: 'medium',  // default fallback
    pairs: {
        easy: 4,
        medium: 6,
        hard: 8
    }
};

const CARD_EMOJIS = ['🍎', '🍊', '🍇', '🍓', '🍒', '🥝', '🍑', '🍌'];

// ============================================================
// GAME STATE
// ============================================================

let gameState = {
    cards: [],
    flipped: [],
    matched: [],
    moves: 0,
    startTime: null,
    pairsTarget: GAME_CONFIG.pairs[GAME_CONFIG.difficulty],
    gameActive: true,
    difficulty: 'medium',  // will be set by fetchDifficulty()
    usedDifficulty: null   // track which difficulty was actually used
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
            initGame();
            return;
        }
        
        const response = await fetch(`/api/difficulty/${USER_ID}`, { credentials: 'include' });
        
        if (!response.ok) {
            console.warn('Failed to fetch difficulty, using default');
            initGame();
            return;
        }
        
        const data = await response.json();
        const difficulty = data.difficulty || 'medium';
        
        // Update game state with fetched difficulty
        gameState.difficulty = difficulty;
        gameState.usedDifficulty = difficulty;
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
        initGame();
        
    } catch (error) {
        console.error('Error fetching difficulty:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Could not load your difficulty level. Using default.');
        }
        initGame();  // Fall back to default
    }
}

function initGame() {
    gameState = {
        cards: [],
        flipped: [],
        matched: [],
        moves: 0,
        startTime: Date.now(),
        pairsTarget: GAME_CONFIG.pairs[GAME_CONFIG.difficulty],
        gameActive: true,
        difficulty: gameState.difficulty,
        usedDifficulty: gameState.usedDifficulty
    };
    
    // Create card pairs
    const emojis = CARD_EMOJIS.slice(0, gameState.pairsTarget);
    const cardPairs = [...emojis, ...emojis].sort(() => Math.random() - 0.5);
    
    gameState.cards = cardPairs.map((emoji, index) => ({
        id: index,
        emoji: emoji,
        flipped: false,
        matched: false
    }));
    
    renderBoard();
    startTimer();
}

// ============================================================
// RENDERING
// ============================================================

function renderBoard() {
    const board = document.getElementById('game-board');
    board.innerHTML = gameState.cards.map((card, idx) => `
        <div class="memory-card ${card.flipped ? 'flipped' : ''} ${card.matched ? 'matched' : ''}" 
             onclick="flipCard(${idx})">
            <div class="card-inner">
                <div class="card-front">?</div>
                <div class="card-back">${card.emoji}</div>
            </div>
        </div>
    `).join('');
    
    updateStats();
}

function updateStats() {
    document.getElementById('moves-count').textContent = gameState.moves;
    document.getElementById('pairs-count').textContent = `${gameState.matched.length}/${gameState.pairsTarget}`;
    
    const elapsed = Math.floor((Date.now() - gameState.startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    document.getElementById('time-count').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

// ============================================================
// GAME LOGIC
// ============================================================

function flipCard(index) {
    if (!gameState.gameActive) return;
    if (gameState.flipped.length >= 2) return;
    if (gameState.cards[index].flipped || gameState.cards[index].matched) return;
    
    gameState.cards[index].flipped = true;
    gameState.flipped.push(index);
    
    renderBoard();
    
    if (gameState.flipped.length === 2) {
        gameState.moves++;
        checkMatch();
    }
}

function checkMatch() {
    const [idx1, idx2] = gameState.flipped;
    const card1 = gameState.cards[idx1];
    const card2 = gameState.cards[idx2];
    
    if (card1.emoji === card2.emoji) {
        // Match found
        card1.matched = true;
        card2.matched = true;
        gameState.matched.push(idx1, idx2);
        gameState.flipped = [];
        
        // Check if game is complete
        if (gameState.matched.length === gameState.cards.length) {
            setTimeout(completeGame, 500);
        } else {
            renderBoard();
        }
    } else {
        // No match - flip back after delay
        setTimeout(() => {
            card1.flipped = false;
            card2.flipped = false;
            gameState.flipped = [];
            renderBoard();
        }, 1000);
    }
}

// ============================================================
// TIMER
// ============================================================

let timerInterval;

function startTimer() {
    timerInterval = setInterval(() => {
        updateStats();
    }, 100);
}

function stopTimer() {
    clearInterval(timerInterval);
}

// ============================================================
// COMPLETION
// ============================================================

async function completeGame() {
    gameState.gameActive = false;
    stopTimer();
    
    const timeTaken = (Date.now() - gameState.startTime) / 1000;
    const pairs = gameState.matched.length / 2;
    const moves = gameState.moves;
    
    // Calculate accuracy (pairs / moves * 100, capped at 100)
    const accuracy = Math.min((pairs / moves) * 100, 100);
    
    // Calculate score:
    // Base score: 1000
    // Deduct 10 points per move
    // Deduct 1 point per second
    // Bonus: add 50 if accuracy > 90%
    let score = 1000;
    score -= moves * 10;
    score -= Math.floor(timeTaken);
    if (accuracy > 90) score += 50;
    score = Math.max(score, 100);  // Minimum score of 100
    
    // Log game result with the difficulty that was actually used
    const result = await logGameResult({
        game_type: 'memory_match',
        score: Math.floor(score),
        accuracy: parseFloat(accuracy.toFixed(1)),
        time_taken: parseFloat(timeTaken.toFixed(1)),
        difficulty: gameState.usedDifficulty || GAME_CONFIG.difficulty
    });
    
    if (result) {
        showCompletion(score, accuracy, timeTaken);
    }
}

function showCompletion(score, accuracy, timeTaken) {
    const minutes = Math.floor(timeTaken / 60);
    const seconds = Math.floor(timeTaken % 60);
    
    document.getElementById('final-score').textContent = Math.floor(score);
    document.getElementById('final-accuracy').textContent = accuracy.toFixed(1) + '%';
    document.getElementById('final-time').textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
    
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
