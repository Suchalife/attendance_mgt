/**
 * Biometric Enrollment Integration
 * Connects enrollment UI with backend APIs
 */

(function() {
    'use strict';

    let employees = [];

    // Initialize enrollment page
    async function initEnrollment() {
        console.log('Initializing Biometric Enrollment...');
        
        // Setup navigation
        router.setupNavigation();
        
        // Load employees for dropdown
        await loadEmployees();

        // Update camera feed
        updateCameraFeed();

        // Setup button listeners (if they exist)
        setupButtonListeners();
    }

    // Load employees from API
    async function loadEmployees() {
        try {
            const response = await apiClient.getEmployees();
            employees = response.employees || [];

            // Populate employee dropdown if it exists
            const dropdown = document.querySelector('select');
            if (dropdown && employees.length > 0) {
                dropdown.innerHTML = '<option value="">Select Employee</option>';
                employees.forEach(emp => {
                    const option = document.createElement('option');
                    option.value = emp.employeeId;
                    option.textContent = `${emp.employeeName} (${emp.employeeId})`;
                    dropdown.appendChild(option);
                });
            }

        } catch (error) {
            console.error('Error loading employees:', error);
            Utils.showNotification('Error loading employees', 'error');
        }
    }

    // Update camera feed to show backend stream
    function updateCameraFeed() {
        // Find video/image element for camera feed
        const cameraElements = document.querySelectorAll('img[alt*="camera"], img[alt*="Camera"], video');
        
        cameraElements.forEach(element => {
            if (element.tagName === 'IMG') {
                element.src = apiClient.getCameraStreamURL();
                element.onerror = () => {
                    console.error('Camera stream not available');
                };
            }
        });
    }

    // Setup button listeners
    function setupButtonListeners() {
        // Find buttons by text content
        const buttons = document.querySelectorAll('button');
        
        buttons.forEach(button => {
            const text = button.textContent.toLowerCase();
            
            if (text.includes('capture')) {
                button.addEventListener('click', handleCaptureImages);
            } else if (text.includes('train')) {
                button.addEventListener('click', handleTrainModel);
            }
        });
    }

    // Handle capture images
    async function handleCaptureImages(e) {
        e.preventDefault();

        // Get selected employee
        const dropdown = document.querySelector('select');
        if (!dropdown || !dropdown.value) {
            Utils.showNotification('Please select an employee first', 'error');
            return;
        }

        const employeeId = dropdown.value;
        const button = e.target;

        try {
            // Show loading state
            const originalText = button.textContent;
            button.textContent = 'Capturing...';
            button.disabled = true;

            // Start camera if not already started
            await apiClient.startCamera();

            // Capture images (10 images)
            const response = await apiClient.captureImages(employeeId, 10);

            // Show success message
            Utils.showNotification(response.message, 'success');

            // Restore button
            button.textContent = originalText;
            button.disabled = false;

        } catch (error) {
            console.error('Error capturing images:', error);
            Utils.showNotification(`Error: ${error.message}`, 'error');

            // Restore button
            const button = e.target;
            button.textContent = 'Capture Images';
            button.disabled = false;
        }
    }

    // Handle train model
    async function handleTrainModel(e) {
        e.preventDefault();

        // Get selected employee (optional - can train for all)
        const dropdown = document.querySelector('select');
        const employeeId = dropdown && dropdown.value ? dropdown.value : null;

        const button = e.target;

        try {
            // Show loading state
            const originalText = button.textContent;
            button.textContent = 'Training...';
            button.disabled = true;

            Utils.showNotification('Training started...', 'success');

            // Train model
            const response = await apiClient.trainModel(employeeId);

            // Show success message
            Utils.showNotification(response.message, 'success');

            // Restore button
            button.textContent = originalText;
            button.disabled = false;

        } catch (error) {
            console.error('Error training model:', error);
            Utils.showNotification(`Error: ${error.message}`, 'error');

            // Restore button
            const button = e.target;
            button.textContent = 'Train Model';
            button.disabled = false;
        }
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initEnrollment);
    } else {
        initEnrollment();
    }
})();
