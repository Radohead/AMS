<template>
  <div class="mobile-home">
    <!-- 顶部栏 -->
    <div class="header">
      <div class="user-info">
        <div class="avatar">{{ userStore.userInfo?.real_name?.charAt(0) || 'U' }}</div>
        <div class="info">
          <div class="name">{{ userStore.userInfo?.real_name || '用户' }}</div>
          <div class="role">资产管理员</div>
        </div>
      </div>
      <button class="logout-btn" @click="handleLogout">退出</button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-section">
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-value">{{ stats.total || 0 }}</div>
          <div class="stat-label">资产总数</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.in_use || 0 }}</div>
          <div class="stat-label">使用中</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.in_stock || 0 }}</div>
          <div class="stat-label">在库</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ stats.in_repair || 0 }}</div>
          <div class="stat-label">维修中</div>
        </div>
      </div>
    </div>

    <!-- 快捷功能 -->
    <div class="quick-actions">
      <div class="section-title">快捷功能</div>
      <div class="action-grid">
        <div class="action-item" @click="scanCode">
          <div class="action-icon">📷</div>
          <div class="action-text">扫码</div>
        </div>
        <div class="action-item" @click="goToAssets">
          <div class="action-icon">📦</div>
          <div class="action-text">资产</div>
        </div>
        <div class="action-item" @click="goToCheck">
          <div class="action-icon">🔍</div>
          <div class="action-text">盘点</div>
        </div>
        <div class="action-item" @click="goToRepair">
          <div class="action-icon">🔧</div>
          <div class="action-text">报修</div>
        </div>
      </div>
    </div>

    <!-- 最近操作 -->
    <div class="recent-section">
      <div class="section-title">最近操作</div>
      <div class="recent-list">
        <div
          v-for="asset in recentAssets"
          :key="asset.id"
          class="recent-item"
          @click="goToDetail(asset.id)"
        >
          <div class="asset-info">
            <div class="asset-name">{{ asset.name }}</div>
            <div class="asset-no">{{ asset.asset_no }}</div>
          </div>
          <div class="asset-status" :class="asset.status">
            {{ getStatusText(asset.status) }}
          </div>
        </div>
        <div v-if="recentAssets.length === 0" class="empty-tip">
          暂无最近操作
        </div>
      </div>
    </div>

    <!-- 底部导航 -->
    <div class="tab-bar">
      <div class="tab-item active">
        <span class="tab-icon">🏠</span>
        <span class="tab-text">首页</span>
      </div>
      <div class="tab-item" @click="goToAssets">
        <span class="tab-icon">📦</span>
        <span class="tab-text">资产</span>
      </div>
      <div class="tab-item scan-btn" @click="scanCode">
        <span class="tab-icon">📷</span>
      </div>
      <div class="tab-item" @click="goToCheck">
        <span class="tab-icon">🔍</span>
        <span class="tab-text">盘点</span>
      </div>
      <div class="tab-item" @click="goToProfile">
        <span class="tab-icon">👤</span>
        <span class="tab-text">我的</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { assetApi, inventoryCheckApi } from '@/api/modules'

const router = useRouter()
const userStore = useUserStore()

const stats = ref({})
const recentAssets = ref([])
const pendingChecks = ref(0)
const pendingRepairs = ref(0)

onMounted(async () => {
  await Promise.all([
    loadStats(),
    loadRecentAssets(),
    loadPendingTasks()
  ])
})

async function loadStats() {
  try {
    const res = await assetApi.getStats()
    stats.value = res
  } catch (error) {
    console.error('加载统计数据失败', error)
  }
}

async function loadRecentAssets() {
  try {
    const res = await assetApi.list({ page: 1, page_size: 5 })
    recentAssets.value = res.items || []
  } catch (error) {
    console.error('加载最近资产失败', error)
  }
}

async function loadPendingTasks() {
  try {
    // 待盘点任务
    const checkRes = await inventoryCheckApi.list({ status: 'in_progress' })
    pendingChecks.value = checkRes.total || 0

    // 待处理报修
    // 可以通过用户信息获取
  } catch (error) {
    console.error('加载待办任务失败', error)
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

function scanCode() {
  router.push('/mobile/scan')
}

function goToAssets() {
  router.push('/mobile/assets')
}

function goToDetail(id) {
  router.push(`/mobile/assets/${id}`)
}

function goToCheck() {
  router.push('/mobile/check')
}

function goToRepair() {
  router.push('/mobile/repair')
}

function goToProfile() {
  router.push('/mobile/profile')
}

function handleLogout() {
  userStore.logout()
  router.push('/mobile/login')
}
</script>

<style scoped>
.mobile-home {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 80px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px 16px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avatar {
  width: 50px;
  height: 50px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  color: #fff;
}

.info {
  color: #fff;
}

.name {
  font-size: 18px;
  font-weight: 500;
}

.role {
  font-size: 12px;
  opacity: 0.8;
}

.logout-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  padding: 8px 16px;
  border-radius: 20px;
  font-size: 14px;
  cursor: pointer;
}

.stats-section {
  margin: -30px 16px 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  text-align: center;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.quick-actions, .recent-section {
  margin: 16px;
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.section-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
  margin-bottom: 16px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.action-icon {
  width: 48px;
  height: 48px;
  background: #f5f7fa;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.action-text {
  font-size: 12px;
  color: #606266;
}

.recent-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  cursor: pointer;
}

.recent-item:active {
  background: #ebeef5;
}

.asset-name {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.asset-no {
  font-size: 12px;
  color: #909399;
}

.asset-status {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 12px;
  background: #e6f7ff;
  color: #1890ff;
}

.asset-status.in_use {
  background: #f6ffed;
  color: #52c41a;
}

.asset-status.repair {
  background: #fff7e6;
  color: #fa8c16;
}

.asset-status.scrapped {
  background: #fff1f0;
  color: #ff4d4f;
}

.empty-tip {
  text-align: center;
  color: #909399;
  padding: 20px;
  font-size: 14px;
}

.tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  display: flex;
  justify-content: space-around;
  align-items: center;
  height: 60px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  color: #909399;
  cursor: pointer;
}

.tab-item.active {
  color: #667eea;
}

.tab-item.scan-btn .tab-icon {
  width: 50px;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-top: -20px;
  color: #fff;
}

.tab-icon {
  font-size: 22px;
}

.tab-text {
  font-size: 10px;
}
</style>
