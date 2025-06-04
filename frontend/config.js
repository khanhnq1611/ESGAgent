// Configuration for different environments
const CONFIG = {
    // Default to localhost for development
    BACKEND_URL: window.location.hostname.includes('ngrok') 
        ? `${window.location.protocol}//${window.location.hostname.replace('frontend', 'backend')}` 
        : 'http://localhost:5000',
        
    // You can also set this manually for ngrok:
    // BACKEND_URL: 'https://your-backend-ngrok-url.ngrok-free.app'
};

// Export for use in other files
window.APP_CONFIG = CONFIG;
