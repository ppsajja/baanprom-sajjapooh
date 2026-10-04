// จุดเดียวที่หน้าจอใช้เรียก API หลังบ้าน (ตามสัญญา API ใน plan.md ข้อ 4)
// ตอน test ให้ส่ง client จำลองเข้าไปในหน้าจอแทน ไม่ต้องรันหลังบ้านจริง
// เรียกผ่าน /api (ดู proxy ใน vite.config.js) หลังบ้านต้องรันอยู่ที่ port 8000
const BASE = import.meta.env.VITE_API_BASE ?? '/api'

async function readJson(res) {
  return { status: res.status, body: await res.json() }
}

export const api = {
  // REQ-FN-008 ค้นช่างว่างใน 7 วัน
  async getTechnicians({ category, addressId, customerId }) {
    const q = new URLSearchParams({ category, address_id: addressId, customer_id: customerId })
    return readJson(await fetch(`${BASE}/technicians?${q}`))
  },
  // REQ-FN-041 ล็อกช่วงเวลา 10 นาที
  async holdSlot({ slotId, customerId }) {
    return readJson(await fetch(`${BASE}/slots/${slotId}/hold`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId }),
    }))
  },
  // UC-07 ขั้น 5 ยืนยันและชำระมัดจำ ตอบ 201 / 409 slot_taken / 402 payment_failed
  async createBooking({ customerId, slotId, addressId, category }) {
    return readJson(await fetch(`${BASE}/bookings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ customer_id: customerId, slot_id: slotId, address_id: addressId, category }),
    }))
  },
}
