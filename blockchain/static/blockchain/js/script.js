// blockchain/static/blockchain/js/script.js

/**
 * JavaScript Functions for Blockchain Django Application
 * Handles client-side interactions and animations
 */

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @param {HTMLElement} button - Button element that triggered the copy
 */
function copyToClipboard(text, button) {
    navigator.clipboard.writeText(text).then(function() {
        // Success feedback
        const icon = button.querySelector('i');
        const originalClass = icon.className;
        const originalTitle = button.title;

        // Change icon to checkmark
        icon.className = 'fas fa-check';
        button.title = 'Copied!';

        // Add success class
        button.classList.add('text-success');

        // Show tooltip (if Bootstrap tooltip is initialized)
        if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
            const tooltip = new bootstrap.Tooltip(button, {
                title: 'Copied!',
                trigger: 'manual'
            });
            tooltip.show();

            setTimeout(function() {
                tooltip.hide();
            }, 1500);
        }

        // Revert after 2 seconds
        setTimeout(function() {
            icon.className = originalClass;
            button.title = originalTitle || 'Copy to clipboard';
            button.classList.remove('text-success');
        }, 2000);

    }).catch(function(err) {
        console.error('Failed to copy text: ', err);

        // Error feedback
        const icon = button.querySelector('i');
        const originalClass = icon.className;

        icon.className = 'fas fa-times';
        button.classList.add('text-danger');

        setTimeout(function() {
            icon.className = originalClass;
            button.classList.remove('text-danger');
        }, 2000);
    });
}

/**
 * Toggle password visibility
 * @param {string} inputId - ID of the password input
 * @param {HTMLElement} button - Toggle button element
 */
function togglePassword(inputId, button) {
    const input = document.getElementById(inputId);
    const icon = button.querySelector('i');

    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
        button.title = 'Hide';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
        button.title = 'Show';
    }
}

/**
 * Format number with commas
 * @param {number} number - Number to format
 * @returns {string} Formatted number
 */
function formatNumber(number) {
    return number.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/**
 * Truncate text with ellipsis
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} Truncated text
 */
function truncateText(text, maxLength = 20) {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// ============================================================================
// Auto-hide Alerts
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = new bootstrap.Alert(alert);
                // Fade out animation
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    bsAlert.close();
                }, 500);
            }
        });
    }, 5000);
});

// ============================================================================
// Form Validation Enhancement
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Add Bootstrap validation classes
    const forms = document.querySelectorAll('.needs-validation');

    Array.from(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });
});

// ============================================================================
// Wallet Selection Helper
// ============================================================================

/**
 * Update wallet information in transaction form
 */
function updateWalletInfo() {
    const select = document.getElementById('walletSelect');
    if (!select) return;

    const selectedOption = select.options[select.selectedIndex];

    if (selectedOption.value) {
        // Update form fields
        const fromAddress = document.getElementById('id_from_address');
        const privateKey = document.getElementById('id_private_key');
        const balanceAlert = document.getElementById('balanceAlert');
        const balanceSpan = document.getElementById('currentBalance');

        if (fromAddress) fromAddress.value = selectedOption.value;
        if (privateKey) privateKey.value = selectedOption.dataset.private || '';

        // Show balance
        if (balanceAlert && balanceSpan) {
            const balance = selectedOption.dataset.balance || '0';
            balanceSpan.textContent = parseFloat(balance).toFixed(2);
            balanceAlert.style.display = 'block';
        }
    } else {
        // Clear fields
        const fromAddress = document.getElementById('id_from_address');
        const privateKey = document.getElementById('id_private_key');
        const balanceAlert = document.getElementById('balanceAlert');

        if (fromAddress) fromAddress.value = '';
        if (privateKey) privateKey.value = '';
        if (balanceAlert) balanceAlert.style.display = 'none';
    }
}

// ============================================================================
// Mining Progress Animation
// ============================================================================

/**
 * Show mining progress indicator
 */
function showMiningProgress() {
    const form = document.getElementById('miningForm');
    const button = document.getElementById('mineButton');
    const progress = document.getElementById('miningProgress');

    if (form && button && progress) {
        button.disabled = true;
        button.innerHTML = '<span class="loading-spinner me-2"></span>Mining...';
        progress.style.display = 'block';

        // Animate progress bar
        let width = 0;
        const progressBar = progress.querySelector('.progress-bar');

        const interval = setInterval(function() {
            if (width >= 100) {
                clearInterval(interval);
            } else {
                width += 2;
                if (progressBar) {
                    progressBar.style.width = width + '%';
                }
            }
        }, 100);
    }
}

// Attach to mining form if exists
document.addEventListener('DOMContentLoaded', function() {
    const miningForm = document.getElementById('miningForm');
    if (miningForm) {
        miningForm.addEventListener('submit', function(e) {
            showMiningProgress();
        });
    }
});

// ============================================================================
// Smooth Scroll to Top
// ============================================================================

