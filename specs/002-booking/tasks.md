# Tasks: การจองงานบริการซ่อมบำรุง (UC-07)

Feature: SPEC-BOOKING | อ้างอิง: plan.md (plan v1) | สร้างด้วย /tasks วันที่ 2569-10-04 (tasks v1)
แก้รอบที่ 1 (ทีมสั่ง): T-06 เดิม AI ตั้ง "พร้อมทำ" ทั้งที่ R3 รอ Q-14 แก้เป็นทำเฉพาะ R1, R2, R4, R5, R6 ตาม D-07-04 และเพิ่มหมายเหตุ

สรุป: 11 task | 0 task รอ Q-xx ทั้ง task (T-06 ทำได้บางส่วน R3 ใช้พฤติกรรมชั่วคราว)
สถานะปัจจุบัน: เสร็จ 11 (ทุก task ผ่านการตรวจ 5 ข้อแล้ว)

### T-01 ตั้งโครงโปรเจกต์ ฐานข้อมูล และตาราง
- รองรับ: REQ-DAT-002, REQ-PRV-002, MD-DOM-01
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-02 ถึง T-08
- ไฟล์ที่แตะ: backend/requirements.txt, backend/pytest.ini, frontend/package.json, frontend/vite.config.js, backend/app/config.py, backend/app/db/session.py, backend/app/db/models.py, backend/app/db/migrations/m001_init.py, backend/app/main.py, backend/tests/conftest.py
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: pytest และ npm test รันได้ (ยังไม่มี test ของ AC) upgrade(engine) สร้างตาราง 8 ตารางได้ และ jobs.status รับได้เฉพาะ 8 ค่าตาม glossary
- สถานะ: เสร็จ

### T-02 ล็อกช่วงเวลาและหมดอายุอัตโนมัติ
- รองรับ: REQ-FN-041, AS-07, BR-02
- ตรวจด้วย: AC-07-04 (ส่วนล็อก) และ test พื้นฐาน hold หมดอายุใน 10 นาที
- ไฟล์ที่แตะ: backend/app/booking/service.py (hold_slot), backend/app/technicians/service.py (release_expired_holds), backend/app/booking/router.py (POST /slots/{id}/hold)
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: POST /slots/{id}/hold ตอบ hold_expires_at = now + HOLD_MINUTES และคนอื่นล็อกซ้ำได้ 409
- สถานะ: เสร็จ

### T-03 ค้นช่างว่างตามประเภทงาน ระยะทาง และช่วงที่ไม่ซ้อน
- รองรับ: REQ-FN-008, BR-02, BR-03, AS-06
- ตรวจด้วย: AC-07-02
- ไฟล์ที่แตะ: backend/app/technicians/service.py, backend/app/technicians/router.py, backend/app/clock.py, backend/tests/test_booking.py
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: test_AC_07_02_slot_not_rebookable ผ่าน
- สถานะ: เสร็จ

### T-04 สร้าง endpoint จองงาน (POST /bookings) และตัดมัดจำแบบ authorize แล้ว capture
- รองรับ: REQ-FN-008, REQ-FN-041, REQ-IF-001, REQ-CON-003
- ตรวจด้วย: AC-07-01, AC-07-04
- ไฟล์ที่แตะ: backend/app/booking/service.py (create_booking), backend/app/booking/router.py, backend/app/payments/gateway.py, backend/app/payments/service.py, backend/tests/test_booking.py
- ต้องทำหลัง: T-02, T-03
- เสร็จเมื่อ: test_AC_07_01_booking_success และ test_AC_07_04_no_charge_when_slot_taken ผ่าน
- สถานะ: เสร็จ (ระหว่างทำพบ GAP-05 "ใกล้เคียง" ไม่มีตัวเลข เปิด CR-01 ก่อนจึงทำต่อ)

### T-05 gateway-timeout และ status-inquiry ด้วย reference เดิม
- รองรับ: REQ-IF-005, REQ-IF-001, MD-SEQ-07-05
- ตรวจด้วย: AC-07-05, AC-07-06, AC-07-07
- ไฟล์ที่แตะ: backend/app/payments/service.py, backend/app/payments/gateway.py (GatewayTimeout, status_inquiry), backend/tests/test_payment.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: test_AC_07_05, test_AC_07_06, test_AC_07_07 ผ่าน และ authorize ถูกเรียกครั้งเดียวต่อ ref
- สถานะ: เสร็จ (รอบแรก test_AC_07_05 ไม่ผ่านเพราะ GAP-07 ค่า timeout ไม่ตรง แก้ config แล้วผ่าน)

### T-06 ยกเลิกงานและคืนมัดจำตาม BR-01 (เฉพาะ R1, R2, R4, R5, R6)
- รองรับ: REQ-BR-001, BR-01, MD-STM-01
- ตรวจด้วย: AC-07-10 (Scenario Outline ทุกแถวยกเว้น R3)
- ไฟล์ที่แตะ: backend/app/refund/rules.py, backend/app/refund/service.py, backend/app/refund/router.py, backend/tests/test_refund.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: test_AC_07_10_refund ผ่านทุกแถวที่ไม่ใช่ R3 และ R3 ตอบ 409 ตามพฤติกรรมชั่วคราว
- สถานะ: เสร็จ (R3 รอ Q-14 test ข้ามไว้พร้อมเหตุผล)

