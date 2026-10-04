# Tasks: การจองงานบริการซ่อมบำรุง (UC-07)

Feature: SPEC-BOOKING | อ้างอิง: plan.md (plan v1.2) | สร้างด้วย /tasks วันที่ 2569-10-04

สรุป: 11 task | 2 task รอ Q-xx

### T-01 ตั้งโครงโปรเจกต์และพื้นฐาน test
- รองรับ: REQ-DAT-002, REQ-PRV-002, REQ-CON-003
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-02 ถึง T-10
- ไฟล์ที่แตะ: backend/requirements.txt, backend/pytest.ini, backend/app/config.py, backend/app/main.py, backend/app/db/session.py, backend/app/db/models.py, backend/app/db/migrations/m001_init.py, frontend/package.json, frontend/vite.config.js, frontend/src/setupTests.js
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: รัน `cd backend && pytest -q` ได้ผ่าน test เริ่มต้นหนึ่งตัว และโครงโปรเจกต์พร้อมสำหรับ API และ UI
- สถานะ: เสร็จ รอทีมตรวจ

### T-02 ตั้งฐานข้อมูลและโมเดลงาน/slot/payment/refund
- รองรับ: REQ-DAT-002, REQ-PRV-002, AS-03, AS-07
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นงานพื้นฐานของ T-03 ถึง T-08
- ไฟล์ที่แตะ: backend/app/db/models.py, backend/app/db/migrations/m001_init.py, backend/tests/conftest.py
- ต้องทำหลัง: T-01
- เสร็จเมื่อ: ตาราง `customers`, `service_addresses`, `technicians`, `time_slots`, `jobs`, `job_status_history`, `payments`, `refunds` ถูกสร้างได้อย่างถูกต้องและข้อมูล status ตาม glossary
- สถานะ: เสร็จ รอทีมตรวจ

### T-03 ค้นช่างว่างและล็อกช่วงเวลา
- รองรับ: REQ-FN-008, REQ-FN-041, BR-02, BR-03, AS-06, AS-07
- ตรวจด้วย: AC-07-02, AC-07-04
- ไฟล์ที่แตะ: backend/app/technicians/service.py, backend/app/technicians/router.py, backend/app/booking/service.py, backend/app/booking/router.py
- ต้องทำหลัง: T-02
- เสร็จเมื่อ: `GET /technicians` คืนเฉพาะช่างว่างใน 7 วัน และ `POST /slots/{slotId}/hold` ตอบ `409` เมื่อถูกล็อกแล้วและ `holdExpiresAt` เมื่อล็อกใหม่
- สถานะ: พร้อมทำ

### T-04 สร้างงานและชำระมัดจำแบบ authorize ก่อน capture
- รองรับ: REQ-FN-008, REQ-IF-001, REQ-CON-003, REQ-FN-041
- ตรวจด้วย: AC-07-01, AC-07-04
- ไฟล์ที่แตะ: backend/app/booking/service.py, backend/app/booking/router.py, backend/app/payments/gateway.py, backend/app/payments/service.py, backend/tests/test_booking.py
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: `POST /bookings` สร้าง job สำเร็จและ auth/capture เป็นไปตามลำดับที่กำหนด และกรณี slot ถูกจองแล้วให้คืน 409 พร้อม alternative slots
- สถานะ: พร้อมทำ

### T-05 สร้าง timeout และ status inquiry สำหรับ Payment Gateway
- รองรับ: REQ-IF-005, REQ-IF-001, REQ-CON-003
- ตรวจด้วย: AC-07-05, AC-07-06, AC-07-07
- ไฟล์ที่แตะ: backend/app/payments/service.py, backend/app/payments/gateway.py, backend/tests/test_payment.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: timeout ที่กำหนดแล้วเรียก status inquiry ด้วย reference เดิมและจบสถานะอย่างถูกต้องตาม approved / declined / timeout
- สถานะ: รอ Q-19

### T-06 จัดการคืนมัดจำตาม BR-01
- รองรับ: REQ-BR-001, BR-01, MD-STM-01
- ตรวจด้วย: AC-07-10
- ไฟล์ที่แตะ: backend/app/refund/rules.py, backend/app/refund/service.py, backend/app/refund/router.py, backend/tests/test_refund.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: refund ถูกคำนวณตามแถว R1, R2, R4, R5, R6 อย่างถูกต้อง และ R3 ใช้พฤติกรรมชั่วคราวตามทางเลือกของทีม
- สถานะ: รอ Q-14

### T-07 คิวแจ้งเตือนภายใน 60 วินาที และ retry สูงสุด 5 ครั้ง
- รองรับ: REQ-FN-012, ASM-05, IF-02
- ตรวจด้วย: AC-07-03
- ไฟล์ที่แตะ: backend/app/notify/queue.py, backend/app/booking/service.py, backend/app/main.py, backend/tests/test_booking.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: หลังสร้างงานมี notification item สำหรับลูกค้าและช่าง และกรณีส่งไม่สำเร็จระบบส่งซ้ำได้ไม่เกิน 5 ครั้งแล้วคงงานไว้
- สถานะ: พร้อมทำ

