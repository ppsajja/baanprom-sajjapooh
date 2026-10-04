// test หน้าจอของ AC-07-04 (REQ-FN-041, UC-07 E2): API จำลองตอบ 409 slot_taken พร้อมช่วงใกล้เคียง 2 ช่วง
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import ConfirmBooking from '../pages/ConfirmBooking.jsx'

const held = {
  category: 'ประปา',
  technician: { technician_id: 1, name: 'ประสิทธิ์' },
  slot: { slot_id: 1, start: '2026-10-05T14:00:00', end: '2026-10-05T16:00:00' },
}

test('AC-07-04 แสดง "ช่วงเวลาถูกจองแล้ว" และปุ่มช่วงใกล้เคียงอย่างน้อย 2 ปุ่ม โดยไม่ตัดเงิน', async () => {
  // Given ลูกค้าอื่นจองช่วงเวลานั้นไปก่อน (หลังบ้านจำลองตอบ 409 พร้อม alternatives)
  const api = {
    createBooking: vi.fn().mockResolvedValue({
      status: 409,
      body: {
        reason: 'slot_taken',
        alternatives: [
          { slot_id: 2, technician_id: 1, technician_name: 'ประสิทธิ์', start: '2026-10-05T16:00:00', end: '2026-10-05T18:00:00' },
          { slot_id: 3, technician_id: 1, technician_name: 'ประสิทธิ์', start: '2026-10-05T11:00:00', end: '2026-10-05T13:00:00' },
        ],
      },
    }),
  }
  const onConfirmed = vi.fn()
  const onPickAlternative = vi.fn()
  render(<ConfirmBooking api={api} customerId={1} addressId={1} held={held} onConfirmed={onConfirmed} onPickAlternative={onPickAlternative} />)

  // When ลูกค้ากดยืนยัน
  fireEvent.click(screen.getByRole('button', { name: /ยืนยันและชำระมัดจำ/ }))

  // Then ระบบแจ้งว่าช่วงเวลาถูกจองแล้ว
  await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('ช่วงเวลาถูกจองแล้ว'))
  // And ไม่ไปหน้าผลการจอง (ไม่มีการตัดเงิน)
  expect(onConfirmed).not.toHaveBeenCalled()
  // And เสนอช่วงเวลาใกล้เคียงอย่างน้อย 2 ตัวเลือก
  const altButtons = screen.getAllByRole('button', { name: /ช่าง ประสิทธิ์/ })
  expect(altButtons.length).toBeGreaterThanOrEqual(2)
  // And กดเลือกตัวเลือกแล้วส่งช่วงที่เลือกกลับไป
  fireEvent.click(altButtons[0])
  expect(onPickAlternative).toHaveBeenCalledWith(expect.objectContaining({ slot_id: 2 }))
})
