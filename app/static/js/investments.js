document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('invDate').valueAsDate = new Date();
    loadInvestments();

    document.getElementById('invForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const invId = document.getElementById('invId').value;
        const payload = {
            symbol: document.getElementById('invSymbol').value,
            asset_name: document.getElementById('invName').value,
            quantity: parseFloat(document.getElementById('invQuantity').value),
            price: parseFloat(document.getElementById('invPrice').value),
            purchase_date: document.getElementById('invDate').value
        };

        const isUpdate = invId !== "";
        const url = isUpdate ? `/api/investments/${invId}` : '/api/investments';
        const method = isUpdate ? 'PUT' : 'POST';

        const res = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            closeInvestmentModal();
            loadInvestments();
        } else {
            alert('Error saving investment');
        }
    });

    // Setup Asset Search
    setupAssetSearch();
});

let debounceTimeout = null;
let currentTransactionsList = [];

function setupAssetSearch() {
    const invNameInput = document.getElementById('invName');
    const searchResults = document.getElementById('searchResults');

    // Close dropdown on outside click
    document.addEventListener('click', (e) => {
        if (!invNameInput.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });

    invNameInput.addEventListener('input', (e) => {
        const query = e.target.value.trim();
        clearTimeout(debounceTimeout);

        if (query.length < 2) {
            searchResults.classList.add('hidden');
            return;
        }

        debounceTimeout = setTimeout(async () => {
            try {
                const res = await fetch(`/api/assets/search?q=${encodeURIComponent(query)}`);
                const data = await res.json();

                searchResults.innerHTML = '';
                if (data.length > 0) {
                    data.forEach(asset => {
                        const div = document.createElement('div');
                        div.className = 'px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-50 flex justify-between items-center group';
                        div.innerHTML = `
                            <div>
                                <div class="font-bold text-gray-900 group-hover:text-pocketwise-darkGreen transition-colors">${asset.symbol}</div>
                                <div class="text-xs text-gray-500">${asset.name}</div>
                            </div>
                            <span class="text-[10px] font-semibold bg-gray-100 text-gray-600 px-2 py-1 rounded-full uppercase tracking-wider">${asset.type}</span>
                        `;
                        div.onclick = () => selectAsset(asset.symbol, asset.name);
                        searchResults.appendChild(div);
                    });
                    searchResults.classList.remove('hidden');
                } else {
                    searchResults.innerHTML = '<div class="px-4 py-3 text-sm text-gray-500 text-center">No assets found</div>';
                    searchResults.classList.remove('hidden');
                }
            } catch (err) {
                console.error("Search failed:", err);
            }
        }, 300);
    });
}

function selectAsset(symbol, name) {
    document.getElementById('invSymbol').value = symbol;
    document.getElementById('invName').value = name;
    document.getElementById('searchResults').classList.add('hidden');
}

async function loadInvestments() {
    try {
        const [sumRes, transRes] = await Promise.all([
            fetch('/api/investments/summary'),
            fetch('/api/investments')
        ]);

        const summaryData = await sumRes.json();
        const transactionsData = await transRes.json();
        currentTransactionsList = transactionsData.transactions || [];

        const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

        // Populate Top Cards
        document.getElementById('totalInvestmentCard').textContent = formatCurrency(summaryData.total_investment);
        document.getElementById('portfolioValueCard').textContent = formatCurrency(summaryData.portfolio_value);

        const profitCard = document.getElementById('profitCard');
        const sign = summaryData.profit >= 0 ? '+' : '-';
        profitCard.textContent = `${sign}${formatCurrency(Math.abs(summaryData.profit))} (${sign}${Math.abs(summaryData.return_percent).toFixed(1)}%)`;

        if (summaryData.profit > 0) profitCard.className = "text-3xl font-extrabold text-green-600 tracking-tight";
        else if (summaryData.profit < 0) profitCard.className = "text-3xl font-extrabold text-red-600 tracking-tight";
        else profitCard.className = "text-3xl font-extrabold text-gray-900 tracking-tight";

        // Render Grouped Portfolio Table
        const pTbody = document.getElementById('portfolioTableBody');
        if (pTbody) {
            pTbody.innerHTML = '';
            (summaryData.assets || []).forEach(asset => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-50 transition-colors';

                const rColor = asset.profit >= 0 ? 'text-green-600' : 'text-red-600';
                const rSign = asset.profit >= 0 ? '+' : '';

                tr.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap"><div class="text-sm font-bold text-gray-900">${asset.symbol}</div></td>
                    <td class="px-6 py-4 whitespace-nowrap"><div class="text-sm text-gray-500">${asset.asset_name}</div></td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">${asset.total_quantity}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-medium">${formatCurrency(asset.avg_price)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">${formatCurrency(asset.current_price)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-bold ${rColor}">${rSign}${formatCurrency(Math.abs(asset.profit))}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-bold ${rColor}">${rSign}${asset.return_percent}%</td>
                `;
                pTbody.appendChild(tr);
            });
        }

        // Render Transaction History Table
        const tBody = document.getElementById('investmentTableBody');
        if (tBody) {
            tBody.innerHTML = '';
            (transactionsData.transactions || []).forEach(inv => {
                const tr = document.createElement('tr');
                tr.className = 'hover:bg-gray-50 transition-colors group';

                tr.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap"><div class="text-sm font-bold text-gray-900">${inv.symbol.toUpperCase()}</div></td>
                    <td class="px-6 py-4 whitespace-nowrap"><div class="text-sm text-gray-500">${inv.asset_name}</div></td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">${inv.quantity}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-600 font-medium">${formatCurrency(inv.price)}</td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-medium">
                        <div class="flex items-center">
                            <i class="far fa-calendar-alt mr-2 text-gray-400"></i>
                            ${new Date(inv.purchase_date).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div class="flex justify-end space-x-3 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onclick="editInvestment(${inv.id})" class="text-blue-600 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 p-2 rounded-lg transition-colors" title="Edit">
                                <i class="fas fa-edit"></i>
                            </button>
                            <button onclick="deleteInvestment(${inv.id})" class="text-red-600 hover:text-red-900 bg-red-50 hover:bg-red-100 p-2 rounded-lg transition-colors" title="Delete">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </td>
                `;
                tBody.appendChild(tr);
            });
        }

        renderPortfolioChart(summaryData.allocation || {});
        renderPerformanceChart(summaryData.historical || []);

    } catch (err) {
        console.error("Failed to load dashboard data", err);
    }
}

let portfolioChartInstance = null;
function renderPortfolioChart(allocation) {
    const ctx = document.getElementById('portfolioChart');
    if (!ctx) return;

    if (portfolioChartInstance) portfolioChartInstance.destroy();

    const labels = Object.keys(allocation);
    const data = Object.values(allocation);

    if (data.length === 0) {
        labels.push('No Data');
        data.push(1);
    }

    const brandColors = ['#115E59', '#CFE8D5', '#0D9488', '#99F6E4', '#0F766E', '#5EEAD4'];

    portfolioChartInstance = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: brandColors,
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '75%',
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, padding: 20, font: { family: "'Inter', sans-serif" } } }
            }
        }
    });
}

