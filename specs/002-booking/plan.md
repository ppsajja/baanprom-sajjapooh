# Plan: การจองงานบริการซ่อมบำรุง (UC-07)

อ้างอิง: spec.md SPEC-BOOKING v1.1 (B1 + v2 หลัง /clarify) | Updated: 2569-10-04 | สร้างด้วย /plan แล้วทีมตรวจแล้ว (plan v1)
หลังจากนั้น: ข้อ 5 เพิ่มแถว REQ-IF-005 "ใช้แล้ว" เมื่อ Q-19 มีค่าชั่วคราว (แก้โดยทีม 4 ต.ค.)

## 1. สรุปแนวทาง

- ลูกค้าค้นช่างว่างตามประเภทงานและที่อยู่ (BR-02, BR-03) ล็อกช่วงเวลา 10 นาที (REQ-FN-041) แล้วยืนยันพร้อมชำระมัดจำ
- หลังบ้านเป็น API (Python FastAPI) เก็บข้อมูลด้วย SQLAlchemy ต่อ PostgreSQL ในระบบจริง ตอน test ใช้ SQLite ในหน่วยความจำ
- การชำระเป็น authorize แล้ว capture (D-07-03) ถ้า gateway ไม่ตอบใน gateway-timeout ให้ status-inquiry ด้วย reference เดิม (REQ-IF-005) ก่อนตัดสิน
- การแจ้งเตือนไม่รอผล: API วางข้อความลงคิว ตัวส่งแยกทำงาน (REQ-FN-012 ภายใน 60 วินาที)
- ช่างเห็นเบอร์ลูกค้าผ่าน endpoint มุมมองช่างเท่านั้น ซึ่งซ่อนเบอร์จนถึง 2 ชั่วโมงก่อนนัด (REQ-SEC-004) และ log ของระบบไม่มีฟิลด์เบอร์โทร (REQ-PRV-002)
- คืนมัดจำตาม BR-01 เป็นตารางในโค้ด 1 ที่ (rules R1 ถึง R6) R3 ใช้พฤติกรรมชั่วคราวของ Q-14 ตาม spec ข้อ 9

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Payment Gateway รายเดิม (IF-01) | REQ-CON-003 | ในโค้ดเป็น interface `Gateway` ตอน test ใช้ `FakeGateway` ที่สั่งให้ approved / declined / ไม่ตอบ ได้ |
| Python 3.12 + FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | ค่าเริ่มต้นของรายวิชา |
| SQLAlchemy 2 + PostgreSQL 16 | ทีมเลือกเอง ไม่ได้มาจาก spec | ต่อฐานข้อมูลผ่านตัวแปร `DATABASE_URL` ตอน test ใช้ `sqlite:///:memory:` ไม่ต้องติดตั้งอะไรเพิ่ม |
| pytest + httpx (TestClient) | ทีมเลือกเอง ไม่ได้มาจาก spec | ทุก test ชื่อขึ้นต้น test_AC_07_xx |
| React 19 (Vite) + Tailwind CSS 4 | ทีมเลือกเอง ไม่ได้มาจาก spec | โครงเริ่มต้นอยู่ใน `frontend/` แล้ว |
| Vitest + React Testing Library | ทีมเลือกเอง ไม่ได้มาจาก spec | test หน้าจอใช้ API จำลอง ไม่ต้องรันหลังบ้าน |
| คิวในหน่วยความจำ (notify/queue.py) | ทีมเลือกเอง ไม่ได้มาจาก spec | ระบบจริงเปลี่ยนเป็น Redis ได้โดยแก้ไฟล์เดียว ตอน test อ่านคิวตรง ๆ |

library ทั้งหมดอยู่ใน `backend/requirements.txt`
รัน test หลังบ้าน: `cd backend && pytest -v -k "AC_"`
เปิดหลังบ้าน: `cd backend && uvicorn app.main:app --reload --port 8000` (หน้าจอเรียกผ่าน `/api` ซึ่ง Vite ส่งต่อให้)
รัน test หน้าจอ: `cd frontend && npm test` เปิดดูหน้าจอ: `cd frontend && npm run dev`

### โครงไฟล์

