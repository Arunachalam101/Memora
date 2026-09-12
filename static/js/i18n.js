/**
 * MEMORA i18n Module - Phase 8
 * Handles language switching between English and Assamese
 * Persists language choice to localStorage and database
 */

// ============================================================
// I18N STATE
// ============================================================

const I18NState = {
    currentLanguage: 'en',
    translations: {},
    isLoading: false
};

// ============================================================
// LANGUAGE LOADING AND SWITCHING
// ============================================================

/**
 * Load a language JSON file and apply translations to the page
 * @param {string} langCode - Language code ('en' or 'as')
 */
async function loadLanguage(langCode) {
    if (I18NState.isLoading) return;
    
    // Validate language code
    if (!['en', 'as'].includes(langCode)) {
        console.warn(`Invalid language code: ${langCode}, defaulting to 'en'`);
        langCode = 'en';
    }
    
    I18NState.isLoading = true;
    
    try {
        // Fetch the translation file
        const response = await fetch(`/static/i18n/${langCode}.json`);
        if (!response.ok) {
            throw new Error(`Failed to load language file: ${response.status}`);
        }
        
        I18NState.translations = await response.json();
        I18NState.currentLanguage = langCode;
        
        // Apply translations to the page
        applyTranslations();
        
        // Update language toggle UI
        updateLanguageToggleUI(langCode);
        
        // Save to localStorage
        localStorage.setItem('userLanguage', langCode);
        
        // Save to database if user is logged in
        if (window.currentUserId) {
            await saveLanguagePreference(langCode);
        }
        
        console.log(`Language switched to: ${langCode}`);
    } catch (error) {
        console.error('Failed to load language:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Failed to switch language. Please try again.');
        }
        // Fall back to English if something goes wrong
        if (langCode !== 'en') {
            await loadLanguage('en');
        }
    } finally {
        I18NState.isLoading = false;
    }
}

/**
 * Apply loaded translations to all elements with data-i18n-key attribute
 */
function applyTranslations() {
    const elements = document.querySelectorAll('[data-i18n-key]');
    
    elements.forEach(element => {
        const key = element.getAttribute('data-i18n-key');
        const translation = I18NState.translations[key];
        
        if (translation) {
            // Replace text content, preserving child elements if present
            if (element.children.length === 0) {
                element.textContent = translation;
            } else {
                // For elements with children, only replace the first text node
                let textNodeFound = false;
                for (let node of element.childNodes) {
                    if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                        node.textContent = translation;
                        textNodeFound = true;
                        break;
                    }
                }
                // If no text node found, prepend the translation
                if (!textNodeFound) {
                    element.insertBefore(document.createTextNode(translation), element.firstChild);
                }
            }
        } else {
            console.warn(`Missing translation for key: ${key}`);
        }
    });
    
    // Also update any placeholders or aria-labels that might need translation
    updateInputPlaceholders();
}

/**
 * Update input placeholders for translated languages
 * Uses data-i18n-placeholder attribute on input elements
 */
function updateInputPlaceholders() {
    const placeholderElements = document.querySelectorAll('[data-i18n-placeholder]');
    
    placeholderElements.forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        const translation = I18NState.translations[key];
        
        if (translation) {
            element.setAttribute('placeholder', translation);
        } else {
            console.warn(`Missing placeholder translation key: ${key}`);
        }
    });
}

/**
 * Update the language toggle UI to show the currently active language
 */
function updateLanguageToggleUI(langCode) {
    const toggleBtns = document.querySelectorAll('[data-language-toggle]');
    toggleBtns.forEach(btn => {
        const btnLang = btn.getAttribute('data-language-toggle');
        if (btnLang === langCode) {
            btn.classList.add('active');
            btn.setAttribute('aria-pressed', 'true');
        } else {
            btn.classList.remove('active');
            btn.setAttribute('aria-pressed', 'false');
        }
    });
}

/**
 * Save language preference to the database
 */
async function saveLanguagePreference(langCode) {
    try {
        const response = await fetch('/api/user/language', {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ language: langCode })
        });
        
        if (!response.ok) {
            console.error('Failed to save language preference:', response.status);
            if (typeof ErrorHandler !== 'undefined') {
                ErrorHandler.showError('Failed to save language preference.');
            }
        } else {
            console.log('Language preference saved successfully');
        }
    } catch (error) {
        console.error('Error saving language preference:', error);
        if (typeof ErrorHandler !== 'undefined') {
            ErrorHandler.showError('Could not save your language preference.');
        }
    }
}

/**
 * Initialize i18n on page load
 * - Check if user has a saved language preference
 * - Load from localStorage first, then check database
 * - Default to 'en' if nothing is saved
 */
function initializeI18N() {
    // Priority: Database preference > localStorage > Default 'en'
    let languageToLoad = 'en';
    
    // Check if user preference was passed from Flask template
    if (window.userPreferredLanguage && ['en', 'as'].includes(window.userPreferredLanguage)) {
        languageToLoad = window.userPreferredLanguage;
    } else if (localStorage.getItem('userLanguage')) {
        // Fall back to localStorage
        languageToLoad = localStorage.getItem('userLanguage');
    }
    
    // Load the language
    loadLanguage(languageToLoad);
}

// ============================================================
// INITIALIZATION ON PAGE LOAD
// ============================================================

// Initialize i18n when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeI18N);
} else {
    initializeI18N();
}

// ============================================================
// PUBLIC API
// ============================================================

window.I18N = {
    loadLanguage,
    getCurrentLanguage: () => I18NState.currentLanguage,
    getTranslation: (key) => I18NState.translations[key] || key
};
