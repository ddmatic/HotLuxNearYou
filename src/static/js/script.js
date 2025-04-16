// DataTables instances
let allListingsTable;
let newListingsTable;
let wasScraperRunning = false;

// Function to load data into tables
function loadTableData(tableId, tableType) {
    // Get filter values
    const filters = {};
    const prefix = tableType === 'new' ? 'new_filter_' : 'filter_';

    $('.filter-dropdown').each(function() {
        const id = $(this).attr('id');
        if (id && id.startsWith(prefix)) {
            const value = $(this).val();
            if (value) {
                filters[id] = value;
            }
        }
    });

    // Build query string
    let queryParams = new URLSearchParams();
    queryParams.append('table_type', tableType);

    for (const [key, value] of Object.entries(filters)) {
        queryParams.append(key, value);
    }

    // Fetch data
    $.ajax({
        url: `/listings?${queryParams.toString()}`,
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            const tableElement = $(`#${tableId}`);

            // Clear existing table
            if ($.fn.DataTable.isDataTable(`#${tableId}`)) {
                $(`#${tableId}`).DataTable().destroy();
            }

            // Set headers
            const headerRow = $(`#${tableId === 'allListingsTable' ? 'allListingsHeaders' : 'newListingsHeaders'}`);
            headerRow.empty();

            const columnsToShow = response.columns.filter(col =>
                col !== 'is_active' &&
                col !== 'removed_date' &&
                col !== 'id' &&
                col !== 'ReportDate' &&
                col !== 'GoToLink'
            );

            columnsToShow.forEach(column => {
                headerRow.append(`<th>${column}</th>`);
            });

            // Initialize DataTable
            const dataTableConfig = {
                data: response.data,
                columns: columnsToShow.map(column => ({
                    data: column,
                    title: column,
                    render: function(data, type, row) {
                        if (column === 'url') {
                            return data;
                        } else if (column === 'Price' && data) {
                            return new Intl.NumberFormat('sr-RS').format(data) + ' €';
                        } else if (column === 'Area' && data) {
                            return data + ' m²';
                        } else {
                            return data || '';
                        }
                    }
                })),
                order: [[0, 'asc']],
                pageLength: 25,
                lengthMenu: [10, 25, 50, 100],
                responsive: true,
                language: {
                    search: "🔍 _INPUT_",
                    searchPlaceholder: "Search listings...",
                    zeroRecords: "No matching listings found",
                    info: "Showing _START_ to _END_ of _TOTAL_ listings",
                    infoEmpty: "No listings available",
                    infoFiltered: "(filtered from _MAX_ total listings)",
                    paginate: {
                        first: "⏮",
                        last: "⏭",
                        next: "▶",
                        previous: "◀"
                    }
                }
            };

            if (tableId === 'allListingsTable') {
                allListingsTable = tableElement.DataTable(dataTableConfig);
            } else {
                newListingsTable = tableElement.DataTable(dataTableConfig);
            }

            updateListingsCounts();
        },
        error: function(error) {
            console.error("Error loading data:", error);
            $(`#${tableId} tbody`).html('<tr><td colspan="10" class="text-center text-danger">Error loading data</td></tr>');
        }
    });
}

// Function to update the listings counts
function updateListingsCounts() {
    $.ajax({
        url: '/listings?table_type=new',
        method: 'GET',
        dataType: 'json',
        success: function(newResponse) {
            $.ajax({
                url: '/listings?table_type=all',
                method: 'GET',
                dataType: 'json',
                success: function(allResponse) {
                    $('#newListingsCount').html(`
                        <strong>${newResponse.data.length}</strong> new listings | 
                        <strong>${allResponse.data.length}</strong> total active listings
                    `);
                }
            });
        }
    });
}

// Function to update scraper status
function updateScraperStatus() {
    $.ajax({
        url: '/scraper-status',
        method: 'GET',
        dataType: 'json',
        success: function(response) {
            const statusContainer = $('#scraperStatus');
            const runButton = $('#runScraperBtn');

            if (response.is_running) {
                statusContainer.removeClass('status-idle').addClass('status-running');
                statusContainer.html(`<div class="spinner"></div> Mining in progress...`);
                runButton.prop('disabled', true);
                runButton.html('<div class="spinner"></div> Mining...');
                wasScraperRunning = true;
            } else {
                statusContainer.removeClass('status-running').addClass('status-idle');
                statusContainer.html(`<span id="statusIcon">⏸</span> Idle`);
                runButton.prop('disabled', false);
                runButton.html('<span class="crypto-icon">⛏️</span> Mine New Listings');

                if (response.last_run) {
                    $('#lastRunTime').text(`Last scan: ${response.last_run}`);
                }

                // ✅ Only reload tables if scraper just finished
                if (wasScraperRunning) {
                    loadTableData('allListingsTable', 'all');
                    loadTableData('newListingsTable', 'new');
                    wasScraperRunning = false;
                }
            }
        }
    });
}

// Set up polling for scraper status
function setupStatusPolling() {
    updateScraperStatus();
    setInterval(updateScraperStatus, 3000);
}

// Document ready
$(document).ready(function() {
    loadTableData('allListingsTable', 'all');
    loadTableData('newListingsTable', 'new');
    setupStatusPolling();

    $('#runScraperBtn').click(function(e) {
        e.preventDefault();
        if (confirm('Start mining for new apartment listings?')) {
            $.ajax({
                url: '/run-scraper',
                method: 'POST',
                success: function(response) {
                    if (response.status === 'started') {
                        updateScraperStatus();
                    } else {
                        alert("Scraper is already running.");
                    }
                },
                error: function() {
                    alert("Failed to start scraper.");
                }
            });
        }
    });

    // Reload tables when filters change
    $('.filter-dropdown').change(function() {
        loadTableData('allListingsTable', 'all');
        loadTableData('newListingsTable', 'new');
    });

    // Toggle All Listings Filters
    $('#toggleAllFilters').click(function () {
    const section = $('#filtersSection');
    section.slideToggle(300);

    const btn = $(this);
    btn.toggleClass('active');
    btn.text(btn.hasClass('active') ? 'Hide Filters' : 'Show Filters');
    });

    // Toggle New Listings Filters
    $('#toggleNewFilters').click(function () {
    const section = $('#filtersSection');
    section.slideToggle(300);

    const btn = $(this);
    btn.toggleClass('active');
    btn.text(btn.hasClass('active') ? 'Hide Filters' : 'Show Filters');
    });
});

function exportTablesToExcel() {
    const wb = XLSX.utils.book_new();

    // Helper to extract table data
    function getTableData(tableInstance, name) {
        const data = [];
        const headers = tableInstance.columns().header().toArray().map(h => $(h).text().trim());
        data.push(headers);

        tableInstance.rows({ search: 'applied' }).every(function () {
            const rowData = this.data();
            const row = headers.map(header => rowData[header] ?? '');
            data.push(row);
        });

        const ws = XLSX.utils.aoa_to_sheet(data);
        XLSX.utils.book_append_sheet(wb, ws, name);
    }

    if (allListingsTable && newListingsTable) {
        getTableData(allListingsTable, "All Listings");
        getTableData(newListingsTable, "New Listings");

        XLSX.writeFile(wb, "ListingsExport.xlsx");
    } else {
        alert("Tables are not loaded yet.");
    }
}

// Export button click
$('#exportToExcelBtn').click(function () {
    exportTablesToExcel();
});