let performanceChartInstance = null;
function renderPerformanceChart(historical) {
    const ctx = document.getElementById('performanceChart');
    if (!ctx) return;

    if (performanceChartInstance) performanceChartInstance.destroy();

    const labels = historical.map(h => h.month);
    const data = historical.map(h => h.portfolio_value);

    performanceChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Portfolio Value',
                data: data,
                borderColor: '#115E59', // Dark Green
                backgroundColor: 'rgba(17, 94, 89, 0.1)',
                borderWidth: 3,
                pointBackgroundColor: '#115E59',
                pointBorderWidth: 2,
                pointRadius: 4,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: { color: '#F3F4F6' },
                    ticks: {
                        callback: function (value) {
                            return '$' + value;
                        }
                    }
                },
                x: {
                    grid: { display: false }
                }
            }
        }
    });
}

async function deleteInvestment(id) {
    if (confirm('Are you sure you want to delete this transaction?')) {
        try {
            const res = await fetch(`/api/investments/${id}`, { method: 'DELETE' });
            if (res.ok) {
                loadInvestments();
            } else {
                alert('Failed to delete investment');
            }
        } catch (err) {
            console.error(err);
        }
    }
}

async function syncLivePrices() {
    const btn = document.getElementById('syncPricesBtn');
    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i> Syncing...';
    btn.disabled = true;

    try {
        await loadInvestments();
    } catch (err) {
        console.error(err);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function openInvestmentModal() {
    document.getElementById('invForm').reset();
    document.getElementById('invId').value = "";
    document.getElementById('invDate').valueAsDate = new Date();
    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('invModalTitle').textContent = "Add Investment";

    const modal = document.getElementById('investmentModal');
    modal.classList.remove('opacity-0', 'pointer-events-none');
    modal.querySelector('#invModalContent').classList.remove('scale-95');
}

function closeInvestmentModal() {
    const modal = document.getElementById('investmentModal');
    modal.classList.add('opacity-0', 'pointer-events-none');
    modal.querySelector('#invModalContent').classList.add('scale-95');
}

function editInvestment(id) {
    const inv = currentTransactionsList.find(i => i.id === id);
    if (!inv) return;

    document.getElementById('invId').value = inv.id;
    document.getElementById('invSymbol').value = inv.symbol;
    document.getElementById('invName').value = inv.asset_name;
    document.getElementById('invQuantity').value = inv.quantity;
    document.getElementById('invPrice').value = inv.price;
    if (inv.purchase_date) {
        document.getElementById('invDate').value = inv.purchase_date;
    }

    document.getElementById('searchResults').classList.add('hidden');
    document.getElementById('invModalTitle').textContent = "Edit Investment";

    const modal = document.getElementById('investmentModal');
    modal.classList.remove('opacity-0', 'pointer-events-none');
    modal.querySelector('#invModalContent').classList.remove('scale-95');
}
