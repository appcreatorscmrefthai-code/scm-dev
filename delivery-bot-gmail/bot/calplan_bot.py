# -*- coding: utf-8 -*-
"""
calplan_bot.py  รุ่น 2026.10.22-p8g  (p8g : ส่งอีเมลแจ้งงานหายผ่าน Gmail (SMTP + App Password) แทน Outlook ใช้กับเครื่องที่ไม่มี Outlook / Excel 2013 ;  p8 : ตั้งวันที่ 2 ค่าเสมอ B1 = วันนี้ / C1 = วันถัดไป (ศุกร์ = ถึงวันจันทร์) แล้วเพิ่ม/แก้งานตามช่วงนี้ ; รันทุกวัน 06:00-20:00 ทุก 60 นาที ;  p7 : ปิด Excel ที่บอตเปิดเองให้สนิททุกรอบ (ปิดไฟล์ + Quit + รอจนโปรเซสหาย / เก็บกวาดตัวที่ค้างจากรอบก่อน) ;  p6 : รันทุกวัน 14:00-20:00 ทุก 30 นาที (run_from / run_to / every_min) + ตรวจงานที่เคยส่งแต่ไม่มีใน Calendar Plan แล้ว (Notepad + อีเมล) ;  p5 : รันได้หลายเวลาต่อวัน + งานเดิมที่ข้อมูลเปลี่ยน/เพิ่งกรอกครบ Macro ส่งอัปเดตให้ (ยึด Client Name) ;  p4 : กดรัน Task Scheduler เองได้ทุกขั้นตอน ไม่เช็กช่วงเวลา / ไม่รันย้อนหลังเมื่อเปิดเครื่อง ;  p3 : ดึงงานพรุ่งนี้เสมอ / ศุกร์ = เสาร์-จันทร์ / เสาร์ = อาทิตย์-จันทร์ / ตั้งช่วงวันที่บนเว็บทุกครั้ง / 15:00 น.)
ส่งแผนงานขึ้นระบบ Delivery Tracking อัตโนมัติ (ทุกวัน 06:00-20:00 ทุก 60 นาที ตาม config.ini ผ่าน Task Scheduler)

ช่วงวันที่งาน (ใส่ Plan!B1 - C1 และตั้งในหน้าค้นหาของเว็บ) : ตั้ง 2 ค่าเสมอ
  B1 = วันที่ปัจจุบัน (วันที่รัน)
  C1 = วันพรุ่งนี้ ; ถ้าวันที่รันเป็นวันศุกร์ (หรือพรุ่งนี้ตรงกับเสาร์-อาทิตย์) = C1 ไปถึงวันจันทร์
  ทุกขั้นตอน (ดึงแผน เพิ่มงานใหม่ แก้งานเดิม ตรวจงานที่หายไป) ทำตามช่วง B1-C1 นี้ เพราะวันปัจจุบันอาจมีงานเพิ่มหรือแก้รายละเอียด

ขั้นตอน
  1) เปิดเว็บ Calendar Plan (calendar-plan.scmref-thai.com) -> ปุ่มค้นหาขั้นสูง (⌄) -> ค้นหา -> ดาวน์โหลด export-tasks
     บันทึกไฟล์ไว้ในโฟลเดอร์เดียวกับไฟล์ Delivery Tracking ชื่อ export-tasks_ปปปปดดวว_ชชนนวว.xlsx
  2) เปิดไฟล์ Delivery Tracking.xlsm แล้วรัน Macro DP_AutoRun :
     ใส่ช่วงวันที่ที่ Plan!B1-C1 > ดึงแผน (ใช้ไฟล์ข้อ 1 + ใบจองรถ 1Template_TB ตามชีต Config ไม่ต้องเลือกไฟล์)
     > เพิ่มเฉพาะงานที่ยังไม่มี > ส่งงานใหม่ขึ้นระบบ > งานที่มีอยู่แล้ว (จับคู่ด้วย Client Name) ถ้าข้อมูลต้นทางเปลี่ยน/เพิ่งกรอกครบ
     ส่งอัปเดตเฉพาะช่องที่เปลี่ยนไปแก้ที่เว็บ (ไม่ทับสิ่งที่แก้บนเว็บเองถ้าต้นทางไม่ได้เปลี่ยน) > บันทึกผลในชีต Auto_Log > Save ไฟล์
  3) Log : Delivery_Tracking_AutoImport.log ในโฟลเดอร์เดียวกับไฟล์ Delivery Tracking (+ logs\\ ของบอต)

คำสั่ง (ดู README.txt)
  python calplan_bot.py --setup-calplan     ตั้งชื่อผู้ใช้/รหัสผ่านเว็บ Calendar Plan (เก็บใน Windows Credential Manager)
  python calplan_bot.py --setup-password    ตั้งรหัสผ่านบัญชีบอท gpsbot (ถ้าเครื่องนี้ตั้งไว้แล้วสำหรับบอต GPS ข้ามได้)
  python calplan_bot.py --login             เปิดเบราว์เซอร์ให้เข้าสู่ระบบ Calendar Plan ด้วยมือ (จำไว้ในโปรไฟล์ของบอต)
  python calplan_bot.py --download-only     ทดสอบขั้นที่ 1 อย่างเดียว (ไม่เปิด Excel)
  python calplan_bot.py --excel-only ไฟล์    ทดสอบขั้นที่ 2 ด้วยไฟล์ export-tasks ที่มีอยู่
  python calplan_bot.py                     ทำครบทุกขั้นทันที 1 รอบ (ช่วงวันที่ตามกติกาข้างบน นับจากวันนี้)
      --as-of ปปปป-ดด-วว                    คิดช่วงวันที่เหมือนรันในวันนั้น (เช่น ทดสอบกติกาวันศุกร์)
      --date ปปปป-ดด-วว [--end ปปปป-ดด-วว]  กำหนดช่วงวันที่งานเอง
  python calplan_bot.py --setup-mail         ตั้งอีเมล Gmail + App Password สำหรับส่งอีเมลแจ้งงานหาย (เก็บใน Windows Credential Manager)
  python calplan_bot.py --test-mail          ส่งอีเมลทดสอบถึงตัวเอง
  python calplan_bot.py --send-mail          ส่งอีเมลที่ค้างในโฟลเดอร์ mail_outbox ทันที
  python calplan_bot.py --install-task      สร้าง Task Scheduler : ทุกวัน ตั้งต้น 06:00-20:00 ทุก 60 นาที (ตาม run_from / run_to / every_min)
  python calplan_bot.py --uninstall-task    ลบ Task Scheduler
  python calplan_bot.py --status            ดูสถานะล่าสุด

ความปลอดภัย : ไม่มีรหัสผ่านในไฟล์ใดๆ (เก็บใน Windows Credential Manager) ; ใช้เฉพาะ Publishable key + บัญชีบอทสิทธิ์ edit
ใช้เฉพาะ Playwright / pywin32 / schtasks ไม่ซ่อนโปรเซส ไม่เรียก WinAPI เอง ไม่ใช้ไฟล์ .bat
ไม่แก้หรือข้าม reCAPTCHA : ถ้าเว็บถามยืนยันตัวตน บอตหยุดและแจ้งให้เข้าสู่ระบบเองด้วย --login
"""
import sys

if sys.version_info < (3, 10):
    print("ต้องใช้ Python 3.10 ขึ้นไป"); sys.exit(2)

import argparse, configparser, datetime as dt, json, logging, os, re, subprocess, tempfile, threading, time, traceback
import urllib.error, urllib.request
import smtplib, ssl, shutil
from email.message import EmailMessage
from email.utils import formataddr
from logging.handlers import RotatingFileHandler
from pathlib import Path
from xml.sax.saxutils import escape as xesc

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

