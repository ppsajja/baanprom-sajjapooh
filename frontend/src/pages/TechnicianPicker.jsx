// หน้าเลือกช่าง (UC-07 ขั้น 1 ถึง 3) รองรับ REQ-FN-008 และ REQ-FN-041
import { useState } from 'react'

const CATEGORIES = ['ประปา', 'ไฟฟ้า', 'แอร์']

function fmt(iso) {
  const d = new Date(iso)
  return d.toLocaleString('th-TH', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

export default function TechnicianPicker({ api, customerId, addressId, onHeld }) {
  const [category, setCategory] = useState('ประปา')
  const [technicians, setTechnicians] = useState(null)
  const [error, setError] = useState('')

  async function search() {
    setError('')
    const { status, body } = await api.getTechnicians({ category, addressId, customerId })
    if (status !== 200) return setError('ค้นหาไม่สำเร็จ')
    setTechnicians(body)
  }

  async function pick(tech, slot) {
    const { status, body } = await api.holdSlot({ slotId: slot.slot_id, customerId })
    if (status === 409) return setError('ช่วงเวลานี้เพิ่งถูกจองไป กรุณาเลือกใหม่')
    onHeld({ slot, technician: tech, category, holdExpiresAt: body.hold_expires_at })
  }

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-800">1. เลือกประเภทงานและช่างที่ว่าง</h2>
      <div className="mt-3 flex flex-wrap items-center gap-2">
        {CATEGORIES.map((c) => (
          <button key={c} type="button" onClick={() => setCategory(c)}
            className={`rounded-full border px-4 py-1 text-sm ${category === c ? 'border-teal-700 bg-teal-700 text-white' : 'border-slate-300 bg-white text-slate-700'}`}>
            {c}
          </button>
        ))}
        <button type="button" onClick={search} className="ml-auto rounded-lg bg-orange-500 px-4 py-2 text-sm font-medium text-white hover:bg-orange-600">
          ค้นหาช่างที่ว่างใน 7 วัน
        </button>
      </div>
      {error && <p className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p>}
      {technicians && technicians.length === 0 && (
        <p className="mt-3 text-sm text-slate-600">ไม่มีช่างว่างใน 7 วันข้างหน้า (A1: ลองช่วงถัดไป หรือเข้า waitlist)</p>
      )}
      <ul className="mt-4 space-y-3">
        {technicians?.map((t) => (
          <li key={t.technician_id} className="rounded-lg border border-slate-200 p-3">
            <p className="font-medium text-slate-800">ช่าง {t.name}</p>
            <div className="mt-2 flex flex-wrap gap-2">
              {t.slots.map((s) => (
                <button key={s.slot_id} type="button" onClick={() => pick(t, s)}
                  className="rounded-md border border-teal-600 px-3 py-1 text-sm text-teal-800 hover:bg-teal-50">
                  {fmt(s.start)}
                </button>
              ))}
            </div>
          </li>
        ))}
      </ul>
    </section>
  )
}