```
backend/
  requirements.txt
  pytest.ini
  app/
    main.py                     สร้าง FastAPI app รวม router และสร้างตารางตอนเริ่ม
    config.py                   DATABASE_URL, HOLD_MINUTES (Q-18), GATEWAY_TIMEOUT_SECONDS (Q-19), PHONE_REVEAL_HOURS
    db/models.py                ตาราง customers, service_addresses, technicians, time_slots, jobs, job_status_history, payments, refunds
    db/session.py               engine, SessionLocal, get_db
    db/migrations/m001_init.py  ฟังก์ชัน upgrade(engine) สร้างทุกตาราง
    clock.py                    เวลาปัจจุบันที่ test กำหนดได้ (now=...)
    technicians/service.py      ค้นช่างว่าง (BR-02, BR-03, AS-06) และหาช่วงใกล้เคียง (AC-07-04)
    technicians/router.py       GET /technicians
    booking/service.py          ล็อกช่วงเวลา (REQ-FN-041) และสร้างงาน (REQ-FN-008)
    booking/router.py           POST /slots/{id}/hold, POST /bookings, GET /jobs/{id}, GET /jobs/{id}/technician-view
    payments/gateway.py         interface Gateway + FakeGateway (IF-01)
    payments/service.py         authorize + timeout + status-inquiry + capture (REQ-IF-001, REQ-IF-005)
    refund/rules.py             ตาราง BR-01 R1 ถึง R6
    refund/service.py           ยกเลิกงานและสร้าง Refund (REQ-BR-001)
    refund/router.py            POST /jobs/{id}/cancel
    notify/queue.py             คิวข้อความและเวลาส่ง (REQ-FN-012)
    privacy.py                  ตัวกรอง log ไม่ให้มีเบอร์โทร (REQ-PRV-002)
  tests/
    conftest.py                 ฐานข้อมูลในหน่วยความจำ, FakeGateway, นาฬิกาจำลอง, ข้อมูลตั้งต้น (ช่าง ประสิทธิ์ ฯลฯ)
    test_booking.py             AC-07-01, 02, 03, 04
    test_payment.py             AC-07-05, 06, 07
    test_privacy.py             AC-07-09
    test_refund.py              AC-07-10 (R1, R2, R4, R5, R6; R3 ข้ามรอ Q-14)
    test_load_scaled.py         AC-07-08 แบบย่อส่วน (รอ CR-02 จึงยังเป็นฉบับทดลอง)
frontend/
  src/api/client.js             เรียก API ตามสัญญาข้อ 4
  src/pages/TechnicianPicker.jsx   เลือกประเภทงาน ที่อยู่ แล้วเลือกช่างและช่วงเวลา (ล็อก)
  src/pages/ConfirmBooking.jsx     แสดงราคา มัดจำ เงื่อนไข BR-01 แล้วกดยืนยัน รับ 409 แสดงช่วงใกล้เคียง
  src/pages/BookingResult.jsx      แสดงหมายเลขงานและสถานะ
  src/__tests__/AC-07-04.test.jsx  test หน้าจอของ AC-07-04
```

## 3. โมเดลข้อมูล

| ตาราง | ฟิลด์หลัก | รองรับ |
|---|---|---|
| customers | id, name, phone (PII) | REQ-PRV-002 |
| service_addresses | id, customer_id, text, lat, lng | AS-03, BR-03 |
| technicians | id, name, skills (คั่นด้วยจุลภาค), base_lat, base_lng | BR-03 |
| time_slots | id, technician_id, start, end, state (ว่าง / ล็อกชั่วคราว / จองแล้ว), held_by_customer_id, hold_expires_at | REQ-FN-041, BR-02, AS-07 |
| jobs | id, customer_id, technician_id, slot_id, address_id, category, status (8 ค่า), deposit_amount, scheduled_start, created_at | REQ-FN-008, REQ-DAT-002 |
| job_status_history | id, job_id, from_status, to_status, at | REQ-DAT-002 (ประวัติ 24 เดือน) |
| payments | id, job_id, amount, gateway_ref, result (สำเร็จ / ล้มเหลว / หมดเวลา), authorized_at | REQ-IF-001 |
| refunds | id, job_id, amount, rule (R1..R6) | REQ-BR-001 |

- ตาราง log ไม่มี ระบบใช้ logging ของ Python ผ่าน privacy.py ที่กรองรูปแบบเบอร์โทรออก (REQ-PRV-002)
- status ของ jobs ใช้ชื่อในโค้ดจาก glossary.md เท่านั้น (pending_payment, confirmed, auto_cancelled, rematching, en_route, in_progress, done, cancelled)

