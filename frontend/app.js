// Configuration
const API_BASE_URL = 'http://localhost:5000/api';
const API_KEY = 'default-secure-key';
const ITEMS_PER_PAGE = 15;

// State management
let currentPage = 1;
let allLogs = [];
let filteredLogs = [];
let users = [];

// DOM elements
const elements = {
    logsList: document.getElementById('logsList'),
    search: document.getElementById('search'),
    userFilter: document.getElementById('userFilter'),
    typeFilter: document.getElementById('typeFilter'),
    dateFrom: document.getElementById('dateFrom'),
    dateTo: document.getElementById('dateTo'),
    refreshBtn: document.getElementById('refreshBtn'),
    exportBtn: document.getElementById('exportBtn'),
    addLogBtn: document.getElementById('addLogBtn'),
    clearFiltersBtn: document.getElementById('clearFiltersBtn'),
    clearLogsBtn: document.getElementById('clearLogsBtn'),
    prevPage: document.getElementById('prevPage'),
    nextPage: document.getElementById('nextPage'),
    startItem: document.getElementById('startItem'),
    endItem: document.getElementById('endItem'),
    totalItems: document.getElementById('totalItems'),
    totalLogs: document.getElementById('totalLogs'),
    infoLogs: document.getElementById('infoLogs'),
    warningLogs: document.getElementById('warningLogs'),
    errorLogs: document.getElementById('errorLogs'),
    apiStatus: document.getElementById('apiStatus'),
    toast: document.getElementById('toast'),
    addLogModal: document.getElementById('addLogModal'),
    logForm: document.getElementById('logForm'),
    cancelAddLog: document.getElementById('cancelAddLog'),
    newUser: document.getElementById('newUser'),
    newAction: document.getElementById('newAction'),
    newType: document.getElementById('newType'),
    newDetails: document.getElementById('newDetails')
};

// Initialize the application
document.addEventListener('DOMContentLoaded', async () => {
    await setupEventListeners();
    await checkApiStatus();
    await fetchLogs();
    
    // Set default dates (last 7 days)
    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 7);
    
    elements.dateFrom.valueAsDate = weekAgo;
    elements.dateTo.valueAsDate = today;
});

async function setupEventListeners() {
    // Filter controls
    elements.search.addEventListener('input', applyFilters);
    elements.userFilter.addEventListener('change', applyFilters);
    elements.typeFilter.addEventListener('change', applyFilters);
    elements.dateFrom.addEventListener('change', applyFilters);
    elements.dateTo.addEventListener('change', applyFilters);
    
    // Action buttons
    elements.refreshBtn.addEventListener('click', fetchLogs);
    elements.exportBtn.addEventListener('click', exportLogs);
    elements.addLogBtn.addEventListener('click', showAddLogModal);
    elements.clearFiltersBtn.addEventListener('click', clearFilters);
    elements.clearLogsBtn.addEventListener('click', confirmClearLogs);
    
    // Pagination
    elements.prevPage.addEventListener('click', goToPreviousPage);
    elements.nextPage.addEventListener('click', goToNextPage);
    
    // Modal
    elements.cancelAddLog.addEventListener('click', hideAddLogModal);
    elements.logForm.addEventListener('submit', handleAddLog);
}

async function checkApiStatus() {
    try {
        const response = await fetch(`${API_BASE_URL}/stats`);
        if (response.ok) {
            elements.apiStatus.innerHTML = '<i class="fas fa-circle" style="color: #4ade80;"></i> API Connected';
            return true;
        }
        throw new Error('API returned non-OK status');
    } catch (error) {
        elements.apiStatus.innerHTML = '<i class="fas fa-circle" style="color: #f87171;"></i> API Offline';
        showToast('Failed to connect to API', 'error');
        return false;
    }
}

async function fetchLogs() {
    try {
        showToast('Loading logs...', 'info');
        
        const params = new URLSearchParams();
        if (elements.userFilter.value) params.append('user', elements.userFilter.value);
        if (elements.typeFilter.value) params.append('type', elements.typeFilter.value);
        if (elements.dateFrom.value) params.append('from', elements.dateFrom.value);
        if (elements.dateTo.value) params.append('to', elements.dateTo.value);
        
        const [logsResponse, statsResponse] = await Promise.all([
            fetch(`${API_BASE_URL}/logs?${params.toString()}`),
            fetch(`${API_BASE_URL}/stats`)
        ]);
        
        if (!logsResponse.ok || !statsResponse.ok) {
            throw new Error('Failed to fetch data');
        }
        
        allLogs = await logsResponse.json();
        const stats = await statsResponse.json();
        
        updateStats(stats);
        updateUserFilter(allLogs);
        applyFilters();
        
        showToast('Logs loaded successfully', 'success');
    } catch (error) {
        console.error('Error fetching logs:', error);
        showToast('Failed to load logs: ' + error.message, 'error');
    }
}

function updateStats(stats) {
    elements.totalLogs.textContent = stats.total;
    elements.infoLogs.textContent = stats.info;
    elements.warningLogs.textContent = stats.warning;
    elements.errorLogs.textContent = stats.error;
}

function updateUserFilter(logs) {
    const uniqueUsers = [...new Set(logs.map(log => log.user))];
    users = uniqueUsers;
    
    elements.userFilter.innerHTML = '<option value="">All Users</option>';
    uniqueUsers.forEach(user => {
        const option = document.createElement('option');
        option.value = user;
        option.textContent = user;
        elements.userFilter.appendChild(option);
    });
}

