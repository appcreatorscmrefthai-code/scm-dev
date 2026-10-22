บอตส่งแผนอัตโนมัติ  Calendar Plan -> Delivery Tracking   (รุ่น p8 / 2026.10.22)

ทำอะไร (อัตโนมัติ ทุกวัน 06:00-20:00 น. ทุก 60 นาที : แก้ได้ที่ run_from / run_to / every_min ใน config.ini)
 ช่วงวันที่งาน : ตั้ง 2 ค่าเสมอ
     Plan!B1 = วันที่ปัจจุบัน (วันที่รัน)
     Plan!C1 = วันพรุ่งนี้ ; ถ้ารันวันศุกร์ = C1 ไปถึงวันจันทร์
     ทุกขั้นตอน (ดึงแผน / เพิ่มงานใหม่ / แก้งานเดิม / ตรวจงานที่หาย) ทำตามช่วง B1-C1 เพราะวันปัจจุบันอาจมีงานเพิ่มหรือแก้รายละเอียด
 Client Name ที่ดึงมาไม่ครบ : LNnn- (เช่น LN26-) ต่อด้วยรหัส 10 ตัวใน Customer Code (LN26-SANYPO1285,SMIAPO1286) ; SAL ใช้ข้อความหลัง ✅ ใน Detail (SALลูกค้า ...)
 1. เปิดเว็บ calendar-plan.scmref-thai.com (เข้าสู่ระบบให้เอง) > ปุ่ม ⌄ ข้าง IN/OUT > พิมพ์ช่วงวันที่ตามข้างบน > ค้นหา > ดาวน์โหลด export-tasks
    เก็บไฟล์ในโฟลเดอร์เดียวกับไฟล์ Delivery Tracking ชื่อ export-tasks_ปปปปดดวว_ชชนนวว.xlsx (เก็บ 30 วัน)
 2. เปิดไฟล์ Delivery Tracking.xlsm แล้วรัน Macro DP_AutoRun (ไม่มีหน้าต่างให้กด) :
      - ดึงงานล่าสุดจากระบบลง Plan_Backup (ใช้กันงานซ้ำ)
      - ใส่ช่วงวันที่ที่ Plan!B1-C1 > ดึงแผน : ไฟล์ export-tasks จากข้อ 1 + ใบจองรถ 1Template_TB ล่าสุดตามชีต Config
      - คอลัมน์ E = Type จาก export-tasks (oversea = งานต่างประเทศ / domestic = ในประเทศ)
      - เพิ่มเฉพาะงานที่ยังไม่มี (เทียบ วันที่ + Client Name + Schedule + Detail กับชีต Plan และ Plan_Backup)
        รันซ้ำได้ ไม่เพิ่มงานซ้ำ
      - งานที่มีอยู่แล้ว (จับคู่ด้วย Client Name ตัด Rev.nn) : ตรวจข้อมูลต้นทางที่ User เพิ่งกรอกเพิ่ม/แก้ไข (วันที่ Detail Type Transport Schedule
        Arrival Time ข้อมูลใบจองรถ ทะเบียน ผู้ขับ จุดส่ง ฯลฯ) แล้วส่งอัปเดตเฉพาะช่องที่เปลี่ยนไปแก้งานเดิมที่เว็บ (บันทึกใน Edit_Log ช่องทาง Excel (Macro))
          * ต้นทาง (Calendar Plan / ใบจองรถ) เป็นตัวหลัก : ช่องไหนต่างจากบนเว็บ ส่งค่าต้นทางไปแก้ รวมถึงลบข้อความในต้นทางจนว่าง = ล้างช่องบนเว็บด้วย
          * สิ่งที่แก้บนเว็บเอง (Popup) จะถูกทับด้วยค่าต้นทางในรอบถัดไป : ให้ User แก้ที่ Calendar Plan / ใบจองรถเท่านั้น
          * ข้อยกเว้น : หาใบจองรถของงานนั้นไม่พบ (ช่อง K-Y ว่างทั้งหมด) = ไม่ล้างช่อง K-Y บนเว็บ
          * งานที่ถูกยกเลิกแล้วแก้ไม่ได้ / งานที่ยังไม่ได้ส่งขึ้นเว็บยังไม่อัปเดต
      - ตรวจงานที่เคยส่งขึ้น Delivery Tracking แล้วแต่ "ไม่มีใน Calendar Plan" ช่วงวันที่นั้นแล้ว (คีย์ = Client Name ตัด Rev.nn ; ไม่ตรวจงานที่ยกเลิกแล้ว)
        พบ : เปิด Notepad ค้างไว้ (ไฟล์ Delivery_Tracking_MissingJobs.txt ข้างไฟล์ Excel) พร้อมรายละเอียดงาน + ส่งอีเมลต่อ 1 งาน
        หัวเรื่อง "ไม่มีงาน <Client Name> - <Task Code> นี้ใน Calendar Plan แล้ว" (ใช้ Outlook Classic ในเครื่อง)
        ผู้รับตั้งที่ชีต Config ในไฟล์ Delivery Tracking.xlsm : mail_to (To) / mail_cc (CC) / mail_enabled (Yes/No) คั่นหลายคนด้วย ;
        แจ้งทุกครั้งที่บอตรัน (Notepad + อีเมล) จนกว่า Admin จะลบงานออกจากแผน (ประวัติในชีตซ่อน Missing_Notified)
        ถ้า Calendar Plan ไม่มีงานเลยในช่วงวันที่นั้น บอตก็ยังรัน Macro เพื่อตรวจข้อนี้
      - ส่งงานใหม่ขึ้นระบบ (เหมือนกดปุ่ม ส่งงานใหม่) แล้วบันทึกผล 1 แถวในชีต Auto_Log และ Save ไฟล์
 3. Log : Delivery_Tracking_AutoImport.log ในโฟลเดอร์เดียวกับไฟล์ Delivery Tracking
          + logs\calplan.log / logs\STATUS.txt ในโฟลเดอร์บอต (ผิดพลาดมีภาพหน้าจอใน logs)

