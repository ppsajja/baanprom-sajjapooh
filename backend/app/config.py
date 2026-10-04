"""ค่าตั้งต้นของระบบ (ค่าที่มาจาก Open Question ติดป้าย Q-xx ไว้ แก้ที่นี่ที่เดียวเมื่อได้คำตอบ)"""
import os

# ต่อฐานข้อมูลผ่านตัวแปรแวดล้อม ระบบจริงเป็น PostgreSQL (ทีมเลือกเอง ไม่ได้มาจาก spec)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./baanprom.db")

# REQ-FN-041 ระยะล็อกช่วงเวลาชั่วคราว (Q-18 ค่าชั่วคราว 10 นาที จาก EV-041)
HOLD_MINUTES = int(os.getenv("HOLD_MINUTES", "10"))

# REQ-IF-005 เวลารอ gateway ก่อน status-inquiry (Q-19 ค่าชั่วคราว 30 วินาที)
GATEWAY_TIMEOUT_SECONDS = int(os.getenv("GATEWAY_TIMEOUT_SECONDS", "30"))

# REQ-SEC-004 ช่างเห็นเบอร์ลูกค้าได้ก่อนนัดกี่ชั่วโมง
PHONE_REVEAL_HOURS = 2

# REQ-FN-012 ต้องแจ้งสองฝ่ายภายในกี่วินาที
NOTIFY_WITHIN_SECONDS = 60

# BR-03 ระยะให้บริการสูงสุด (กิโลเมตร)
MAX_SERVICE_DISTANCE_KM = 15.0

# REQ-FN-008 / AS-06 ค้นช่างว่างกี่วันข้างหน้า
SEARCH_DAYS_AHEAD = 7

# AC-07-04 (CR-01) ช่วงใกล้เคียงต้องเริ่มห่างจากช่วงที่เลือกไม่เกินกี่ชั่วโมง
ALTERNATIVE_WINDOW_HOURS = 3

# UC-07 E1 ถ้าไม่ชำระภายในกี่นาที ยกเลิกอัตโนมัติ
PAYMENT_DEADLINE_MINUTES = 30
