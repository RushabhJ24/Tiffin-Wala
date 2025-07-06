/**
 * Main JavaScript file for Tiffin Service Platform
 * Handles general functionality, UI interactions, and utility functions
 */

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

/**
 * Initialize the application
 */
function initializeApp() {
    initializeTooltips();
    initializeAlerts();
    initializeFormValidation();
    initializeAnimations();
    initializeUtilityFunctions();
}

/**
 * Initialize Bootstrap tooltips
 */
function initializeTooltips() {
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

/**
 * Initialize alert dismissal functionality
 */
function initializeAlerts() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert.alert-dismissible');
    alerts.forEach(alert => {
        if (!alert.classList.contains('alert-danger')) {
            setTimeout(() => {
                const closeButton = alert.querySelector('.btn-close');
                if (closeButton) {
                    closeButton.click();
                }
            }, 5000);
        }
    });
}

/**
 * Initialize form validation
 */
function initializeFormValidation() {
    // Add real-time validation for forms
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });

        // Email validation
        const emailInputs = form.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('blur', validateEmail);
        });

        // Phone validation
        const phoneInputs = form.querySelectorAll('input[type="tel"]');
        phoneInputs.forEach(input => {
            input.addEventListener('input', validatePhone);
        });

        // Password confirmation validation
        const passwordInputs = form.querySelectorAll('input[name="password"]');
        const confirmPasswordInputs = form.querySelectorAll('input[name="confirm_password"]');
        
        if (passwordInputs.length && confirmPasswordInputs.length) {
            confirmPasswordInputs.forEach(confirmInput => {
                confirmInput.addEventListener('input', function() {
                    const password = passwordInputs[0].value;
                    const confirmPassword = confirmInput.value;
                    
                    if (password !== confirmPassword) {
                        confirmInput.setCustomValidity('Passwords do not match');
                    } else {
                        confirmInput.setCustomValidity('');
                    }
                });
            });
        }
    });
}

/**
 * Email validation function
 */
function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        event.target.setCustomValidity('Please enter a valid email address');
    } else {
        event.target.setCustomValidity('');
    }
}

/**
 * Phone validation function
 */
function validatePhone(event) {
    const phone = event.target.value;
    // Remove non-numeric characters
    const cleanPhone = phone.replace(/\D/g, '');
    
    if (cleanPhone.length < 10) {
        event.target.setCustomValidity('Phone number must be at least 10 digits');
    } else {
        event.target.setCustomValidity('');
    }
    
    // Format phone number as user types
    if (cleanPhone.length <= 10) {
        event.target.value = cleanPhone;
    }
}

/**
 * Initialize animations
 */
function initializeAnimations() {
    // Add fade-in animation to cards when they come into view
    const cards = document.querySelectorAll('.card');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        observer.observe(card);
    });
}

/**
 * Initialize utility functions
 */
function initializeUtilityFunctions() {
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading state to buttons with forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                const originalText = submitBtn.innerHTML;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitBtn.disabled = true;
                
                // Reset button after 10 seconds (fallback)
                setTimeout(() => {
                    submitBtn.innerHTML = originalText;
                    submitBtn.disabled = false;
                }, 10000);
            }
        });
    });
}

/**
 * Utility function to show loading state
 */
function showLoading(element, text = 'Loading...') {
    if (element) {
        element.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
        element.disabled = true;
    }
}

/**
 * Utility function to hide loading state
 */
function hideLoading(element, originalText) {
    if (element) {
        element.innerHTML = originalText;
        element.disabled = false;
    }
}

/**
 * Format currency for display
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

/**
 * Format date for display
 */
function formatDate(date) {
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

/**
 * Format time for display
 */
function formatTime(date) {
    return new Intl.DateTimeFormat('en-IN', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
    }).format(new Date(date));
}

/**
 * Show success message
 */
function showSuccessMessage(message) {
    showAlert(message, 'success');
}

/**
 * Show error message
 */
function showErrorMessage(message) {
    showAlert(message, 'danger');
}

/**
 * Show warning message
 */
function showWarningMessage(message) {
    showAlert(message, 'warning');
}

/**
 * Show info message
 */
function showInfoMessage(message) {
    showAlert(message, 'info');
}

/**
 * Generic function to show alert
 */
function showAlert(message, type = 'info') {
    const alertContainer = document.querySelector('.container');
    if (!alertContainer) return;

    const alertElement = document.createElement('div');
    alertElement.className = `alert alert-${type} alert-dismissible fade show`;
    alertElement.setAttribute('role', 'alert');
    alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    // Insert at the beginning of the container
    alertContainer.insertBefore(alertElement, alertContainer.firstChild);

    // Auto-dismiss after 5 seconds
    if (type !== 'danger') {
        setTimeout(() => {
            const closeButton = alertElement.querySelector('.btn-close');
            if (closeButton) {
                closeButton.click();
            }
        }, 5000);
    }
}

/**
 * Confirm action with user
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showSuccessMessage('Copied to clipboard!');
    }).catch(() => {
        showErrorMessage('Failed to copy to clipboard');
    });
}

/**
 * Print current page
 */
function printPage() {
    window.print();
}

/**
 * Refresh current page
 */
function refreshPage() {
    window.location.reload();
}

/**
 * Redirect to URL
 */
function redirectTo(url) {
    window.location.href = url;
}

/**
 * Open URL in new tab
 */
function openInNewTab(url) {
    window.open(url, '_blank');
}

/**
 * Check if user is online
 */
function isOnline() {
    return navigator.onLine;
}

/**
 * Handle network status changes
 */
window.addEventListener('online', function() {
    showSuccessMessage('Connection restored');
});

window.addEventListener('offline', function() {
    showWarningMessage('Connection lost. Some features may not work.');
});

/**
 * Debounce function for performance optimization
 */
function debounce(func, wait, immediate) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            timeout = null;
            if (!immediate) func(...args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func(...args);
    };
}

/**
 * Throttle function for performance optimization
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Local storage utilities
 */
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Failed to save to localStorage:', e);
            return false;
        }
    },
    
    get: (key, defaultValue = null) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : defaultValue;
        } catch (e) {
            console.error('Failed to read from localStorage:', e);
            return defaultValue;
        }
    },
    
    remove: (key) => {
        try {
            localStorage.removeItem(key);
            return true;
        } catch (e) {
            console.error('Failed to remove from localStorage:', e);
            return false;
        }
    },
    
    clear: () => {
        try {
            localStorage.clear();
            return true;
        } catch (e) {
            console.error('Failed to clear localStorage:', e);
            return false;
        }
    }
};

// Export functions for use in other scripts
window.TiffinService = {
    showLoading,
    hideLoading,
    formatCurrency,
    formatDate,
    formatTime,
    showSuccessMessage,
    showErrorMessage,
    showWarningMessage,
    showInfoMessage,
    confirmAction,
    copyToClipboard,
    printPage,
    refreshPage,
    redirectTo,
    openInNewTab,
    isOnline,
    debounce,
    throttle,
    storage
};
