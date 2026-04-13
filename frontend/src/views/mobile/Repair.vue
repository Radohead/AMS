<template>
  <div class="mobile-repair">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>报修管理</h1>
      <button class="add-btn" @click="goToCreate">+</button>
    </div>

    <div class="repair-content">
      <!-- 筛选标签 -->
      <div class="filter-tabs">
        <div
          v-for="tab in statusTabs"
          :key="tab.value"
          class="filter-tab"
          :class="{ active: currentStatus === tab.value }"
          @click="filterByStatus(tab.value)"
        >
          {{ tab.label }}
        </div>
      </div>

      <!-- 报修列表 -->
      <div class="repair-list">
        <div
          v-for="item in repairList"
          :key="item.id"
          class="repair-item"
          @click="goToDetail(item.id)"
        >
          <div class="repair-header">
            <div class="repair-title">{{ item.title || '报修申请' }}</div>
            <div class="repair-status" :class="item.status">
              {{ getStatusText(item.status) }}
            </div>
          </div>
          <div class="repair-info">
            <div class="info-row">
              <span class="label">资产</span>
              <span class="value">{{ item.asset?.name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">申请人</span>
              <span class="value">{{ item.reporter?.name || '-' }}</span>
            </div>
            <div class="info-row">
              <span class="label">申请时间</span>
              <span class="value">{{ formatDate(item.created_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 加载更多 -->
        <div class="load-more" v-if="hasMore && !loading" @click="loadMore">
          加载更多
        </div>

        <!-- 加载中 -->
        <div class="loading" v-if="loading">
          <div class="spinner"></div>
          <span>加载中...</span>
        </div>

        <!-- 空状态 -->
        <div class="empty" v-if="!loading && repairList.length === 0">
          <div class="empty-icon">🔧</div>
          <p>暂无报修记录</p>
          <button class="create-btn" @click="goToCreate">新建报修</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { repairApi } from '@/api/modules'

const router = useRouter()

const currentStatus = ref('')
const page = ref(1)
const pageSize = 20
const repairList = ref([])
const loading = ref(false)
const hasMore = ref(true)

const statusTabs = [
  { label: '全部', value: '' },
  { label: '待处理', value: 'pending' },
  { label: '处理中', value: 'processing' },
  { label: '已完成', value: 'completed' }
]

onMounted(() => {
  loadRepairList()
})

async function loadRepairList() {
  if (loading.value) return

  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }
    if (currentStatus.value) {
      params.status = currentStatus.value
    }

    const res = await repairApi.list(params)

    if (page.value === 1) {
      repairList.value = res.items || []
    } else {
      repairList.value = [...repairList.value, ...(res.items || [])]
    }

    hasMore.value = repairList.value.length < (res.total || 0)
  } catch (error) {
    console.error('加载报修列表失败', error)
  } finally {
    loading.value = false
  }
}

function filterByStatus(status) {
  currentStatus.value = status
  page.value = 1
  repairList.value = []
  loadRepairList()
}

function loadMore() {
  page.value++
  loadRepairList()
}

function getStatusText(status) {
  const map = {
    pending: '待处理',
    processing: '处理中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}

function goToDetail(id) {
  router.push(`/mobile/repair/${id}`)
}

function goToCreate() {
  router.push('/mobile/repair/create')
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-repair {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 20px;
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

.add-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  font-size: 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.repair-content {
  padding: 12px 16px;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  overflow-x: auto;
}

.filter-tab {
  padding: 8px 16px;
  background: #fff;
  border-radius: 20px;
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.filter-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.repair-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.repair-item {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.repair-item:active {
  background: #f5f7fa;
}

.repair-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.repair-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.repair-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  background: #e6f7ff;
  color: #1890ff;
}

.repair-status.processing {
  background: #fff7e6;
  color: #fa8c16;
}

.repair-status.completed {
  background: #f6ffed;
  color: #52c41a;
}

.repair-status.cancelled {
  background: #f5f5f5;
  color: #999;
}

.repair-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.info-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.info-row .label {
  color: #909399;
}

.info-row .value {
  color: #606266;
}

.load-more {
  text-align: center;
  padding: 16px;
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px;
  color: #909399;
  font-size: 14px;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid #f5f7fa;
  border-top-color: #667eea;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
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
</style>
