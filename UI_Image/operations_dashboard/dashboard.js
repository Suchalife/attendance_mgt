/**
 * Operations Dashboard JavaScript
 * Fetches real-time data from backend API and updates the dashboard
 */

// Configuration
// API_BASE_URL is defined in api-client.js
const POLL_INTERVAL = 3000; // 3 seconds

// DOM Elements
let totalEmployeesElement;
let pollIntervalId;

/**
 * Initialize dashboard when DOM is ready
 */
document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard initializing...');
    
    // Get DOM elements
    totalEmployeesElement = document.querySelector('.text-3xl.font-extrabold.text-on-surface.tracking-tighter');
    
    if (!totalEmployeesElement) {
        console.error('Could not find total employees element');
        return;
    }
    
    // Setup router navigation
    if (typeof router !== 'undefined' && router.setupNavigation) {
        router.setupNavigation();
        console.log('Router navigation setup complete');
    }
    
    // Initial data fetch
    fetchDashboardData();
    
    // Start polling for updates
    startPolling();
    
    console.log('Dashboard initialized successfully');
});

/**
 * Fetch dashboard data from API
 */
async function fetchDashboardData() {
    try {
        // Use apiClient if available, otherwise fall back to direct fetch
        let data;
        
        if (typeof apiClient !== 'undefined') {
            data = await apiClient.getEmployeeCount();
        } else {
            const response = await fetch(`${API_BASE_URL}/api/employees/count`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            data = await response.json();
        }
        
        // Update UI
        updateTotalEmployees(data.count);
        
        console.log('Dashboard data updated:', data);
    } catch (error) {
        console.error('Error fetching dashboard data:', error);
        // Don't update UI on error - keep showing last known value
    }
}

/**
 * Update total employees count in UI
 */
function updateTotalEmployees(count) {
    if (totalEmployeesElement) {
        // Format number with comma separator
        const formattedCount = count.toLocaleString();
        totalEmployeesElement.textContent = formattedCount;
    }
}

/**
 * Start polling for real-time updates
 */
function startPolling() {
    // Clear any existing interval
    if (pollIntervalId) {
        clearInterval(pollIntervalId);
    }
    
    // Set up new polling interval
    pollIntervalId = setInterval(() => {
        fetchDashboardData();
    }, POLL_INTERVAL);
    
    console.log(`Polling started (every ${POLL_INTERVAL}ms)`);
}

/**
 * Stop polling (cleanup)
 */
function stopPolling() {
    if (pollIntervalId) {
        clearInterval(pollIntervalId);
        pollIntervalId = null;
        console.log('Polling stopped');
    }
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    stopPolling();
});
