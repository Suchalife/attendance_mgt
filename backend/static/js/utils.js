/**
 * Utility Functions
 * Common helper functions for frontend
 */

const Utils = {
    /**
     * Format date to readable string
     */
    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    },

    /**
     * Format time to readable string
     */
    formatTime(dateString) {
        const date = new Date(dateString);
        return date.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
        });
    },

    /**
     * Format timestamp to readable string
     */
    formatTimestamp(dateString) {
        return `${this.formatDate(dateString)} ${this.formatTime(dateString)}`;
    },

    /**
     * Show notification banner
     */
    showNotification(message, type = 'success') {
        // Remove existing notification
        const existing = document.getElementById('notification-banner');
        if (existing) {
            existing.remove();
        }

        // Create notification
        const notification = document.createElement('div');
        notification.id = 'notification-banner';
        notification.className = `fixed top-20 right-8 z-50 px-6 py-4 rounded-lg shadow-lg transition-all duration-300 ${
            type === 'success' ? 'bg-tertiary-container text-white' : 'bg-error-container text-error'
        }`;
        notification.innerHTML = `
            <div class="flex items-center space-x-3">
                <span class="material-symbols-outlined">${type === 'success' ? 'check_circle' : 'error'}</span>
                <span class="font-bold text-sm">${message}</span>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 3 seconds
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    },

    /**
     * Show loading spinner
     */
    showLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = `
                <div class="flex items-center justify-center py-8">
                    <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
                </div>
            `;
        }
    },

    /**
     * Hide loading spinner
     */
    hideLoading(elementId) {
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = '';
        }
    },

    /**
     * Validate form data
     */
    validateForm(formData, requiredFields) {
        const errors = [];
        
        requiredFields.forEach(field => {
            if (!formData[field] || formData[field].trim() === '') {
                errors.push(`${field} is required`);
            }
        });

        return {
            isValid: errors.length === 0,
            errors,
        };
    },

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    /**
     * Poll function - execute callback at interval
     */
    startPolling(callback, interval = 3000) {
        callback(); // Execute immediately
        return setInterval(callback, interval);
    },

    /**
     * Stop polling
     */
    stopPolling(intervalId) {
        if (intervalId) {
            clearInterval(intervalId);
        }
    },
};
