/* หน้าตั้งค่าผู้ใช้ (users.html) : เฉพาะ admin  ใช้ฟังก์ชัน admin_users / admin_save_user / admin_create_user / admin_set_password (supabase/users_part.sql) */
(function () {
  const $ = id => document.getElementById(id);
  const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const DOMAIN = '@' + ((window.APP_CONFIG || {}).LOGIN_DOMAIN || 'scmdelivery.local');
  const loginName = e => String(e || '').endsWith(DOMAIN) ? String(e).slice(0, -DOMAIN.length) : String(e || '');
  const ROLES = [['', '— ไม่มีสิทธิ์ —'], ['viewer', 'ดูอย่างเดียว (viewer)'], ['edit', 'แก้ไขได้ (edit)'], ['admin', 'ผู้ดูแล (admin)']];
  const MON = ['ม.ค.', 'ก.พ.', 'มี.ค.', 'เม.ย.', 'พ.ค.', 'มิ.ย.', 'ก.ค.', 'ส.ค.', 'ก.ย.', 'ต.ค.', 'พ.ย.', 'ธ.ค.'];
  const fmt = iso => { const t = Date.parse(iso); if (isNaN(t)) return '-'; const d = new Date(t + 7 * 3600e3), p = n => String(n).padStart(2, '0'); return `${d.getUTCDate()} ${MON[d.getUTCMonth()]} ${d.getUTCFullYear()} ${p(d.getUTCHours())}:${p(d.getUTCMinutes())}`; };
  const say = (t, ok) => { $('msg').textContent = t || ''; $('msg').className = ok ? 'ok' : 'err'; clearTimeout(say.t); if (t && ok) say.t = setTimeout(() => say(''), 4000); };

  async function load() {
    const me = Auth.get() || {};
    $('usersBody').innerHTML = '<tr><td colspan="6" class="muted">กำลังโหลด…</td></tr>';
    try {
      const users = await Auth.rpc('admin_users');
      $('usersBody').innerHTML = (users || []).map(u => `
        <tr data-id="${esc(u.user_id)}">
          <td>${esc(loginName(u.email))}${u.user_id === me.uid ? ' (คุณ)' : ''}</td>
          <td><input type="text" class="uName" value="${esc(u.name)}"></td>
          <td><select class="uRole">${ROLES.map(([v, l]) => `<option value="${v}" ${u.role === v ? 'selected' : ''}>${l}</option>`).join('')}</select></td>
          <td style="text-align:center"><input type="checkbox" class="uActive" ${u.active || !u.role ? 'checked' : ''}></td>
          <td class="small muted">${esc(fmt(u.last_sign_in_at))}</td>
          <td style="white-space:nowrap"><button type="button" class="primary uSave">บันทึก</button> <button type="button" class="uPass">ตั้งรหัสผ่าน</button></td>
        </tr>`).join('') || '<tr><td colspan="6" class="muted">ไม่มีผู้ใช้</td></tr>';
      $('usersBody').querySelectorAll('tr[data-id]').forEach(tr => {
        const id = tr.dataset.id;
        tr.querySelector('.uSave').onclick = async e => {
          const b = e.target; b.disabled = true;
          try {
            await Auth.rpc('admin_save_user', { p_user: id, p_name: tr.querySelector('.uName').value.trim(), p_role: tr.querySelector('.uRole').value, p_active: tr.querySelector('.uActive').checked });
            say('บันทึกแล้ว', true);
          } catch (err) { say('บันทึกไม่สำเร็จ: ' + err.message, false); }
          b.disabled = false;
        };
        tr.querySelector('.uPass').onclick = async () => {
          const pw = prompt('รหัสผ่านใหม่ (อย่างน้อย 6 ตัว)');
          if (!pw) return;
          try { await Auth.rpc('admin_set_password', { p_user: id, p_password: pw }); say('ตั้งรหัสผ่านใหม่แล้ว', true); }
          catch (err) { say('ตั้งรหัสผ่านไม่สำเร็จ: ' + err.message, false); }
        };
      });
    } catch (err) {
      $('usersBody').innerHTML = `<tr><td colspan="6" class="err">โหลดรายชื่อไม่ได้: ${esc(err.message)}<br><span class="muted small">ถ้าขึ้นว่าไม่พบฟังก์ชัน ให้รัน supabase/users_part.sql ใน Supabase SQL Editor ก่อน</span></td></tr>`;
    }
  }

  $('newUserForm').addEventListener('submit', async e => {
    e.preventDefault();
    const btn = $('nuBtn'), m = $('nuMsg'); btn.disabled = true; m.textContent = '';
    try {
      const r = await Auth.rpc('admin_create_user', { p_login: $('nuLogin').value.trim(), p_password: $('nuPass').value, p_name: $('nuName').value.trim(), p_role: $('nuRole').value });
      m.className = 'ok'; m.textContent = `เพิ่มผู้ใช้แล้ว — เข้าสู่ระบบด้วย "${loginName(r.email)}" และรหัสผ่านที่ตั้งไว้`;
      $('newUserForm').reset(); load();
    } catch (err) { m.className = 'err'; m.textContent = 'เพิ่มผู้ใช้ไม่สำเร็จ: ' + err.message; }
    btn.disabled = false;
  });

  (async () => {
    if (!Auth.get()) await Auth.login();
    Auth.badge($('userBox'));
    if (!Auth.isAdmin()) { document.querySelector('main').innerHTML = '<section><b class="err">หน้านี้สำหรับ Admin เท่านั้น</b></section>'; return; }
    load();
  })();
})();