ติดตั้ง (ครั้งเดียว)
 1. วางโฟลเดอร์นี้ที่ C:\DeliveryGPS\plan-bot  (ห้ามอยู่ใน OneDrive/SharePoint)
 2. PowerShell ในโฟลเดอร์นี้ :   pip install playwright keyring pywin32
    (เครื่องที่ติดตั้งบอต GPS แล้วมี playwright / keyring อยู่แล้ว ; ใช้ Microsoft Edge ในเครื่อง ไม่ต้องโหลดเบราว์เซอร์เพิ่ม)
 3. Excel : Import โมดูลใหม่ 2 ไฟล์จาก scm-dev\delivery-dashboard\excel เข้า Delivery Tracking.xlsm
      modDeliveryPlan.bas (y8) + modImportCalendar.bas (k)  (Alt+F11 > Remove ตัวเดิม > File > Import > Save)
    แล้วรัน Macro DP_SetupConfig 1 ครั้ง (Alt+F8) ตรวจชีต Config :
      export_folder = Downloads ของเครื่อง (ใช้ตอนกดปุ่มดึงแผนเอง ; บอตส่งชื่อไฟล์ให้เอง)
      tb_folder     = ...\Sales Domestic - เอกสาร\4.Transport Booking Confirmation(TB)
 4. แก้ config.ini ช่อง workbook = path เต็มของไฟล์ Delivery Tracking.xlsm
 5. python calplan_bot.py --setup-calplan     (ชื่อผู้ใช้/รหัสผ่านเว็บ Calendar Plan เก็บใน Windows Credential Manager)
    ถ้าเครื่องนี้ยังไม่เคยตั้งรหัสบัญชีบอท gpsbot :  python calplan_bot.py --setup-password
 6. ทดสอบ :  python calplan_bot.py --download-only --show   (เห็นหน้าต่างเว็บ ต้องได้ไฟล์ export-tasks_... ในโฟลเดอร์ไฟล์ Excel)
             python calplan_bot.py                          (ทำครบ 1 รอบ แล้วดูชีต Auto_Log + log)
 7. python calplan_bot.py --install-task     (Task "Delivery Tracking Plan Import" ทุกวัน 06:00-20:00 ทุก 60 นาที ตาม config.ini ; แก้เวลาแล้วรันซ้ำเพื่อเปลี่ยน)

