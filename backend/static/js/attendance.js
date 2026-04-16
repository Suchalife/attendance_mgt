/**
 * Live Attendance Integration
 * Connects live attendance UI with backend APIs
 */

(function() {
    'use strict';

    let pollingInterval = null;
    let isAttendanceActive = false;
    let currentSessionId = null;

    // Initialize attendance page
    function initAttendance() {
        console.log('Initializing Live Attendance...');
        
        // Setup navigation
        router.setupNavigation();
        
        // Add event listener to Start Attendance button
        const startButton = document.getElementById("startAttendanceBtn") || 
                           document.querySelector('button:has(span[data-icon="play_circle"])') ||
                           Array.from(document.querySelectorAll('button')).find(btn => 
                               btn.textContent.includes('Start Attendance'));
        
        if (startButton) {
            startButton.addEventListener("click", async () => {
                console.log("Start Attendance clicked");
                try {
                    const response = await fetch("http://127.0.0.1:5000/api/attendance/start", {
                        method: "POST",
                        headers: {
                            'Content-Type': 'application/json'
                        }
                    });
                    const data = await response.json();
                    console.log("Response:", data);
                    
                    if (data.success) {
                        alert("Attendance started successfully");
                    } else {
                        alert("Error: " + (data.error || "Failed to start attendance"));
                    }
                } catch (error) {
                    console.error("Error:", error);
                    alert("Error: " + error.message);
                }
            });
            console.log('Event listener added to Start Attendance button');
        } else {
            console.error('Start Attendance button not found!');
        }

        // Update camera feed source
        updateCameraFeed();
    }

    // Update camera feed to show backend stream
    function updateCameraFeed() {
        const cameraImg = document.querySelector('.aspect-video img');
        if (cameraImg) {
            // Set camera stream URL
            cameraImg.src = apiClient.getCameraStreamURL();
            cameraImg.onerror = () => {
                console.error('Camera stream not available');
                // Keep placeholder image on error
            };
        }
    }

    // Handle start attendance
    async function handleStartAttendance(e) {
        e.preventDefault();
        e.stopPropagation();
        
        console.log('Start Attendance button clicked!');

        const button = e.target.closest('button');
        console.log('Button element:', button);

        if (!isAttendanceActive) {
            // Start attendance
            try {
                console.log('Starting attendance session...');
                button.textContent = 'Starting...';
                button.disabled = true;

                // Start camera
                console.log('Starting camera...');
                await apiClient.startCamera();
                console.log('Camera started successfully');

                // Update button
                const iconSpan = button.querySelector('span[data-icon="play_circle"]');
                if (iconSpan) {
                    iconSpan.setAttribute('data-icon', 'stop_circle');
                    iconSpan.textContent = 'stop_circle';
                }
                button.innerHTML = `
                    <span class="material-symbols-outlined" data-icon="stop_circle">stop_circle</span>
                    Stop Attendance
                `;
                button.classList.remove('bg-primary');
                button.classList.add('bg-error');
                button.disabled = false;

                isAttendanceActive = true;

                // Start polling for face detection every 2 seconds
                console.log('Starting polling for face detection...');
                pollingInterval = Utils.startPolling(detectAndMarkAttendance, 2000);

                Utils.showNotification('Attendance session started', 'success');

            } catch (error) {
                console.error('Error starting attendance:', error);
                Utils.showNotification(`Error: ${error.message}`, 'error');
                button.innerHTML = `
                    <span class="material-symbols-outlined" data-icon="play_circle">play_circle</span>
                    Start Attendance
                `;
                button.disabled = false;
            }

        } else {
            // Stop attendance
            try {
                console.log('Stopping attendance session...');
                button.textContent = 'Stopping...';
                button.disabled = true;

                // Stop polling
                if (pollingInterval) {
                    console.log('Stopping polling...');
                    Utils.stopPolling(pollingInterval);
                    pollingInterval = null;
                }

                // Stop camera
                console.log('Stopping camera...');
                await apiClient.stopCamera();
                console.log('Camera stopped successfully');

                // Update button
                button.innerHTML = `
                    <span class="material-symbols-outlined" data-icon="play_circle">play_circle</span>
                    Start Attendance
                `;
                button.classList.remove('bg-error');
                button.classList.add('bg-primary');
                button.disabled = false;

                isAttendanceActive = false;
                currentSessionId = null;

                Utils.showNotification('Attendance session stopped', 'success');

            } catch (error) {
                console.error('Error stopping attendance:', error);
                Utils.showNotification(`Error: ${error.message}`, 'error');
                button.innerHTML = `
                    <span class="material-symbols-outlined" data-icon="stop_circle">stop_circle</span>
                    Stop Attendance
                `;
                button.disabled = false;
            }
        }
    }

    // Detect face and mark attendance
    async function detectAndMarkAttendance() {
        try {
            console.log('Polling for face detection...');
            
            // Call attendance start endpoint
            const response = await apiClient.startAttendance();
            console.log('Attendance API response:', response);

            // Store session ID
            if (response.session_id) {
                currentSessionId = response.session_id;
            }

            // Update bounding box overlays based on detection result
            const overlayRecognized = document.getElementById('overlay-recognized');
            const overlayUnknown = document.getElementById('overlay-unknown');
            const overlayLabel = document.getElementById('overlay-recognized-label');

            if (response.face_detected && response.employee_recognized && response.employee) {
                console.log('Employee recognized:', response.employee);

                // Show ONLY green box
                if (overlayRecognized) {
                    if (overlayLabel) {
                        overlayLabel.textContent = 'ID: ' + response.employee.employeeId + ' [RECOGNIZED]';
                    }
                    overlayRecognized.style.display = '';
                }
                if (overlayUnknown) overlayUnknown.style.display = 'none';

                // Add to recognized employees list
                addRecognizedEmployee(response.employee, response.attendance);

                // Update stats
                updateStats();

                // Show notification for recognition
                Utils.showNotification(`${response.employee.employeeName} marked present`, 'success');
            } else if (response.face_detected && !response.employee_recognized) {
                console.log('Face detected but employee not recognized');

                // Show ONLY red box
                if (overlayUnknown) overlayUnknown.style.display = '';
                if (overlayRecognized) overlayRecognized.style.display = 'none';
            } else {
                console.log('No face detected in current frame');

                // Hide both boxes when no face detected
                if (overlayRecognized) overlayRecognized.style.display = 'none';
                if (overlayUnknown) overlayUnknown.style.display = 'none';
            }

        } catch (error) {
            console.error('Error detecting attendance:', error);
            // Don't show error notifications for polling failures to avoid spam
            // Utils.showNotification(`Detection error: ${error.message}`, 'error');
        }
    }

    // Add recognized employee to list
    function addRecognizedEmployee(employee, attendance) {
        const container = document.querySelector('.flex-1.overflow-y-auto.p-2.space-y-1');
        if (!container) {
            console.error('Employee list container not found');
            return;
        }

        // Check if employee already in list (avoid duplicates within short time)
        const existingEntry = Array.from(container.children).find(child => {
            const idElement = child.querySelector('.text-\\[10px\\].text-slate-500');
            return idElement && idElement.textContent.includes(employee.employeeId);
        });

        // Get current time for timestamp
        const currentTime = new Date();
        const timeString = Utils.formatTime(currentTime.toISOString());

        if (existingEntry) {
            // Update timestamp of existing entry
            const timeElement = existingEntry.querySelector('.text-\\[10px\\].font-medium.text-slate-400');
            if (timeElement) {
                timeElement.textContent = timeString;
            }
            console.log(`Updated timestamp for existing employee: ${employee.employeeName}`);
            return;
        }

        // Create new entry
        const entry = document.createElement('div');
        entry.className = 'flex items-center gap-4 p-4 rounded-lg hover:bg-surface-container-low transition-colors group';
        
        entry.innerHTML = `
            <div class="relative">
                <div class="w-10 h-10 rounded-lg bg-surface-container-highest flex items-center justify-center">
                    <span class="material-symbols-outlined text-on-surface-variant">person</span>
                </div>
                <div class="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-tertiary border-2 border-white"></div>
            </div>
            <div class="flex-1 min-w-0">
                <div class="flex justify-between items-start">
                    <h4 class="font-bold text-sm truncate">${employee.employeeName}</h4>
                    <span class="text-[10px] font-medium text-slate-400">${timeString}</span>
                </div>
                <p class="text-[10px] text-slate-500 uppercase tracking-wider">ID: ${employee.employeeId} • ${employee.department || 'Unknown'}</p>
            </div>
            <div class="px-2 py-1 bg-tertiary-container/10 text-tertiary text-[9px] font-bold rounded uppercase tracking-tighter">
                Present
            </div>
        `;

        // Add to top of list
        container.insertBefore(entry, container.firstChild);
        console.log(`Added new employee to list: ${employee.employeeName}`);

        // Keep only last 10 entries
        while (container.children.length > 10) {
            container.removeChild(container.lastChild);
        }
    }

    // Update statistics
    async function updateStats() {
        try {
            const statsData = await apiClient.getAttendanceStats();
            const stats = statsData.stats;

            // Update Total Checked-In
            const statElements = document.querySelectorAll('.text-3xl.font-extrabold');
            if (statElements[1]) {
                statElements[1].textContent = stats.present_today || '0';
            }

            // Update Shift Coverage percentage
            if (statElements[0] && stats.total_employees > 0) {
                const percentage = Math.round((stats.present_today / stats.total_employees) * 100);
                statElements[0].textContent = `${percentage}%`;
            }

        } catch (error) {
            console.error('Error updating stats:', error);
        }
    }

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
        if (pollingInterval) {
            Utils.stopPolling(pollingInterval);
        }
        if (isAttendanceActive) {
            apiClient.stopCamera().catch(err => console.error('Error stopping camera:', err));
        }
    });

    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAttendance);
    } else {
        initAttendance();
    }
})();
