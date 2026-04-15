/**
 * Attendance Reports Integration
 * Connects reports UI with backend APIs
 */

(function() {
    'use strict';

    let allRecords = [];

    // Initialize reports page
    async function initReports() {
        console.log('Initializing Attendance Reports...');
        
        // Setup navigation
        router.setupNavigation();
        
        // Load attendance data
        await loadAttendanceData();

        // Setup filter listeners
        setupFilters();
    }

    // Load attendance data from API
    async function loadAttendanceData() {
        try {
            const response = await apiClient.getAttendance();
            allRecords = response.records || [];

            // Display records in table
            displayRecords(allRecords);

        } catch (error) {
            console.error('Error loading attendance data:', error);
            Utils.showNotification('Error loading attendance data', 'error');
        }
    }

    // Display records in table
    function displayRecords(records) {
        // Find table body
        const tbody = document.querySelector('tbody');
        if (!tbody) {
            console.error('Table body not found');
            return;
        }

        // Clear existing rows
        tbody.innerHTML = '';

        if (records.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="5" class="px-6 py-8 text-center text-sm text-on-surface-variant">
                        No attendance records found
                    </td>
                </tr>
            `;
            return;
        }

        // Add rows
        records.forEach(record => {
            const row = createTableRow(record);
            tbody.appendChild(row);
        });
    }

    // Create table row
    function createTableRow(record) {
        const tr = document.createElement('tr');
        tr.className = 'hover:bg-surface-container-low transition-colors';

        const date = Utils.formatDate(record.timestamp);
        const time = Utils.formatTime(record.timestamp);
        const statusClass = record.status === 'Present' ? 'bg-tertiary-container/10 text-tertiary' : 'bg-error-container/20 text-error';

        tr.innerHTML = `
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-on-surface">${record.employeeId}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm font-medium text-on-surface">${record.employeeName}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-on-surface-variant">${record.department}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <div class="text-sm text-on-surface-variant">${date}</div>
                <div class="text-xs text-slate-400">${time}</div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 py-1 ${statusClass} text-xs font-bold rounded uppercase tracking-wide">
                    ${record.status}
                </span>
            </td>
        `;

        return tr;
    }

    // Setup filter listeners
    function setupFilters() {
        // Find filter dropdowns
        const departmentFilter = document.querySelector('select[name="department"]');
        const dateFilter = document.querySelector('input[type="date"]');

        if (departmentFilter) {
            departmentFilter.addEventListener('change', applyFilters);
        }

        if (dateFilter) {
            dateFilter.addEventListener('change', applyFilters);
        }

        // Find export button
        const exportButton = document.querySelector('button[data-action="export"]');
        if (exportButton) {
            exportButton.addEventListener('click', handleExport);
        }
    }

    // Apply filters
    function applyFilters() {
        const departmentFilter = document.querySelector('select[name="department"]');
        const dateFilter = document.querySelector('input[type="date"]');

        let filteredRecords = [...allRecords];

        // Filter by department
        if (departmentFilter && departmentFilter.value) {
            filteredRecords = filteredRecords.filter(r => 
                r.department === departmentFilter.value
            );
        }

        // Filter by date
        if (dateFilter && dateFilter.value) {
            filteredRecords = filteredRecords.filter(r => 
                r.timestamp.startsWith(dateFilter.value)
            );
        }

        // Display filtered records
        displayRecords(filteredRecords);
    }

    // Handle export to CSV
    function handleExport(e) {
        e.preventDefault();

        if (allRecords.length === 0) {
            Utils.showNotification('No data to export', 'error');
            return;
        }

        // Create CSV content
        const headers = ['Employee ID', 'Employee Name', 'Department', 'Timestamp', 'Status'];
        const rows = allRecords.map(r => [
            r.employeeId,
            r.employeeName,
            r.department,
            r.timestamp,
            r.status
        ]);

        const csvContent = [
            headers.join(','),
            ...rows.map(row => row.join(','))
        ].join('\n');

        // Create download link
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `attendance_report_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);

        Utils.showNotification('Report exported successfully', 'success');
    }

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initReports);
    } else {
        initReports();
    }
})();
