# Plan: การจองงานบริการซ่อมบำรุง (UC-07)

อ้างอิง: spec.md SPEC-BOOKING v1.2 | Updated: 2569-10-04 | สร้างด้วย /plan จากติส Spec v1.2

## 1. สรุปแนวทาง

- ระบบจะให้ลูกค้าเลือกประเภทงาน ที่อยู่ ช่าง และช่วงเวลา จากช่างที่ว่างใน 7 วัน แล้วล็อกช่วงเวลาตั้งแต่ขั้นยืนยันจนกว่าจะชำระสำเร็จหรือยกเลิก (REQ-FN-008, REQ-FN-041, AS-06, AS-07)
- หลังบ้านจะสร้าง API หลักเพื่อค้นช่าง วาง hold งาน จองงาน จัดการชำระ และคืนเงินตาม BR-01 พร้อมประวัติสถานะ 24 เดือน (REQ-FN-008, REQ-IF-001, REQ-BR-001, REQ-DAT-002)
- ระบบส่งข้อความให้ลูกค้าและช่างจะถูกจัดเก็บในคิวและส่งซ้ำสูงสุด 5 ครั้ง หากยังไม่ได้ส่งสำเร็จ จะยังคงสถานะงานไว้ (REQ-FN-012, ASM-05)
- ฝั่งหน้าเว็บจะให้ผู้ใช้เลือกช่างและยืนยันการชำระแบบ step-by-step เพื่อให้เห็นราคา มัดจำ และเงื่อนไขยกเลิกก่อนสร้างงาน (REQ-FN-008, AC-07-04)
- ส่วนรักษาความปลอดภัยจะใช้การซ่อนข้อมูลติดต่อช่างและ log ที่กรองเบอร์โทรให้พ้นจาก record ของระบบ (REQ-SEC-004, REQ-PRV-002)

## 2. เทคโนโลยีที่ใช้

| สิ่งที่เลือก | มาจาก | หมายเหตุ |
|---|---|---|
| Python 3.12 + FastAPI | ทีมเลือกเอง ไม่ได้มาจาก spec | พื้นฐานของทีมและสอดคล้องกับการทดสอบ API ที่ต้องเรียกเร็วและง่ายต่อ maintenance |
| SQLAlchemy + PostgreSQL สำหรับระบบจริง | ทีมเลือกเอง ไม่ได้มาจาก spec | โครงสร้างเริ่มต้นใน `backend/` ใช้ ORM สำหรับตาราง `jobs`, `time_slots`, `payments`, `refunds` และประวัติสถานะ |
| SQLite สำหรับ test | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้ใน `tests/conftest.py` เพื่อให้เคลียร์ข้อมูลแต่ละ test และรันเร็ว |
| React + Vite สำหรับหน้าแอป | ทีมเลือกเอง ไม่ได้มาจาก spec | โครงเริ่มต้นอยู่ที่ `frontend/` โดยมี `src/pages` สำหรับเลือกช่างและยืนยันการจอง |
| pytest + FastAPI TestClient | ทีมเลือกเอง ไม่ได้มาจาก spec | คำสั่งรัน test หลังบ้าน: `cd backend && pytest -v -k "AC_"` |
| Vitest + @testing-library/react | ทีมเลือกเอง ไม่ได้มาจาก spec | คำสั่งรัน test หน้าจอ: `cd frontend && npm test` |
| Payment Gateway รายเดิม | REQ-CON-003 | ใช้ interface ที่รองรับ gateway จริงตามสัญญา โดยใน test ใช้ mock/fake gateway เพื่อจำลอง approve, decline และ timeout |
| คิวแจ้งเตือนในหน่วยความจำ | ทีมเลือกเอง ไม่ได้มาจาก spec | ใช้ `notify/queue.py` เป็นตัวกลางก่อนส่งไปยัง IF-02; สามารถสลับเป็น Redis ได้ในภายหลัง แต่ยังไม่ใช่ข้อกำหนดใน spec |

