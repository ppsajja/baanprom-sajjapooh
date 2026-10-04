// หน้ายืนยัน (UC-07 ขั้น 4 ถึง 5) แสดงมัดจำและเงื่อนไข BR-01 แล้วยืนยัน
// รองรับ AC-07-04: ถ้าได้ 409 slot_taken แสดง "ช่วงเวลาถูกจองแล้ว" และปุ่มช่วงใกล้เคียง
import { useState } from 'react'

export function fmt(iso) {
  const d = new Date(iso)
  return d.toLocaleString('th-TH', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
}

const DEPOSIT = { ประปา: 350, ไฟฟ้า: 400, แอร์: 500 }

export default function ConfirmBooking({ api, customerId, addressId, held, onConfirmed, onPickAlternative }) {
  const [state, setState] = useState({ kind: 'idle' })
  const deposit = DEPOSIT[held.category] ?? 300

  async function confirm() {
    setState({ kind: 'loading' })
    const { status, body } = await api.createBooking({
      customerId, slotId: held.slot.slot_id, addressId, category: held.category,
    })
    if (status === 201) return onConfirmed(body)
    if (status === 409 && body.reason === 'slot_taken') return setState({ kind: 'taken', alternatives: body.alternatives })
    if (status === 402) return setState({ kind: 'payment_failed' })
    setState({ kind: 'error' })
  }

  return (
    <section className="rounded-xl bg-white p-6 shadow-sm">
      <h2 className="text-lg font-semibold text-slate-800">2. ตรวจรายละเอียดและชำระมัดจำ</h2>
      <dl className="mt-3 grid grid-cols-2 gap-y-2 text-sm">
        <dt className="text-slate-500">ช่าง</dt><dd className="text-slate-800">{held.technician.name}</dd>
        <dt className="text-slate-500">ช่วงเวลา</dt><dd className="text-slate-800">{fmt(held.slot.start)} ถึง {fmt(held.slot.end)}</dd>
        <dt className="text-slate-500">ประเภทงาน</dt><dd className="text-slate-800">{held.category}</dd>
        <dt className="text-slate-500">มัดจำ</dt><dd className="font-semibold text-slate-900">{deposit} บาท</dd>
      </dl>
      <p className="mt-3 rounded-lg bg-slate-50 p-3 text-xs text-slate-600">
        เงื่อนไขการยกเลิก (BR-01): ยกเลิกก่อนนัด 24 ชั่วโมงขึ้นไป คืนมัดจำเต็มจำนวน
        น้อยกว่า 24 ชั่วโมง คืนครึ่งหนึ่ง เมื่อช่างออกเดินทางแล้ว กรุณาติดต่อ call center
        ช่วงเวลานี้ถูกล็อกไว้ให้คุณ 10 นาที
      </p>

      {state.kind === 'taken' && (
        <div role="alert" className="mt-4 rounded-lg border border-orange-300 bg-orange-50 p-4">
          <p className="font-medium text-orange-800">ช่วงเวลาถูกจองแล้ว</p>
          <p className="mt-1 text-sm text-orange-700">ยังไม่มีการตัดเงิน เลือกช่วงเวลาใกล้เคียงด้านล่าง หรือกลับไปค้นหาใหม่</p>
          <ul className="mt-3 flex flex-wrap gap-2">
            {state.alternatives.map((a) => (
              <li key={a.slot_id}>
                <button type="button" onClick={() => onPickAlternative(a)}
                  className="rounded-md border border-teal-600 bg-white px-3 py-1 text-sm text-teal-800 hover:bg-teal-50">
                  ช่าง {a.technician_name} {fmt(a.start)}
                </button>
              </li>
            ))}
          </ul>
        </div>
      )}
      {state.kind === 'payment_failed' && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">ชำระมัดจำไม่สำเร็จ การจองถูกยกเลิก ช่วงเวลากลับเป็นว่างแล้ว</p>
      )}
      {state.kind === 'error' && (
        <p role="alert" className="mt-4 rounded-lg bg-red-50 p-3 text-sm text-red-700">เกิดข้อผิดพลาด กรุณาลองใหม่</p>
      )}

      <button type="button" onClick={confirm} disabled={state.kind === 'loading' || state.kind === 'taken'}
        className="mt-5 w-full rounded-lg bg-teal-700 px-4 py-3 font-medium text-white hover:bg-teal-800 disabled:cursor-not-allowed disabled:bg-slate-300">
        {state.kind === 'loading' ? 'กำลังชำระมัดจำ...' : `ยืนยันและชำระมัดจำ ${deposit} บาท`}
      </button>
    </section>
  )
}