/**
 * Scroll to top button
 */
document.addEventListener('DOMContentLoaded', function() {
    // Create scroll to top button
    const scrollBtn = document.createElement('button');
    scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    scrollBtn.className = 'btn btn-primary position-fixed bottom-0 end-0 m-3 rounded-circle';
    scrollBtn.style.display = 'none';
    scrollBtn.style.width = '50px';
    scrollBtn.style.height = '50px';
    scrollBtn.style.zIndex = '1000';
    scrollBtn.onclick = function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };
    document.body.appendChild(scrollBtn);

    // Show/hide button on scroll
    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollBtn.style.display = 'block';
        } else {
            scrollBtn.style.display = 'none';
        }
    });
});

// ============================================================================
// Confirmation Dialogs
// ============================================================================

/**
 * Confirm action before proceeding
 * @param {string} message - Confirmation message
 * @returns {boolean} User's choice
 */
function confirmAction(message) {
    return confirm(message || 'Are you sure you want to proceed?');
}

// Attach to delete buttons
document.addEventListener('DOMContentLoaded', function() {
    const deleteButtons = document.querySelectorAll('.btn-delete, .delete-action');

    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            const message = this.dataset.confirmMessage || 'Are you sure you want to delete this item?';
            if (!confirmAction(message)) {
                e.preventDefault();
                return false;
            }
        });
    });
});

// ============================================================================
// Real-time Balance Update (AJAX)
// ============================================================================

/**
 * Fetch and update balance for an address
 * @param {string} address - Wallet address
 */
async function updateBalance(address) {
    try {
        const response = await fetch(`/blockchain/api/balance/${address}/`);
        const data = await response.json();

        const balanceElement = document.getElementById('balance-' + address);
        if (balanceElement && data.balance !== undefined) {
            balanceElement.textContent = parseFloat(data.balance).toFixed(2);

            // Animate the change
            balanceElement.classList.add('text-success');
            setTimeout(function() {
                balanceElement.classList.remove('text-success');
            }, 1000);
        }
    } catch (error) {
        console.error('Error fetching balance:', error);
    }
}

// ============================================================================
// Block Hash Highlighting
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    const blockHashes = document.querySelectorAll('.block-hash');

    blockHashes.forEach(function(hash) {
        hash.addEventListener('click', function() {
            // Select text on click
            const range = document.createRange();
            range.selectNodeContents(this);
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        });
    });
});

// ============================================================================
// Tooltips Initialization
// ============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(
            document.querySelectorAll('[data-bs-toggle="tooltip"]')
        );
        tooltipTriggerList.map(function(tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// ============================================================================
// Animate Elements on Scroll
// ============================================================================

/**
 * Intersection Observer for scroll animations
 */
document.addEventListener('DOMContentLoaded', function() {
    const animateElements = document.querySelectorAll('.animate-on-scroll');

    if (animateElements.length > 0) {
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        animateElements.forEach(function(element) {
            observer.observe(element);
        });
    }
});

// ============================================================================
// Format Timestamps
// ============================================================================

/**
 * Format Unix timestamp to readable date
 * @param {number} timestamp - Unix timestamp
 * @returns {string} Formatted date string
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
}

// Apply to all timestamp elements
document.addEventListener('DOMContentLoaded', function() {
    const timestamps = document.querySelectorAll('.timestamp');

    timestamps.forEach(function(element) {
        const unix = element.dataset.timestamp;
        if (unix) {
            element.textContent = formatTimestamp(parseInt(unix));
        }
    });
});

// ============================================================================
// Keyboard Shortcuts
// ============================================================================

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K: Focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('input[type="search"], input[name="address"]');
        if (searchInput) searchInput.focus();
    }

    // Escape: Close modals
    if (e.key === 'Escape') {
        const modals = document.querySelectorAll('.modal.show');
        modals.forEach(function(modal) {
            if (typeof bootstrap !== 'undefined' && bootstrap.Modal) {
                const bsModal = bootstrap.Modal.getInstance(modal);
                if (bsModal) bsModal.hide();
            }
        });
    }
});

// ============================================================================
// Console Welcome Message
// ============================================================================

console.log('%c🔗 Blockchain Django Application',
    'font-size: 20px; font-weight: bold; color: #3498db;');
console.log('%cBuilt with Python, Django & Love ❤️',
    'font-size: 14px; color: #27ae60;');
console.log('%cIslamic University of Gaza - 2024/2025',
    'font-size: 12px; color: #7f8c8d;');

// ============================================================================
// Export functions for global use
// ============================================================================

window.blockchainApp = {
    copyToClipboard: copyToClipboard,
    togglePassword: togglePassword,
    formatNumber: formatNumber,
    truncateText: truncateText,
    updateWalletInfo: updateWalletInfo,
    showMiningProgress: showMiningProgress,
    confirmAction: confirmAction,
    updateBalance: updateBalance,
    formatTimestamp: formatTimestamp
};