<template>
  <div class="mobile-scan">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>扫码查询</h1>
      <div class="placeholder"></div>
    </div>

    <div class="scan-content">
      <!-- HTTPS 提示 -->
      <div class="https-warning" v-if="!isHttps && !scanResult">
        <div class="warning-icon">🔒</div>
        <h3>建议使用 HTTPS 访问</h3>
        <p>当前使用 HTTP 协议，部分浏览器可能限制摄像头功能。</p>
        <p class="https-url">HTTPS 访问地址：<br/><span>{{ httpsUrl }}</span></p>
      </div>

      <!-- 扫码区域 -->
      <div class="scanner-section" v-if="!scanResult && !showManualInput && !showUploadOption">
        <div id="qr-reader" class="qr-reader" v-if="cameraSupported"></div>
        <div class="scanner-tip" v-if="cameraSupported">将二维码放入框内即可自动扫描</div>

        <!-- 权限状态提示 -->
        <div class="permission-status" v-if="cameraPermission === 'denied'">
          <p>摄像头权限被阻止</p>
          <p class="hint">请在浏览器设置中允许摄像头访问</p>
        </div>

        <div class="action-buttons-row">
          <button class="action-btn-outline" @click="showUploadOption = true">
            📷 拍照识别
          </button>
          <button class="action-btn-outline" @click="showManualInput = true">
            ⌨️ 手动输入
          </button>
        </div>
      </div>

      <!-- 拍照上传方案 -->
      <div class="upload-section" v-if="showUploadOption">
        <h3>拍照识别二维码</h3>
        <p class="upload-tip">点击下方按钮，拍摄资产二维码照片自动识别</p>

        <div class="upload-area">
          <input
            ref="fileInputRef"
            type="file"
            accept="image/*"
            capture="environment"
            @change="handleFileUpload"
            style="display: none"
          />
          <button class="camera-btn" @click="triggerCamera">
            📷 拍照/选择图片
          </button>
          <p class="upload-hint">支持从相册选择图片识别</p>
        </div>

        <button class="back-link" @click="showUploadOption = false">返回扫码</button>
      </div>

      <!-- 手动输入 -->
      <div class="manual-section" v-if="showManualInput && !scanResult">
        <h3 class="section-title">手动输入资产编码</h3>
        <div class="manual-input-box">
          <input
            v-model="assetNo"
            type="text"
            placeholder="请输入资产编码，如 AS20260410A17618"
          />
          <button class="search-btn" @click="searchByNo">查询</button>
        </div>
        <p class="manual-hint">资产编码可在资产详情页查看</p>
        <button class="back-link" @click="showManualInput = false; checkCameraPermission()">返回扫码</button>
      </div>

      <!-- 加载中 -->
      <div class="loading-section" v-if="loading">
        <div class="spinner"></div>
        <p>{{ loadingText }}</p>
      </div>

      <!-- 扫码结果 -->
      <div class="result-section" v-if="scanResult && !loading">
        <div class="result-card">
          <div class="asset-header">
            <div class="asset-name">{{ scanResult.name }}</div>
            <div class="asset-status" :class="scanResult.status">
              {{ getStatusText(scanResult.status) }}
            </div>
          </div>

          <div class="asset-info">
            <div class="info-row">
              <span class="label">资产编码</span>
              <span class="value">{{ scanResult.asset_no }}</span>
            </div>
            <div class="info-row">
              <span class="label">分类</span>
              <span class="value">{{ scanResult.category?.name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">品牌型号</span>
              <span class="value">{{ scanResult.brand || '' }} {{ scanResult.model || '' }}</span>
            </div>
            <div class="info-row">
              <span class="label">使用部门</span>
              <span class="value">{{ scanResult.department?.name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">使用人</span>
              <span class="value">{{ scanResult.user?.name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">存放位置</span>
              <span class="value">{{ scanResult.location || '-' }}</span>
            </div>
            <div class="info-row" v-if="scanResult.purchase_price">
              <span class="label">购买价格</span>
              <span class="value">¥{{ scanResult.purchase_price.toFixed(2) }}</span>
            </div>
          </div>

          <div class="action-buttons">
            <button class="action-btn primary" @click="viewDetail">查看详情</button>
            <button class="action-btn secondary" @click="resetScan">继续扫描</button>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div class="error-section" v-if="error && !loading">
        <div class="error-icon">❌</div>
        <p class="error-text">{{ error }}</p>
        <button class="manual-btn-large" @click="showManualInput = true">手动输入资产编码</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Html5Qrcode } from 'html5-qrcode'
import { assetApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const assetNo = ref('')
const scanResult = ref(null)
const loading = ref(false)
const loadingText = ref('正在处理...')
const error = ref('')
const showManualInput = ref(false)
const showUploadOption = ref(false)
const fileInputRef = ref(null)
const cameraPermission = ref('prompt') // 'prompt' | 'granted' | 'denied'
const cameraSupported = ref(true)
const isHttps = ref(true)
const httpsUrl = ref('')

let html5Qrcode = null

onMounted(() => {
  checkEnvironment()
  checkCameraSupport()
  startScanner()
})

onUnmounted(() => {
  stopScanner()
})

// 检查环境
function checkEnvironment() {
  isHttps.value = window.location.protocol === 'https:'
  if (!isHttps.value) {
    // 生成 HTTPS URL
    const host = window.location.hostname
    const port = window.location.port || (window.location.protocol === 'https' ? '443' : '80')
    httpsUrl.value = `https://${host}${port ? ':' + port : ''}/mobile`
  }
}

// 检查摄像头支持
function checkCameraSupport() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    cameraSupported.value = false
    showUploadOption.value = true
    return
  }
}

// 检查摄像头权限
async function checkCameraPermission() {
  try {
    if (navigator.permissions && navigator.permissions.query) {
      const result = await navigator.permissions.query({ name: 'camera' })
      cameraPermission.value = result.state
      result.addEventListener('change', () => {
        cameraPermission.value = result.state
      })
    }
  } catch (err) {
    console.log('权限检测失败:', err)
  }
}

async function startScanner() {
  // 先检查权限
  await checkCameraPermission()

  if (!cameraSupported.value) {
    showUploadOption.value = true
    return
  }

  try {
    html5Qrcode = new Html5Qrcode('qr-reader')

    const config = {
      fps: 10,
      qrbox: { width: 250, height: 250 },
      aspectRatio: 1
    }

    await html5Qrcode.start(
      { facingMode: 'environment' },
      config,
      onScanSuccess,
      onScanFailure
    )
    cameraPermission.value = 'granted'
  } catch (err) {
    console.error('无法访问摄像头', err)
    cameraPermission.value = 'denied'
    cameraSupported.value = false
    showUploadOption.value = true

    if (err.toString().includes('Permission')) {
      error.value = '摄像头权限被拒绝，请点击下方"拍照识别"按钮上传图片'
    } else if (err.toString().includes('NotFound')) {
      error.value = '未找到摄像头设备，请使用拍照识别功能'
    }
  }
}

async function stopScanner() {
  if (html5Qrcode) {
    try {
      await html5Qrcode.stop()
    } catch (err) {
      console.error('停止扫码失败', err)
    }
  }
}

// 触发相机/文件选择
function triggerCamera() {
  fileInputRef.value?.click()
}

// 处理图片上传
async function handleFileUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return

  loading.value = true
  loadingText.value = '正在识别二维码...'
  error.value = ''

  try {
    const html5QrCode = new Html5Qrcode('qr-reader')

    // 使用图片文件进行二维码识别
    const result = await html5QrCode.scanFile(file, true)
    console.log('识别结果:', result)

    loading.value = false
    showUploadOption.value = false
    onScanSuccess(result)
  } catch (err) {
    loading.value = false
    console.error('图片二维码识别失败', err)
    error.value = '无法识别图片中的二维码，请确保图片中包含清晰的二维码'
  }

  // 清空input，允许重复选择
  event.target.value = ''
}

function onScanSuccess(decodedText) {
  stopScanner()

  let assetIdentifier = decodedText

  // 解析二维码内容
  // 1. 处理完整URL（如 https://10.0.0.113:5173/mobile/assets/1）
  if (decodedText.includes('/mobile/assets/')) {
    const match = decodedText.match(/\/mobile\/assets\/(\d+)/)
    if (match) {
      assetIdentifier = match[1]
      fetchAssetById(assetIdentifier)
      return
    }
  }

  // 2. 处理相对路径（如 /mobile/assets/1 或 /assets/1）
  if (decodedText.startsWith('/')) {
    const match = decodedText.match(/\/assets\/(\d+)/)
    if (match) {
      assetIdentifier = match[1]
      fetchAssetById(assetIdentifier)
      return
    }
  }

  // 3. 尝试解析JSON格式
  try {
    const data = JSON.parse(decodedText)
    if (data.id) {
      fetchAssetById(data.id)
      return
    }
    if (data.no || data.asset_no) {
      fetchAsset(data.no || data.asset_no)
      return
    }
    if (data.url) {
      const match = data.url.match(/\/assets\/(\d+)/)
      if (match) {
        fetchAssetById(match[1])
        return
      }
    }
  } catch (e) {
    // 不是JSON
  }

  // 4. 最后尝试按资产编码查询
  fetchAsset(assetIdentifier)
}

async function fetchAssetById(id) {
  loading.value = true
  error.value = ''

  try {
    // 使用公开API，无需认证
    const res = await assetApi.getPublic(id)
    // 扫码成功后直接跳转到详情页
    router.push(`/mobile/assets/${id}`)
  } catch (err) {
    error.value = '未找到该资产'
    loading.value = false
  }
}

function onScanFailure(err) {
  // 扫描失败，忽略
}

async function searchByNo() {
  if (!assetNo.value.trim()) {
    alert('请输入资产编码')
    return
  }
  await fetchAsset(assetNo.value.trim())
}

async function fetchAsset(identifier) {
  loading.value = true
  error.value = ''
  scanResult.value = null

  try {
    // 使用公开API，无需认证
    const res = await assetApi.getByNo(identifier)
    scanResult.value = res
    // 跳转到详情页
    router.push(`/mobile/assets/${res.id}`)
  } catch (err) {
    error.value = '未找到该资产'
    loading.value = false
  }
}

function getStatusText(status) {
  const map = {
    stock: '在库',
    in_use: '使用中',
    repair: '维修中',
    scrapped: '已报废',
    lost: '丢失'
  }
  return map[status] || status
}

function viewDetail() {
  if (scanResult.value) {
    router.push(`/mobile/assets/${scanResult.value.id}`)
  }
}

async function resetScan() {
  scanResult.value = null
  error.value = ''
  assetNo.value = ''
  showManualInput.value = false
  showUploadOption.value = false
  await startScanner()
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-scan {
  min-height: 100vh;
  background: #f5f7fa;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  width: 40px;
  height: 40px;
}

.header h1 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}

.placeholder {
  width: 40px;
}

.scan-content {
  padding: 16px;
}

.https-warning {
  background: #fff8e6;
  border: 1px solid #ffb900;
  border-radius: 8px;
  padding: 16px;
  text-align: center;
  margin-bottom: 16px;
}

.https-warning .warning-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.https-warning h3 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #333;
}

.https-warning p {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}

.https-url {
  background: #fff;
  padding: 8px;
  border-radius: 4px;
  margin-top: 8px !important;
}

.https-url span {
  color: #409eff;
  word-break: break-all;
  font-size: 11px;
}

.scanner-section {
  text-align: center;
}

.qr-reader {
  width: 100%;
  max-width: 300px;
  margin: 0 auto;
  border-radius: 12px;
  overflow: hidden;
}

.scanner-tip {
  margin-top: 16px;
  font-size: 14px;
  color: #909399;
}

.permission-status {
  background: #fef0f0;
  border-radius: 8px;
  padding: 12px;
  margin: 12px auto;
  max-width: 300px;
}

.permission-status p {
  margin: 0;
  font-size: 13px;
  color: #f56c6c;
}

.permission-status .hint {
  font-size: 12px;
  color: #909399;
  margin-top: 4px !important;
}

.action-buttons-row {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.action-btn-outline {
  flex: 1;
  max-width: 150px;
  padding: 12px;
  border: 1px solid #667eea;
  background: #fff;
  color: #667eea;
  border-radius: 8px;
  font-size: 13px;
  cursor: pointer;
}

.upload-section {
  text-align: center;
  padding: 20px 0;
}

.upload-section h3 {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #333;
}

.upload-tip {
  font-size: 13px;
  color: #909399;
  margin-bottom: 20px;
}

.upload-area {
  background: #f5f7fa;
  border-radius: 12px;
  padding: 30px 20px;
}

.camera-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  padding: 16px 32px;
  border-radius: 8px;
  font-size: 15px;
  cursor: pointer;
}

.upload-hint {
  margin: 12px 0 0 0;
  font-size: 12px;
  color: #909399;
}

.back-link {
  margin-top: 20px;
  background: none;
  border: none;
  color: #909399;
  font-size: 14px;
  cursor: pointer;
}

.manual-section {
  text-align: center;
  padding: 20px 0;
}

.section-title {
  margin: 0 0 20px 0;
  font-size: 16px;
  color: #333;
}

.manual-input-box {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-width: 360px;
  margin: 0 auto;
}

.manual-input-box input {
  height: 48px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 0 16px;
  font-size: 14px;
  text-align: center;
}

.search-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  padding: 14px;
  border-radius: 8px;
  font-size: 14px;
}

.manual-hint {
  font-size: 12px;
  color: #909399;
  margin: 12px 0;
}

.loading-section {
  text-align: center;
  padding: 60px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f5f7fa;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.result-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.asset-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.asset-name {
  color: #fff;
  font-size: 18px;
  font-weight: 500;
}

.asset-status {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.asset-info {
  padding: 16px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 10px 0;
  border-bottom: 1px solid #f5f7fa;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  color: #909399;
  font-size: 14px;
}

.info-row .value {
  color: #303133;
  font-size: 14px;
}

.action-buttons {
  padding: 16px;
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  height: 44px;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.action-btn.secondary {
  background: #f5f7fa;
  color: #606266;
}

.error-section {
  text-align: center;
  padding: 40px 0;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.error-text {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.manual-btn-large {
  display: block;
  width: 100%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  padding: 14px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}
</style>
