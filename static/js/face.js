const video = document.getElementById('camera');
const placeholder = document.getElementById('camera-placeholder');
const cameraMessage = document.getElementById('camera-message');
let stream = null;
document.getElementById('start-camera').addEventListener('click', async () => {
 try {
  stream = await navigator.mediaDevices.getUserMedia({video:true, audio:false});
  video.srcObject = stream; placeholder.hidden = true;
  document.getElementById('camera-status').textContent = 'Camera ready';
  cameraMessage.textContent = 'Camera started. This preview does not perform recognition yet.';
  document.getElementById('stop-camera').disabled = false;
 } catch(e) { cameraMessage.textContent = 'Could not access camera. Check browser permissions and use localhost.'; cameraMessage.className='form-message error'; }
});
document.getElementById('stop-camera').addEventListener('click', stopCamera);
function stopCamera(){ if(stream) stream.getTracks().forEach(t=>t.stop()); stream=null; video.srcObject=null; placeholder.hidden=false; document.getElementById('camera-status').textContent='Camera off'; document.getElementById('stop-camera').disabled=true; }
async function loadToday(){
 const body = document.getElementById('today-body');
 try {
  const res = await fetch('/api/attendance/today'); const rows = await res.json();
  body.innerHTML = rows.length ? rows.map(r=>`<tr><td><b>${escapeHtml(r.name)}</b></td><td>${escapeHtml(r.student_code)}</td><td>${r.time}</td><td>${escapeHtml(r.method)}</td><td><span class="status present">${r.status}</span></td></tr>`).join('') : '<tr><td colspan="5" class="empty">No records today.</td></tr>';
 } catch { body.innerHTML='<tr><td colspan="5">Could not load records.</td></tr>'; }
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
document.getElementById('refresh-attendance').addEventListener('click', loadToday);
document.getElementById('mark-attendance').addEventListener('click', async()=>{
 const id=document.getElementById('attendance-student').value, msg=document.getElementById('attendance-message');
 if(!id){msg.textContent='Please select a student first.';msg.className='form-message error';return;}
 try{
  const res=await fetch('/api/attendance',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({student_id:id,method:'Manual Demo'})});
  const data=await res.json(); if(!res.ok) throw new Error(data.error||'Unable to mark attendance.');
  msg.textContent=data.message+' Time: '+data.time;msg.className='form-message success';await loadToday();
 }catch(e){msg.textContent=e.message;msg.className='form-message error';}
});
loadToday();
