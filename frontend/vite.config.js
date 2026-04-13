import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'
import fs from 'fs'

// ========== IP配置（项目唯一需要修改IP的地方）==========
const BACKEND_IP = '10.0.0.113'
const BACKEND_PORT = '8000'
const BACKEND_URL = `http://${BACKEND_IP}:${BACKEND_PORT}`
// ======================================================

// 读取 SSL 证书
const sslOptions = {
  key: fs.readFileSync(path.join(__dirname, 'ssl/key.pem')),
  cert: fs.readFileSync(path.join(__dirname, 'ssl/cert.pem'))
}

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  },
  server: {
    port: 5173,
    host: '0.0.0.0',
    https: sslOptions,
    proxy: {
      '/api': {
        target: BACKEND_URL,
        changeOrigin: true
      },
      '/uploads': {
        target: BACKEND_URL,
        changeOrigin: true
      }
    }
  }
})
