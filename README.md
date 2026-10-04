# baanprom-swreqspec

repo ตัวอย่างของรายวิชา 517 511 Requirements Engineering (AI-Native RE)
ภาควิชาคอมพิวเตอร์ คณะวิทยาศาสตร์ มหาวิทยาลัยศิลปากร | ภาคต้น 1/2569

เคส: บ้านพร้อม (แพลตฟอร์มจองช่างซ่อมบ้าน) feature ที่ทำครบรอบคือ UC-07 จองงานบริการซ่อมบำรุง
ข้อมูลทั้งหมดในเคสนี้เป็นข้อมูลสมมติเพื่อการสอน

repo นี้คือ "สภาพหลังจบบทเรียน ให้ AI สร้างจากสเปก" ของกลุ่มตัวอย่าง (กลุ่ม X)
ทุกไฟล์ที่ AI สร้างถูกเก็บไว้ตามที่สร้างจริง รวมถึงจุดที่ AI ทำผิดกติกาและทีมสั่งแก้ (ดู gaps.md และ prompt-log.md)

## ทีม

- ชื่อทีม: กลุ่ม X (ตัวอย่างของรายวิชา)
- สมาชิก: สมาชิก A, สมาชิก B, สมาชิก C, สมาชิก D
- เครื่องมือ AI ที่ใช้: Copilot Chat โหมด Agent ใน GitHub Codespaces (ผู้สอนเดโมด้วย Claude Code)

## โครงของ repo

```
README.md                      ไฟล์นี้
AGENTS.md                      กติกาที่ AI ต้องทำตาม 7 ข้อ + ข้อ 8 ของรายวิชา 517 511
CLAUDE.md                      ชี้ไป AGENTS.md (สำหรับ Claude Code)
prompt-log.md                  บันทึกทุกคำสั่ง คำถาม คำตอบ และสิ่งที่ AI เดา (เพิ่มต่อท้ายเท่านั้น)
docs/srs/                      ต้นฉบับจากบทเรียนก่อนหน้า: catalogue, UC-07, glossary, baseline B1
docs/agent-pack-README.md      วิธีติดตั้งและใช้ชุดคำสั่ง
specs/README.md                ดัชนี feature
specs/002-booking/             feature ที่ทำครบรอบ (ดูตารางด้านล่าง)
backend/                       Python FastAPI + SQLAlchemy (test ใช้ SQLite ในหน่วยความจำ)
frontend/                      React (Vite) + Tailwind CSS + Vitest
.github/prompts/               คำสั่ง /clarify /plan /tasks /implement สำหรับ Copilot
.claude/commands/              คำสั่งชุดเดียวกัน สำหรับ Claude Code
.cursor/commands/              คำสั่งชุดเดียวกัน สำหรับ Cursor
```

## ไฟล์ใน specs/002-booking/ และใครสร้าง

| ไฟล์ | ใครสร้าง | เกิดในขั้นไหน |
|---|---|---|
| spec.md | กลุ่มเขียน v1, AI แก้เป็น v2 หลัง /clarify, กลุ่มแก้ v3 ผ่าน CR-01 | บทเรียน Living Specification และ /clarify |
| booking.feature | กลุ่ม (จากบทเรียน Acceptance Criteria) | ก่อน /clarify |
| rules.md, models.md | กลุ่ม (สรุปจาก docs/srs) | ก่อน /clarify |
| plan.md | AI (/plan) ทีมตรวจแล้ว | /plan |
| plan-compare.md | กลุ่ม | เทียบ plan ของ AI กับที่กลุ่มเขียนเอง |
| tasks.md | AI (/tasks) ทีมสั่งแก้ 1 รอบ | /tasks |
| tasks-compare.md | กลุ่ม | เทียบ tasks ของ AI กับที่กลุ่มเขียนเอง |
| test-run.txt | pytest (ผลรันจริง) | รัน test ทั้งชุด |
| ac-results.md | กลุ่ม | กรอกจาก test-run.txt |
| gaps.md | กลุ่ม | ทุกครั้งที่พบจุดพลาด |
| changes/CR-01.md, CR-02.md | กลุ่ม | เมื่อต้องแก้สิ่งที่อยู่ใน Baseline B1 |
| quality-requirements.md | กลุ่ม | บทเรียนข้อกำหนดคุณภาพ |

## วิธีรัน

หลังบ้าน

```
cd backend
pip install -r requirements.txt
pytest -v -k "AC_" 2>&1 | tee ../specs/002-booking/test-run.txt
uvicorn app.main:app --reload --port 8000
```

หน้าจอ

```
cd frontend
npm install
npm test
npm run dev
```

(ถ้าเปิดด้วย GitHub Codespaces คำสั่ง pip install และ npm install ถูกรันให้แล้วตอนสร้างเครื่อง)

## ถ้าจะทำของกลุ่มเอง

อย่า fork repo นี้ ให้ไปที่ template ของรายวิชา github.com/ppsajja/reqeng-template กด Use this template
แล้วเอาไฟล์ของกลุ่มใส่ตาม README ของ template repo นี้มีไว้เปิดดูเทียบทีละขั้นเท่านั้น

## สิ่งที่รู้อยู่แล้วว่ายังไม่ใช่ของจริง

- ทุก endpoint รับ `now=...` ใน query เพื่อให้ test กำหนดเวลาได้ (backend/app/clock.py) ก่อนขึ้นระบบจริงต้องปิดช่องนี้
- FakeGateway ใช้แทน Payment Gateway จริง (IF-01) และคิวแจ้งเตือนอยู่ในหน่วยความจำ (IF-02)
- ระยะทาง BR-03 ใช้สูตรคำนวณจากพิกัดแทนบริการแผนที่ (IF-03)
- AC-07-08 ผ่านแบบย่อส่วน 20 คำขอเท่านั้น ผลตรวจรับจริงต้องวัดบนเครื่องทดสอบ (รอ CR-02)
- `backend/seed_demo.py` ใส่ข้อมูลสมมติไว้เปิดดูหน้าจอ ไม่ใช่ส่วนของระบบ

## Reflection ของกลุ่ม X (5 บรรทัด)

1. คำถามของ AI ที่ไม่คาดคิด: ถามว่า "ใกล้เคียง" ใน AC-07-04 หมายถึงกี่ชั่วโมง ทั้งทีมไม่เคยสงสัยเลยจนกระทั่งต้องเขียน assert
2. คำถามของเพื่อนที่ AI ไม่ถาม: กลุ่มข้างเคียงถามว่าถ้าลูกค้าปิดเบราว์เซอร์ระหว่างล็อกช่วงเวลา ใครปลดล็อก (AI ถือว่าหมดอายุเองโดยไม่ถาม)
3. กฎที่ AI ละเมิดและจับได้: /implement T-01 แตะ router.py ซึ่งเป็นไฟล์ของ T-04 (กติกา "แตะเฉพาะไฟล์ในช่องไฟล์ที่แตะ") และ /tasks ตั้ง T-06 เป็นพร้อมทำทั้งที่ R3 รอ Q-14
4. สิ่งที่สเปกของกลุ่มคุมได้: ทุก endpoint อ้าง REQ ได้ ไม่มีฟีเจอร์เกิน ไม่มีคอลัมน์เบอร์โทรใน log และช่างไม่เห็นเบอร์ก่อน 2 ชั่วโมง
5. สิ่งที่หลุด: ค่า timeout ของ gateway ที่สเปกกับ Interface Contract บอกไม่ตรงกัน (GAP-07) และ "ระบบต้องเร็ว" ที่ยังวัดไม่ได้จนต้องเปิด CR-02
