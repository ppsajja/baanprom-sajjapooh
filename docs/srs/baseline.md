# BL-01 | Specification Baseline B1 | บ้านพร้อม R1

tag: B1 | date: 2569-09-06 | approved-by: SH-01 (เจ้าของ), กลุ่ม X (RE) | next-review: Baseline B2

## ขอบเขตของ baseline

- เข้า B1: REQ สถานะ Approved 23 ข้อ | UC-07, UC-03 (fully dressed) + 3 brief | BR-01..05 | AC-07-01..10, AC-03-01..04 |
  MD-ACT-07, MD-DOM-01, MD-STM-01, MD-CTX-01, MD-SEQ-07-05 | glossary v1.0 | data-dictionary v1.0
- ไม่เข้า B1: REQ สถานะ Draft (REQ-FN-041, REQ-IF-005, REQ-IF-006, REQ-PRV-00x) รอ Q-18/19/22 | REQ-AI-002 (Won't R1) |
  หมวด QA/OP/SEC/CMP จะเติมในบทเรียนกลุ่มความต้องการเชิงคุณภาพ
- คำถามเปิดที่ประกาศพร้อม baseline: Q-14, Q-18, Q-19, Q-20, Q-22 (พฤติกรรมชั่วคราวอยู่ใน spec)
- CC ที่ยังเปิด: CC-02, CC-05, CC-06, CC-07

## กติกาการเปลี่ยนแปลงหลัง B1

1. ทุกการเปลี่ยน REQ/AC/BR/MD ที่อยู่ใน B1 ต้องเปิด CR-xx (ผู้ขอ เหตุผล EV ใหม่ถ้ามี) ไว้ใน specs/<feature>/changes/
2. วิเคราะห์ผลกระทบด้วย RTM: กระทบ REQ/AC/MD/task ใดบ้าง
3. ผู้อนุมัติ: เปลี่ยน Must/ขอบเขต/BR = SH-01 | เปลี่ยนถ้อยคำ/แก้ CC = RE lead
4. เวอร์ชัน: patch (x.y.Z) = แก้ถ้อยคำไม่เปลี่ยนความหมาย | minor (x.Y) = เพิ่ม/แก้ REQ | major (X) = เปลี่ยนขอบเขต
5. Draft ที่ยังไม่เข้า B1 แก้ได้อิสระ แต่ต้องมีสถานะ Draft ชัดเจน

## CR ที่เปิดหลัง B1

| CR | เรื่อง | สถานะ |
|---|---|---|
| CR-01 | AC-07-04 นิยาม "ใกล้เคียง" เป็นไม่เกิน 3 ชั่วโมง | Approved 4 ต.ค. 2569 (RE lead: แก้ถ้อยคำให้วัดได้ ไม่เปลี่ยนความหมาย) |
| CR-02 | ทำให้ REQ-QA-003 วัดได้ด้วย QAS | Proposed รอ SH-01 |