VERSION = "2026.10.22-p8g"
DEFAULT_FROM, DEFAULT_TO, DEFAULT_EVERY = "06:00", "20:00", 60
HERE = Path(__file__).resolve().parent
os.chdir(HERE)
(HERE / "logs").mkdir(exist_ok=True)
TASK_NAME = "Delivery Tracking Plan Import"
BKK = dt.timezone(dt.timedelta(hours=7))
KR_CAL = "DeliveryPlanBot-CALPLAN"         # Windows Credential Manager : ชื่อผู้ใช้/รหัสผ่านเว็บ Calendar Plan
KR_MAIL = "DeliveryPlanBot-GMAIL"           # Gmail ที่ใช้ส่งอีเมลแจ้งงานหาย (ที่อยู่อีเมล + App Password)
KR_BOT = "DeliveryPlanBot"                 # บัญชีบอท gpsbot (ใช้ร่วมกับบอต GPS / Backup)
LOG_NAME = "Delivery_Tracking_AutoImport.log"

EXIT_CONFIG, EXIT_LOGIN, EXIT_EXPORT, EXIT_EXCEL, EXIT_BUSY, EXIT_TIMEOUT, EXIT_CRASH, EXIT_WARN, EXIT_SKIP = 2, 3, 4, 5, 6, 7, 8, 9, 10
EXIT_TEXT = {0: "สำเร็จ", 2: "ตั้งค่าไม่ครบ", 3: "เข้าสู่ระบบเว็บ Calendar Plan ไม่ได้", 4: "ดาวน์โหลด export-tasks ไม่ได้",
             5: "รัน Macro ใน Excel ไม่สำเร็จ", 6: "มีรอบก่อนหน้าค้างอยู่", 7: "ทำงานนานเกินกำหนด", 8: "เกิดข้อผิดพลาดที่ไม่คาดคิด",
             9: "ดึงแผนได้ แต่ส่งงานขึ้นระบบไม่สำเร็จ", 10: "ข้ามรอบ (นอกเวลาที่กำหนด)"}


class _Last(logging.Handler):
    msg = ""

    def emit(self, r):
        if r.levelno >= logging.ERROR:
            _Last.msg = r.getMessage()


log = logging.getLogger("calplan")
log.setLevel(logging.INFO)
_fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
_h = RotatingFileHandler(HERE / "logs" / "calplan.log", maxBytes=500_000, backupCount=3, encoding="utf-8")
_h.setFormatter(_fmt)
log.addHandler(_h)
log.addHandler(_Last())
if sys.stdout and sys.stdout.isatty():
    log.addHandler(logging.StreamHandler(sys.stdout))


def add_book_log(folder):
    """Log ชุดที่สองในโฟลเดอร์เดียวกับไฟล์ Delivery Tracking"""
    try:
        h = RotatingFileHandler(Path(folder) / LOG_NAME, maxBytes=1_000_000, backupCount=5, encoding="utf-8")
        h.setFormatter(_fmt)
        log.addHandler(h)
    except OSError as e:
        log.warning("เขียน log ในโฟลเดอร์ไฟล์ Excel ไม่ได้ (%s) : ใช้ logs\\calplan.log อย่างเดียว", e)


def now_bkk():
    return dt.datetime.now(BKK)


def cfg():
    c = configparser.ConfigParser(interpolation=None)
    if not c.read(HERE / "config.ini", encoding="utf-8"):
        log.error("ไม่พบ config.ini"); sys.exit(EXIT_CONFIG)
    for s in ("calendar", "excel", "supabase", "mail"):
        if s not in c:
            c[s] = {}
    return c


def book_path(c):
    p = c["excel"].get("workbook", "").strip().strip('"')
    if not p:
        log.error("ยังไม่ได้ใส่ path ไฟล์ Delivery Tracking.xlsm ในช่อง workbook ของ config.ini"); sys.exit(EXIT_CONFIG)
    p = Path(os.path.expandvars(os.path.expanduser(p)))
    if not p.exists():
        log.error("ไม่พบไฟล์ Excel ตามที่ตั้งไว้ (workbook ใน config.ini) : %s", p); sys.exit(EXIT_CONFIG)
    if p.is_dir():                                      # ใส่เป็นโฟลเดอร์ : ใช้ไฟล์ .xlsm ไฟล์เดียวในโฟลเดอร์นั้น
        xs = [f for f in p.glob("*.xlsm") if not f.name.startswith("~$")]
        if len(xs) != 1:
            log.error("ช่อง workbook ใน config.ini เป็นโฟลเดอร์ และพบไฟล์ .xlsm %d ไฟล์ : ใส่ path เต็มของไฟล์ เช่น %s", len(xs), p / "Delivery Tracking.xlsm")
            sys.exit(EXIT_CONFIG)
        p = xs[0]
    return p


