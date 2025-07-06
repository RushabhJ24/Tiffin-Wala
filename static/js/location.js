/**
 * Location handling JavaScript for Tiffin Service Platform
 * Handles geolocation, address validation, and service area checking
 */

// Configuration
const LOCATION_CONFIG = {
    // Service radius in kilometers
    SERVICE_RADIUS: 5,
    // Central coordinates (will be loaded from server)
    CENTRAL_LAT: 28.6139,
    CENTRAL_LNG: 77.2090,
    // Geolocation options
    GEO_OPTIONS: {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
    }
};

// Location service class
class LocationService {
    constructor() {
        this.currentPosition = null;
        this.isServiceable = false;
        this.callbacks = {
            onLocationUpdate: [],
            onServiceabilityCheck: [],
            onError: []
        };
        
        this.initializeEventListeners();
    }

    /**
     * Initialize event listeners
     */
    initializeEventListeners() {
        // Listen for location buttons
        document.addEventListener('click', (e) => {
            if (e.target.matches('#getCurrentLocation, .get-location-btn')) {
                e.preventDefault();
                this.getCurrentLocation(e.target);
            }
            
            if (e.target.matches('#verifyLocation, .verify-location-btn')) {
                e.preventDefault();
                this.verifyCurrentLocation(e.target);
            }
        });

        // Listen for address input changes
        document.addEventListener('input', (e) => {
            if (e.target.matches('#address, .address-input')) {
                this.handleAddressChange(e.target);
            }
        });
    }

    /**
     * Get current location using Geolocation API
     */
    getCurrentLocation(button) {
        if (!navigator.geolocation) {
            this.handleError('Geolocation is not supported by this browser', button);
            return;
        }

        // Update button state
        this.setButtonLoading(button, 'Getting Location...');
        
        // Clear previous status
        this.updateLocationStatus('Getting your location...', 'info');

        navigator.geolocation.getCurrentPosition(
            (position) => this.handleLocationSuccess(position, button),
            (error) => this.handleLocationError(error, button),
            LOCATION_CONFIG.GEO_OPTIONS
        );
    }

    /**
     * Handle successful location retrieval
     */
    handleLocationSuccess(position, button) {
        const lat = position.coords.latitude;
        const lng = position.coords.longitude;
        
        this.currentPosition = { lat, lng };
        
        // Update hidden form fields
        this.updateLocationInputs(lat, lng);
        
        // Check if location is serviceable
        this.checkServiceability(lat, lng)
            .then((isServiceable) => {
                this.isServiceable = isServiceable;
                
                if (isServiceable) {
                    this.updateLocationStatus(
                        'Location verified! We deliver to your area.',
                        'success'
                    );
                } else {
                    this.updateLocationStatus(
                        'Sorry, we don\'t deliver to your current location.',
                        'error'
                    );
                }
                
                // Trigger callbacks
                this.triggerCallbacks('onServiceabilityCheck', { lat, lng, isServiceable });
            })
            .catch((error) => {
                this.updateLocationStatus(
                    'Could not verify location. Please try again.',
                    'warning'
                );
                console.error('Serviceability check failed:', error);
            });

        // Reset button
        this.resetButton(button, 'Use Current Location');
        
        // Trigger callbacks
        this.triggerCallbacks('onLocationUpdate', { lat, lng });
    }

    /**
     * Handle location retrieval error
     */
    handleLocationError(error, button) {
        let errorMessage = 'Unable to get your location.';
        
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = 'Location access denied. Please enable location permissions.';
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = 'Location information is unavailable.';
                break;
            case error.TIMEOUT:
                errorMessage = 'Location request timed out. Please try again.';
                break;
            default:
                errorMessage = 'An unknown error occurred while retrieving location.';
                break;
        }
        
        this.updateLocationStatus(errorMessage, 'error');
        this.resetButton(button, 'Use Current Location');
        