โครงโฟลเดอร์เริ่มต้นที่ใช้ร่วมกัน:
- `backend/` สำหรับ API, ORM, business rules, payment flow และ tests
- `frontend/` สำหรับ UI ของ TechnicianPicker, ConfirmBooking และ BookingResult
- `specs/002-booking/` สำหรับ spec, plan, rules, models และ acceptance artifacts

## 3. โมเดลข้อมูล

| Entity | ฟิลด์หลัก | รองรับ FR/Requirement |
|---|---|---|
| Customer | `id`, `name`, `phone` | REQ-PRV-002, REQ-FN-008 |
| ServiceAddress | `id`, `customer_id`, `text`, `geoPoint`, `lat`, `lng` | AS-03, BR-03 |
| Technician | `id`, `name`, `skill`, `base_lat`, `base_lng` | REQ-FN-008, BR-02, BR-03 |
| TimeSlot | `id`, `technician_id`, `start`, `end`, `state`, `holdExpiresAt`, `heldByCustomerId` | REQ-FN-041, AS-07, BR-02 |
| Job | `id`, `customer_id`, `technician_id`, `service_address_id`, `status`, `category`, `depositAmount`, `scheduledStart`, `createdAt` | REQ-FN-008, REQ-DAT-002 |
| JobStatusHistory | `id`, `job_id`, `fromStatus`, `toStatus`, `changedAt` | REQ-DAT-002 |
| Payment | `id`, `job_id`, `amount`, `gatewayRef`, `result`, `createdAt` | REQ-IF-001, REQ-IF-005 |
| Refund | `id`, `job_id`, `amount`, `rule`, `createdAt` | REQ-BR-001 |
| NotificationQueueItem | `id`, `job_id`, `recipientType`, `recipientId`, `message`, `status`, `attemptCount`, `nextAttemptAt` | REQ-FN-012, ASM-05 |

หมายเหตุ:
- ไม่มีฟิลด์เลขบัตรประชาชนหรือข้อมูล PII เพิ่มเติมที่นอกเหนือจาก `Customer.phone` และ `ServiceAddress.geoPoint` ตาม spec
- `ServiceAddress.geoPoint` ถูกยอมให้เก็บไว้ในระบบ แต่ยังถูกค้างไว้ให้ตอบคำถาม `Q-22` ก่อนชัดเจนว่าต้องมี rule รักษาความลับเพิ่มเติมหรือไม่

## 4. API / หน้าจอ

| รายการ | Method / Path | Input / Output หลัก | รองรับ |
|---|---|---|---|
| ค้นช่างว่าง | `GET /technicians` | Input: `category`, `addressId`, `customerId`; Output: รายการช่างพร้อมช่วงว่าง 7 วัน | REQ-FN-008, BR-02, BR-03 |
| ล็อกช่วงเวลา | `POST /slots/{slotId}/hold` | Input: `customerId`; Output: `holdExpiresAt` หรือ 409 | REQ-FN-041 |
| สร้างงาน | `POST /bookings` | Input: `customerId`, `slotId`, `addressId`, `category`; Output: `jobId`, `status`, `depositAmount` | REQ-FN-008, REQ-IF-001 |
| ดูสถานะงาน | `GET /jobs/{jobId}` | Output: job details, status และ payment state | REQ-FN-008, REQ-DAT-002 |
| ดูมุมมองช่าง | `GET /jobs/{jobId}/technician-view` | Output: ข้อมูลงานสำหรับช่าง พร้อมเงื่อนไขเปิดเผยเบอร์ตามเวลา | REQ-SEC-004 |
| ยกเลิก/คืนเงิน | `POST /jobs/{jobId}/cancel` | Input: `reason`, `cancelledBy`; Output: status ใหม่และ refund ถ้าควรคืน | REQ-BR-001 |
| ตรวจสถานะ gateway | `POST /payments/status-inquiry` | Input: `gatewayRef`; Output: approved / declined / timeout | REQ-IF-005 |
| ส่งข้อความ | `POST /notifications/queue` หรือ internal job | Input: `jobId`, `recipientType`, `message`; Output: queue confirmation | REQ-FN-012, ASM-05 |
| หน้ารับข้อมูล | `TechnicianPicker` | เลือกประเภทงาน/ที่อยู่/ช่าง/ช่วงเวลา | REQ-FN-008 |
| หน้ายืนยัน | `ConfirmBooking` | แสดงราคา มัดจำ และเงื่อนไขยกเลิกก่อนยืนยัน | AC-07-04 |
| หน้าผล | `BookingResult` | แสดงสถานะงานหลังจองสำเร็จ | REQ-FN-008 |

