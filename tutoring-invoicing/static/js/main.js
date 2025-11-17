// Common JavaScript functions

// Toast notification system
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, 3000);
}

// Format date helper
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-NZ', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Mobile navigation toggle
document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('navToggle');
    const navMenu = document.querySelector('.nav-menu');

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
        });
    }

    // Highlight active nav link
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-link');

    navLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        if (linkPath === currentPath || (currentPath !== '/' && linkPath !== '/' && currentPath.startsWith(linkPath))) {
            link.style.backgroundColor = 'rgba(255, 255, 255, 0.2)';
        }
    });
});

// Close mobile menu when clicking outside
document.addEventListener('click', (event) => {
    const navMenu = document.querySelector('.nav-menu');
    const navToggle = document.getElementById('navToggle');

    if (navMenu && navToggle) {
        if (!navMenu.contains(event.target) && !navToggle.contains(event.target)) {
            navMenu.classList.remove('active');
        }
    }
});

// Confirm before leaving page with unsaved changes
let hasUnsavedChanges = false;

window.addEventListener('beforeunload', (event) => {
    if (hasUnsavedChanges) {
        event.preventDefault();
        event.returnValue = '';
    }
});

// Mark form as having changes
function trackFormChanges(formId) {
    const form = document.getElementById(formId);
    if (form) {
        form.addEventListener('input', () => {
            hasUnsavedChanges = true;
        });

        form.addEventListener('submit', () => {
            hasUnsavedChanges = false;
        });
    }
}

// Currency formatter
function formatCurrency(amount, currency = 'NZD') {
    return `${currency} $${parseFloat(amount).toFixed(2)}`;
}

// Debounce function for search inputs
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Loading state management
function setLoading(elementId, isLoading) {
    const element = document.getElementById(elementId);
    if (!element) return;

    if (isLoading) {
        element.style.opacity = '0.6';
        element.style.pointerEvents = 'none';
    } else {
        element.style.opacity = '1';
        element.style.pointerEvents = 'auto';
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', (event) => {
    // ESC to close modals
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            if (modal.style.display === 'block') {
                modal.style.display = 'none';
            }
        });
    }
});

// Print invoice function
function printInvoice() {
    window.print();
}

// Copy to clipboard helper
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success');
    } catch (err) {
        showToast('Failed to copy to clipboard', 'error');
    }
}

// Export to JSON helper
function exportToJSON(data, filename) {
    const json = JSON.stringify(data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Validate email
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

// Validate phone number
function isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return phone.length >= 7 && re.test(phone);
}

// Format phone number
function formatPhone(phone) {
    // Remove all non-numeric characters
    const cleaned = phone.replace(/\D/g, '');
    // Format as needed (customize based on your region)
    return cleaned;
}

// Calculate days between dates
function daysBetween(date1, date2) {
    const oneDay = 24 * 60 * 60 * 1000;
    const firstDate = new Date(date1);
    const secondDate = new Date(date2);
    return Math.round(Math.abs((firstDate - secondDate) / oneDay));
}

// Get month name
function getMonthName(monthNumber) {
    const months = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    return months[monthNumber - 1] || '';
}

// Sort table helper
function sortTable(tableId, columnIndex, ascending = true) {
    const table = document.getElementById(tableId);
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));

    rows.sort((a, b) => {
        const aValue = a.cells[columnIndex].textContent.trim();
        const bValue = b.cells[columnIndex].textContent.trim();

        if (!isNaN(aValue) && !isNaN(bValue)) {
            return ascending ? aValue - bValue : bValue - aValue;
        }

        return ascending
            ? aValue.localeCompare(bValue)
            : bValue.localeCompare(aValue);
    });

    tbody.innerHTML = '';
    rows.forEach(row => tbody.appendChild(row));
}

// Auto-save form data to localStorage
function enableAutoSave(formId, storageKey) {
    const form = document.getElementById(formId);
    if (!form) return;

    // Load saved data
    const savedData = localStorage.getItem(storageKey);
    if (savedData) {
        const data = JSON.parse(savedData);
        Object.keys(data).forEach(key => {
            const input = form.querySelector(`[name="${key}"]`);
            if (input) {
                input.value = data[key];
            }
        });
    }

    // Save on input
    form.addEventListener('input', debounce(() => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        localStorage.setItem(storageKey, JSON.stringify(data));
    }, 500));

    // Clear on submit
    form.addEventListener('submit', () => {
        localStorage.removeItem(storageKey);
    });
}

// Initialize tooltips
function initTooltips() {
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', (e) => {
            const tooltip = document.createElement('div');
            tooltip.className = 'tooltip';
            tooltip.textContent = e.target.dataset.tooltip;
            document.body.appendChild(tooltip);

            const rect = e.target.getBoundingClientRect();
            tooltip.style.top = `${rect.top - tooltip.offsetHeight - 5}px`;
            tooltip.style.left = `${rect.left + (rect.width - tooltip.offsetWidth) / 2}px`;
        });

        element.addEventListener('mouseleave', () => {
            const tooltip = document.querySelector('.tooltip');
            if (tooltip) {
                tooltip.remove();
            }
        });
    });
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    initTooltips();
});
