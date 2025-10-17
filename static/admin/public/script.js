// Minimal notification implementation (used by many UI functions)
function showNotification(message, type = 'info') {
    // remove old notifications beyond limit
    const existing = document.querySelectorAll('.pc-notification');
    if (existing.length > 3) existing[0].remove();

    const container = document.createElement('div');
    container.className = `pc-notification pc-notification-${type}`;
    container.innerHTML = `
        <div class="pc-notification-content">
            <div class="pc-notification-icon">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : type === 'warning' ? 'exclamation' : 'info-circle'}"></i>
            </div>
            <div class="pc-notification-body">${message}</div>
        </div>
    `;
    document.body.appendChild(container);

    // show then auto-remove
    requestAnimationFrame(() => container.classList.add('show'));
    setTimeout(() => {
        container.classList.remove('show');
        setTimeout(() => container.remove(), 400);
    }, 3000);
}

// Logs related functions
function filterLogs() {
    const level = document.getElementById('logLevel').value;
    showNotification(`Filtering logs by: ${level}`, 'info');
}

function refreshLogs() {
    showNotification('Refreshing logs...', 'info');
    // Simulate log refresh
    setTimeout(() => {
        showNotification('Logs refreshed successfully', 'success');
    }, 1000);
}

function clearLogs() {
    if (confirm('Are you sure you want to clear all logs?')) {
        showNotification('Logs cleared', 'success');
    }
}

function downloadLogs() {
    showNotification('Downloading log file...', 'info');
}

// Model management functions
function pullNewModel() {
    showNotification('Pulling new model...', 'info');
}

// Database functions
function executeQuery() {
    showNotification('Executing query...', 'info');
}

function createBackup() {
    showNotification('Creating database backup...', 'info');
}

function restoreBackup() {
    showNotification('Restoring from backup...', 'info');
}

// Testing functions
function runModelTest() {
    showNotification('Running model test...', 'info');
}

function clearTestResults() {
    document.getElementById('test-results').innerHTML = `
        <div style="text-align: center; color: var(--text-secondary); padding: 60px;">
            <i class="fas fa-flask" style="font-size: 48px;"></i>
            <p>Test results will appear here</p>
        </div>
    `;
}