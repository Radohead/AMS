<template>
  <div class="mobile-asset-detail">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>资产详情</h1>
      <div class="placeholder"></div>
    </div>

    <!-- 加载中 -->
    <div class="loading-section" v-if="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 资产详情 -->
    <div class="detail-content" v-if="!loading && asset">
      <!-- 基本信息卡片 -->
      <div class="detail-card">
        <div class="card-header">
          <div class="asset-name">{{ asset.name }}</div>
          <div class="asset-status" :class="asset.status">
            {{ getStatusText(asset.status) }}
          </div>
        </div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">资产编码</span>
            <span class="value">{{ asset.asset_no }}</span>
          </div>
          <div class="info-row">
            <span class="label">资产类型</span>
            <span class="value">{{ getAssetTypeText(asset.asset_type) }}</span>
          </div>
          <div class="info-row">
            <span class="label">分类</span>
            <span class="value">{{ asset.category?.name }}</span>
          </div>
        </div>
      </div>

      <!-- 详细信息卡片 -->
      <div class="detail-card">
        <div class="card-title">基本信息</div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">品牌</span>
            <span class="value">{{ asset.brand || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">型号</span>
            <span class="value">{{ asset.model || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">序列号</span>
            <span class="value">{{ asset.serial_no || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">购买日期</span>
            <span class="value">{{ asset.purchase_date || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">购买价格</span>
            <span class="value highlight" v-if="asset.purchase_price">
              ¥{{ asset.purchase_price.toFixed(2) }}
            </span>
            <span class="value" v-else>-</span>
          </div>
          <div class="info-row">
            <span class="label">保修截止</span>
            <span class="value">{{ asset.warranty_end || '-' }}</span>
          </div>
        </div>
      </div>

      <!-- 使用信息卡片 -->
      <div class="detail-card">
        <div class="card-title">使用信息</div>
        <div class="card-body">
          <div class="info-row">
            <span class="label">使用部门</span>
            <span class="value">{{ asset.department?.name || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">使用人</span>
            <span class="value">{{ asset.user?.name || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">保管人</span>
            <span class="value">{{ asset.keeper?.name || '-' }}</span>
          </div>
          <div class="info-row">
            <span class="label">存放位置</span>
            <span class="value">{{ asset.location || '-' }}</span>
          </div>
        </div>
      </div>

      <!-- 房地产专用信息 -->
      <div class="detail-card" v-if="asset.asset_type === 'real_estate'">
        <div class="card-title">房产信息</div>
        <div class="card-body">
          <div class="info-row" v-if="asset.address">
            <span class="label">详细地址</span>
            <span class="value">{{ asset.address }}</span>
          </div>
          <div class="info-row" v-if="asset.area">
            <span class="label">建筑面积</span>
            <span class="value">{{ asset.area }} m²</span>
          </div>
          <div class="info-row" v-if="asset.property_type">
            <span class="label">产权类型</span>
            <span class="value">{{ asset.property_type }}</span>
          </div>
          <div class="info-row" v-if="asset.property_no">
            <span class="label">产权证号</span>
            <span class="value">{{ asset.property_no }}</span>
          </div>
        </div>
      </div>

      <!-- 照片预览 -->
      <div class="detail-card" v-if="asset.images && asset.images.length > 0">
        <div class="card-title">资产照片</div>
        <div class="photo-grid">
          <img
            v-for="(img, index) in asset.images"
            :key="index"
            :src="getImageUrl(img)"
            alt="资产照片"
            class="photo-item"
            @click="previewImage(img)"
          />
        </div>
      </div>

      <!-- 附件列表 -->
      <div class="detail-card" v-if="attachments.length > 0">
        <div class="card-title">资产附件</div>
        <div class="attachment-list">
          <div
            v-for="(file, index) in attachments"
            :key="index"
            class="attachment-item"
            @click="downloadAttachment(file)"
          >
            <span class="file-icon">📎</span>
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatFileSize(file.size) }}</span>
          </div>
        </div>
      </div>

      <!-- 描述备注 -->
      <div class="detail-card" v-if="asset.description || asset.remarks">
        <div class="card-title">备注说明</div>
        <div class="card-body">
          <div class="info-row" v-if="asset.description">
            <span class="label">描述</span>
            <span class="value">{{ asset.description }}</span>
          </div>
          <div class="info-row" v-if="asset.remarks">
            <span class="label">备注</span>
            <span class="value">{{ asset.remarks }}</span>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-section">
        <!-- 已登录用户显示操作按钮 -->
        <template v-if="isLoggedIn">
          <button class="action-btn outline" @click="scanQRCode">
            📷 扫码盘点
          </button>
          <button class="action-btn primary" @click="reportRepair">
            🔧 报修
          </button>
        </template>
        <!-- 未登录用户显示登录提示 -->
        <template v-else>
          <div class="login-prompt">
            <p>登录后可进行盘点、报修等操作</p>
            <button class="action-btn primary" @click="goToLogin">
              🔑 登录
            </button>
          </div>
        </template>
      </div>
    </div>

    <!-- 错误提示 -->
    <div class="error-section" v-if="!loading && error">
      <div class="error-icon">❌</div>
      <p>{{ error }}</p>
      <button @click="loadAsset">重新加载</button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { assetApi } from '@/api/modules'
import { useUserStore } from '@/store/user'
import { getImageUrl } from '@/utils/image'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const asset = ref(null)
const loading = ref(true)
const error = ref('')
const attachments = ref([])

// 是否已登录
const isLoggedIn = computed(() => !!userStore.token)

onMounted(() => {
  loadAsset()
})

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

function getAssetTypeText(type) {
  const map = {
    fixed: '固定资产',
    consumable: '易耗品',
    real_estate: '房地产'
  }
  return map[type] || type
}

async function loadAsset() {
  loading.value = true
  error.value = ''

  try {
    // 使用公开API，无需认证
    const res = await assetApi.getPublic(route.params.id)
    asset.value = res

    // 加载附件
    try {
      const attachList = await assetApi.getAttachments(route.params.id)
      attachments.value = attachList || []
    } catch (e) {
      console.error('加载附件失败:', e)
      attachments.value = []
    }
  } catch (err) {
    error.value = '加载资产详情失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

function previewImage(url) {
  window.open(url, '_blank')
}

// 下载附件
function downloadAttachment(file) {
  const url = getImageUrl(file.url)
  window.open(url, '_blank')
}

// 格式化文件大小
function formatFileSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function scanQRCode() {
  if (!isLoggedIn.value) {
    goToLogin()
    return
  }
  router.push({
    path: '/mobile/check',
    query: { assetId: asset.value.id, assetNo: asset.value.asset_no }
  })
}

function reportRepair() {
  if (!isLoggedIn.value) {
    goToLogin()
    return
  }
  router.push({
    path: '/mobile/repair/create',
    query: { assetId: asset.value.id }
  })
}

function goToLogin() {
  router.push({
    path: '/mobile/login',
    query: { redirect: route.fullPath }
  })
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-asset-detail {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 80px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 10;
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

.loading-section, .error-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f5f7fa;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-section {
  color: #909399;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.error-section button {
  background: #667eea;
  color: #fff;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  margin-top: 16px;
  cursor: pointer;
}

.detail-content {
  padding: 12px 16px;
}

.detail-card {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-header {
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
  flex: 1;
}

.asset-status {
  background: rgba(255, 255, 255, 0.2);
  color: #fff;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.card-title {
  padding: 16px 16px 0;
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}

.card-body {
  padding: 12px 16px 16px;
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
  flex-shrink: 0;
}

.info-row .value {
  color: #303133;
  font-size: 14px;
  text-align: right;
  word-break: break-all;
}

.info-row .value.highlight {
  color: #667eea;
  font-weight: 500;
}

.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  padding: 12px 16px 16px;
}

.photo-item {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
  cursor: pointer;
}

.attachment-list {
  padding: 8px 16px 16px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}

.attachment-item:last-child {
  margin-bottom: 0;
}

.file-icon {
  margin-right: 8px;
}

.file-name {
  flex: 1;
  font-size: 14px;
  color: #333;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  font-size: 12px;
  color: #909399;
  margin-left: 8px;
}

.action-section {
  display: flex;
  gap: 12px;
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
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

.action-btn.outline {
  background: #fff;
  border: 1px solid #667eea;
  color: #667eea;
}

.login-prompt {
  width: 100%;
  text-align: center;
}

.login-prompt p {
  color: #909399;
  font-size: 13px;
  margin: 0 0 12px 0;
}
</style>
