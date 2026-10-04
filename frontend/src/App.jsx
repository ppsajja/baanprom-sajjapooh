// หน้าหลักของ feature UC-07: เลือกช่าง แล้วยืนยัน แล้วดูผล
// ตัวอย่างใช้ลูกค้าและที่อยู่คงที่ (การเข้าสู่ระบบ UC-10 และเลือกที่อยู่ UC-02 อยู่นอกขอบเขต feature นี้)
import { useState } from 'react'
import { api as realApi } from './api/client.js'
import TechnicianPicker from './pages/TechnicianPicker.jsx'
import ConfirmBooking from './pages/ConfirmBooking.jsx'
import BookingResult from './pages/BookingResult.jsx'

export default function App({ api = realApi, customerId = 1, addressId = 1 }) {
  const [held, setHeld] = useState(null)
  const [job, setJob] = useState(null)

  return (
    <main className="mx-auto max-w-2xl p-6">
      <header className="mb-6">
        <h1 className="text-2xl font-bold text-teal-800">บ้านพร้อม</h1>
        <p className="text-slate-600">จองช่างซ่อมบ้านที่ว่างจริง ไม่ต้องโทรถาม</p>
      </header>
      {!held && !job && (
        <TechnicianPicker api={api} customerId={customerId} addressId={addressId} onHeld={setHeld} />
      )}
      {held && !job && (
        <ConfirmBooking api={api} customerId={customerId} addressId={addressId} held={held}
          onConfirmed={setJob}
          onPickAlternative={(a) => setHeld({ ...held, slot: a, technician: { technician_id: a.technician_id, name: a.technician_name } })} />
      )}
      {job && <BookingResult job={job} onRestart={() => { setHeld(null); setJob(null) }} />}
    </main>
  )
}
