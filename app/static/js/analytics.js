document.addEventListener('DOMContentLoaded', () => {
    loadForecastData();
});

async function loadForecastData() {
    try {
        const res = await fetch('/api/forecast');
        if (!res.ok) throw new Error('Failed to load forecast data');
        const data = await res.json();

        const forecastingSection = document.getElementById('forecastingSection');
        forecastingSection.classList.remove('hidden');

        const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

        // --------------------------------------------------
        // SECTION 1: Monthly Forecast
        // --------------------------------------------------
        const monthlyCard = document.getElementById('monthlyForecastCard');
        const monthlyBlocker = document.getElementById('monthlyDataBlocker');

        if (data.next_month_income !== undefined && data.next_month_expense !== undefined) {
            document.getElementById('forecastIncome').textContent = formatCurrency(data.next_month_income);
            document.getElementById('forecastExpense').textContent = formatCurrency(data.next_month_expense);
            document.getElementById('forecastSavings').textContent = formatCurrency(data.expected_saving);

            monthlyCard.classList.remove('hidden');
            monthlyBlocker.classList.add('hidden');
        } else {
            monthlyCard.classList.add('hidden');
            monthlyBlocker.classList.remove('hidden');
        }

        // --------------------------------------------------
        // SECTION 2: Balance Projection
        // --------------------------------------------------
        const balanceCard = document.getElementById('balanceProjectionCard');
        const balanceBlocker = document.getElementById('balanceDataBlocker');

        if (data.estimated_days_remaining !== undefined && data.current_balance !== undefined) {
            document.getElementById('forecastDays').textContent = `${data.estimated_days_remaining} days`;
            document.getElementById('forecastCurrentBalance').textContent = formatCurrency(data.current_balance);
            document.getElementById('forecastDailyExpense').textContent = formatCurrency(data.average_daily_expense);

            balanceCard.classList.remove('hidden');
            balanceBlocker.classList.add('hidden');
        } else {
            balanceCard.classList.add('hidden');
            balanceBlocker.classList.remove('hidden');
        }

        // --------------------------------------------------
        // SECTION 3: Investment Projection
        // --------------------------------------------------
        const investmentCard = document.getElementById('investmentProjectionCard');
        const investmentBlocker = document.getElementById('investmentDataBlocker');

        if (data.expected_portfolio_6m !== undefined && data.expected_portfolio_12m !== undefined) {
            document.getElementById('forecast6m').textContent = formatCurrency(data.expected_portfolio_6m);
            document.getElementById('forecast12m').textContent = formatCurrency(data.expected_portfolio_12m);

            const returnPercent = (data.average_return * 100).toFixed(1);
            const returnSign = data.average_return >= 0 ? '+' : '';
            document.getElementById('forecastReturn').textContent = `${returnSign}${returnPercent}%`;

            investmentCard.classList.remove('hidden');
            investmentBlocker.classList.add('hidden');
        } else {
            investmentCard.classList.add('hidden');
            investmentBlocker.classList.remove('hidden');
        }

        // Load Charts
        await loadForecastCharts();

    } catch (error) {
        console.error("Error loading forecast data:", error);
    }
}

let trendChartInst = null;
let balanceChartInst = null;
let investChartInst = null;

async function loadForecastCharts() {
    try {
        const [trendRes, balanceRes, investRes] = await Promise.all([
            fetch('/api/forecast/trend'),
            fetch('/api/forecast/balance'),
            fetch('/api/forecast/investment')
        ]);

        if (trendRes.ok) {
            const trendData = await trendRes.json();
            if (trendData.months && trendData.months.length > 0) {
                document.getElementById('trendChartContainer').classList.remove('hidden');
                renderTrendChart(trendData);
            }
        }

        if (balanceRes.ok) {
            const balanceData = await balanceRes.json();
            if (balanceData.days && balanceData.days.length > 0) {
                document.getElementById('balanceChartContainer').classList.remove('hidden');
                renderBalanceChart(balanceData);
            }
        }

        if (investRes.ok) {
            const investData = await investRes.json();
            if (investData.labels && investData.labels.length > 0) {
                document.getElementById('investmentChartContainer').classList.remove('hidden');
                renderInvestmentChart(investData);
            }
        }
    } catch (error) {
        console.error("Error loading forecast charts:", error);
    }
}

function renderTrendChart(data) {
    const ctx = document.getElementById('trendChart').getContext('2d');
    if (trendChartInst) trendChartInst.destroy();

    trendChartInst = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.months,
            datasets: [
                {
                    label: 'Income',
                    data: data.income,
                    borderColor: '#10B981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    segment: {
                        borderDash: ctx => ctx.p0DataIndex >= data.forecast_index - 1 ? [5, 5] : []
                    }
                },
                {
                    label: 'Expense',
                    data: data.expense,
                    borderColor: '#EF4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    segment: {
                        borderDash: ctx => ctx.p0DataIndex >= data.forecast_index - 1 ? [5, 5] : []
                    }
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } }
            }
        }
    });
}

function renderBalanceChart(data) {
    const ctx = document.getElementById('balanceChart').getContext('2d');
    if (balanceChartInst) balanceChartInst.destroy();

    balanceChartInst = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.days,
            datasets: [{
                label: 'Projected Balance',
                data: data.balance,
                borderColor: '#8B5CF6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { title: { display: true, text: 'Days from now' } }
            },
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } }
            }
        }
    });
}

function renderInvestmentChart(data) {
    const ctx = document.getElementById('investmentChart').getContext('2d');
    if (investChartInst) investChartInst.destroy();

    investChartInst = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Portfolio Forecast',
                data: data.values,
                borderColor: '#F59E0B',
                backgroundColor: 'rgba(245, 158, 11, 0.1)',
                fill: true,
                borderDash: [5, 5],
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom', labels: { usePointStyle: true, boxWidth: 8 } }
            }
        }
    });
}