## 5. ตารางตรวจ Constraints

| Constraint ID | ถูกนำไปใช้ที่ไหนใน plan | สถานะ |
|---|---|---|
| REQ-CON-001 | ใช้เป็นเงื่อนไขในการจำกัด scope ในแผนงานให้ไม่รวม A2 จองแทนลูกค้าโดย call center ใน R1 | ใช้แล้ว |
| REQ-CON-003 | ใช้ใน interface payment gateway และ mock gateway สำหรับสัญญาเดิมถึงธันวาคม 2569 | ใช้แล้ว |
| REQ-IF-001 | ใช้ใน flow สร้างงานและชำระผ่าน gateway แบบ `authorize` ก่อน `capture` | ใช้แล้ว |
| REQ-IF-005 | ใช้ใน flow timeout: สำหรับ gateway timeout ให้เรียก status inquiry ด้วย reference เดิม | ใช้แล้ว |
| REQ-SEC-004 | ใช้ใน endpoint `/jobs/{jobId}/technician-view` เพื่อซ่อนเบอร์จนกว่าจะถึงช่วงเวลาเปิดเผย | ใช้แล้ว |
| REQ-PRV-002 | ใช้ใน layer privacy logging และ validation ที่ไม่ให้เบอร์โทรถูกบันทึกลง log | ใช้แล้ว |
| REQ-DAT-002 | ใช้ใน model และ job history flow เพื่อบันทึกการเปลี่ยนแปลงสถานะ 24 เดือน | ใช้แล้ว |

## 6. แผนทดสอบจาก Acceptance Criteria

| AC ID | ชื่อ test | ทดสอบอย่างไร |
|---|---|---|
| AC-07-01 | `test_AC_07_01_booking_success` | ตรวจว่าลูกค้าเลือกช่างและช่วงเวลาได้จริง แล้วระบบสร้าง job และ payment อย่างถูกต้อง |
| AC-07-02 | `test_AC_07_02_technician_availability` | ตรวจว่าช่วงที่ถูกล็อกแล้วไม่ปรากฏในผลค้นหาช่วงเวลาของลูกค้าอื่น |
| AC-07-03 | `test_AC_07_03_notifications_sent` | ตรวจว่าหลังสร้างงาน ระบบเติมข้อความในคิวให้ลูกค้าและช่าง และส่งภายใน 60 วินาที |
| AC-07-04 | `test_AC_07_04_booking_conflict` | ตรวจว่าถ้า slot ถูกจองแล้วจะได้ 409 และหน้าจอแสดงช่วงทางเลือกอื่นที่ใกล้เคียงไม่เกิน 3 ชั่วโมง |
| AC-07-05 | `test_AC_07_05_gateway_timeout` | จำลอง gateway timeout แล้วตรวจว่าระบบทำ status inquiry ด้วย reference เดิม |
| AC-07-06 | `test_AC_07_06_gateway_declined` | จำลอง gateway declined แล้วตรวจว่าระบบยกเลิกงานหรือหยุดขั้นตอนให้ถูกต้อง |
| AC-07-07 | `test_AC_07_07_recovery_after_timeout` | จำลอง timeout แล้ว inquiry ตอบ approved ให้ตรวจว่ามีการ capture อย่างเดียวและไม่โดนเรียกชำระซ้ำ |
| AC-07-08 | `test_AC_07_08_scaled_search_latency` | ใช้สภาวะจำลอง 500 คน/20 request หรือ equivalent เพื่อวัด p95 ให้ต่ำกว่า 2 วินาที |
| AC-07-09 | `test_AC_07_09_phone_visibility` | ตรวจว่าช่างเห็นเบอร์เฉพาะ 2 ชั่วโมงก่อนนัดจนปิดงาน และ log ไม่มีเบอร์โทร |
| AC-07-10 | `test_AC_07_10_refund_rules` | ตรวจทุกแถว BR-01 (ยกเว้น R3 ที่ยังรอ Q-14) ว่า refund ครบและ exact amount ถูกต้อง |

