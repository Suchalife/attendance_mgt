/**
 * Simple Client-Side Router
 * Handles navigation between modules
 */

class Router {
    constructor() {
        this.routes = {
            'dashboard': '../operations_dashboard/code.html',
            'registration': '../employee_registration_updated/code.html',
            'enrollment': '../biometric_enrollment_expanded/code.html',
            'attendance': '../live_attendance/code.html',
            'reports': '../attendance_reports_simplified/code.html',
        };
    }

    navigate(routeName) {
        const path = this.routes[routeName];
        if (path) {
            window.location.href = path;
        } else {
            console.error(`Route not found: ${routeName}`);
        }
    }

    setupNavigation() {
        // Find all navigation links with nav-item class
        const navLinks = document.querySelectorAll('.nav-item');
        
        console.log(`Router: Found ${navLinks.length} navigation items`);
        
        navLinks.forEach((link) => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                
                // Get text content and determine route
                const text = e.currentTarget.textContent.toLowerCase().trim();
                
                console.log(`Router: Clicked navigation item with text: "${text}"`);
                
                if (text.includes('dashboard')) {
                    this.navigate('dashboard');
                } else if (text.includes('registration')) {
                    this.navigate('registration');
                } else if (text.includes('enrollment')) {
                    this.navigate('enrollment');
                } else if (text.includes('attendance')) {
                    this.navigate('attendance');
                } else if (text.includes('report')) {
                    this.navigate('reports');
                } else {
                    console.warn(`Router: No route matched for text: "${text}"`);
                }
            });
        });
        
        console.log('Router: Navigation setup complete');
    }
}

// Create global instance
const router = new Router();
