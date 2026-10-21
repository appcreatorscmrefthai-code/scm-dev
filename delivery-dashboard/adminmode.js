/* โหมด Admin ของฟอร์มมือถือ (pickup / qa / road / road-gps) : เปิดด้วย ?task=รหัสงาน&admin=1 (ปุ่มใน Popup ของ Dashboard)
   ใช้เมื่อ QR หมดอายุ : เข้าสู่ระบบด้วยสิทธิ์ admin แล้วฟอร์มทำงานตามปกติ แต่ไม่ถูกจำกัดช่วงวันที่ / 24 ชม. (ตรวจที่ฐานข้อมูลด้วย is_admin) */
(function () {
  if (!SB.ON || new URLSearchParams(location.search).get('admin') !== '1') return;
  SB.adminMode = true;
  SB.tokenFn = async function () {
    const t = await Auth.token();
    if (!Auth.isAdmin()) { const e = new Error('โหมดนี้ใช้ได้เฉพาะสิทธิ์ Admin (บัญชีนี้ไม่ใช่ Admin)'); e.server = true; e.status = 403; throw e; }
    return t;
  };
  document.addEventListener('DOMContentLoaded', () => {
    const b = document.createElement('div');
    b.style.cssText = 'background:#7c2d12;color:#fff;text-align:center;padding:6px 10px;font-size:14px;font-weight:600';
    b.textContent = 'โหมด Admin · ไม่จำกัดช่วงวันที่/เวลาอัปโหลด · เวลาที่บันทึกคือเวลาปัจจุบัน';
    document.body.insertBefore(b, document.body.firstChild);
  });
})();
