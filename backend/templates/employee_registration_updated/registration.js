/**
 * Employee Registration Integration
 * Connects registration form with backend API
 */

(function() {
    'use strict';

    // Initialize registration page
    function initRegistration() {
        console.log('Initializing Employee Registration...');
        
        // Setup navigation
        router.setupNavigation();
        
        // Get form elements
        const saveButton = document.querySelector('button.bg-primary');
        const resetButton = document.querySelector('button.bg-surface-container-highest');
        const inputs = document.querySelectorAll('input, select');

        // Add event listeners
        if (saveButton) {
            saveButton.addEventListener('click', handleSaveEmployee);
        }

        if (resetButton) {
            resetButton.addEventListener('click', handleReset);
        }
    }

    // Handle save employee
    async function handleSaveEmployee(e) {
        e.preventDefault();

        // Get form values
        const inputs = document.querySelectorAll('input, select');
        const employeeId = inputs[0].value.trim();
        const employeeName = inputs[1].value.trim();
        const department = inputs[2].value;
        const role = inputs[3].value.trim();
        const shift = inputs[4].value; // Branch field
        const phoneNumber = inputs[5].value.trim();

        // Validate required fields
        if (!employeeId || !employeeName || !department) {
            Utils.showNotification('Please fill in all required fields (Employee ID, Name, Department)', 'error');
            return;
        }

        // Prepare employee data
        const employeeData = {
            EmployeeID: employeeId,
            EmployeeName: employeeName,
            Department: department,
            shift: shift || 'Day', // Default shift
            
        };

        try {
            // Show loading state
            const saveButton = document.querySelector('button.bg-primary');
            const originalText = saveButton.textContent;
            saveButton.textContent = 'Saving...';
            saveButton.disabled = true;

            // Call API
            const response = await apiClient.createEmployee(employeeData);

            // Show success message
            Utils.showNotification(`Employee ${employeeName} registered successfully!`, 'success');

            // Reset form
            handleReset();

            // Restore button
            saveButton.textContent = originalText;
            saveButton.disabled = false;

        } catch (error) {
            console.error('Error saving employee:', error);
            Utils.showNotification(`Error: ${error.message}`, 'error');

            // Restore button
            const saveButton = document.querySelector('button.bg-primary');
            saveButton.textContent = 'Save Employee';
            saveButton.disabled = false;
        }
    }

    // Handle reset form
    function handleReset(e) {
        if (e) e.preventDefault();

        const inputs = document.querySelectorAll('input');
        inputs.forEach(input => {
            input.value = '';
        });

        // Reset selects to first option
        const selects = document.querySelectorAll('select');
        selects.forEach(select => {
            select.selectedIndex = 0;
        });
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initRegistration);
    } else {
        initRegistration();
    }
})();