## 7. ลำดับงาน

1. ตั้งต้นระบบข้อมูลและโครงสร้าง ORM: users, technicians, slots, jobs, payments, refunds, history (REQ-DAT-002, REQ-PRV-002)
2. สร้างกระบวนการค้นช่างและเลือกช่วงเวลา: filter ตามประเภท/ที่อยู่/ระยะทางและ 7 วัน (REQ-FN-008, BR-02, BR-03, AS-06)
3. สร้าง flow ล็อกช่วงเวลาและหมดอายุ: `holdExpiresAt`, `AS-07`, REQ-FN-041
4. สร้าง flow จองงานและเรียก gateway `authorize` ก่อน `capture`: `POST /bookings` (REQ-IF-001, AC-07-01, AC-07-04)
5. สร้าง flow timeout และ status inquiry ตาม gateway timeout (REQ-IF-005, AC-07-05, AC-07-06, AC-07-07)
6. สร้างกฎคืนเงินตาม BR-01 และ endpoint cancel/refund (REQ-BR-001, AC-07-10)
7. สร้างคิวแจ้งเตือนและ retry mechanism สูงสุด 5 ครั้ง (REQ-FN-012, ASM-05, AC-07-03)
8. สร้าง endpoint มุมมองช่างและตรวจสอบการเปิดเผยเบอร์ตามเวลา (REQ-SEC-004, AC-07-09)
9. ทดสอบโหลดและประสิทธิภาพ p95 สำหรับ AC-07-08 (REQ-QA-003)
10. สร้างหน้า UI ที่เรียก API ที่มีอยู่: TechnicianPicker, ConfirmBooking, BookingResult (AC-07-04)

## 8. สิ่งที่ยังไม่ทำ

- Q-14: BR-01 R3 ยังไม่รู้ว่าจะคืนเงินเท่าไรเมื่อช่างเดินทางแล้วลูกค้าหยุดจอง ดังนั้นส่วน R3 จะยังไม่สร้าง logics ที่ถาวรจนกว่าจะได้คำตอบ
- Q-18: ระยะล็อก 10 นาทียังต้องยืนยันเป็นลายลักษณ์อักษรให้ครบถ้วนก่อนยืนยันค่า config สุดท้าย
- Q-19: gateway timeout ยังคงมีค่า 30 วินาทีแบบชั่วคราวตาม spec จนกว่าจะได้รับคำตอบจาก Dev lead
- Q-22: การจัดการ `ServiceAddress.geoPoint` เป็น PII หรือไม่ยังต้องให้ RE lead ตัดสินก่อนปรับกฎความลับในระบบ
- Q-23: ถ้าลูกค้าปิดเบราว์เซอร์ระหว่างล็อก ต้องยืนยันว่าใครเป็นผู้ปลดล็อกและการหมดอายุจะจัดการอย่างไร
- A2: การจองแทนลูกค้าโดย call center ยังถูกเลื่อนไป R2 ตาม D-07-02 และจะยังไม่รวมไว้ใน plan นี้
