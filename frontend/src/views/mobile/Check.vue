<template>
  <div class="mobile-check">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>资产盘点</h1>
      <div class="placeholder"></div>
    </div>

    <div class="check-content">
      <!-- 待盘点列表 -->
      <div class="section" v-if="!showScanner">
        <div class="section-title">待盘点资产</div>
        <div class="check-list">
          <div
            v-for="item in checkItems"
            :key="item.id"
            class="check-item"
            :class="{ checked: item.checked }"
            @click="startCheckItem(item)"
          >
            <div class="item-info">
              <div class="item-name">{{ item.asset?.name || '未知资产' }}</div>
              <div class="item-no">{{ item.asset?.asset_no }}</div>
            </div>
            <div class="item-status">
              <span v-if="item.checked" class="status-tag success">已盘点</span>
              <span v-else class="status-tag pending">待盘点</span>
            </div>
          </div>

          <div v-if="checkItems.length === 0" class="empty">
            <div class="empty-icon">📋</div>
            <p>暂无待盘点资产</p>
            <button class="create-btn" @click="goToCreateCheck">创建盘点任务</button>
          </div>
        </div>
      </div>

      <!-- 扫码盘点 -->
      <div class="scanner-section" v-if="showScanner">
        <div id="check-reader" class="qr-reader"></div>
        <div class="scanner-tip">扫描资产二维码进行盘点</div>
        <button class="cancel-btn" @click="cancelScan">取消</button>
      </div>

      <!-- 盘点结果 -->
      <div class="result-section" v-if="checkResult">
        <div class="result-card">
          <div class="result-header">
            <div class="result-icon" :class="checkResult.success ? 'success' : 'error'">
              {{ checkResult.success ? '✓' : '✗' }}
            </div>
            <div class="result-text">
              <div class="result-title">{{ checkResult.success ? '盘点成功' : '盘点失败' }}</div>
              <div class="result-asset">{{ checkResult.assetName }}</div>
            </div>
          </div>
          <div class="result-actions">
            <button class="action-btn primary" @click="continueScan">继续盘点</button>
            <button class="action-btn secondary" @click="finishCheck">完成</button>
          </div>
        </div>
      </div>

      <!-- 盘点统计 -->
      <div class="stats-section" v-if="checkItems.length > 0">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ checkItems.length }}</div>
            <div class="stat-label">待盘点</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ checkedCount }}</div>
            <div class="stat-label">已盘点</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ checkItems.length - checkedCount }}</div>
            <div class="stat-label">未盘点</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Html5Qrcode } from 'html5-qrcode'