# ---------------------------------------------------------------- สถานะ
def load_state():
    try:
        return json.loads((HERE / "state.json").read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_state(s):
    try:
        tmp = HERE / "state.json.tmp"
        tmp.write_text(json.dumps(s, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(tmp, HERE / "state.json")
    except OSError:
        pass


def write_status(code, extra=""):
    s = load_state()
    lines = [f"บอตส่งแผนอัตโนมัติ (Calendar Plan -> Delivery Tracking) รุ่น {VERSION}",
             f"รอบล่าสุด : {now_bkk():%Y-%m-%d %H:%M:%S} (เวลาไทย)",
             f"ผลล่าสุด  : {EXIT_TEXT.get(code, code)}" + (f" -- {_Last.msg}" if code not in (0, EXIT_SKIP) and _Last.msg else ""),
             f"สำเร็จล่าสุด : {s.get('last_ok', '-')}",
             f"ผลจาก Macro ล่าสุด : {s.get('last_macro', '-')}"]
    if extra:
        lines.append(extra)
    try:
        (HERE / "logs" / "STATUS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError:
        pass


def lock():
    p = HERE / "calplan.lock"
    try:
        if p.exists() and time.time() - p.stat().st_mtime < 45 * 60:
            log.warning("มีรอบก่อนหน้ายังทำงานอยู่ ข้ามรอบนี้"); sys.exit(EXIT_BUSY)
        p.write_text(str(os.getpid()))
    except OSError as e:
        log.warning("เขียนไฟล์ล็อกไม่ได้ (%s) ทำงานต่อ", e)
    return p


# ---------------------------------------------------------------- รหัสผ่าน (Windows Credential Manager)
def kr_get(service, user):
    try:
        import keyring
        return keyring.get_password(service, user) or ""
    except ImportError:
        log.error("ยังไม่ได้ติดตั้ง keyring : pip install keyring"); sys.exit(EXIT_CONFIG)


def cal_credentials(c):
    u = c["calendar"].get("username", "").strip() or kr_get(KR_CAL, "__username__")
    p = kr_get(KR_CAL, u) if u else ""
    return u, p


# ---------------------------------------------------------------- อีเมลผ่าน Gmail (Macro เขียนไฟล์ไว้ที่ mail_outbox แล้วบอตส่ง)
def _mail_creds(c):
    addr = c["mail"].get("gmail_address", "").strip() or kr_get(KR_MAIL, "__address__")
    pw = os.environ.get("DELIVERY_MAIL_PASSWORD", "") or (kr_get(KR_MAIL, addr) if addr else "")
    return addr, pw.replace(" ", "")


def _smtp_open(c, addr, pw):
    host = c["mail"].get("smtp_host", "smtp.gmail.com").strip() or "smtp.gmail.com"
    port = int(c["mail"].get("smtp_port", "587").strip() or 587)
    ctx = ssl.create_default_context()
    if port == 465:
        s = smtplib.SMTP_SSL(host, port, timeout=60, context=ctx)
    else:
        s = smtplib.SMTP(host, port, timeout=60)
        s.ehlo(); s.starttls(context=ctx); s.ehlo()
    s.login(addr, pw)
    return s


def _read_mail_file(f):
    raw = f.read_bytes()
    txt = raw.decode("utf-16") if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else raw.decode("utf-8-sig")
    head, _, body = txt.replace("\r\n", "\n").partition("\n\n")
    h = {}
    for ln in head.split("\n"):
        k, _, v = ln.partition(":")
        h[k.strip().lower()] = v.strip()
    return h.get("to", ""), h.get("cc", ""), h.get("subject", "(ไม่มีหัวเรื่อง)"), body


def _make_message(c, addr, to, cc, subj, html):
    m = EmailMessage()
    m["From"] = formataddr((c["mail"].get("from_name", "Delivery Tracking BOT"), addr))
    m["To"] = to.replace(";", ",")
    if cc:
        m["Cc"] = cc.replace(";", ",")
    m["Subject"] = subj
    plain = re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>|</p>", "\n", html))
    m.set_content(plain.replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip())
    m.add_alternative(html, subtype="html")
    return m


def send_outbox(c, folder):
    """ส่งไฟล์ในโฟลเดอร์ mail_outbox (ข้างไฟล์ Excel) ผ่าน Gmail แล้วย้ายไป mail_sent ; ส่งไม่สำเร็จเก็บไว้ส่งรอบหน้า"""
    out = Path(folder) / "mail_outbox"
    files = sorted(out.glob("*.txt")) if out.is_dir() else []
    if not files:
        return 0, 0
    addr, pw = _mail_creds(c)
    if not addr or not pw:
        log.error("มีอีเมลรอส่ง %d ฉบับ แต่ยังไม่ได้ตั้งอีเมล Gmail : python calplan_bot.py --setup-mail", len(files))
        return 0, len(files)
    sent_dir = Path(folder) / "mail_sent"; sent_dir.mkdir(exist_ok=True)
    ok = bad = 0
    try:
        s = _smtp_open(c, addr, pw)
    except smtplib.SMTPAuthenticationError:
        log.error("Gmail ปฏิเสธรหัสผ่าน : ต้องใช้ App Password 16 ตัว (ไม่ใช่รหัสผ่านปกติ) แล้วตั้งใหม่ด้วย --setup-mail")
        return 0, len(files)
    except Exception as e:
        log.error("เชื่อมต่อ Gmail ไม่ได้ (%s) : ตรวจอินเทอร์เน็ต / Firewall พอร์ต %s", str(e)[:200], c["mail"].get("smtp_port", "587"))
        return 0, len(files)
    with s:
        for f in files:
            try:
                to, cc, subj, html = _read_mail_file(f)
                if not to:
                    raise ValueError("ไม่มีผู้รับ (ตรวจ mail_to ในชีต Config)")
                s.send_message(_make_message(c, addr, to, cc, subj, html))
                shutil.move(str(f), str(sent_dir / f.name)); ok += 1
            except Exception as e:
                bad += 1; log.error("ส่งอีเมล %s ไม่สำเร็จ : %s", f.name, str(e)[:200])
    log.info("ส่งอีเมลแจ้งงานหายผ่าน Gmail : สำเร็จ %d ฉบับ / ไม่สำเร็จ %d ฉบับ", ok, bad)
    try:
        days = int(c["excel"].get("keep_days", "30")); lim = time.time() - days * 86400
        for f in sent_dir.glob("*.txt"):
            if f.stat().st_mtime < lim:
                f.unlink()
    except Exception:
        pass
    return ok, bad


def setup_mail(c):
    import getpass, keyring
    addr = input("อีเมล Gmail ที่ใช้ส่ง (เช่น scm.bot@gmail.com): ").strip()
    keyring.set_password(KR_MAIL, "__address__", addr)
    keyring.set_password(KR_MAIL, addr, getpass.getpass("App Password 16 ตัว (พิมพ์แล้วไม่แสดงบนจอ): ").replace(" ", ""))
    print("เก็บใน Windows Credential Manager แล้ว  ทดสอบ: python calplan_bot.py --test-mail")
    return 0


def test_mail(c):
    addr, pw = _mail_creds(c)
    if not addr or not pw:
        print("ยังไม่ได้ตั้งอีเมล : python calplan_bot.py --setup-mail"); return EXIT_CONFIG
    try:
        with _smtp_open(c, addr, pw) as s:
            s.send_message(_make_message(c, addr, addr, "", "ทดสอบอีเมลจากบอต Delivery Tracking",
                                         "<p style='font-family:Tahoma;font-size:14pt'>ทดสอบส่งอีเมลผ่าน Gmail สำเร็จ</p>"))
    except Exception as e:
        print("ส่งไม่สำเร็จ :", str(e)[:300]); return EXIT_CONFIG
    print("ส่งอีเมลทดสอบถึง", addr, "แล้ว"); return 0


# ---------------------------------------------------------------- Supabase (บัญชีบอท gpsbot)
class HttpErr(RuntimeError):
    def __init__(self, code, body):
        super().__init__(f"HTTP {code}: {body}")
        self.code = code


def sb_token(c):
    base = c["supabase"].get("url", "").rstrip("/"); key = c["supabase"].get("key", "")
    user = c["supabase"].get("user", "gpsbot").strip().lower()
    if "@" not in user:
        user += "@" + c["supabase"].get("login_domain", "scmdelivery.local")
    pw = os.environ.get("DELIVERY_BOT_PASSWORD", "") or kr_get(KR_BOT, c["supabase"].get("user", "gpsbot").strip())
    if not pw:
        log.error("ยังไม่ได้ตั้งรหัสผ่านบัญชีบอท : python calplan_bot.py --setup-password"); sys.exit(EXIT_CONFIG)
    req = urllib.request.Request(base + "/auth/v1/token?grant_type=password", data=json.dumps({"email": user, "password": pw}).encode(),
                                 headers={"apikey": key, "Content-Type": "application/json"}, method="POST")
    last = None
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode("utf-8"))["access_token"]
        except urllib.error.HTTPError as e:
            raise HttpErr(e.code, e.read().decode("utf-8", "replace")[:200])
        except (urllib.error.URLError, OSError) as e:
            last = e
            time.sleep(5 * (i + 1))
    raise last


def bot_ping(c, tok):
    """บันทึกเวลารอบที่บอตทำงานไว้ที่ Supabase (Dashboard แสดง 'อัปเดตแผนล่าสุดเมื่อ') แม้ข้อมูลไม่เปลี่ยน"""
    try:
        base = c["supabase"].get("url", "").rstrip("/")
        req = urllib.request.Request(base + "/rest/v1/rpc/bot_ping", data=b"{}", method="POST",
                                     headers={"apikey": c["supabase"].get("key", ""), "Authorization": "Bearer " + tok, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            r.read()
    except Exception as e:
        log.warning("บันทึกเวลารอบบอตไม่สำเร็จ (รัน supabase/s25_part.sql แล้วหรือยัง) : %s", str(e)[:150])


# ---------------------------------------------------------------- ขั้นที่ 1 : เว็บ Calendar Plan
class LoginNeeded(RuntimeError):
    pass


class NoRows(RuntimeError):
    pass


SEL_USER = 'input[placeholder="Username"]'
SEL_PASS = 'input[type="password"]'
SEL_LOGIN_BTN = 'button.btn-login'
SEL_QUICK = 'input[placeholder="Quick filter..."]'
SEL_FORM = 'form:has(input[placeholder="Quick filter..."])'
SEL_GROUP = SEL_FORM + ' div.btn-group:has(> button[type="submit"])'
# ปุ่ม ⌄ (ค้นหาขั้นสูง) อยู่ถัดจากปุ่ม IN / OUT บนแถบด้านบนของหน้าปฏิทิน
JS_OPEN_ADV = """() => {
  const outs = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'OUT' && !b.closest('.swal2-container, form'));
  for (const b of outs) {
    const nx = b.parentElement && b.parentElement.nextElementSibling;
    const a = nx && nx.querySelector('a[href="#"]');
    if (a) { a.click(); return true; }
  }
  return false;
}"""


def launch(pw, c, headless):
    kw = {"headless": headless, "accept_downloads": True, "viewport": {"width": 1500, "height": 900}, "locale": "th-TH", "timezone_id": "Asia/Bangkok"}
    exe = c["calendar"].get("chromium_path", "").strip()
    if exe:
        kw["executable_path"] = exe
    elif c["calendar"].get("channel", "").strip():
        kw["channel"] = c["calendar"]["channel"].strip()       # chrome / msedge = ใช้เบราว์เซอร์ที่ติดตั้งในเครื่อง
    return pw.chromium.launch_persistent_context(str(HERE / "profile"), **kw)


def shot(page, name):
    try:
        page.screenshot(path=str(HERE / "logs" / f"{name}_{now_bkk():%Y%m%d_%H%M%S}.png"), full_page=False)
    except Exception:
        pass


def challenge_visible(page):
    """reCAPTCHA แบบให้ผู้ใช้ทำ (เลือกรูป) โผล่ขึ้นมาไหม : บอตไม่แก้เอง"""
    try:
        return page.locator('iframe[src*="recaptcha"][src*="bframe"]:visible').count() > 0
    except Exception:
        return False


def ensure_login(page, c, base, tmo):
    page.goto(base + "/dashboard", wait_until="domcontentloaded", timeout=tmo)
    # รอให้หน้าเว็บตัดสินใจว่าเข้าสู่ระบบอยู่แล้ว (แสดงปฏิทิน) หรือต้องเข้าสู่ระบบ
    # หน้าเข้าสู่ระบบโผล่ขึ้นแวบหนึ่งก่อนเว็บโหลดการเข้าสู่ระบบเดิมเสร็จ : เห็นช่องรหัสผ่านติดกัน 8 วินาทีจึงถือว่าต้องเข้าสู่ระบบ
    end = time.time() + tmo / 1000
    seen = None
    while time.time() < end:
        if page.locator('button:text-is("OUT")').count() > 0:
            return False
        vis = False
        try:
            vis = page.locator(SEL_PASS).count() > 0 and page.locator(SEL_PASS).first.is_visible()
        except Exception:
            pass
        if vis:
            seen = seen or time.time()
            if time.time() - seen >= 8:
                break
        else:
            seen = None
        page.wait_for_timeout(500)
    else:
        raise RuntimeError("เปิดหน้าเว็บ Calendar Plan ไม่ขึ้น (หมดเวลา)")
    u, p = cal_credentials(c)
    if not (u and p):
        raise LoginNeeded("ยังไม่ได้ตั้งชื่อผู้ใช้/รหัสผ่านเว็บ Calendar Plan : python calplan_bot.py --setup-calplan (หรือ --login เพื่อเข้าสู่ระบบเอง)")
    log.info("เข้าสู่ระบบเว็บ Calendar Plan ด้วยผู้ใช้ %s", u)
    try:
        page.fill(SEL_USER, u, timeout=15000)
        page.fill(SEL_PASS, p, timeout=15000)
        page.click(SEL_LOGIN_BTN, timeout=15000)
    except Exception as e:
        if page.locator('button:text-is("OUT")').count() > 0:        # ระหว่างนั้นเว็บโหลดการเข้าสู่ระบบเดิมเสร็จแล้ว
            return False
        log.warning("กดเข้าสู่ระบบไม่สำเร็จ (%s) รอดูผลอีกครั้ง", str(e).splitlines()[0][:120])
    end = time.time() + 45
    while time.time() < end:
        if page.locator('button:text-is("OUT")').count() > 0:
            log.info("เข้าสู่ระบบสำเร็จ")
            return True
        if challenge_visible(page):
            shot(page, "login_challenge")
            raise LoginNeeded("เว็บขอยืนยันตัวตน (reCAPTCHA) : เปิด PowerShell แล้วรัน python calplan_bot.py --login เพื่อเข้าสู่ระบบเองครั้งหนึ่ง")
        page.wait_for_timeout(500)
    shot(page, "login_failed")
    err = ""
    try:
        err = page.locator(".login-box").inner_text(timeout=2000)[-200:]
    except Exception:
        pass
    raise LoginNeeded("เข้าสู่ระบบไม่สำเร็จ (ตรวจชื่อผู้ใช้/รหัสผ่านด้วย --setup-calplan หรือเข้าสู่ระบบเองด้วย --login) " + err.replace("\n", " "))


def date_range_text(page):
    try:
        return f"{page.input_value('#search_start_date', timeout=2000)} - {page.input_value('#search_end_date', timeout=2000)}"
    except Exception:
        return "?"


def range_want(d1, d2):
    return f"{d1:%d/%m/%Y} - {d2:%d/%m/%Y}"


def set_range(page, d1, d2):
    """ตั้งช่วงวันที่ของหน้าค้นหาขั้นสูง (พิมพ์ DD/MM/YYYY ในช่องวันที่) ; คืน True ถ้าช่องวันที่ตรงตามที่ตั้ง"""
    want = range_want(d1, d2)
    for attempt in range(3):
        try:
            for sel, d in (("#search_start_date", d1), ("#search_end_date", d2)):
                el = page.locator(sel).first
                el.click(timeout=8000)
                page.wait_for_timeout(200)
                el.press("Control+a")
                el.press("Backspace")
                el.type(d.strftime("%d/%m/%Y"), delay=40 + attempt * 40)
                page.wait_for_timeout(400)
            page.keyboard.press("Escape")
            page.wait_for_timeout(300)
            if modal_open(page):
                page.locator(SEL_QUICK).first.click(timeout=5000)     # ออกจากช่องวันที่ (คลิกในหน้าต่างค้นหา ไม่ปิดหน้าต่าง)
            page.wait_for_timeout(500)
        except Exception as e:
            log.warning("ตั้งช่วงวันที่ครั้งที่ %d ไม่สำเร็จ (%s)", attempt + 1, str(e)[:120])
            if not modal_open(page):
                return False
        got = date_range_text(page)
        if got == want:
            return True
        log.warning("ช่องวันที่บนเว็บเป็น %s ไม่ตรงกับ %s : ลองใหม่", got, want)
    return False


def covers(txt, d1, d2):
    """ช่วงวันที่บนเว็บ (ข้อความ DD/MM/YYYY - DD/MM/YYYY) ครอบคลุม d1 ถึง d2 หรือไม่"""
    m = re.findall(r"(\d{1,2})/(\d{1,2})/(\d{4})", txt or "")
    if len(m) < 2:
        return False
    try:
        a, b = [dt.date(int(y), int(mo), int(da)) for da, mo, y in m[:2]]
    except ValueError:
        return False
    return a <= d1 and d2 <= b


def modal_open(page):
    try:
        return page.locator(SEL_QUICK).count() > 0 and page.locator(SEL_QUICK).first.is_visible()
    except Exception:
        return False


def open_modal(page):
    """เปิดหน้าค้นหาขั้นสูง (ปุ่ม ⌄ ถัดจาก IN / OUT)"""
    if modal_open(page):
        return
    page.locator('button:text-is("OUT")').first.wait_for(state="visible")
    page.wait_for_timeout(1000)
    try:
        page.locator('div.btn-group:has(> button:text-is("OUT")) + div a[href="#"]').first.click(timeout=8000)
    except Exception:
        if not page.evaluate(JS_OPEN_ADV):
            shot(page, "no_adv_button")
            raise RuntimeError("ไม่พบปุ่มค้นหาขั้นสูง (⌄) ข้างปุ่ม IN / OUT : ผู้ใช้นี้อาจไม่มีสิทธิ์ หรือหน้าเว็บเปลี่ยน")
    page.locator(SEL_QUICK).first.wait_for(state="visible", timeout=20000)
    page.wait_for_timeout(1200)                       # รอหน้าต่างเลื่อนเข้าที่


def search_tasks(page, d1, d2, tmo):
    """เปิดหน้าค้นหา > ตั้งช่วงวันที่ d1-d2 > กดค้นหา > รอผล ; หน้าต่างถูกปิดระหว่างรอ (เช่น มีคนคลิกในหน้าต่างเบราว์เซอร์ของบอต)
    = เปิดใหม่ ลองได้ 3 ครั้ง ; คืน (กลุ่มปุ่ม, ช่วงวันที่) ; ไม่มีงาน = NoRows"""
    want = range_want(d1, d2)
    for attempt in range(1, 4):
        open_modal(page)
        rng = date_range_text(page)
        if rng != want:
            log.info("ตั้งช่วงวันที่บนเว็บ %s -> %s", rng, want)
            set_range(page, d1, d2)
            rng = date_range_text(page)
        if rng != want:
            if not modal_open(page):
                log.warning("หน้าต่างค้นหาถูกปิดระหว่างตั้งวันที่ : เปิดใหม่")
                continue
            if not covers(rng, d1, d2):
                shot(page, "date_range")
                raise RuntimeError(f"ตั้งช่วงวันที่บนเว็บไม่ได้ (ช่องวันที่เป็น {rng} ต้องการ {want})")
            log.warning("ช่วงวันที่บนเว็บเป็น %s (กว้างกว่า %s) : ใช้ได้ Macro กรองตามวันที่ B1-C1 อีกครั้ง", rng, want)
        log.info("ค้นหางานช่วงวันที่ %s%s", rng, f" (ครั้งที่ {attempt})" if attempt > 1 else "")
        grp = page.locator(SEL_GROUP).first
        try:
            grp.locator('button[type="submit"]').click(timeout=15000)
        except Exception:
            page.evaluate("() => { const f = [...document.querySelectorAll('form')].find(x => x.querySelector('input[placeholder=\"Quick filter...\"]')); if (f) f.requestSubmit(); }")
        end, t0, closed = time.time() + tmo / 1000, time.time(), False
        while True:
            if not modal_open(page):
                closed = True
                break
            btns = grp.locator("button")
            busy = grp.locator(".spinner-border").count() > 0
            if not busy and btns.count() >= 3:
                return grp, rng
            if not busy and time.time() - t0 > 6 and page.locator("text=No Rows To Show").count() > 0:
                raise NoRows(f"ไม่มีงานในช่วงวันที่ {rng}")
            if time.time() > end:
                shot(page, "search_timeout")
                raise RuntimeError("ค้นหางานไม่เสร็จ (หมดเวลา)")
            page.wait_for_timeout(500)
        if closed:
            log.warning("หน้าต่างค้นหาถูกปิดระหว่างรอผล (อย่าคลิกในหน้าต่างเบราว์เซอร์ของบอตขณะทำงาน) : เปิดใหม่")
            shot(page, "search_closed")
            page.wait_for_timeout(1500)
    raise RuntimeError("หน้าต่างค้นหาถูกปิด 3 ครั้ง : ค้นหาไม่สำเร็จ")


def download_export(c, dest_dir, d1, d2, headless=None):
    """คืน path ไฟล์ที่โหลด ; ไม่มีงานในช่วงวันที่ = NoRows"""
    from playwright.sync_api import sync_playwright
    cc = c["calendar"]
    base = cc.get("url", "https://calendar-plan.scmref-thai.com").rstrip("/")
    tmo = int(cc.get("timeout_sec", "90")) * 1000
    hl = cc.getboolean("headless", False) if headless is None else headless
    with sync_playwright() as pw:
        ctx = launch(pw, c, hl)
        try:
            page = ctx.pages[0] if ctx.pages else ctx.new_page()
            page.set_default_timeout(tmo)
            ensure_login(page, c, base, tmo)
            page.locator('button:text-is("OUT")').first.wait_for(state="visible")
            page.wait_for_timeout(1500)
            grp, rng = search_tasks(page, d1, d2, tmo)
            page.wait_for_timeout(800)
            total = ""
            try:
                m = re.search(r"of\s+([\d,]+)", page.locator(".ag-paging-row-summary-panel").first.inner_text(timeout=3000))
                total = m.group(1) if m else ""
            except Exception:
                pass
            dest = Path(dest_dir) / f"export-tasks_{now_bkk():%Y%m%d_%H%M%S}.xlsx"
            with page.expect_download(timeout=tmo) as dl:
                grp.locator("button").nth(2).click(timeout=20000)
            dl.value.save_as(str(dest))
            if not dest.exists() or dest.stat().st_size < 1000:
                raise RuntimeError(f"ไฟล์ที่ดาวน์โหลดผิดปกติ ({dest.name})")
            log.info("ดาวน์โหลด %s แล้ว (%s งาน, %.1f KB)", dest.name, total or "?", dest.stat().st_size / 1024)
            return dest
        except (NoRows, LoginNeeded):
            raise
        except Exception:
            try:
                shot(ctx.pages[0], "error")
            except Exception:
                pass
            raise
        finally:
            try:
                ctx.close()
            except Exception:
                pass


def manual_login(c):
    """เปิดเบราว์เซอร์ (โปรไฟล์ของบอต) ให้ผู้ใช้เข้าสู่ระบบเอง : จำการเข้าสู่ระบบไว้ใช้รอบถัดไป"""
    from playwright.sync_api import sync_playwright
    base = c["calendar"].get("url", "https://calendar-plan.scmref-thai.com").rstrip("/")
    with sync_playwright() as pw:
        ctx = launch(pw, c, False)
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(base + "/login")
        print("เข้าสู่ระบบในหน้าต่างเบราว์เซอร์ที่เปิดขึ้น (รอได้ถึง 5 นาที) ...")
        end = time.time() + 300
        ok = False
        while time.time() < end:
            try:
                if page.locator('button:text-is("OUT")').count() > 0:
                    ok = True; break
            except Exception:
                pass
            time.sleep(1)
        page.wait_for_timeout(2000)
        ctx.close()
    print("เข้าสู่ระบบแล้ว บอตจำไว้ในโปรไฟล์ของบอต" if ok else "ยังไม่เห็นหน้าปฏิทิน (หมดเวลา) ลองใหม่อีกครั้ง")
    return 0 if ok else EXIT_LOGIN


# ---------------------------------------------------------------- ขั้นที่ 2 : Excel Macro DP_AutoRun
def _same_path(a, b):
    try:
        return os.path.normcase(os.path.abspath(str(a))) == os.path.normcase(os.path.abspath(str(b)))
    except Exception:
        return False


def _com_retry(fn, what, tries=8, wait=15):
    """Excel ไม่ว่าง (ผู้ใช้กำลังแก้เซลล์ / มีหน้าต่างค้าง) = COM ปฏิเสธการเรียก : รอแล้วลองใหม่"""
    last = None
    for i in range(tries):
        try:
            return fn()
        except Exception as e:
            s = str(e)
            if "-2147418111" in s or "-2147417846" in s or "rejected" in s.lower() or "busy" in s.lower():
                last = e
                log.warning("Excel ไม่ว่าง (%s) รอ %d วินาทีแล้วลองใหม่ (%d/%d)", what, wait, i + 1, tries)
                time.sleep(wait)
                continue
            raise
    raise last


PID_FILE = HERE / "excel_bot.pid"          # PID ของ Excel ที่บอตเปิดเอง (ไว้เก็บกวาดถ้ารอบก่อนปิดไม่สนิท)


def _excel_pid(app):
    """PID ของโปรเซส Excel ตัวนั้น (0 = หาไม่ได้)"""
    try:
        import win32process
        return int(win32process.GetWindowThreadProcessId(app.Hwnd)[1])
    except Exception:
        return 0


def _is_excel_pid(pid):
    """True ถ้า PID นี้ยังอยู่และเป็น EXCEL.EXE (กันฆ่าโปรเซสอื่นที่ได้ PID ซ้ำ)"""
    if not pid:
        return False
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {int(pid)}", "/FO", "CSV", "/NH"],
                             capture_output=True, text=True, timeout=30).stdout
        return "excel.exe" in out.lower()
    except Exception:
        return False


def _end_excel_pid(pid, why):
    """ปิดโปรเซส Excel ที่บอตเปิดเองและยังค้างอยู่ (เฉพาะ PID ที่บอตบันทึกไว้ และต้องเป็น EXCEL.EXE)"""
    if _is_excel_pid(pid):
        try:
            import signal
            os.kill(int(pid), signal.SIGTERM)
            log.warning("ปิด Excel ที่บอตเปิดไว้แล้วค้างอยู่ (PID %s) : %s", pid, why)
        except Exception as e:
            log.warning("ปิด Excel PID %s ไม่สำเร็จ: %s", pid, str(e)[:150])


def _clean_stale_excel():
    """รอบก่อนเปิด Excel เองแล้วปิดไม่สนิท (ค้างอยู่) : ปิดตัวนั้นก่อนเริ่มรอบนี้"""
    try:
        if PID_FILE.exists():
            pid = int(PID_FILE.read_text().strip() or "0")
            PID_FILE.unlink()
            _end_excel_pid(pid, "ค้างจากรอบก่อน")
    except Exception:
        pass


def _wait_pid_gone(pid, secs=20):
    for _ in range(secs):
        if not _is_excel_pid(pid):
            return True
        time.sleep(1)
    return False


def run_macro(book, token, run_date, export_file, macro="DP_AutoRun", save=True, com=None, end_date=""):
    """เปิดไฟล์ (หรือใช้ไฟล์ที่เปิดอยู่) รัน DP_AutoRun แล้ว Save ; คืน (สถานะ OK/WARN/ERROR, ข้อความ)
    โทเคนส่งให้ Macro เป็นอาร์กิวเมนต์ ไม่ถูกบันทึกลง log
    Excel ที่บอตเปิดเอง (หรือตัวที่ซ่อนอยู่ไม่มีใครใช้) : ปิดไฟล์ + Quit แล้วรอจนโปรเซสหายจริง ; Excel ของผู้ใช้ที่เปิดอยู่แล้วไม่ถูกปิด"""
    if com is None:
        try:
            import win32com.client as com
        except ImportError:
            return "ERROR", "ยังไม่ได้ติดตั้ง pywin32 : pip install pywin32"
    book = str(Path(book).resolve())
    _clean_stale_excel()
    app, wb, opened_by_us, old_alerts, owned, pid = None, None, False, None, False, 0
    try:
        try:
            app = com.GetActiveObject("Excel.Application")
        except Exception:
            app = None
        if app is None:
            app = com.DispatchEx("Excel.Application")          # เปิด Excel ตัวใหม่แยกต่างหาก
            owned = True
            app.Visible = False
            app.DisplayAlerts = False
        else:
            try:
                if not app.Visible:                             # Excel ที่ซ่อนอยู่ (ไม่มีผู้ใช้เปิดหน้าต่าง) = ตัวค้างจากบอต : ปิดให้หลังเสร็จ
                    owned = True
            except Exception:
                pass
            for w in app.Workbooks:
                if _same_path(w.FullName, book):
                    wb = w
                    break
        pid = _excel_pid(app) if owned else 0
        if owned and pid:
            try:
                PID_FILE.write_text(str(pid))
            except OSError:
                pass
        attached = wb is not None
        if wb is None:
            if not owned:
                old_alerts = app.DisplayAlerts
                app.DisplayAlerts = False
            wb = _com_retry(lambda: app.Workbooks.Open(book, UpdateLinks=0), "เปิดไฟล์")
            opened_by_us = True
        if wb.ReadOnly:
            return "ERROR", "ไฟล์ Delivery Tracking เปิดแบบอ่านอย่างเดียว (มีคนอื่นเปิดอยู่ / ไฟล์ถูกล็อก) : ไม่ได้รัน เพื่อกันงานซ้ำ"
        log.info("รัน Macro %s ในไฟล์ %s%s", macro, wb.Name, " (ไฟล์เปิดอยู่ใน Excel ของผู้ใช้)" if attached and not owned else "")
        name = wb.Name

        def call():
            last = None
            for pref in (f"'{name}'!{macro}", f"'{name}'!modDeliveryPlan.{macro}"):
                try:
                    return app.Run(pref, token, run_date, str(export_file or ""), str(end_date or ""))
                except Exception as e:
                    last = e
                    if "-2147418111" in str(e):
                        raise
            raise last
        try:
            res = str(_com_retry(call, "รัน Macro") or "")
        except Exception as e:
            if "-2147352562" in str(e) or "argument" in str(e).lower():     # DISP_E_BADPARAMCOUNT : Macro รุ่นเก่า
                return "ERROR", "Macro ในไฟล์เป็นรุ่นเก่า : Import modDeliveryPlan.bas (y8b) + modImportCalendar.bas (m-gmail) ก่อน"
            raise
        st = res.split("|", 1)[0].strip().upper() if res else ""
        if st not in ("OK", "WARN", "ERROR"):
            st, res = "ERROR", "Macro ไม่ได้ส่งผลกลับ : " + res[:200]
        if save:
            try:
                _com_retry(wb.Save, "บันทึกไฟล์")
                log.info("บันทึกไฟล์ %s แล้ว", name)
            except Exception as e:
                res += " | บันทึกไฟล์ไม่สำเร็จ: " + str(e)[:150]
                st = "ERROR" if st == "OK" else st
        return st, res
    except Exception as e:
        return "ERROR", "รัน Macro ไม่สำเร็จ: " + str(e)[:300]
    finally:
        try:
            if (opened_by_us or owned) and wb is not None:
                wb.Close(SaveChanges=False)
        except Exception:
            pass
        try:
            if old_alerts is not None and app is not None:
                app.DisplayAlerts = old_alerts
        except Exception:
            pass
        try:
            if owned and app is not None:
                try:
                    app.DisplayAlerts = False
                    for w in list(app.Workbooks):               # ไฟล์อื่นที่ Macro เปิดค้างไว้ (ถ้ามี) ปิดให้หมดก่อน Quit
                        try:
                            w.Close(SaveChanges=False)
                        except Exception:
                            pass
                except Exception:
                    pass
                app.Quit()
        except Exception:
            pass
        wb = None
        app = None
        try:
            import gc
            gc.collect()                                        # ปล่อยการอ้างอิง COM ให้ Excel ปิดตัวได้จริง
        except Exception:
            pass
        if owned and pid:
            if _wait_pid_gone(pid, 20):
                try:
                    PID_FILE.unlink()
                except OSError:
                    pass
            else:
                _end_excel_pid(pid, "สั่ง Quit แล้วแต่ยังไม่ปิดภายใน 20 วินาที")
                try:
                    PID_FILE.unlink()
                except OSError:
                    pass


def cleanup_exports(folder, keep_days):
    n = 0
    for f in (HERE / "logs").glob("*.png"):                 # ภาพหน้าจอตอนผิดพลาด เก็บ 14 วัน
        try:
            if f.stat().st_mtime < time.time() - 14 * 86400:
                f.unlink()
        except OSError:
            pass
    cut = time.time() - keep_days * 86400
    for f in Path(folder).glob("export-tasks_*.xlsx"):
        try:
            if f.stat().st_mtime < cut:
                f.unlink(); n += 1
        except OSError:
            pass
    if n:
        log.info("ลบไฟล์ export-tasks ที่บอตโหลดเก่ากว่า %d วัน %d ไฟล์", keep_days, n)


# ---------------------------------------------------------------- Task Scheduler (จันทร์-เสาร์ 15:00)
def parse_hm(t, name):
    m = re.fullmatch(r"(\d{1,2})[:.](\d{2})", (t or "").strip())
    if not m or int(m[1]) > 23 or int(m[2]) > 59:
        raise ValueError(f"{name} ต้องเป็นเวลา HH:MM เช่น 14:00 (ได้ \"{t}\")")
    return int(m[1]) * 60 + int(m[2])


def run_plan(c):
    """(เริ่ม, สิ้นสุด, ทุกกี่นาที) จาก config.ini : run_from / run_to / every_min"""
    e = c["excel"]
    a = parse_hm(e.get("run_from", "").strip() or DEFAULT_FROM, "run_from")
    z = parse_hm(e.get("run_to", "").strip() or DEFAULT_TO, "run_to")
    try:
        n = int(e.get("every_min", "").strip() or DEFAULT_EVERY)
    except ValueError:
        raise ValueError("every_min ต้องเป็นตัวเลขนาที เช่น 30")
    if not 5 <= n <= 720 or z < a:
        raise ValueError("run_from / run_to / every_min ไม่ถูกต้อง (run_to ต้องไม่ก่อน run_from ; every_min 5-720)")
    return a, z, n


def run_times(c):
    a, z, n = run_plan(c)
    return [f"{t // 60:02d}:{t % 60:02d}" for t in range(a, z + 1, n)]


def task_xml(plan=None, py=None, script=None):
    py = Path(py or sys.executable)
    exe = py.with_name("python.exe") if py.with_name("python.exe").exists() else py
    script = Path(script or (HERE / "calplan_bot.py"))
    a, z, n = plan or (parse_hm(DEFAULT_FROM, "from"), parse_hm(DEFAULT_TO, "to"), DEFAULT_EVERY)
    dur = (z - a) + 1                                  # +1 นาที : รอบสุดท้าย (run_to) ต้องอยู่ในช่วงทำซ้ำ
    start = f"{a // 60:02d}:{a % 60:02d}"
    tl = [f"{t // 60:02d}:{t % 60:02d}" for t in range(a, z + 1, n)]
    trig = f"""    <CalendarTrigger>
      <Repetition><Interval>PT{n}M</Interval><Duration>PT{dur}M</Duration><StopAtDurationEnd>true</StopAtDurationEnd></Repetition>
      <StartBoundary>2026-01-05T{start}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay><DaysInterval>1</DaysInterval></ScheduleByDay>
    </CalendarTrigger>"""
    return f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo><Description>โหลด export-tasks จาก Calendar Plan แล้วรัน Macro ดึงแผน + ส่งงานใหม่ + อัปเดตงานเดิมที่ข้อมูลเปลี่ยน ขึ้น Delivery Tracking ทุกวัน {tl[0]}-{tl[-1]} ทุก {n} นาที</Description></RegistrationInfo>
  <Triggers>
{trig}
  </Triggers>
  <Principals><Principal id="Author"><LogonType>InteractiveToken</LogonType><RunLevel>LeastPrivilege</RunLevel></Principal></Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings><StopOnIdleEnd>false</StopOnIdleEnd><RestartOnIdle>false</RestartOnIdle></IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT40M</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{xesc(str(exe))}</Command>
      <Arguments>{xesc('"' + str(script) + '" --scheduled')}</Arguments>
      <WorkingDirectory>{xesc(str(script.parent))}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>
"""


def install_task(plan):
    f = Path(tempfile.gettempdir()) / "calplan_task.xml"
    f.write_text(task_xml(plan), encoding="utf-16")
    r = subprocess.run(["schtasks", "/Create", "/TN", TASK_NAME, "/XML", str(f), "/F"], capture_output=True, text=True, errors="replace")
    try:
        f.unlink()
    except OSError:
        pass
    print((r.stdout or "") + (r.stderr or ""))
    if r.returncode == 0:
        print(f"สร้าง Task \"{TASK_NAME}\" แล้ว : ทุกวัน {plan[0] // 60:02d}:{plan[0] % 60:02d}-{plan[1] // 60:02d}:{plan[1] % 60:02d} น. ทุก {plan[2]} นาที (เครื่องปิด/หลับตอนนั้น = ข้ามรอบนั้น ไม่รันย้อนหลัง ; กด Run เองใน Task Scheduler = รันทุกขั้นตอนทันที)")
    return r.returncode


def uninstall_task():
    r = subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"], capture_output=True, text=True, errors="replace")
    print((r.stdout or "") + (r.stderr or ""))
    return r.returncode


def show_status():
    p = HERE / "logs" / "STATUS.txt"
    print(p.read_text(encoding="utf-8") if p.exists() else "ยังไม่มีสถานะ (บอตยังไม่เคยรัน)")
    try:
        r = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"], capture_output=True, text=True, errors="replace")
        print("\nTask Scheduler:\n" + (r.stdout.strip() if r.returncode == 0 else "ยังไม่ได้ติดตั้ง (python calplan_bot.py --install-task)"))
    except OSError:
        pass


# ---------------------------------------------------------------- รอบทำงาน
def job_range(run_day):
    """B1 = วันที่รัน ; C1 = วันถัดไป ถ้าตรงเสาร์-อาทิตย์ (เช่นรันวันศุกร์) ให้ไปจนถึงวันจันทร์"""
    d1 = run_day
    d2 = d1 + dt.timedelta(days=1)
    while d2.weekday() in (5, 6):          # เสาร์ / อาทิตย์ : ต่อไปจนถึงวันจันทร์
        d2 += dt.timedelta(days=1)
    return d1, d2


def target_range(a, c):
    if a.date:
        d1 = dt.date.fromisoformat(a.date)
        d2 = dt.date.fromisoformat(a.end) if a.end else d1
        return d1, max(d1, d2)
    return job_range(dt.date.fromisoformat(a.as_of) if a.as_of else now_bkk().date())


def range_th(d1, d2):
    return d1.isoformat() + (f" ถึง {d2.isoformat()}" if d2 > d1 else "")


def in_window(c):
    """โหมด Task Scheduler : ทำเฉพาะจันทร์-เสาร์ ระหว่าง run_time ถึง latest_time (กันเครื่องเปิดเช้าวันถัดไปแล้วรันย้อนหลังผิดวัน)"""
    n = now_bkk()
    t0 = run_times(c)[0]; t1 = c["excel"].get("latest_time", "23:30")
    hm = n.strftime("%H:%M")
    ok = (dt.datetime.strptime(t0, "%H:%M") - dt.timedelta(minutes=5)).strftime("%H:%M") <= hm <= t1
    return ok, f"เวลา {hm} นอกช่วง {t0}-{t1}"


def run(a, c):
    if a.scheduled:
        log.info("รันจาก Task Scheduler (รันทุกขั้นตอนเสมอ ไม่เช็กช่วงเวลา)")
    book = book_path(c)
    folder = book.parent
    add_book_log(folder)
    lk = lock()
    try:
        d1, d2 = target_range(a, c)
        log.info("===== เริ่มรอบ (รุ่น %s) วันที่งาน %s ไฟล์ %s =====", VERSION, range_th(d1, d2), book.name)
        # ----- 1) export-tasks
        if a.excel_only:
            export = Path(a.excel_only).resolve()
            if not export.exists():
                log.error("ไม่พบไฟล์ %s", export); return EXIT_CONFIG
        else:
            export, err = None, None
            for i in range(2):
                try:
                    export = download_export(c, folder, d1, d2, headless=False if a.show else None)
                    break
                except NoRows as e:
                    log.warning("%s : รัน Macro ต่อเพื่อตรวจงานที่เคยส่งขึ้นระบบแต่ไม่มีใน Calendar Plan แล้ว", e)
                    export = "@EMPTY"; break
                except LoginNeeded as e:
                    log.error(str(e)); return EXIT_LOGIN
                except Exception as e:
                    err = e
                    log.warning("ดาวน์โหลดไม่สำเร็จ (ครั้งที่ %d): %s", i + 1, str(e)[:300])
                    time.sleep(20)
            if export is None:
                log.error("ดาวน์โหลด export-tasks ไม่สำเร็จ: %s (ดูภาพหน้าจอใน logs)", str(err)[:300]); return EXIT_EXPORT
            if a.download_only:
                log.info("--download-only : จบที่ขั้นที่ 1"); return 0
        # ----- 2) Excel
        try:
            tok = sb_token(c)
        except Exception as e:
            log.error("เข้าสู่ระบบ Delivery Tracking (บัญชีบอท) ไม่ได้: %s", str(e)[:200]); return EXIT_EXCEL
        st, res = run_macro(book, tok, d1.isoformat(), export, c["excel"].get("macro", "DP_AutoRun").strip() or "DP_AutoRun",
                            c["excel"].getboolean("save_workbook", True), end_date=d2.isoformat() if d2 > d1 else "")
        try:                                           # ส่งอีเมลแจ้งงานหายที่ Macro เขียนไว้ (Gmail) แม้ Macro จบด้วยคำเตือน
            send_outbox(c, folder)
        except Exception as e:
            log.error("ส่งอีเมลไม่สำเร็จ : %s", str(e)[:300])
        if st in ("OK", "WARN"):
            bot_ping(c, tok)
        s = load_state(); s["last_macro"] = f"{now_bkk():%Y-%m-%d %H:%M} {res[:300]}"; save_state(s)
        if st == "OK":
            log.info("Macro สำเร็จ : %s", res[:1500])
        elif st == "WARN":
            log.error("Macro : %s", res[:1500])
        else:
            log.error("Macro ไม่สำเร็จ : %s", res[:1500])
        try:
            cleanup_exports(folder, int(c["excel"].get("keep_days", "30")))
        except Exception:
            pass
        return 0 if st == "OK" else EXIT_WARN if st == "WARN" else EXIT_EXCEL
    finally:
        try:
            lk.unlink()
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(description="ส่งแผนจาก Calendar Plan ขึ้น Delivery Tracking อัตโนมัติ")
    for f in ("--setup-calplan", "--setup-password", "--login", "--install-task", "--uninstall-task", "--status", "--scheduled", "--show",
              "--download-only", "--print-task-xml", "--setup-mail", "--test-mail", "--send-mail"):
        ap.add_argument(f, action="store_true")
    ap.add_argument("--excel-only", metavar="ไฟล์")
    ap.add_argument("--date", metavar="ปปปป-ดด-วว", help="วันแรกของงาน (กำหนดเอง)")
    ap.add_argument("--end", metavar="ปปปป-ดด-วว", help="วันสุดท้ายของงาน (ใช้กับ --date)")
    ap.add_argument("--as-of", metavar="ปปปป-ดด-วว", help="คิดช่วงวันที่เหมือนรันในวันนั้น")
    a = ap.parse_args()
    c = cfg()
    try:
        rt = run_plan(c)
    except ValueError as e:
        print(e); return EXIT_CONFIG
    if a.print_task_xml:
        print(task_xml(rt)); return 0
    if a.install_task:
        return install_task(rt)
    if a.uninstall_task:
        return uninstall_task()
    if a.status:
        show_status(); return 0
    if a.setup_calplan:
        import getpass, keyring
        u = input("ชื่อผู้ใช้เว็บ Calendar Plan: ").strip()
        keyring.set_password(KR_CAL, "__username__", u)
        keyring.set_password(KR_CAL, u, getpass.getpass("รหัสผ่าน (พิมพ์แล้วไม่แสดงบนจอ): "))
        print("เก็บใน Windows Credential Manager แล้ว (ไม่มีในไฟล์ใดๆ)  ลองทันที: python calplan_bot.py --download-only --show"); return 0
    if a.setup_password:
        import getpass, keyring
        u = c["supabase"].get("user", "gpsbot").strip()
        keyring.set_password(KR_BOT, u, getpass.getpass(f"รหัสผ่านบัญชีบอท {u} (พิมพ์แล้วไม่แสดงบนจอ): "))
        print("เก็บใน Windows Credential Manager แล้ว"); return 0
    if a.setup_mail:
        return setup_mail(c)
    if a.test_mail:
        return test_mail(c)
    if a.send_mail:
        ok, bad = send_outbox(c, book_path(c).parent)
        print(f"ส่งแล้ว {ok} ฉบับ / ไม่สำเร็จ {bad} ฉบับ"); return 0 if bad == 0 else EXIT_CONFIG
    if a.login:
        return manual_login(c)

    wd = int(c["excel"].get("watchdog_min", "35")) * 60

    def _die():
        log.error("ทำงานนานเกิน %d นาที : จบรอบนี้", wd // 60)
        write_status(EXIT_TIMEOUT)
        try:
            (HERE / "calplan.lock").unlink()
        except OSError:
            pass
        os._exit(EXIT_TIMEOUT)
    timer = threading.Timer(wd, _die); timer.daemon = True; timer.start()
    try:
        try:
            code = run(a, c)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else EXIT_CRASH
        except Exception:
            log.error("ข้อผิดพลาดที่ไม่คาดคิด:\n%s", traceback.format_exc()[-1500:]); code = EXIT_CRASH
    finally:
        timer.cancel()
    if code not in (EXIT_BUSY, EXIT_SKIP):
        s = load_state()
        if code == 0:
            s["last_ok"] = now_bkk().strftime("%Y-%m-%d %H:%M:%S")
        save_state(s)
        log.info("===== จบรอบ : %s =====", EXIT_TEXT.get(code, code))
        write_status(code)
    return code


if __name__ == "__main__":
    sys.exit(main())
