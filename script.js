// OpenPhone API Configuration
const OPENPHONE_API_KEY = 'E49dtiHbVNgXyu2JEabHrB1gdNKjq4Vd';
const OPENPHONE_BASE_URL = 'https://api.openphone.com/v1';

// Global variables
let businessData = [];
let filteredData = [];
let currentPage = 1;
const itemsPerPage = 50;

// DOM elements
const csvFileInput = document.getElementById('csvFile');
const searchInput = document.getElementById('searchInput');
const countryFilter = document.getElementById('countryFilter');
const businessTypeFilter = document.getElementById('businessTypeFilter');
const businessTable = document.getElementById('businessTable');
const businessTableBody = document.getElementById('businessTableBody');
const prevPageBtn = document.getElementById('prevPage');
const nextPageBtn = document.getElementById('nextPage');
const pageInfo = document.getElementById('pageInfo');
const totalBusinesses = document.getElementById('totalBusinesses');
const withPhones = document.getElementById('withPhones');
const withWebsites = document.getElementById('withWebsites');
const callModal = document.getElementById('callModal');
const detailsModal = document.getElementById('detailsModal');
const messageContainer = document.getElementById('messageContainer');

// Event listeners
csvFileInput.addEventListener('change', handleFileUpload);
searchInput.addEventListener('input', debounce(handleSearch, 300));
countryFilter.addEventListener('change', handleFilter);
businessTypeFilter.addEventListener('change', handleFilter);
prevPageBtn.addEventListener('click', () => changePage(-1));
nextPageBtn.addEventListener('click', () => changePage(1));

// Modal event listeners
document.querySelectorAll('.close').forEach(closeBtn => {
    closeBtn.addEventListener('click', closeModals);
});

document.getElementById('cancelCall').addEventListener('click', closeModals);
document.getElementById('makeCall').addEventListener('click', makeOpenPhoneCall);

window.addEventListener('click', (e) => {
    if (e.target.classList.contains('modal')) {
        closeModals();
    }
});

// File upload handler
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (file.type !== 'text/csv') {
        showMessage('Please select a CSV file', 'error');
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        const csv = e.target.result;
        parseCSV(csv);
    };
    reader.readAsText(file);
}

