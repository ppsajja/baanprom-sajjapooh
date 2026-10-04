// หน้าผลการจอง (UC-07 ขั้น 6) รองรับ REQ-FN-008
export default function BookingResult({ job, onRestart }) {
  const start = new Date(job.scheduled_start).toLocaleString('th-TH', { dateStyle: 'medium', timeStyle: 'short' })
  return (
    <section className="rounded-xl bg-white p-6 text-center shadow-sm">
      <p className="text-sm text-teal-700">จองสำเร็จ</p>
      <h2 className="mt-1 text-2xl font-bold text-slate-900">งาน #{job.job_id}</h2>
      <p className="mt-2 text-slate-700">สถานะ: ยืนยันแล้ว</p>
      <p className="text-slate-700">นัดหมาย {start}</p>
      <p className="mt-3 text-sm text-slate-500">ระบบจะแจ้งคุณและช่างภายใน 60 วินาที</p>
      <button type="button" onClick={onRestart} className="mt-5 rounded-lg border border-slate-300 px-4 py-2 text-sm text-slate-700">
        จองงานใหม่
      </button>
    </section>
  )
}
