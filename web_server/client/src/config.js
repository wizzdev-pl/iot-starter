const Configuration = {
    API_BASE_URL: process.env.NODE_ENV === "development" ? "http://localhost:5000/api" : '/api',
    DEBUG: process.env.NODE_ENV === "development",
    PAGE_SIZE: 8,
    DEFAULT_MIN_TIMESTAMP_RANGE: 4 * 60 * 60 * 1000, //4 hours in milliseconds
    MAX_CHART_POINTS: 50,
    BREAK_POINT_VALUE: 7.5 * 60,  // 7.5 minute in seconds
    TOAST_DISPLAY_TIME_IN_MS: 20 * 1000, //  20 seconds in milliseconds
};

export default Configuration;