// CSV parser
function parseCSV(csvText) {
    const lines = csvText.split('\n');
    const headers = lines[0].split(',').map(h => h.trim().replace(/"/g, ''));
    
    businessData = [];
    
    for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim();
        if (line) {
            const values = parseCSVLine(line);
            if (values.length >= headers.length) {
                const business = {};
                headers.forEach((header, index) => {
                    business[header] = values[index] || '';
                });
                businessData.push(business);
            }
        }
    }

    filteredData = [...businessData];
    populateFilters();
    updateStats();
    displayBusinesses();
    showMessage(`Successfully loaded ${businessData.length} businesses`, 'success');
}

// Parse CSV line handling quoted values
function parseCSVLine(line) {
    const values = [];
    let current = '';
    let inQuotes = false;
    
    for (let i = 0; i < line.length; i++) {
        const char = line[i];
        
        if (char === '"' && (i === 0 || line[i-1] === ',')) {
            inQuotes = true;
        } else if (char === '"' && inQuotes && (i === line.length - 1 || line[i+1] === ',')) {
            inQuotes = false;
        } else if (char === ',' && !inQuotes) {
            values.push(current.trim());
            current = '';
        } else {
            current += char;
        }
    }
    
    values.push(current.trim());
    return values.map(v => v.replace(/"/g, ''));
}

// Populate filter dropdowns
function populateFilters() {
    const countries = [...new Set(businessData.map(b => b.country || 'Unknown'))].sort();
    const businessTypes = [...new Set(businessData.map(b => b.business_type || 'Unknown'))].sort();
    
    countryFilter.innerHTML = '<option value="">All Countries</option>';
    countries.forEach(country => {
        const option = document.createElement('option');
        option.value = country;
        option.textContent = country;
        countryFilter.appendChild(option);
    });
    
    businessTypeFilter.innerHTML = '<option value="">All Business Types</option>';
    businessTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        businessTypeFilter.appendChild(option);
    });
}

// Update statistics
function updateStats() {
    const total = filteredData.length;
    const phonesCount = filteredData.filter(b => b.phone && b.phone.trim() !== '').length;
    const websitesCount = filteredData.filter(b => b.website && b.website.trim() !== '').length;
    
    totalBusinesses.textContent = total.toLocaleString();
    withPhones.textContent = phonesCount.toLocaleString();
    withWebsites.textContent = websitesCount.toLocaleString();
}

// Search handler
function handleSearch() {
    const searchTerm = searchInput.value.toLowerCase();
    applyFilters(searchTerm);
}

// Filter handler
function handleFilter() {
    const searchTerm = searchInput.value.toLowerCase();
    applyFilters(searchTerm);
}

// Apply all filters
function applyFilters(searchTerm = '') {
    const selectedCountry = countryFilter.value;
    const selectedBusinessType = businessTypeFilter.value;
    
    filteredData = businessData.filter(business => {
        const matchesSearch = !searchTerm || 
            (business.name && business.name.toLowerCase().includes(searchTerm)) ||
            (business.address && business.address.toLowerCase().includes(searchTerm)) ||
            (business.phone && business.phone.toLowerCase().includes(searchTerm));
        
        const matchesCountry = !selectedCountry || business.country === selectedCountry;
        const matchesBusinessType = !selectedBusinessType || business.business_type === selectedBusinessType;
        
        return matchesSearch && matchesCountry && matchesBusinessType;
    });
    
    currentPage = 1;
    updateStats();
    displayBusinesses();
}

// Display businesses in table
function displayBusinesses() {
    if (filteredData.length === 0) {
        businessTableBody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    <i class="fas fa-search"></i>
                    <h3>No businesses found</h3>
                    <p>Try adjusting your search or filters</p>
                </td>
            </tr>
        `;
        updatePagination();
        return;
    }

    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const pageData = filteredData.slice(startIndex, endIndex);
    
    businessTableBody.innerHTML = pageData.map(business => `
        <tr>
            <td>
                <div class="action-buttons">
                    ${business.phone ? `<button class="btn btn-primary" onclick="showCallModal(\`${business.name}\`, \`${business.phone}\`)" title="Call">
                        <i class="fas fa-phone"></i>
                    </button>` : ''}
                    ${business.website ? `<a href="${business.website}" target="_blank" class="btn btn-warning" title="Visit Website">
                        <i class="fas fa-globe"></i>
                    </a>` : ''}
                    <button class="btn btn-info" onclick="showDetailsModal(${JSON.stringify(business).replace(/"/g, '&quot;')})" title="View Details">
                        <i class="fas fa-info-circle"></i>
                    </button>
                </div>
            </td>
            <td><strong>${escapeHtml(business.name || 'N/A')}</strong></td>
            <td>${business.phone ? formatPhoneNumber(business.phone) : 'N/A'}</td>
            <td>${escapeHtml(business.address || 'N/A')}</td>
            <td>${business.website ? `<a href="${business.website}" target="_blank" title="${business.website}">View</a>` : 'N/A'}</td>
            <td>${formatRating(business.rating, business.total_ratings)}</td>
            <td>${escapeHtml(business.business_type || 'N/A')}</td>
            <td>${escapeHtml(business.country || 'N/A')}</td>
            <td>${formatBusinessStatus(business.business_status)}</td>
        </tr>
    `).join('');
    
    updatePagination();
}

// Format phone number
function formatPhoneNumber(phone) {
    if (!phone) return 'N/A';
    
    // Remove all non-digit characters
    const digits = phone.replace(/\D/g, '');
    
    // Format based on length
    if (digits.length === 10) {
        return `(${digits.slice(0, 3)}) ${digits.slice(3, 6)}-${digits.slice(6)}`;
    } else if (digits.length === 11 && digits[0] === '1') {
        return `+1 (${digits.slice(1, 4)}) ${digits.slice(4, 7)}-${digits.slice(7)}`;
    }
    
    return phone; // Return original if can't format
}

// Format rating
function formatRating(rating, totalRatings) {
    if (!rating || rating === 0) return 'No ratings';
    
    const stars = '★'.repeat(Math.floor(rating)) + '☆'.repeat(5 - Math.floor(rating));
    const ratingsText = totalRatings ? ` (${totalRatings})` : '';
    
    return `
        <div class="rating">
            <span class="stars">${stars}</span>
            <span class="rating-text">${rating}${ratingsText}</span>
        </div>
    `;
}

// Format business status
// Format business status
function formatBusinessStatus(status) {
    if (!status) return 'Unknown';
    
    const statusMap = {
        'OPERATIONAL': '<span class="status-badge status-operational">Operational</span>',
        'CLOSED_TEMPORARILY': '<span class="status-badge status-closed">Temporarily Closed</span>',
        'CLOSED_PERMANENTLY': '<span class="status-badge status-permanent">Permanently Closed</span>',
        'UNKNOWN': '<span class="status-badge status-unknown">Unknown</span>'
    };
    
    return statusMap[status] || `<span class="status-badge status-unknown">${escapeHtml(status)}</span>`;
}

// Update pagination controls
function updatePagination() {
    const totalItems = filteredData.length;
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    
    prevPageBtn.disabled = currentPage === 1;
    nextPageBtn.disabled = currentPage === totalPages || totalItems === 0;
    
    if (totalItems > 0) {
        pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
    } else {
        pageInfo.textContent = 'No pages';
    }
}

// Change page
function changePage(direction) {
    const totalPages = Math.ceil(filteredData.length / itemsPerPage);
    
    if (direction === 1 && currentPage < totalPages) {
        currentPage++;
    } else if (direction === -1 && currentPage > 1) {
        currentPage--;
    }
    
    displayBusinesses();
}

// Show call modal
function showCallModal(businessName, phoneNumber) {
    document.getElementById('callBusinessName').textContent = businessName;
    document.getElementById('callPhoneNumber').textContent = phoneNumber;
    callModal.style.display = 'block';
}

// Show details modal
function showDetailsModal(business) {
    try {
        const detailsContainer = document.getElementById('businessDetails');
        
        detailsContainer.innerHTML = `
            <div class="business-detail-grid">
                <div class="detail-item">
                    <strong>Name:</strong> ${escapeHtml(business.name || 'N/A')}
                </div>
                <div class="detail-item">
                    <strong>Phone:</strong> ${business.phone ? formatPhoneNumber(business.phone) : 'N/A'}
                </div>
                <div class="detail-item">
                    <strong>Address:</strong> ${escapeHtml(business.address || 'N/A')}
                </div>
                <div class="detail-item">
                    <strong>Website:</strong> ${business.website ? `<a href="${business.website}" target="_blank">${business.website}</a>` : 'N/A'}
                </div>
                <div class="detail-item">
                    <strong>Business Type:</strong> ${escapeHtml(business.business_type || 'N/A')}
                </div>
                <div class="detail-item">
                    <strong>Country:</strong> ${escapeHtml(business.country || 'N/A')}
                </div>
                <div class="detail-item">
                    <strong>Rating:</strong> ${formatRating(business.rating, business.total_ratings)}
                </div>
                <div class="detail-item">
                    <strong>Status:</strong> ${formatBusinessStatus(business.business_status)}
                </div>
                ${business.hours ? `
                    <div class="detail-item">
                        <strong>Hours:</strong> ${escapeHtml(business.hours)}
                    </div>
                ` : ''}
                ${business.description ? `
                    <div class="detail-item">
                        <strong>Description:</strong> ${escapeHtml(business.description)}
                    </div>
                ` : ''}
            </div>
        `;
        
        detailsModal.style.display = 'block';
    } catch (error) {
        console.error('Error parsing business data:', error);
        showMessage('Error displaying business details', 'error');
    }
}

// Make OpenPhone call
async function makeOpenPhoneCall() {
    const businessName = document.getElementById('callBusinessName').textContent;
    const phoneNumber = document.getElementById('callPhoneNumber').textContent;
    
    if (!OPENPHONE_API_KEY) {
        showMessage('OpenPhone API key not configured', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${OPENPHONE_BASE_URL}/calls`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${OPENPHONE_API_KEY}`,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                to: phoneNumber,
                from: 'your-openphone-number', // Replace with your OpenPhone number
                // Additional call parameters as needed
            })
        });
        
        if (response.ok) {
            const callData = await response.json();
            showMessage(`Call initiated to ${businessName}`, 'success');
            closeModals();
        } else {
            const errorData = await response.json();
            showMessage(`Call failed: ${errorData.message || 'Unknown error'}`, 'error');
        }
    } catch (error) {
        console.error('Error making call:', error);
        showMessage('Error making call: ' + error.message, 'error');
    }
}

// Close modals
function closeModals() {
    callModal.style.display = 'none';
    detailsModal.style.display = 'none';
}

// Show message to user
function showMessage(message, type = 'info') {
    const messageElement = document.createElement('div');
    messageElement.className = `message ${type}`;
    messageElement.textContent = message;
    
    messageContainer.appendChild(messageElement);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageElement.parentNode) {
            messageElement.parentNode.removeChild(messageElement);
        }
    }, 5000);
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Debounce function for search
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

// Export filtered data as CSV
function exportFilteredData() {
    if (filteredData.length === 0) {
        showMessage('No data to export', 'error');
        return;
    }
    
    const headers = Object.keys(filteredData[0]);
    const csvContent = [
        headers.join(','),
        ...filteredData.map(row => 
            headers.map(header => {
                const value = row[header] || '';
                // Escape quotes and wrap in quotes if necessary
                const escapedValue = value.toString().replace(/"/g, '""');
                return `"${escapedValue}"`;
            }).join(',')
        )
    ].join('\n');
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `filtered_businesses_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showMessage('Data exported successfully', 'success');
}

