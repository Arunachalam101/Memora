/**
 * MEMORA Error & Loading Handler
 * Centralized error display and loading state management
 */

const ErrorHandler = {
    /**
     * Show a user-friendly error message
     */
    showError(message, duration = 5000) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-banner';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-text">${message}</span>
                <button class="error-close" onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;
        
        document.body.insertBefore(errorDiv, document.body.firstChild);
        
        if (duration > 0) {
            setTimeout(() => {
                if (errorDiv.parentElement) {
                    errorDiv.remove();
                }
            }, duration);
        }
    },
    
    /**
     * Show a success message
     */
    showSuccess(message, duration = 3000) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-banner';
        successDiv.innerHTML = `
            <div class="success-content">
                <span class="success-icon">✓</span>
                <span class="success-text">${message}</span>
                <button class="success-close" onclick="this.parentElement.parentElement.remove()">✕</button>
            </div>
        `;
        
        document.body.insertBefore(successDiv, document.body.firstChild);
        
        if (duration > 0) {
            setTimeout(() => {
                if (successDiv.parentElement) {
                    successDiv.remove();
                }
            }, duration);
        }
    },
    
    /**
     * Show loading indicator
     */
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const loadingDiv = document.createElement('div');
        loadingDiv.className = 'loading-indicator';
        loadingDiv.innerHTML = `
            <div class="spinner"></div>
            <p>Loading...</p>
        `;
        
        element.innerHTML = '';
        element.appendChild(loadingDiv);
    },
    
    /**
     * Hide loading indicator
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (!element) return;
        
        const loader = element.querySelector('.loading-indicator');
        if (loader) {
            loader.remove();
        }
    },
    
    /**
     * Wrap a fetch call with error handling
     */
    async fetchWithErrorHandling(url, options = {}, friendlyErrorMessage = 'Failed to load data') {
        try {
            const response = await fetch(url, options);
            
            // Handle 401 Unauthorized - redirect to login
            if (response.status === 401) {
                window.location.href = '/login';
                return null;
            }
            
            // Handle other error status codes
            if (!response.ok) {
                let errorMessage = friendlyErrorMessage;
                
                // Try to parse JSON error response for more details
                if (response.headers.get('content-type')?.includes('application/json')) {
                    try {
                        const errorData = await response.json();
                        if (errorData.error) {
                            errorMessage = errorData.error;
                        }
                    } catch (e) {
                        // If JSON parsing fails, use default message
                    }
                }
                
                throw new Error(errorMessage);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Fetch error:', error);
            this.showError(error.message || 'Something went wrong. Please try again.');
            return null;
        }
    }
};

// Add CSS styles for error/success banners and loading indicator
document.addEventListener('DOMContentLoaded', () => {
    if (!document.getElementById('error-handler-styles')) {
        const style = document.createElement('style');
        style.id = 'error-handler-styles';
        style.textContent = `
            .error-banner, .success-banner {
                position: fixed;
                top: 20px;
                left: 20px;
                right: 20px;
                max-width: 400px;
                z-index: 10000;
                border-radius: 8px;
                animation: slideIn 0.3s ease-out;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
            }
            
            .error-banner {
                background: #fee;
                border-left: 4px solid #dc3545;
            }
            
            .error-content, .success-content {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 12px 16px;
            }
            
            .error-icon {
                font-size: 20px;
                flex-shrink: 0;
            }
            
            .error-text, .success-text {
                flex: 1;
                color: #333;
                font-size: 14px;
            }
            
            .error-close, .success-close {
                background: none;
                border: none;
                color: #999;
                cursor: pointer;
                font-size: 18px;
                padding: 0;
                flex-shrink: 0;
            }
            
            .error-close:hover, .success-close:hover {
                color: #333;
            }
            
            .success-banner {
                background: #efe;
                border-left: 4px solid #28a745;
            }
            
            .success-icon {
                font-size: 20px;
                color: #28a745;
                flex-shrink: 0;
            }
            
            .success-text {
                color: #155724;
            }
            
            .loading-indicator {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 40px 20px;
                gap: 15px;
            }
            
            .spinner {
                width: 40px;
                height: 40px;
                border: 4px solid #f0f0f0;
                border-top-color: #667eea;
                border-radius: 50%;
                animation: spin 0.8s linear infinite;
            }
            
            .loading-indicator p {
                color: #666;
                font-size: 16px;
                margin: 0;
            }
            
            @keyframes slideIn {
                from {
                    opacity: 0;
                    transform: translateX(-100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes spin {
                to {
                    transform: rotate(360deg);
                }
            }
        `;
        document.head.appendChild(style);
    }
});
