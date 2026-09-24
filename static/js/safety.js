/**
 * Safety.js - Patient safety and emergency alert system
 * Handles SOS alerts, safety status, and confirmation dialogs
 */

const SafetyUI = {
    state: {
        isSubmitting: false,
        currentStatus: 'safe',
        activeAlert: null
    },
    
    /**
     * Initialize safety page
     */
    initSafetyPage: function() {
        this.loadSafetyStatus();
        this.attachEventListeners();
    },
    
    /**
     * Attach event listeners
     */
    attachEventListeners: function() {
        const sosButton = document.getElementById('sos-button');
        if (sosButton) {
            sosButton.addEventListener('click', () => this.handleSOSClick());
        }
    },
    
    /**
     * Handle SOS button click - show confirmation
     */
    handleSOSClick: function() {
        if (this.state.isSubmitting) {
            return;
        }
        
        // Show confirmation dialog
        const message = getTranslation('safety_are_you_sure') || 'Are you sure you need help?';
        const confirmed = confirm(message);
        
        if (confirmed) {
            this.submitSOS();
        }
    },
    
    /**
     * Submit SOS alert to server
     */
    submitSOS: function() {
        this.state.isSubmitting = true;
        const sosButton = document.getElementById('sos-button');
        if (sosButton) {
            sosButton.disabled = true;
        }
        
        fetch('/api/safety/sos', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success || data.alert) {
                // Show success message
                this.showSuccessMessage();
                // Update status
                this.loadSafetyStatus();
            } else {
                console.error('SOS submission failed:', data.message);
                alert(data.message || 'Failed to create alert. Please try again.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error creating alert. Please try again.');
        })
        .finally(() => {
            this.state.isSubmitting = false;
            const sosButton = document.getElementById('sos-button');
            if (sosButton) {
                sosButton.disabled = false;
            }
        });
    },
    
    /**
     * Load current safety status
     */
    loadSafetyStatus: function() {
        fetch('/api/safety/status', { credentials: 'include' })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.updateStatusUI(data.status, data.active_alert);
                }
            })
            .catch(error => {
                console.error('Error loading safety status:', error);
            });
    },
    
    /**
     * Update UI with safety status
     */
    updateStatusUI: function(status, activeAlert) {
        this.state.currentStatus = status;
        this.state.activeAlert = activeAlert;
        
        const statusCard = document.querySelector('.safety-status-card');
        const statusLabel = document.getElementById('safety-status-label');
        const statusDetail = document.getElementById('safety-status-detail');
        const safetyIcon = document.querySelector('.safety-icon');
        
        if (status === 'alert' && activeAlert) {
            // Alert active
            statusCard.classList.add('alert-active');
            statusLabel.textContent = getTranslation('safety_alert_active') || 'ALERT ACTIVE';
            statusLabel.setAttribute('data-i18n-key', 'safety_alert_active');
            statusDetail.textContent = getTranslation('safety_caregiver_alerted') || 'Your caregiver has been alerted.';
            statusDetail.setAttribute('data-i18n-key', 'safety_caregiver_alerted');
            safetyIcon.textContent = '⚠️';
        } else {
            // Safe
            statusCard.classList.remove('alert-active');
            statusLabel.textContent = getTranslation('safety_status_safe') || 'SAFE';
            statusLabel.setAttribute('data-i18n-key', 'safety_status_safe');
            statusDetail.textContent = getTranslation('safety_no_active_alerts') || 'No active alerts';
            statusDetail.setAttribute('data-i18n-key', 'safety_no_active_alerts');
            safetyIcon.textContent = '🛡️';
        }
    },
    
    /**
     * Show success message
     */
    showSuccessMessage: function() {
        const successMsg = document.getElementById('success-message');
        if (successMsg) {
            successMsg.style.display = 'block';
            // Hide after 5 seconds
            setTimeout(() => {
                successMsg.style.display = 'none';
            }, 5000);
        }
    }
};

/**
 * Caregiver safety dashboard functions
 */
const CaregiversSafetyDashboard = {
    /**
     * Load and display safety alerts for caregiver dashboard
     */
    loadSafetyAlerts: function(callback) {
        fetch('/api/safety/alerts', { credentials: 'include' })
            .then(response => response.json())
            .then(data => {
                if (data.success && callback) {
                    callback(data.alerts || []);
                }
            })
            .catch(error => {
                console.error('Error loading safety alerts:', error);
            });
    },
    
    /**
     * Resolve an alert (caregiver)
     */
    resolveAlert: function(alertId, callback) {
        fetch(`/api/safety/alerts/${alertId}/resolve`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && callback) {
                callback(data.alert);
            }
        })
        .catch(error => {
            console.error('Error resolving alert:', error);
        });
    }
};
