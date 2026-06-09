/* MediWholesale Ethiopia - Main JavaScript */

// ===== SIDEBAR TOGGLE =====
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('show');
        });
        document.addEventListener('click', function (e) {
            if (!sidebar.contains(e.target) && !sidebarToggle.contains(e.target)) {
                sidebar.classList.remove('show');
            }
        });
    }

    // ===== DATATABLE INIT =====
    const tables = document.querySelectorAll('.datatable');
    tables.forEach(function (table) {
        if (typeof $.fn.DataTable !== 'undefined') {
            $(table).DataTable({
                pageLength: 25,
                responsive: true,
                language: { search: '', searchPlaceholder: 'Search...' },
                dom: '<"row"<"col-md-6"l><"col-md-6"f>>rtip',
            });
        }
    });

    // ===== AUTO DISMISS ALERTS =====
    const alerts = document.querySelectorAll('.alert-dismissible.auto-dismiss');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4000);
    });

    // ===== TOOLTIP INIT =====
    const tooltipEls = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipEls.forEach(el => new bootstrap.Tooltip(el));

    // ===== CONFIRM DELETE =====
    document.querySelectorAll('.confirm-delete').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            if (!confirm('Are you sure you want to delete this record?')) {
                e.preventDefault();
            }
        });
    });

    // ===== ORDER ITEMS DYNAMIC FORM =====
    initOrderItemsForm();

    // ===== PURCHASE ORDER ITEMS DYNAMIC FORM =====
    initPurchaseOrderItemsForm();
});

// ===== DYNAMIC SALES ORDER ITEMS =====
function initOrderItemsForm() {
    const addBtn = document.getElementById('addSalesOrderItem');
    if (!addBtn) return;

    let formCount = parseInt(document.getElementById('id_items-TOTAL_FORMS').value);

    addBtn.addEventListener('click', function () {
        const tbody = document.getElementById('salesOrderItemsBody');
        const emptyRow = document.getElementById('empty-sales-item-row');
        if (!emptyRow) return;

        const newRow = emptyRow.cloneNode(true);
        newRow.id = '';
        newRow.style.display = '';
        newRow.querySelectorAll('[name]').forEach(function (input) {
            input.name = input.name.replace('__prefix__', formCount);
            input.id = input.id ? input.id.replace('__prefix__', formCount) : '';
            input.value = '';
        });
        tbody.appendChild(newRow);
        formCount++;
        document.getElementById('id_items-TOTAL_FORMS').value = formCount;
        attachPriceAutoFill(newRow);
    });

    // Attach to existing rows
    document.querySelectorAll('#salesOrderItemsBody tr.item-row').forEach(attachPriceAutoFill);
}

// ===== DYNAMIC PURCHASE ORDER ITEMS =====
function initPurchaseOrderItemsForm() {
    const addBtn = document.getElementById('addPurchaseOrderItem');
    if (!addBtn) return;

    let formCount = parseInt(document.getElementById('id_items-TOTAL_FORMS').value);

    addBtn.addEventListener('click', function () {
        const tbody = document.getElementById('purchaseOrderItemsBody');
        const emptyRow = document.getElementById('empty-purchase-item-row');
        if (!emptyRow) return;

        const newRow = emptyRow.cloneNode(true);
        newRow.id = '';
        newRow.style.display = '';
        newRow.querySelectorAll('[name]').forEach(function (input) {
            input.name = input.name.replace('__prefix__', formCount);
            input.id = input.id ? input.id.replace('__prefix__', formCount) : '';
            input.value = '';
        });
        tbody.appendChild(newRow);
        formCount++;
        document.getElementById('id_items-TOTAL_FORMS').value = formCount;
    });
}

// ===== AUTO FILL PRICE FROM VARIANT SELECTION =====
function attachPriceAutoFill(row) {
    const variantSelect = row.querySelector('select[name*="product_variant"]');
    const priceInput = row.querySelector('input[name*="unit_price"]');
    if (!variantSelect || !priceInput) return;

    variantSelect.addEventListener('change', function () {
        const variantId = this.value;
        if (!variantId) return;
        fetch(`/products/api/variant-price/${variantId}/`)
            .then(r => r.json())
            .then(data => {
                if (data.selling_price) {
                    priceInput.value = data.selling_price;
                    updateRowTotal(row);
                }
            })
            .catch(() => {});
    });

    // Update total on quantity/price/discount changes
    ['input[name*="quantity"]', 'input[name*="unit_price"]', 'input[name*="discount_percent"]'].forEach(function (sel) {
        const input = row.querySelector(sel);
        if (input) input.addEventListener('input', function () { updateRowTotal(row); });
    });
}

function updateRowTotal(row) {
    const qty = parseFloat(row.querySelector('input[name*="quantity"]')?.value) || 0;
    const price = parseFloat(row.querySelector('input[name*="unit_price"]')?.value) || 0;
    const discount = parseFloat(row.querySelector('input[name*="discount_percent"]')?.value) || 0;
    const total = qty * price * (1 - discount / 100);
    const totalEl = row.querySelector('.row-total');
    if (totalEl) totalEl.textContent = 'Br ' + total.toFixed(2);
    updateOrderTotals();
}

function updateOrderTotals() {
    let subtotal = 0;
    document.querySelectorAll('#salesOrderItemsBody tr.item-row .row-total').forEach(function (el) {
        const val = parseFloat(el.textContent.replace('Br ', '')) || 0;
        subtotal += val;
    });
    const vatRate = 0.15;
    const discountEl = document.getElementById('id_discount_amount');
    const discount = discountEl ? parseFloat(discountEl.value) || 0 : 0;
    const vat = subtotal * vatRate;
    const total = subtotal + vat - discount;

    const subtotalEl = document.getElementById('order-subtotal');
    const vatEl = document.getElementById('order-vat');
    const totalEl = document.getElementById('order-total');
    if (subtotalEl) subtotalEl.textContent = 'Br ' + subtotal.toFixed(2);
    if (vatEl) vatEl.textContent = 'Br ' + vat.toFixed(2);
    if (totalEl) totalEl.textContent = 'Br ' + total.toFixed(2);
}

// ===== PRINT PAGE =====
function printPage() {
    window.print();
}

// ===== EXPORT TABLE TO CSV =====
function exportTableToCSV(tableId, filename) {
    const table = document.getElementById(tableId);
    if (!table) return;
    const rows = Array.from(table.querySelectorAll('tr'));
    const csv = rows.map(function (row) {
        return Array.from(row.querySelectorAll('th, td'))
            .map(cell => '"' + cell.innerText.replace(/"/g, '""') + '"')
            .join(',');
    }).join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename || 'export.csv';
    a.click();
    URL.revokeObjectURL(url);
}

// ===== FILTER FORM AUTO-SUBMIT =====
document.querySelectorAll('.auto-submit-filter select, .auto-submit-filter input[type="date"]').forEach(function (el) {
    el.addEventListener('change', function () {
        this.closest('form').submit();
    });
});

// ===== STOCK LEVEL BARS =====
document.querySelectorAll('.stock-bar-fill').forEach(function (bar) {
    const pct = parseFloat(bar.dataset.pct) || 0;
    bar.style.width = Math.min(pct, 100) + '%';
    if (pct < 25) { bar.classList.add('stock-critical'); }
    else if (pct < 50) { bar.classList.add('stock-low'); }
    else { bar.classList.add('stock-ok'); }
});