## 4. API / หน้าจอ

| รายการ | input / output หลัก | รองรับ |
|---|---|---|
| GET /technicians | in: category, address_id, customer_id / out: ช่างและช่วงเวลาที่ว่างใน 7 วัน (ไม่รวมช่วงที่จองแล้วหรือล็อกโดยคนอื่น) | REQ-FN-008, BR-02, BR-03, AS-06 |
| POST /slots/{slot_id}/hold | in: customer_id / out: hold_expires_at หรือ 409 ถ้าถูกล็อกโดยคนอื่น | REQ-FN-041 |
| POST /bookings | in: customer_id, slot_id, address_id, category / out: 201 job (confirmed) หรือ 409 {reason: slot_taken, alternatives[]} หรือ 402 {reason: payment_failed} | REQ-FN-008, REQ-IF-001, REQ-IF-005, AC-07-04 |
| GET /jobs/{id} | out: งานและสถานะ (มุมมองลูกค้า) | REQ-FN-008 |
| GET /jobs/{id}/technician-view | in: technician_id, now / out: งาน; ฟิลด์ customer_phone มีเฉพาะเมื่ออยู่ในช่วง 2 ชั่วโมงก่อนนัดจนปิดงาน | REQ-SEC-004 |
| POST /jobs/{id}/cancel | in: cancelled_by (customer / system), now / out: สถานะใหม่ และ refund ถ้ามี หรือ 409 (R3 ชั่วคราว, R6) | REQ-BR-001 |
| GET /notifications/queue | out: ข้อความในคิว (ใช้ตรวจใน test และหน้าแอดมิน) | REQ-FN-012 |
| หน้าเลือกช่าง (TechnicianPicker) | เรียก GET /technicians แล้ว POST /slots/{id}/hold | REQ-FN-008, REQ-FN-041 |
| หน้ายืนยัน (ConfirmBooking) | แสดงมัดจำและ BR-01 แล้ว POST /bookings ถ้าได้ 409 แสดง "ช่วงเวลาถูกจองแล้ว" และปุ่มเลือกช่วงใกล้เคียง | AC-07-04 |
| หน้าผลการจอง (BookingResult) | แสดงหมายเลขงานและสถานะ "ยืนยันแล้ว" | REQ-FN-008 |

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| REQ-CON-003 | ข้อ 2: gateway รายเดิมอยู่หลัง interface `Gateway` ไม่เปลี่ยนราย | ใช้แล้ว |
| REQ-CON-001 | ข้อ 7: ลำดับงานตัด A2 ออก (D-07-02) ให้พอ 8 สัปดาห์ | ใช้แล้ว |
| REQ-PRV-002 | ข้อ 3: ไม่มีตาราง log ที่เก็บเบอร์ และ privacy.py กรอง log | ใช้แล้ว |
| REQ-SEC-004 | ข้อ 4: GET /jobs/{id}/technician-view ซ่อนเบอร์จนก่อนนัด 2 ชั่วโมง | ใช้แล้ว |
| REQ-IF-001 | ข้อ 4: POST /bookings authorize ก่อน capture | ใช้แล้ว |
| REQ-IF-005 | payments/service.py: timeout แล้ว status-inquiry ด้วย ref เดิม | ใช้แล้ว (ค่า timeout ชั่วคราว 30 วินาที รอ Q-19) |
| REQ-DAT-002 | ข้อ 3: jobs.status 8 ค่า + job_status_history | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-07-01 | test_AC_07_01_booking_success | ล็อก slot, POST /bookings กับ FakeGateway approved แล้วตรวจ job confirmed, slot จองแล้ว, payment 1 รายการ |
| AC-07-02 | test_AC_07_02_slot_not_rebookable | ทำให้ slot จองแล้ว แล้ว GET /technicians ด้วยลูกค้าอื่น ตรวจว่าไม่มี slot นั้น |
| AC-07-03 | test_AC_07_03_notify_both_within_60s | หลังจองสำเร็จ อ่านคิว ตรวจว่ามีข้อความถึงลูกค้าและช่าง และ due_at ไม่เกิน created_at + 60 วินาที |
| AC-07-04 | test_AC_07_04_no_charge_when_slot_taken | ลูกค้าอื่นจองก่อน แล้วสมชายยืนยัน ตรวจ 409, ไม่มี payment ของสมชาย, alternatives อย่างน้อย 2 และห่างไม่เกิน 3 ชั่วโมง |
| AC-07-05 | test_AC_07_05_payment_timeout | FakeGateway ไม่ตอบ และ inquiry ตอบ unknown ตรวจ job auto_cancelled, slot ว่าง, ไม่มี payment สำเร็จ |
| AC-07-06 | test_AC_07_06_payment_declined | FakeGateway declined ตรวจ 402, job auto_cancelled, slot ว่าง, มีข้อความแจ้งลูกค้า |
| AC-07-07 | test_AC_07_07_inquiry_approved_no_double_charge | FakeGateway ไม่ตอบ แต่ inquiry ตอบ approved ตรวจ job confirmed, authorize ถูกเรียก 1 ครั้ง, payment สำเร็จ 1 รายการ |
| AC-07-08 | test_AC_07_08_search_under_load_scaled | ยิง GET /technicians 20 คำขอพร้อมกัน (ย่อจาก 500) ตรวจว่า 19 ใน 20 ไม่เกิน 2 วินาที ผลจริงต้องวัดบนเครื่องทดสอบ (รอ CR-02) |
| AC-07-09 | test_AC_07_09_phone_hidden_until_2h | technician-view ที่ now = 11:30 ไม่มี customer_phone, ที่ 12:00 มี และ log ที่จับได้ไม่มีเบอร์ |
| AC-07-10 | test_AC_07_10_refund_R1 ถึง R6 (parametrize) | ตั้งสถานะงานตามแถว แล้ว POST /jobs/{id}/cancel ตรวจสถานะและยอดคืน R3 ข้ามด้วยเหตุผล "รอ Q-14" |
| AC-07-04 (หน้าจอ) | AC-07-04.test.jsx | API จำลองตอบ 409 พร้อม alternatives 2 ช่วง ตรวจว่าหน้าจอแสดง "ช่วงเวลาถูกจองแล้ว" และปุ่ม 2 ปุ่ม |

