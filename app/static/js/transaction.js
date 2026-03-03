document.addEventListener('DOMContentLoaded', () => {
    // Set today's date as default in modal
    document.getElementById('txDate').valueAsDate = new Date();

    // Set default month filter to current month
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    document.getElementById('monthFilter').value = `${yyyy}-${mm}`;

    // Setup filter listeners
    ['monthFilter', 'categoryFilter', 'typeFilter'].forEach(id => {
        document.getElementById(id).addEventListener('change', () => loadTransactions());
    });

    loadTransactions();

    document.getElementById('txForm').addEventListener('submit', async (e) => {
        e.preventDefault();

        const txId = document.getElementById('txId').value;
        const type = document.getElementById('txType').value;
        const amount = document.getElementById('txAmount').value;
        const category = document.getElementById('txCategory').value;
        const date = document.getElementById('txDate').value;

        const payload = { type, amount, category, date };

        try {
            let url = '/api/transactions';
            let method = 'POST';

            if (txId) {
                url = `/api/transactions/${txId}`;
                method = 'PUT';
            }

            const res = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                showToast(txId ? 'Transaction updated successfully!' : 'Transaction added successfully!');
                closeTransactionModal();
                loadTransactions();
            } else {
                showToast('Failed to add transaction.', 'error');
            }
        } catch (err) {
            console.error(err);
            showToast('Network error.', 'error');
        }
    });
});

async function loadTransactions() {
    try {
        const month = document.getElementById('monthFilter').value;
        const category = document.getElementById('categoryFilter').value;
        const type = document.getElementById('typeFilter').value;

        const params = new URLSearchParams();
        if (month) params.append('month', month);
        if (category) params.append('category', category);
        if (type) params.append('type', type);

        const url = params.toString() ? `/api/transactions?${params.toString()}` : '/api/transactions';
        const res = await fetch(url);
        const data = await res.json();
        const tbody = document.getElementById('transactionTableBody');
        tbody.innerHTML = '';

        // Populate category dropdown dynamically
        const categoryFilter = document.getElementById('categoryFilter');
        const currentCategory = categoryFilter.value;
        const uniqueCategories = [...new Set((data.transactions || []).map(tx => tx.category))].sort();

        categoryFilter.innerHTML = '<option value="">All Categories</option>';
        uniqueCategories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            if (cat === currentCategory) option.selected = true;
            categoryFilter.appendChild(option);
        });

        const formatCurrency = (val) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

        if (data.transactions && data.transactions.length > 0) {
            data.transactions.forEach(tx => {
                const tr = document.createElement('tr');
                tr.className = "hover:bg-gray-50 transition-colors";

                const typeStyle = tx.type === 'income' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800';
                const amountClass = tx.type === 'income' ? 'text-fintech-green' : 'text-gray-900';
                const sign = tx.type === 'income' ? '+' : '-';

                tr.innerHTML = `
                    <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${tx.date}</td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center">
                            <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">${tx.category}</div>
                            </div>
                        </div>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap">
                        <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${typeStyle} capitalize">
                            ${tx.type}
                        </span>
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-sm font-medium ${amountClass}">
                        ${sign}${formatCurrency(tx.amount)}
                    </td>
                    <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button onclick='editTransaction(${JSON.stringify(tx).replace(/'/g, "&#39;")})' class="text-blue-600 hover:text-blue-900"><i class="fas fa-edit"></i></button>
                        <button onclick="deleteTransaction(${tx.id})" class="text-red-600 hover:text-red-900 ml-3"><i class="fas fa-trash"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `<tr><td colspan="5" class="px-6 py-8 text-center text-gray-500">No transactions found.</td></tr>`;
        }
    } catch (err) {
        console.error(err);
    }
}

async function deleteTransaction(id) {
    if (!confirm('Are you sure you want to delete this transaction?')) return;

    try {
        const res = await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
        if (res.ok) {
            showToast('Transaction deleted');
            loadTransactions();
        } else {
            showToast('Error deleting transaction', 'error');
        }
    } catch (err) {
        console.error(err);
    }
}

function openTransactionModal() {
    document.getElementById('txId').value = '';
    document.getElementById('txForm').reset();
    document.getElementById('txDate').valueAsDate = new Date();
    document.getElementById('modal-title').textContent = 'New Transaction';
    document.getElementById('txModal').classList.remove('hidden');
}

function editTransaction(tx) {
    document.getElementById('txId').value = tx.id;
    document.getElementById('txType').value = tx.type;
    document.getElementById('txAmount').value = tx.amount;
    document.getElementById('txCategory').value = tx.category;
    document.getElementById('txDate').value = tx.date;
    document.getElementById('modal-title').textContent = 'Edit Transaction';
    document.getElementById('txModal').classList.remove('hidden');
}

function closeTransactionModal() {
    document.getElementById('txModal').classList.add('hidden');
}