### T-07 คิวแจ้งเตือนลูกค้าและช่างภายใน 60 วินาที
- รองรับ: REQ-FN-012, IF-02
- ตรวจด้วย: AC-07-03
- ไฟล์ที่แตะ: backend/app/notify/queue.py, backend/app/booking/service.py (enqueue), backend/app/main.py (GET /notifications/queue), backend/tests/test_booking.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: test_AC_07_03_notify_both_within_60s ผ่าน
- สถานะ: เสร็จ

### T-08 มุมมองช่างซ่อนเบอร์ลูกค้าจนก่อนนัด 2 ชั่วโมง และตัวกรอง log
- รองรับ: REQ-SEC-004, REQ-PRV-002
- ตรวจด้วย: AC-07-09
- ไฟล์ที่แตะ: backend/app/privacy.py, backend/app/booking/service.py (technician_view), backend/app/booking/router.py (GET /jobs/{id}/technician-view), backend/tests/test_privacy.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: test_AC_07_09_phone_hidden_until_2h ผ่าน และเมื่อแก้ PHONE_REVEAL_HOURS เป็น 3 test ต้องพัง (พิสูจน์ชั้น 3 แล้ว)
- สถานะ: เสร็จ

### T-09 test ย่อส่วนรับโหลดสำหรับ REQ-QA-003
- รองรับ: REQ-QA-003
- ตรวจด้วย: AC-07-08 (ฉบับย่อส่วน 20 คำขอ รอ CR-02 เป็นเกณฑ์ตรวจรับจริง)
- ไฟล์ที่แตะ: backend/tests/test_load_scaled.py
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: test_AC_07_08_search_under_load_scaled รันได้และบันทึกวิธีย่อส่วนใน ac-results.md
- สถานะ: เสร็จ (ผลเป็นสัญญาณบนเครื่องนักศึกษา ไม่ใช่ผลตรวจรับ)

### T-10 หน้าจอเลือกช่าง ยืนยัน และผลการจอง (ใช้ API จำลอง)
- รองรับ: REQ-FN-008, REQ-FN-041, AC-07-04 (ส่วนแสดงผล)
- ตรวจด้วย: AC-07-04 (หน้าจอ)
- ไฟล์ที่แตะ: frontend/src/App.jsx, frontend/src/api/client.js, frontend/src/pages/TechnicianPicker.jsx, frontend/src/pages/ConfirmBooking.jsx, frontend/src/pages/BookingResult.jsx, frontend/src/__tests__/AC-07-04.test.jsx, frontend/src/setupTests.js, frontend/vite.config.js, frontend/package.json, frontend/index.html
- ต้องทำหลัง: ไม่มี (ใช้สัญญา API ใน plan.md ข้อ 4)
- เสร็จเมื่อ: npm test ผ่าน AC-07-04.test.jsx
- สถานะ: เสร็จ

### T-11 ต่อหน้าจอกับ API จริง
- รองรับ: REQ-FN-008
- ตรวจด้วย: ไม่มี AC ตรง ๆ ตรวจด้วยตา: npm run dev + uvicorn แล้วจองได้จนเห็นหน้าผลการจอง
- ไฟล์ที่แตะ: frontend/vite.config.js (proxy /api), backend/seed_demo.py
- ต้องทำหลัง: T-03, T-04, T-05, T-10
- เสร็จเมื่อ: กดค้นหา เลือกช่วงเวลา ยืนยัน แล้วเห็น "งาน #1 สถานะ ยืนยันแล้ว" บนหน้าจอ
- สถานะ: เสร็จ

## ตารางตรวจความครบ

| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-07-01 | T-04 |
| AC-07-02 | T-03 |
| AC-07-03 | T-07 |
| AC-07-04 | T-02, T-04, T-10 (หน้าจอ) |
| AC-07-05 | T-05 |
| AC-07-06 | T-05 |
| AC-07-07 | T-05 |
| AC-07-08 | T-09 (ย่อส่วน รอ CR-02) |
| AC-07-09 | T-08 |
| AC-07-10 | T-06 (R3 รอ Q-14) |

| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| REQ-CON-003 | T-04 (interface Gateway ไม่เปลี่ยนราย) |
| REQ-CON-001 | ทุก task ตัด A2 ออก (D-07-02) |
| REQ-PRV-002 | T-01 (ไม่มีตาราง log), T-08 (privacy.py) |
| REQ-SEC-004 | T-08 |
| REQ-IF-001 | T-04 |
| REQ-IF-005 | T-05 |
| REQ-DAT-002 | T-01 |

## สิ่งที่ยังไม่ทำ

- Q-14 BR-01 R3: T-06 ทำแถวอื่นแล้ว R3 ใช้พฤติกรรมชั่วคราว "ไม่อนุญาต" รอคำตอบ 11 ต.ค.
- Q-18 ระยะล็อก: ทำเป็น config HOLD_MINUTES = 10 ถ้าคำตอบต่าง แก้ config
- Q-19 gateway-timeout: config GATEWAY_TIMEOUT_SECONDS = 30 (ดู GAP-07)
- Q-22 geoPoint: เก็บแต่ไม่ส่งออก ยังไม่มี task เพราะไม่มี REQ รองรับ
- Q-23 ใครปลดล็อก: ใช้ AS-07 หมดอายุเอง (T-02) รอกลุ่มยืนยันกับเจ้าของ
