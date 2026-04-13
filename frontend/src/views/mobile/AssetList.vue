<template>
  <div class="mobile-assets">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>资产列表</h1>
      <div class="placeholder"></div>
    </div>

    <!-- 搜索栏 -->
    <div class="search-bar">
      <input
        v-model="keyword"
        type="text"
        placeholder="搜索资产名称/编码/序列号"
        @input="debounceSearch"
      />
    </div>

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

    <!-- 资产列表 -->
    <div class="asset-list">
      <div
        v-for="asset in assets"
        :key="asset.id"
        class="asset-item"
        @click="goToDetail(asset.id)"
      >
        <div class="asset-main">
          <div class="asset-name">{{ asset.name }}</div>
          <div class="asset-meta">
            <span class="asset-no">{{ asset.asset_no }}</span>
            <span class="asset-category">{{ asset.category?.name }}</span>
          </div>
        </div>
        <div class="asset-status" :class="asset.status">
          {{ getStatusText(asset.status) }}
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
      <div class="empty" v-if="!loading && assets.length === 0">
        <div class="empty-icon">📦</div>
        <p>暂无资产</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { assetApi } from '@/api/modules'

const router = useRouter()

const keyword = ref('')
const currentStatus = ref('')
const page = ref(1)
const pageSize = 20
const assets = ref([])
const loading = ref(false)
const hasMore = ref(true)

const statusTabs = [
  { label: '全部', value: '' },
  { label: '在库', value: 'stock' },
  { label: '使用中', value: 'in_use' },
  { label: '维修中', value: 'repair' }
]

let searchTimer = null

onMounted(() => {
  loadAssets()
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

function debounceSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    assets.value = []
    loadAssets()
  }, 300)
}

function filterByStatus(status) {
  currentStatus.value = status
  page.value = 1
  assets.value = []
  loadAssets()
}

async function loadAssets() {
  if (loading.value) return

  loading.value = true
  try {
    const params = {
      page: page.value,
      page_size: pageSize
    }
    if (keyword.value) {
      params.keyword = keyword.value
    }
    if (currentStatus.value) {
      params.status = currentStatus.value
    }

    const res = await assetApi.list(params)

    if (page.value === 1) {
      assets.value = res.items || []
    } else {
      assets.value = [...assets.value, ...(res.items || [])]
    }

    hasMore.value = assets.value.length < res.total
  } catch (error) {
    console.error('加载资产失败', error)
  } finally {
    loading.value = false
  }
}

function loadMore() {
  page.value++
  loadAssets()
}

function goToDetail(id) {
  router.push(`/mobile/assets/${id}`)
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-assets {
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

.search-bar {
  padding: 12px 16px;
  background: #fff;
}

.search-bar input {
  width: 100%;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  padding: 0 16px;
  font-size: 14px;
  outline: none;
  box-sizing: border-box;
}

.search-bar input:focus {
  border-color: #667eea;
}

.filter-tabs {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  background: #fff;
  overflow-x: auto;
}

.filter-tab {
  padding: 8px 16px;
  background: #f5f7fa;
  border-radius: 16px;
  font-size: 14px;
  color: #606266;
  white-space: nowrap;
  cursor: pointer;
}

.filter-tab.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.asset-list {
  padding: 12px 16px;
}

.asset-item {
  background: #fff;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 12px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.asset-item:active {
  background: #f5f7fa;
}

.asset-main {
  flex: 1;
  min-width: 0;
}

.asset-name {
  font-size: 16px;
  color: #303133;
  font-weight: 500;
  margin-bottom: 6px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: #909399;
}

.asset-status {
  padding: 4px 10px;
  border-radius: 12px;
  font-size: 12px;
  background: #e6f7ff;
  color: #1890ff;
  white-space: nowrap;
}

.asset-status.in_use {
  background: #f6ffed;
  color: #52c41a;
}

.asset-status.repair {
  background: #fff7e6;
  color: #fa8c16;
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
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.empty p {
  color: #909399;
  font-size: 14px;
}
</style>
