Delivery Tracking BOT : รุ่นส่งอีเมลผ่าน Gmail (ไม่ต้องมี Outlook) / ใช้กับ Excel 2013
รุ่น 2026.10.22  : calplan_bot.py p8g , modImportCalendar m-gmail , modDeliveryPlan y8b
(โฟลเดอร์นี้แยกจากของเดิม ไม่ทับไฟล์ชุดเดิม)

ต่างจากชุดเดิมตรงไหน
  - อีเมลแจ้งงานหาย : Macro เขียนเป็นไฟล์ในโฟลเดอร์ mail_outbox (ข้างไฟล์ Delivery Tracking.xlsm)
    แล้วบอต Python ส่งผ่าน Gmail (SMTP + App Password) ส่งเสร็จย้ายไปโฟลเดอร์ mail_sent (เก็บตาม keep_days)
    ส่งไม่สำเร็จ = ไฟล์ค้างใน mail_outbox แล้วส่งใหม่ในรอบถัดไป
  - รูปแบบเมล / ผู้รับ To-CC (ชีต Config : mail_enabled, mail_to, mail_cc) เหมือนเดิม
  - ส่วนอื่น (กติกา Client Name LNnn- / SAL, B1 = วันนี้ C1 = วันถัดไป, รัน 06:00-20:00 ทุก 60 นาที) เหมือนชุดล่าสุด

ติดตั้งบนเครื่อง Admin (Excel 2013)
  1) ติดตั้ง Python 3.10+ (ชนิด 32/64 บิตให้ตรงกับ Excel) แล้วรัน :
       pip install playwright pywin32 keyring
       python -m playwright install msedge   (หรือใช้ Chrome/Edge ที่มีในเครื่อง ตั้ง channel ใน config.ini)
  2) คัดลอกโฟลเดอร์ bot ไปไว้ เช่น C:\DeliveryGPS\plan-bot  แล้วแก้ workbook = ... ใน config.ini ให้ตรงที่เก็บไฟล์ Delivery Tracking.xlsm
  3) Excel 2013 : File > Options > Trust Center > Trust Center Settings > Macro Settings
       - เปิด "Trust access to the VBA project object model"
       - Import ไฟล์ excel\modDeliveryPlan.bas และ excel\modImportCalendar.bas ด้วย Alt+F11 > File > Import File (ไม่ใช่คัดลอกวาง)
         (ลบโมดูลเดิมออกก่อน ถ้ามี)
  4) ตั้งรหัสผ่าน (เก็บใน Windows Credential Manager) :
       python calplan_bot.py --setup-calplan     (ผู้ใช้เว็บ Calendar Plan)
       python calplan_bot.py --setup-password    (บัญชีบอท gpsbot)
       python calplan_bot.py --setup-mail        (Gmail + App Password)
  5) ทดสอบเมล : python calplan_bot.py --test-mail   (ควรได้เมลถึงตัวเอง)
  6) ทดสอบทั้งระบบ : python calplan_bot.py --show   แล้วค่อย python calplan_bot.py --install-task

ตั้ง Gmail App Password
  - บัญชี Gmail ต้องเปิด 2-Step Verification ก่อน
  - Google Account > Security > 2-Step Verification > App passwords > สร้างรหัส 16 ตัว (ใส่ตอน --setup-mail)
  - ถ้าเป็น Google Workspace ของบริษัท แอดมินต้องอนุญาต App Password / SMTP
  - เครื่องต้องออกพอร์ต 587 (หรือ 465 : แก้ smtp_port ใน config.ini) ได้
  - ใช้บัญชีกลางของระบบ ไม่ใช่บัญชีส่วนตัว

แก้ปัญหา
  - "Gmail ปฏิเสธรหัสผ่าน"        = ใช้รหัสผ่านปกติอยู่ ต้องเป็น App Password แล้ว --setup-mail ใหม่
  - "เชื่อมต่อ Gmail ไม่ได้"       = อินเทอร์เน็ต / Firewall บล็อกพอร์ต 587
  - อีเมลค้างใน mail_outbox        = ดู logs\ ของบอต แล้วสั่ง python calplan_bot.py --send-mail ส่งใหม่ทันที
  - ไม่มีเมลเลย แต่มี Notepad เตือน = ตรวจชีต Config : mail_enabled = Yes และมี mail_to