function applyFilters() {
    const searchTerm = elements.search.value.toLowerCase();
    const selectedUser = elements.userFilter.value;
    const selectedType = elements.typeFilter.value;
    const dateFrom = elements.dateFrom.value;
    const dateTo = elements.dateTo.value;
    
    filteredLogs = allLogs.filter(log => {
        // Search filter
        if (searchTerm && 
            !log.user?.toLowerCase().includes(searchTerm) && 
            !log.action?.toLowerCase().includes(searchTerm)) {
            return false;
        }
        
        // User filter
        if (selectedUser && log.user !== selectedUser) {
            return false;
        }
        
        // Type filter
        if (selectedType && log.type !== selectedType) {
            return false;
        }
        
        // Date filter
        const logDate = log.timestamp?.split('T')[0];
        if (dateFrom && logDate < dateFrom) return false;
        if (dateTo && logDate > dateTo) return false;
        
        return true;
    });
    
    currentPage = 1;
    displayLogs();
}

function displayLogs() {
    const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
    const endIndex = startIndex + ITEMS_PER_PAGE;
    const paginatedLogs = filteredLogs.slice(startIndex, endIndex);
    
    elements.logsList.innerHTML = '';
    
    if (paginatedLogs.length === 0) {
        elements.logsList.innerHTML = `
            <div class="log-entry" style="grid-column: 1/-1; text-align: center;">
                No logs found matching your criteria
            </div>`;
    } else {
        paginatedLogs.forEach(log => {
            const logElement = document.createElement('div');
            logElement.className = 'log-entry';
            logElement.innerHTML = `
                <div><span class="log-type type-${log.type}">${log.type}</span></div>
                <div>${log.user || 'System'}</div>
                <div>${log.action || 'No action specified'}</div>
                <div class="log-time">${formatDateTime(log.timestamp)}</div>
                <div>${log.details || '-'}</div>
            `;
            elements.logsList.appendChild(logElement);
        });
    }
    
    updatePaginationInfo();
}

function updatePaginationInfo() {
    const totalItems = filteredLogs.length;
    const startItem = Math.min((currentPage - 1) * ITEMS_PER_PAGE + 1, totalItems);
    const endItem = Math.min(currentPage * ITEMS_PER_PAGE, totalItems);
    
    elements.startItem.textContent = startItem;
    elements.endItem.textContent = endItem;
    elements.totalItems.textContent = totalItems;
    
    elements.prevPage.disabled = currentPage <= 1;
    elements.nextPage.disabled = endItem >= totalItems;
}

function goToPreviousPage() {
    if (currentPage > 1) {
        currentPage--;
        displayLogs();
    }
}

function goToNextPage() {
    const totalPages = Math.ceil(filteredLogs.length / ITEMS_PER_PAGE);
    if (currentPage < totalPages) {
        currentPage++;
        displayLogs();
    }
}

function clearFilters() {
    elements.search.value = '';
    elements.userFilter.value = '';
    elements.typeFilter.value = '';
    
    const today = new Date();
    const weekAgo = new Date();
    weekAgo.setDate(today.getDate() - 7);
    
    elements.dateFrom.valueAsDate = weekAgo;
    elements.dateTo.valueAsDate = today;
    
    applyFilters();
}

async function exportLogs() {
    try {
        const blob = new Blob([JSON.stringify(filteredLogs, null, 2)], { 
            type: 'application/json' 
        });
        const url = URL.createObjectURL(blob);
        
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit_logs_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        showToast('Logs exported successfully', 'success');
    } catch (error) {
        console.error('Export failed:', error);
        showToast('Failed to export logs', 'error');
    }
}

function showAddLogModal() {
    elements.addLogModal.style.display = 'flex';
    elements.newUser.focus();
}

function hideAddLogModal() {
    elements.addLogModal.style.display = 'none';
    elements.logForm.reset();
}

async function handleAddLog(e) {
    e.preventDefault();
    
    const user = elements.newUser.value.trim();
    const action = elements.newAction.value.trim();
    const type = elements.newType.value;
    const details = elements.newDetails.value.trim();
    
    if (!user || !action || !type) {
        showToast('Please fill all required fields', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/log`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-API-KEY': API_KEY
            },
            body: JSON.stringify({
                user,
                action,
                type,
                details: details || undefined
            })
        });
        
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.message || 'Failed to add log');
        }
        
        hideAddLogModal();
        showToast('Log added successfully', 'success');
        await fetchLogs();
    } catch (error) {
        console.error('Error adding log:', error);
        showToast(error.message || 'Failed to add log', 'error');
    }
}

function confirmClearLogs() {
    if (confirm('Are you sure you want to clear ALL logs? This cannot be undone.')) {
        clearAllLogs();
    }
}

async function clearAllLogs() {
    try {
        const response = await fetch(`${API_BASE_URL}/clear`, {
            method: 'POST',
            headers: {
                'X-API-KEY': API_KEY
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to clear logs');
        }
        
        showToast('All logs cleared', 'success');
        await fetchLogs();
    } catch (error) {
        console.error('Error clearing logs:', error);
        showToast('Failed to clear logs', 'error');
    }
}

function formatDateTime(isoString) {
    try {
        if (!isoString) return 'N/A';
        const date = new Date(isoString);
        return isNaN(date.getTime()) ? 'Invalid date' : date.toLocaleString();
    } catch {
        return 'N/A';
    }
}

function showToast(message, type = 'info') {
    elements.toast.textContent = message;
    elements.toast.className = 'toast ' + type;
    elements.toast.classList.add('show');
    
    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}