const search = document.getElementById('report-search');
if (search) search.addEventListener('input', () => {
 document.querySelectorAll('#reports-table tbody tr').forEach(row => row.hidden = !row.innerText.toLowerCase().includes(search.value.toLowerCase()));
});
