import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// test หน้าจอรันใน jsdom (เบราว์เซอร์จำลอง) ไม่ต้องเปิดเบราว์เซอร์จริง
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // หน้าจอเรียก /api/... แล้ว Vite ส่งต่อไปหลังบ้านที่ port 8000 ในเครื่องเดียวกัน
  // ทำให้ไม่ติดปัญหา CORS และใช้ได้ทั้ง Codespace บนเบราว์เซอร์และบน VS Code
  server: {
    host: true,
    port: 5173,
    proxy: { '/api': { target: 'http://localhost:8000', rewrite: (p) => p.replace(/^\/api/, '') } },
  },
  test: { environment: 'jsdom', globals: true, setupFiles: './src/setupTests.js' },
})
