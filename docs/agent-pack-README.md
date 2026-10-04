# agent-pack: ชุดคำสั่ง /clarify /plan /tasks /implement

ชุดไฟล์นี้ทำให้ Copilot, Claude Code และ Cursor มีคำสั่ง 4 คำสั่งเหมือนกัน ไม่ต้องติดตั้งโปรแกรมเพิ่ม
repo นี้และ repo ที่สร้างจาก template ของรายวิชา (reqeng-template) มีชุดนี้อยู่แล้ว

## ไฟล์ในชุด

| ไฟล์ | ใครอ่าน | ทำอะไร |
|---|---|---|
| `AGENTS.md` | Copilot, Cursor | กติกาของโปรเจกต์ 8 ข้อ AI อ่านเองทุกครั้ง |
| `CLAUDE.md` | Claude Code | ชี้ไปที่ AGENTS.md |
| `.github/prompts/*.prompt.md` | Copilot | คำสั่ง clarify, plan, tasks, implement |
| `.claude/commands/*.md` | Claude Code | คำสั่งชุดเดียวกัน |
| `.cursor/commands/*.md` | Cursor | คำสั่งชุดเดียวกัน |
| `.devcontainer/devcontainer.json` | Codespaces | ติดตั้ง library และเปิด Copilot Chat ให้เมื่อสร้าง Codespace |

เนื้อหาคำสั่งทั้ง 3 เครื่องมือเหมือนกันทุกตัวอักษร ต่างกันแค่โฟลเดอร์ที่วาง

## วิธีใช้ (ทำตามลำดับ หยุดตรวจทุกขั้น)

| ขั้น | พิมพ์ | ได้ | ตรวจก่อนไปต่อ |
|---|---|---|---|
| 1 | `/clarify specs/002-<feature>/spec.md` | คำถาม 3 ส่วน แล้ว spec.md v2 หลังทีมตอบ | ตอบด้วย "รู้ เพราะ..." หรือ "ไม่รู้ ต้องถาม..." เท่านั้น ดู diff ไม่มี ID ใหม่ |
| 2 | `/plan specs/002-<feature>/spec.md` | plan.md 8 หัวข้อ | ตารางข้อ 5 ครบทุก Constraint |
| 3 | `/tasks specs/002-<feature>/spec.md` | tasks.md | ตาราง AC ไม่มีช่อง "ว่าง" task ที่ติดคำถามเปิดเป็น "รอ Q-xx" |
| 4 | `/implement T-01 specs/002-<feature>/tasks.md` (แล้ว T-02 ...) | โค้ดและ test ของ task เดียว | ตรวจ 5 ข้อ เห็น passed ด้วยตา commit ทีละ task |

ทุกคำสั่งเพิ่มบันทึกท้าย `prompt-log.md` ให้เอง

## ถ้าเครื่องมือใช้ไม่ได้

เปิดไฟล์ `.github/prompts/clarify.prompt.md` คัดลอกเนื้อหาทั้งหมด วางในแชต AI ตัวไหนก็ได้ ตามด้วยเนื้อหา spec.md ของกลุ่ม จะได้คำถามแบบเดียวกัน แล้วแก้ spec.md เอง