หลักแยก: AC ที่ Then บอกว่า "บันทึก" หรือ "สถานะ" ตรวจที่หลังบ้าน AC ที่ Then บอกว่า "แจ้ง" หรือ "เสนอ" ต้องมี test หน้าจอด้วย

## 7. ลำดับงาน

หลังบ้าน
1. ตั้งฐานข้อมูลและตาราง (REQ-DAT-002, REQ-PRV-002)
2. ล็อกช่วงเวลาและหมดอายุ (REQ-FN-041, AS-07)
3. ค้นช่างว่าง (REQ-FN-008, BR-02, BR-03, AC-07-02)
4. POST /bookings สร้างงานและตัดมัดจำ (REQ-FN-008, REQ-IF-001, AC-07-01, AC-07-04)
5. timeout และ status-inquiry (REQ-IF-005, AC-07-05, 06, 07)
6. คืนมัดจำตาม BR-01 (REQ-BR-001, AC-07-10)
7. คิวแจ้งเตือน (REQ-FN-012, AC-07-03)
8. มุมมองช่างซ่อนเบอร์ และตัวกรอง log (REQ-SEC-004, REQ-PRV-002, AC-07-09)
9. test ย่อส่วนรับโหลด (REQ-QA-003, AC-07-08)

หน้าจอ (ใช้ API จำลองตามสัญญาข้อ 4 จึงเริ่มพร้อมหลังบ้านได้)
10. หน้าเลือกช่าง หน้ายืนยัน หน้าผล (REQ-FN-008, AC-07-04 หน้าจอ)
11. ต่อหน้าจอกับ API จริง ทำหลังข้อ 3, 4, 5 และ 10

## 8. สิ่งที่ยังไม่ทำ

- Q-14 (BR-01 R3) ยังไม่มีคำตอบ ข้อ 6 ทำได้เฉพาะ R1, R2, R4, R5, R6 ส่วน R3 ใช้พฤติกรรมชั่วคราว "ไม่อนุญาต" ตาม spec ข้อ 9 (D-07-04)
- Q-18 และ Q-19 เป็น config พร้อมค่าชั่วคราว ถ้าคำตอบมาต่างจากนี้ แก้ config ไม่ต้องแก้โค้ด
- AC-07-08 ฉบับวัดได้รอ CR-02 test ที่เขียนเป็นฉบับทดลองย่อส่วน
- A2 จองแทนโดย call center ไม่ทำใน R1 (D-07-02)
