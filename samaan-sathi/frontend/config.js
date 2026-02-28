// API Configuration
const CONFIG = {
    API_URL: 'https://d2dzik9z94.execute-api.ap-south-1.amazonaws.com/prod',
    
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