        // Trigger error callbacks
        this.triggerCallbacks('onError', { error, message: errorMessage });
    }

    /**
     * Verify current location serviceability
     */
    verifyCurrentLocation(button) {
        if (!this.currentPosition) {
            this.getCurrentLocation(button);
            return;
        }

        this.setButtonLoading(button, 'Verifying...');
        
        this.checkServiceability(this.currentPosition.lat, this.currentPosition.lng)
            .then((isServiceable) => {
                this.isServiceable = isServiceable;
                
                if (isServiceable) {
                    this.updateLocationStatus(
                        'Location verified! We deliver to your area.',
                        'success'
                    );
                } else {
                    this.updateLocationStatus(
                        'Sorry, we don\'t deliver to your current location.',
                        'error'
                    );
                }
                
                this.resetButton(button, 'Verify Location');
            })
            .catch((error) => {
                this.updateLocationStatus(
                    'Could not verify location. Please try again.',
                    'warning'
                );
                this.resetButton(button, 'Verify Location');
                console.error('Verification failed:', error);
            });
    }

    /**
     * Check if coordinates are within service area
     */
    async checkServiceability(lat, lng) {
        try {
            const response = await fetch('/api/check-location', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    latitude: lat,
                    longitude: lng
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data.serviceable;
        } catch (error) {
            console.error('API check failed, falling back to client-side calculation:', error);
            return this.calculateDistanceServiceability(lat, lng);
        }
    }

    /**
     * Calculate distance-based serviceability (fallback)
     */
    calculateDistanceServiceability(lat, lng) {
        const distance = this.calculateDistance(
            LOCATION_CONFIG.CENTRAL_LAT,
            LOCATION_CONFIG.CENTRAL_LNG,
            lat,
            lng
        );
        
        return distance <= LOCATION_CONFIG.SERVICE_RADIUS;
    }

    /**
     * Calculate distance between two points using Haversine formula
     */
    calculateDistance(lat1, lng1, lat2, lng2) {
        const R = 6371; // Earth's radius in kilometers
        const dLat = this.toRadians(lat2 - lat1);
        const dLng = this.toRadians(lng2 - lng1);
        
        const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                  Math.cos(this.toRadians(lat1)) * Math.cos(this.toRadians(lat2)) *
                  Math.sin(dLng / 2) * Math.sin(dLng / 2);
        
        const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
        
        return R * c;
    }

    /**
     * Convert degrees to radians
     */
    toRadians(degrees) {
        return degrees * (Math.PI / 180);
    }

    /**
     * Update location input fields
     */
    updateLocationInputs(lat, lng) {
        const latInput = document.querySelector('#latitude, input[name="latitude"]');
        const lngInput = document.querySelector('#longitude, input[name="longitude"]');
        const deliveryLatInput = document.querySelector('#delivery_lat, input[name="delivery_lat"]');
        const deliveryLngInput = document.querySelector('#delivery_lng, input[name="delivery_lng"]');
        
        if (latInput) latInput.value = lat;
        if (lngInput) lngInput.value = lng;
        if (deliveryLatInput) deliveryLatInput.value = lat;
        if (deliveryLngInput) deliveryLngInput.value = lng;
    }

    /**
     * Update location status display
     */
    updateLocationStatus(message, type) {
        const statusElements = document.querySelectorAll('#locationStatus, .location-status');
        
        statusElements.forEach(element => {
            let iconClass = 'fas fa-info-circle';
            let textClass = 'text-info';
            
            switch(type) {
                case 'success':
                    iconClass = 'fas fa-check-circle';
                    textClass = 'text-success';
                    break;
                case 'error':
                    iconClass = 'fas fa-times-circle';
                    textClass = 'text-danger';
                    break;
                case 'warning':
                    iconClass = 'fas fa-exclamation-triangle';
                    textClass = 'text-warning';
                    break;
            }
            
            element.innerHTML = `
                <span class="${textClass}">
                    <i class="${iconClass} me-2"></i>${message}
                </span>
            `;
            
            // Add CSS class for styling
            element.className = `location-status ${type}`;
        });
    }

    /**
     * Set button to loading state
     */
    setButtonLoading(button, text) {
        if (!button) return;
        
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${text}`;
        button.disabled = true;
    }

    /**
     * Reset button to original state
     */
    resetButton(button, defaultText) {
        if (!button) return;
        
        const originalText = button.dataset.originalText || defaultText;
        button.innerHTML = originalText.includes('fa-') ? originalText : `<i class="fas fa-crosshairs me-2"></i>${originalText}`;
        button.disabled = false;
    }

    /**
     * Handle address input changes
     */
    handleAddressChange(input) {
        // Debounced address validation could go here
        // For now, we'll just clear location status when address changes
        if (input.value.trim()) {
            this.updateLocationStatus('Please verify your location for delivery.', 'info');
        }
    }

    /**
     * Handle generic errors
     */
    handleError(message, button) {
        this.updateLocationStatus(message, 'error');
        if (button) {
            this.resetButton(button, 'Try Again');
        }
        
        this.triggerCallbacks('onError', { message });
    }

    /**
     * Add event callback
     */
    on(event, callback) {
        if (this.callbacks[event]) {
            this.callbacks[event].push(callback);
        }
    }

    /**
     * Remove event callback
     */
    off(event, callback) {
        if (this.callbacks[event]) {
            const index = this.callbacks[event].indexOf(callback);
            if (index > -1) {
                this.callbacks[event].splice(index, 1);
            }
        }
    }

    /**
     * Trigger callbacks
     */
    triggerCallbacks(event, data) {
        if (this.callbacks[event]) {
            this.callbacks[event].forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`Error in ${event} callback:`, error);
                }
            });
        }
    }

    /**
     * Get current position
     */
    getCurrentPosition() {
        return this.currentPosition;
    }

    /**
     * Check if current location is serviceable
     */
    isLocationServiceable() {
        return this.isServiceable;
    }

    /**
     * Format coordinates for display
     */
    formatCoordinates(lat, lng) {
        return `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    }

    /**
     * Get distance to service center
     */
    getDistanceToCenter(lat, lng) {
        return this.calculateDistance(
            LOCATION_CONFIG.CENTRAL_LAT,
            LOCATION_CONFIG.CENTRAL_LNG,
            lat || this.currentPosition?.lat,
            lng || this.currentPosition?.lng
        );
    }
}

