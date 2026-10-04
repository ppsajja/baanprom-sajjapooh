# ตารางผล AC หลังรัน test ทั้งชุด (specs/002-booking/test-run.txt)

รันวันที่ 4 ต.ค. 2569 | คำสั่ง: cd backend && pytest -v -k "AC_" | cd frontend && npm test
สถานะที่ใช้: ผ่าน | ไม่ผ่าน | ยังไม่มี test | รอ Q-xx

## รอบที่ 1 (ก่อนแก้ GAP-07)

| AC ID | REQ ที่พิสูจน์ | test | task | ผล | หมายเหตุ |
|---|---|---|---|---|---|
| AC-07-01 | REQ-FN-008 | test_AC_07_01_booking_success | T-04 | ผ่าน | หลังเพิ่ม assert จำนวน Payment (GAP-06) |
| AC-07-02 | REQ-FN-008, BR-02, BR-03 | test_AC_07_02_slot_not_rebookable | T-03 | ผ่าน | |
| AC-07-03 | REQ-FN-012 | test_AC_07_03_notify_both_within_60s | T-07 | ผ่าน | |
| AC-07-04 | REQ-FN-041 (CR-01) | test_AC_07_04_no_charge_when_slot_taken | T-02, T-04 | ผ่าน | พิสูจน์ชั้น 3: เปลี่ยน ALTERNATIVE_WINDOW_HOURS เป็น 1 แล้ว test พัง |
| AC-07-04 (หน้าจอ) | REQ-FN-041 | AC-07-04.test.jsx | T-10 | ผ่าน | |
| AC-07-05 | REQ-IF-001, REQ-IF-005 | test_AC_07_05_payment_timeout | T-05 | ไม่ผ่าน | assert timeout 30 วินาที แต่ config ใช้ 60 (GAP-07 สาเหตุ spec) |
| AC-07-06 | REQ-IF-001 | test_AC_07_06_payment_declined | T-05 | ผ่าน | |
| AC-07-07 | REQ-IF-005 | test_AC_07_07_inquiry_approved_no_double_charge | T-05 | ผ่าน | |
| AC-07-08 | REQ-QA-003 | ไม่มี | T-09 | ยังไม่มี test | ต้องการผู้ใช้ 500 คน ทดสอบย่อส่วนตามที่ทีมตัดสิน ดู CR-02 |
| AC-07-09 | REQ-SEC-004, REQ-PRV-002 | test_AC_07_09_phone_hidden_until_2h | T-08 | ผ่าน | พิสูจน์ชั้น 3: เปลี่ยน PHONE_REVEAL_HOURS เป็น 3 แล้ว test พัง |
| AC-07-10 R1, R2, R4, R5, R6 | REQ-BR-001 | test_AC_07_10_refund (parametrize), _R6_not_allowed | T-06 | ผ่าน | |
| AC-07-10 R3 | REQ-BR-001 | test_AC_07_10_refund_R3 (skip) | T-06 | รอ Q-14 | พฤติกรรมชั่วคราวตรวจด้วย _R3_temporary_behaviour ผ่าน |

สรุปรอบที่ 1: AC ทั้งหมด 10 ข้อ | มี test 9 | ผ่าน 8 | ไม่ผ่าน 1 | ยังไม่มี test 1 | รอ Q 1 (R3 ของ AC-07-10)
ไม่ผ่านเพราะสเปก 1 (GAP-07) | เพราะ AI 0 | เพราะ test 0
สเปกคุม AI ได้: 8 ใน 9 AC ที่มี test จุดที่หลุดคือ timeout ของ gateway ที่สเปก (30 วินาที) กับ Interface Contract IF-01 ที่ AI อ่าน (60 วินาที) บอกไม่ตรงกัน

## รอบที่ 2 (หลังตั้ง GATEWAY_TIMEOUT_SECONDS ตาม spec ข้อ 9 = 30 และเพิ่ม test ย่อส่วน T-09) = test-run.txt ปัจจุบัน

| AC ID | ผล | เปลี่ยนจากรอบ 1 |
|---|---|---|
| AC-07-05 | ผ่าน | แก้ config ให้ตรง spec (ค่าจริงรอ Q-19) |
| AC-07-08 | ผ่าน (ย่อส่วน 20 จาก 500, 19 ใน 20 ไม่เกิน 2 วินาที) | เพิ่ม test_AC_07_08_search_under_load_scaled ไม่ใช่ผลตรวจรับจริง รอ CR-02 |
| อื่น ๆ | เหมือนรอบ 1 | |

สรุปรอบที่ 2: AC ทั้งหมด 10 ข้อ | มี test 10 | ผ่าน 9 (1 ข้อเป็นแบบย่อส่วน) | ไม่ผ่าน 0 | รอ Q 1 (R3)
pytest: 15 passed, 1 skipped | vitest: 1 passed
