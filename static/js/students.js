const form = document.getElementById('student-form');
if (form) {
 form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const message = document.getElementById('student-message');
  const data = Object.fromEntries(new FormData(form).entries());
  try {
   const res = await fetch('/api/students', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
   const body = await res.json();
   if (!res.ok) throw new Error(body.error || 'Could not add student.');
   message.textContent = body.message + ' Reloading…'; message.className = 'form-message success';
   setTimeout(()=>location.reload(), 650);
  } catch(err) { message.textContent = err.message; message.className = 'form-message error'; }
 });
}
const search = document.getElementById('student-search');
if (search) search.addEventListener('input', () => {
 document.querySelectorAll('#students-table tbody tr').forEach(row => row.hidden = !row.innerText.toLowerCase().includes(search.value.toLowerCase()));
});
