/**
 * API Client for Employee Attendance System
 * Simple fetch wrapper for backend communication
 */

const API_BASE_URL = 'http://localhost:5000';

class APIClient {
    constructor(baseURL = API_BASE_URL) {
        this.baseURL = baseURL;
    }

    /**
     * Generic fetch wrapper
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    }

    // Employee endpoints
    async createEmployee(employeeData) {
        return this.request('/api/employees', {
            method: 'POST',
            body: JSON.stringify(employeeData),
        });
    }

    async getEmployees() {
        return this.request('/api/employees');
    }

    async getEmployeeCount() {
        return this.request('/api/employees/count');
    }

    // Camera endpoints
    getCameraStreamURL() {
        return `${this.baseURL}/api/camera/stream`;
    }

    async startCamera() {
        return this.request('/api/camera/start', { method: 'POST' });
    }

    async stopCamera() {
        return this.request('/api/camera/stop', { method: 'POST' });
    }

    async getCameraStatus() {
        return this.request('/api/camera/status');
    }

    async captureImages(employeeId, numImages = 10) {
        return this.request('/api/camera/capture', {
            method: 'POST',
            body: JSON.stringify({ employeeId, numImages }),
        });
    }

    async trainModel(employeeId = null) {
        const body = employeeId ? JSON.stringify({ employeeId }) : JSON.stringify({});
        return this.request('/api/camera/train', {
            method: 'POST',
            body: body,
        });
    }

    // Attendance endpoints
    async startAttendance() {
        return this.request('/api/attendance/start', { method: 'POST' });
    }

    async getAttendance(filters = {}) {
        const params = new URLSearchParams(filters);
        const query = params.toString() ? `?${params.toString()}` : '';
        return this.request(`/api/attendance${query}`);
    }

    async getAttendanceStats() {
        return this.request('/api/attendance/stats');
    }

    async markAttendance(attendanceData) {
        return this.request('/api/attendance/mark', {
            method: 'POST',
            body: JSON.stringify(attendanceData),
        });
    }
}

// Create global instance
const apiClient = new APIClient();