// Add export button functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add export button to controls
    const exportBtn = document.createElement('button');
    exportBtn.className = 'btn btn-success';
    exportBtn.innerHTML = '<i class="fas fa-download"></i> Export Filtered Data';
    exportBtn.onclick = exportFilteredData;
    
    const controlsDiv = document.querySelector('.controls');
    controlsDiv.appendChild(exportBtn);
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'f':
                e.preventDefault();
                searchInput.focus();
                break;
            case 'e':
                e.preventDefault();
                exportFilteredData();
                break;
            case 'Escape':
                closeModals();
                break;
        }
    }
});

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    // Show initial empty state
    updateStats();
    displayBusinesses();
    
    // Add loading state styles
    const style = document.createElement('style');
    style.textContent = `
        .message {
            padding: 12px 20px;
            margin: 10px 0;
            border-radius: 8px;
            font-weight: 500;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .message.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .message.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        .message.info {
            background: #cce7ff;
            color: #004085;
            border: 1px solid #b8daff;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8rem;
            font-weight: 600;
        }
        .status-operational {
            background: #d4edda;
            color: #155724;
        }
        .status-closed {
            background: #fff3cd;
            color: #856404;
        }
        .status-permanent {
            background: #f8d7da;
            color: #721c24;
        }
        .status-unknown {
            background: #e2e3e5;
            color: #383d41;
        }
        .business-detail-grid {
            display: grid;
            gap: 15px;
            margin: 20px 0;
        }
        .detail-item {
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
            border-left: 3px solid #007bff;
        }
        .detail-item strong {
            display: block;
            margin-bottom: 5px;
            color: #495057;
        }
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: #6c757d;
        }
        .empty-state i {
            font-size: 3rem;
            margin-bottom: 20px;
            opacity: 0.5;
        }
        .empty-state h3 {
            margin-bottom: 10px;
            color: #495057;
        }
    `;
    document.head.appendChild(style);
    
    console.log('Business Data CSV Viewer initialized');
});