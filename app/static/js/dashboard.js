document.addEventListener('DOMContentLoaded', async () => {
    // Set default month filter to current month
    const monthFilter = document.getElementById('dashboard-month-filter');
    if (monthFilter) {
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        monthFilter.value = `${yyyy}-${mm}`;

        monthFilter.addEventListener('change', async () => {
            await fetchDashboardData();
        });
    }

    await fetchDashboardData();
});

async function fetchDashboardData() {
    try {
        let url = '/api/analytics/me';
        const monthFilter = document.getElementById('dashboard-month-filter');
        if (monthFilter && monthFilter.value) {
            url += `?month=${monthFilter.value}`;
        }

        const res = await fetch(url);
        if (!res.ok) {
            if (res.status === 401 || res.status === 403) {
                window.location.href = '/login';
            }
            return;
        }

        const data = await res.json();

        const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

        document.getElementById('dash-income').textContent = formatCurrency(data.total_income || 0);
        document.getElementById('dash-expense').textContent = formatCurrency(data.total_expense || 0);

        const savingRatePct = ((data.saving_rate || 0) * 100).toFixed(1);
        document.getElementById('dash-saving-rate').textContent = `${savingRatePct}%`;

        const score = data.financial_score || 0;
        document.getElementById('dash-health-score').innerHTML = `${score}<span class="text-lg font-medium text-gray-400">/100</span>`;
        document.getElementById('dash-score-bar').style.width = `${score}%`;

        // Colorize score bar
        const scoreBar = document.getElementById('dash-score-bar');
        if (score >= 80) scoreBar.className = "bg-fintech-green h-1.5 rounded-full";
        else if (score >= 50) scoreBar.className = "bg-yellow-400 h-1.5 rounded-full";
        else scoreBar.className = "bg-red-500 h-1.5 rounded-full";

        document.getElementById('dash-top-category').textContent = data.top_category || 'N/A';

        // Recommendations
        const recList = document.getElementById('dash-recommendations');
        recList.innerHTML = '';
        if (data.recommendations && data.recommendations.length > 0) {
            data.recommendations.forEach(r => {
                const div = document.createElement('div');
                div.className = "p-4 bg-blue-50 text-blue-800 rounded-lg text-sm border border-blue-100 flex items-start";
                div.innerHTML = `<i class="fas fa-info-circle mt-0.5 mr-3 text-fintech-blue"></i> <span>${r}</span>`;
                recList.appendChild(div);
            });
        } else {
            recList.innerHTML = `<p class="text-gray-500 text-sm">No insights available right now.</p>`;
        }

        // Investment Overview Cards
        const totalInvestment = data.total_investment || 0;
        const portfolioValue = data.portfolio_value || 0;
        const profit = data.profit || 0;
        const returnPercent = data.return_percent || 0;

        const dashTotalInvestment = document.getElementById('dashTotalInvestment');
        const dashPortfolioValue = document.getElementById('dashPortfolioValue');
        const dashProfit = document.getElementById('dashProfit');

        if (dashTotalInvestment) dashTotalInvestment.textContent = formatCurrency(totalInvestment);
        if (dashPortfolioValue) dashPortfolioValue.textContent = formatCurrency(portfolioValue);

        if (dashProfit) {
            const sign = profit > 0 ? '+' : (profit < 0 ? '-' : '');
            dashProfit.textContent = `${sign}${formatCurrency(Math.abs(profit))} (${sign}${Math.abs(returnPercent).toFixed(1)}%)`;

            dashProfit.classList.remove('text-green-600', 'text-red-600', 'text-gray-900');
            if (profit > 0) {
                dashProfit.classList.add('text-green-600');
            } else if (profit < 0) {
                dashProfit.classList.add('text-red-600');
            } else {
                dashProfit.classList.add('text-gray-900');
            }
        }

        // Render real charts with data
        renderCharts(data);

    } catch (err) {
        console.error('Error fetching dashboard data:', err);
    }
}

function renderCharts(data) {
    // Expense Pie Chart
    const expenseData = data.expense_breakdown || { labels: [], data: [] };
    const ctxExpense = document.getElementById('expenseChart').getContext('2d');

    if (window.expenseChartInst) window.expenseChartInst.destroy();

    window.expenseChartInst = new Chart(ctxExpense, {
        type: 'doughnut',
        data: {
            labels: expenseData.labels,
            datasets: [{
                data: expenseData.data,
                backgroundColor: ['#10B981', '#0F52BA', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#14B8A6'],
                borderWidth: 0,
                cutout: '70%'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { boxWidth: 12 } },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            let label = context.label || '';
                            if (label) {
                                label += ': ';
                            }
                            const value = context.parsed;
                            const total = context.dataset.data.reduce((acc, curr) => acc + curr, 0);
                            const percentage = total > 0 ? ((value / total) * 100).toFixed(1) + '%' : '0%';

                            const formattedValue = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
                            return `${label}${percentage} (${formattedValue})`;
                        }
                    }
                }
            }
        }
    });

    // Cashflow Line Chart
    const cashflowData = data.cashflow_trend || { labels: [], income: [], expense: [] };
    const ctxCashflow = document.getElementById('cashflowChart').getContext('2d');

    if (window.cashflowChartInst) window.cashflowChartInst.destroy();

    window.cashflowChartInst = new Chart(ctxCashflow, {
        type: 'line',
        data: {
            labels: cashflowData.labels,
            datasets: [
                {
                    label: 'Income',
                    data: cashflowData.income,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Expense',
                    data: cashflowData.expense,
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { position: 'top' } },
            scales: {
                y: { beginAtZero: true, grid: { borderDash: [2, 4] } },
                x: { grid: { display: false } }
            }
        }
    });
}