// Initialize location service when DOM is loaded
let locationService;

document.addEventListener('DOMContentLoaded', function() {
    locationService = new LocationService();
    
    // Make it globally available
    window.LocationService = locationService;
    
    // Auto-verify location on order pages if coordinates are already present
    const latInput = document.querySelector('#latitude, input[name="latitude"]');
    const lngInput = document.querySelector('#longitude, input[name="longitude"]');
    
    if (latInput && lngInput && latInput.value && lngInput.value) {
        const lat = parseFloat(latInput.value);
        const lng = parseFloat(lngInput.value);
        
        locationService.currentPosition = { lat, lng };
        locationService.checkServiceability(lat, lng)
            .then((isServiceable) => {
                locationService.isServiceable = isServiceable;
                
                if (isServiceable) {
                    locationService.updateLocationStatus(
                        'Your registered location is serviceable.',
                        'success'
                    );
                } else {
                    locationService.updateLocationStatus(
                        'Your registered location is outside our service area.',
                        'warning'
                    );
                }
            })
            .catch(() => {
                locationService.updateLocationStatus(
                    'Unable to verify location serviceability.',
                    'warning'
                );
            });
    }
});

// Export for use in other scripts
window.TiffinLocation = {
    service: () => locationService,
    getCurrentPosition: () => locationService?.getCurrentPosition(),
    isServiceable: () => locationService?.isLocationServiceable(),
    calculateDistance: (lat1, lng1, lat2, lng2) => locationService?.calculateDistance(lat1, lng1, lat2, lng2),
    config: LOCATION_CONFIG
};