คำสั่งอื่น
 python calplan_bot.py --status                 ดูสถานะล่าสุด
 python calplan_bot.py --as-of 2026-10-16      ทดสอบกติกาวันที่ : คิดเหมือนรันวันนั้น (ศุกร์ 16 = B1 16, C1 19)
 python calplan_bot.py --date 2026-10-17 --end 2026-10-19   กำหนดช่วงวันที่งานเอง
 python calplan_bot.py --excel-only ไฟล์.xlsx    ข้ามเว็บ ใช้ไฟล์ export-tasks ที่มีอยู่
 python calplan_bot.py --login                  เข้าสู่ระบบเว็บเองในหน้าต่างของบอต (ใช้เมื่อเว็บถามยืนยันตัวตน)
 python calplan_bot.py --uninstall-task         ลบ Task

ข้อควรทราบ
 - Excel : ถ้าไฟล์ไม่ได้เปิดอยู่ บอตเปิด Excel ตัวใหม่ (ซ่อน) รัน Macro แล้วปิดไฟล์ + Quit + รอจนโปรเซสหายทุกรอบ ; ถ้ารอบก่อนปิดไม่สนิท รอบถัดไปปิดตัวที่ค้างให้ก่อน (จำ PID ใน excel_bot.pid)
   Excel ที่ User เปิดไฟล์ค้างไว้เอง บอตใช้รันแล้วไม่ปิดให้
 - เว็บ Calendar Plan ใช้ reCAPTCHA แบบมองไม่เห็น : บอตเปิดหน้าต่าง Edge ให้เห็นระหว่างทำงาน (headless = false)
   บอตไม่แก้ reCAPTCHA เอง ถ้าเว็บถามยืนยัน บอตจะหยุดและแจ้งใน log ให้รัน --login แล้วเข้าสู่ระบบเอง 1 ครั้ง
   การเข้าสู่ระบบถูกจำไว้ในโฟลเดอร์ profile ของบอต รอบต่อไปไม่ต้องเข้าสู่ระบบใหม่
 - ไฟล์ Delivery Tracking เปิดค้างอยู่ใน Excel : บอตรันในไฟล์ที่เปิดอยู่แล้ว Save ให้ (ถ้ากำลังแก้เซลล์อยู่ บอตรอแล้วลองใหม่)
   ไฟล์ถูกล็อก/อ่านอย่างเดียว : บอตไม่รัน (กันงานซ้ำ) และแจ้งใน log
 - งานที่บอตส่ง ผู้ส่งบนระบบเป็นบัญชีบอท gpsbot
 - เครื่องปิด/หลับตอนถึงเวลารอบนั้น : ข้ามรอบนั้น (รอบถัดไปของวันทำงานต่อ) ไม่รันย้อนหลัง  /  กด Run เองใน Task Scheduler = รันทุกขั้นตอนทันที ไม่เช็กเวลา (ต้องรัน --install-task ใหม่หลังอัปเดตรุ่น)
 - ไม่มีงานในช่วงวันที่บนเว็บ : จบรอบโดยไม่เปิด Excel
 - ตั้งช่วงวันที่บนเว็บไม่ได้ (ช่องวันที่ไม่ตรง) : บอตหยุด ไม่โหลดไฟล์ผิดช่วง มีภาพหน้าจอ date_range ใน logs
 - Excel ถูกสั่งงานผ่าน COM (pywin32) : SentinelOne อาจแจ้งเตือนครั้งแรก ให้ขอ IT อนุญาตโฟลเดอร์นี้ ; ไม่มีไฟล์ .bat ไม่ซ่อนโปรเซส
 - กดปุ่ม "ดึงแผนจาก Calendar" เองใน Excel ก็ไม่ต้องเลือกไฟล์แล้ว : หยิบ export-tasks ล่าสุดใน Downloads + 1Template_TB ตามชีต Config
   (ต้องการเลือกเองทุกครั้ง ใส่ Yes ที่ ask_file ในชีต Config)