### T-08 ซ่อนเบอร์ลูกค้าในมุมมองช่างและกรอง log
- รองรับ: REQ-SEC-004, REQ-PRV-002, AC-07-09
- ตรวจด้วย: AC-07-09
- ไฟล์ที่แตะ: backend/app/privacy.py, backend/app/booking/service.py, backend/app/booking/router.py, backend/tests/test_privacy.py
- ต้องทำหลัง: T-04
- เสร็จเมื่อ: ช่างเห็นเบอร์ได้เฉพาะช่วง 2 ชั่วโมงก่อนนัดจนปิดงาน และ log ไม่บันทึกเบอร์โทรของลูกค้า
- สถานะ: พร้อมทำ

### T-09 ทดสอบโหลดและ latency สำหรับ REQ-QA-003
- รองรับ: REQ-QA-003
- ตรวจด้วย: AC-07-08
- ไฟล์ที่แตะ: backend/tests/test_load_scaled.py, specs/002-booking/ac-results.md
- ต้องทำหลัง: T-03
- เสร็จเมื่อ: มีสคริปต์ทดสอบแบบย่อส่วนที่จำลองผู้ใช้พร้อมกันและบันทึกผล p95 ของการค้นหาและยืนยันให้เห็นว่าอยู่ในเกณฑ์ที่ยอมรับได้
- สถานะ: พร้อมทำ

### T-10 สร้างหน้า UI สำหรับเลือกช่างและยืนยันการจอง
- รองรับ: REQ-FN-008, REQ-FN-041, AC-07-04
- ตรวจด้วย: AC-07-04 (หน้าจอ)
- ไฟล์ที่แตะ: frontend/src/App.jsx, frontend/src/api/client.js, frontend/src/pages/TechnicianPicker.jsx, frontend/src/pages/ConfirmBooking.jsx, frontend/src/pages/BookingResult.jsx, frontend/src/__tests__/AC-07-04.test.jsx
- ต้องทำหลัง: ไม่มี
- เสร็จเมื่อ: หน้าจอแสดงการค้นหาและจองได้ตรงตามสัญญา API และกรณี slot ถูกจองแล้วจะแสดงคำเตือนพร้อมตัวเลือกช่วงใกล้เคียง
- สถานะ: เสร็จ รอทีมตรวจ

### T-11 ต่อหน้าจอกับ API จริง และยืนยันการใช้งานจริง
- รองรับ: REQ-FN-008, REQ-FN-012
- ตรวจด้วย: ไม่มี AC ตรง ๆ เป็นการยืนยันสภาพแวดล้อมจริง
- ไฟล์ที่แตะ: frontend/vite.config.js, backend/seed_demo.py
- ต้องทำหลัง: T-04, T-10
- เสร็จเมื่อ: เปิด frontend และ backend พร้อมกันแล้วทำการจองจริงจาก UI จนครบจนเห็นสถานะงานที่ถูกสร้างและข้อมูลที่ตอบกลับสอดคล้องกับ API
- สถานะ: พร้อมทำ

## ตารางตรวจความครบ

| AC ID | task ที่ตรวจ AC นี้ |
|---|---|
| AC-07-01 | T-04 |
| AC-07-02 | T-03 |
| AC-07-03 | T-07 |
| AC-07-04 | T-03, T-04, T-10 |
| AC-07-05 | T-05 |
| AC-07-06 | T-05 |
| AC-07-07 | T-05 |
| AC-07-08 | T-09 |
| AC-07-09 | T-08 |
| AC-07-10 | T-06 |

| Constraint ID | task ที่ทำให้เป็นจริง |
|---|---|
| REQ-CON-001 | T-01 ถึง T-11 ทั้งหมด (ตัด A2 ออกจาก R1 ตาม D-07-02) |
| REQ-CON-003 | T-04, T-05 |

## สิ่งที่ยังไม่ทำ

- Q-14: การคืนเงินสำหรับ BR-01 R3 ยังต้องให้ SH-01 ตัดสินใจที่ชัดเจนก่อนนำไป implement ต่อ
- Q-19: ค่า gateway-timeout ระหว่าง 30 วินาทีและค่าจริงในสัญญายังไม่ชัด จึงคงให้ T-05 รอ Q-19
- Q-23: การปลดล็อกเมื่อผู้ใช้ปิดเบราว์เซอร์ยังไม่ชัด แต่ AS-07 ระบุว่าหมดอายุเองตาม holdExpiresAt จึงให้ T-03 ทำต่อไปได้ตามกรอบนี้
- Q-22: `ServiceAddress.geoPoint` ยังไม่มีคำตอบว่าต้องเป็น PII หรือไม่ จึงยังไม่จัดการกฎความลับเพิ่มเติมใน T-02/T-08
- Q-18: ระยะล็อก 10 นาทียังต้องมีการยืนยันเป็นลายลักษณ์อักษรก่อนปิดจุดนี้ หากไม่เข้าใจให้กลับมาปรับ config HOLD_MINUTES