import { inventoryCheckApi, assetApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const checkTasks = ref([])
const checkItems = ref([])
const showScanner = ref(false)
const checkResult = ref(null)
let html5Qrcode = null
let currentCheckTask = ref(null)

const checkedCount = computed(() => {
  return checkItems.value.filter(item => item.checked).length
})

onMounted(() => {
  loadCheckTasks()
})

onUnmounted(() => {
  stopScanner()
})

async function loadCheckTasks() {
  try {
    const res = await inventoryCheckApi.list({ status: 'in_progress' })
    checkTasks.value = res.items || []

    // 如果有待处理任务，加载第一个任务的盘点项
    if (checkTasks.value.length > 0) {
      currentCheckTask.value = checkTasks.value[0]
      await loadCheckItems(currentCheckTask.value.id)
    }
  } catch (error) {
    console.error('加载盘点任务失败', error)
  }
}

async function loadCheckItems(taskId) {
  try {
    const res = await inventoryCheckApi.getItems(taskId, { page: 1, page_size: 100 })
    checkItems.value = res.items || []
  } catch (error) {
    console.error('加载盘点项失败', error)
  }
}

function startCheckItem(item) {
  if (item.checked) return

  // 如果已有扫描器在运行，先停止
  stopScanner()

  showScanner.value = true
  setTimeout(() => {
    startScanner(item)
  }, 300)
}

async function startScanner(item) {
  try {
    html5Qrcode = new Html5Qrcode('check-reader')

    const config = {
      fps: 10,
      qrbox: { width: 250, height: 250 },
      aspectRatio: 1
    }

    await html5Qrcode.start(
      { facingMode: 'environment' },
      config,
      (decodedText) => onScanSuccess(decodedText, item),
      (err) => console.error('扫码失败', err)
    )
  } catch (err) {
    console.error('无法访问摄像头', err)
    alert('无法访问摄像头')
    showScanner.value = false
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

async function onScanSuccess(decodedText, item) {
  await stopScanner()
  showScanner.value = false

  // 解析资产编码
  let assetNo = decodedText
  if (decodedText.includes('/assets/')) {
    const match = decodedText.match(/\/assets\/([^/]+)/)
    if (match) {
      assetNo = match[1]
    }
  }

  // 验证是否是目标资产
  const targetAssetNo = item.asset?.asset_no || item.asset_no
  if (assetNo === targetAssetNo || decodedText.includes(item.asset_id?.toString())) {
    await confirmCheck(item)
    checkResult.value = {
      success: true,
      assetName: item.asset?.name || '资产'
    }
  } else {
    checkResult.value = {
      success: false,
      assetName: '资产编码不匹配'
    }
  }
}

async function confirmCheck(item) {
  try {
    await inventoryCheckApi.updateItem(currentCheckTask.value.id, item.id, {
      status: 'checked',
      checked_at: new Date().toISOString()
    })

    // 更新本地状态
    const index = checkItems.value.findIndex(i => i.id === item.id)
    if (index !== -1) {
      checkItems.value[index].checked = true
    }
  } catch (error) {
    console.error('盘点确认失败', error)
    alert('盘点确认失败')
  }
}

function continueScan() {
  checkResult.value = null
  // 自动选择下一个未盘点的项目
  const nextItem = checkItems.value.find(item => !item.checked)
  if (nextItem) {
    startCheckItem(nextItem)
  }
}

function cancelScan() {
  stopScanner()
  showScanner.value = false
}

function finishCheck() {
  checkResult.value = null
  if (checkedCount.value === checkItems.value.length) {
    alert('盘点完成！')
  }
}

function goToCreateCheck() {
  router.push('/inventory-check/create')
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-check {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 100px;
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
  display: flex;
  align-items: center;
  justify-content: center;
}

.header h1 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}

.placeholder {
  width: 40px;
}

.check-content {
  padding: 16px;
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 12px;
}

.check-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.check-item {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.check-item:active {
  background: #f5f7fa;
}

.check-item.checked {
  opacity: 0.6;
}

.item-name {
  font-size: 16px;
  color: #303133;
  margin-bottom: 4px;
}

.item-no {
  font-size: 12px;
  color: #909399;
}

.status-tag {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.status-tag.pending {
  background: #fff7e6;
  color: #fa8c16;
}

.status-tag.success {
  background: #f6ffed;
  color: #52c41a;
}

.empty {
  text-align: center;
  padding: 60px 0;
  background: #fff;
  border-radius: 12px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty p {
  color: #909399;
  font-size: 14px;
  margin-bottom: 20px;
}

.create-btn {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: #fff;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.scanner-section {
  text-align: center;
  padding: 20px 0;
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

.cancel-btn {
  margin-top: 16px;
  background: #f5f7fa;
  border: none;
  color: #606266;
  padding: 12px 32px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
}

.result-section {
  padding: 20px 0;
}

.result-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.result-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 24px;
}

.result-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.result-icon.success {
  background: #f6ffed;
  color: #52c41a;
}

.result-icon.error {
  background: #fff1f0;
  color: #ff4d4f;
}

.result-title {
  font-size: 18px;
  font-weight: 500;
  color: #303133;
}

.result-asset {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.result-actions {
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

.stats-section {
  margin-top: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.stat-item {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}
</style>
