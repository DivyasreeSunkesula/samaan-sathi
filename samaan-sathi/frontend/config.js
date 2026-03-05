// API Configuration
const CONFIG = {
    API_URL: 'https://ozx9x2csyg.execute-api.ap-south-1.amazonaws.com/prod',
    
    FEATURES: {
        ENABLE_AUTO_REFRESH: true,
        REFRESH_INTERVAL: 30000,
        ENABLE_NOTIFICATIONS: true,
        ENABLE_CHARTS: true,
        ENABLE_EXPORT: true
    },
    
    ENDPOINTS: {
        AUTH_REGISTER: '/auth/register',
        AUTH_LOGIN: '/auth/login',
        INVENTORY: '/inventory',
        SALES: '/sales',
        SALES_ANALYTICS: '/sales/analytics',
        UDHAAR: '/udhaar',
        UDHAAR_PAYMENT: '/udhaar/payment',
        FORECAST: '/forecast',
        FORECAST_DEMAND: '/forecast/demand',
        PRICING: '/pricing/recommendations',
        RECOMMENDATIONS: '/recommendations',
        ALERTS: '/alerts',
        OCR_PROCESS: '/ocr/process'
    },
    
    UI: {
        ITEMS_PER_PAGE: 20,
        TOAST_DURATION: 5000,
        ANIMATION_DURATION: 300
    }
};

// Expose API_URL globally for backward compatibility
const API_URL = CONFIG.API_URL;
window.API_URL = API_URL;
