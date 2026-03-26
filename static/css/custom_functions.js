function fShowHideCreateForm() {
    let x = document.getElementById("custom_form");
    if (x.style.display === "none") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }
}

function handleTableSearch() {
    // Get the input value
    const searchQuery = document.getElementById("searchInput").value;
    
    // Check if the input is not empty
    if (!searchQuery.trim()) {
        alert("Please enter a search term");
        return;
    }
    
    // Send the search query to your Django main view
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')  // Django CSRF protection
        },
        body: JSON.stringify({
            search_query: searchQuery
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Search results:', data);
            updateTableWithResults(data.results);
            
            // Show a clear search button or message
            showSearchStatus(data.count, searchQuery);
        } else {
            alert('Search failed: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Search failed. Please try again.');
    });
}

function showSearchStatus(count, query) {
    // Remove existing search status if any
    const existingStatus = document.querySelector('.search-status');
    if (existingStatus) {
        existingStatus.remove();
    }
    
    // Create search status message
    const statusDiv = document.createElement('div');
    statusDiv.className = 'search-status';
    statusDiv.style.cssText = 'padding: 10px; margin: 10px 0; background-color: #e3f2fd; border-left: 4px solid #2196F3; display: flex; justify-content: space-between; align-items: center;';
    statusDiv.innerHTML = `
        <span>Found ${count} result(s) for "${query}"</span>
        <button onclick="clearSearch()" style="padding: 5px 15px; cursor: pointer;">Clear Search</button>
    `;
    
    // Insert before the table
    const tableContainer = document.querySelector('.content-container-wrapper-bottom');
    if (tableContainer) {
        tableContainer.insertBefore(statusDiv, tableContainer.firstChild);
    }
}

function clearSearch() {
    // Simply reload the page to show all results
    window.location.reload();
}

function updateTableWithResults(results) {
    // Find the table tbody
    const tbody = document.querySelector('.content-container-wrapper-bottom table tbody');
    
    if (!tbody) {
        console.error('Table not found');
        return;
    }
    
    // Clear existing rows
    tbody.innerHTML = '';
    
    // If no results found
    if (results.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9">No results found</td></tr>';
        return;
    }
    
    // Get CSRF token for the forms
    const csrfToken = getCookie('csrftoken');
    
    // Generate new rows
    results.forEach(item => {
        // Main data row
        const row1 = document.createElement('tr');
        row1.innerHTML = `
            <td>${item.id}</td>
            <td>${item.year}</td>
            <td>${item.BG_Vor_Nr}</td>
            <td>${item.company_name_bg}</td>
            <td>${item.company_name_en}</td>
            <td>${item.company_id}</td>
            <td>${item.VAT_number || ''}</td>
            <td>
                <form method="POST">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <button type="submit" name="edit" value="${item.id}" class="btn btn-danger">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                </form>
            </td>
            <td>
                <form method="POST">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <button type="submit" name="delete" value="${item.id}" class="btn btn-danger"
                            onclick="return confirm('Are you sure?')">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </form>
            </td>
        `;
        tbody.appendChild(row1);
        
        // File display row (if needed - currently empty for search results)
        const row2 = document.createElement('tr');
        row2.innerHTML = '<td colspan="9"></td>';
        tbody.appendChild(row2);
    });
    
    // Hide pagination if it exists (since we're showing search results)
    const pagination = document.querySelector('.content-container-wrapper-bottom .pagination');
    if (pagination) {
        pagination.style.display = 'none';
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
