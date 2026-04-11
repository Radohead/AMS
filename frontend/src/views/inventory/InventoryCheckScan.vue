<template>
  <div class="scan-check">
    <div class="page-header">
      <el-button @click="goBack">返回</el-button>
      <span class="title">{{ check.name }} - 扫码盘点</span>
      <span class="stats">
        已盘点: {{ checkedCount }} / {{ totalCount }}
      </span>
    </div>

    <el-card class="scan-card">
      <div class="scan-area">
        <el-icon class="scan-icon" :size="60"><Camera /></el-icon>
        <p class="scan-hint">扫描资产二维码或输入资产编码</p>
        <el-input
          v-model="scanInput"
          placeholder="输入资产编码"
          class="scan-input"
          @keyup.enter="handleManualInput"
        >
          <template #append>
            <el-button @click="handleManualInput">确认</el-button>
          </template>
        </el-input>
      </div>
    </el-card>

    <el-card class="current-item" v-if="currentItem">
      <template #header>
        <div class="item-header">
          <span>当前资产</span>
          <el-tag :type="getResultType(currentItem.check_result)">{{ getResultLabel(currentItem.check_result) }}</el-tag>
        </div>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="资产编码">{{ currentItem.asset?.asset_no }}</el-descriptions-item>
        <el-descriptions-item label="资产名称">{{ currentItem.asset?.name }}</el-descriptions-item>
        <el-descriptions-item label="预期状态">{{ currentItem.expected_status }}</el-descriptions-item>
        <el-descriptions-item label="实际状态">
          <el-select v-model="currentItem.actual_status" style="width: 100%">
            <el-option label="空闲" value="stock" />
            <el-option label="使用中" value="in_use" />
            <el-option label="维修中" value="repair" />
            <el-option label="已报废" value="scrapped" />
            <el-option label="丢失" value="lost" />
          </el-select>
        </el-descriptions-item>
        <el-descriptions-item label="预期位置">{{ currentItem.expected_location || '-' }}</el-descriptions-item>
        <el-descriptions-item label="实际位置">
          <el-input v-model="currentItem.actual_location" placeholder="请输入实际位置" />
        </el-descriptions-item>
      </el-descriptions>
      <div class="item-actions">
        <el-button type="primary" @click="confirmItem">确认盘点</el-button>
        <el-button type="warning" @click="markMissing">标记缺失</el-button>
      </div>
    </el-card>

    <el-card class="unchecked-list">
      <template #header>
        <span>待盘点资产 ({{ uncheckedItems.length }})</span>
      </template>
      <el-table :data="uncheckedItems" stripe max-height="400">
        <el-table-column prop="asset.asset_no" label="资产编码" width="150" />
        <el-table-column prop="asset.name" label="资产名称" min-width="150" />
        <el-table-column prop="expected_status" label="预期状态" width="100" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button type="primary" link @click="selectItem(row)">盘点</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { inventoryCheckApi, assetApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const check = ref({})
const items = ref([])
const scanInput = ref('')
const currentItem = ref(null)

const totalCount = computed(() => items.value.length)
const checkedCount = computed(() => items.value.filter(i => i.check_result).length)
const uncheckedItems = computed(() => items.value.filter(i => !i.check_result))

onMounted(async () => {
  await loadData()
})

async function loadData() {
  loading.value = true
  try {
    const checkId = route.params.id
    check.value = await inventoryCheckApi.get(checkId)
    const res = await inventoryCheckApi.getItems(checkId, { page_size: 1000 })
    items.value = res.items
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function handleManualInput() {
  if (!scanInput.value.trim()) return

  try {
    const asset = await assetApi.getByNo(scanInput.value.trim())
    const item = items.value.find(i => i.asset_id === asset.id)
    if (item) {
      selectItem(item)
      scanInput.value = ''
    } else {
      ElMessage.warning('该资产不在本次盘点范围内')
    }
  } catch (error) {
    ElMessage.error('未找到该资产')
  }
}

function selectItem(item) {
  currentItem.value = { ...item }
}

async function confirmItem() {
  if (!currentItem.value) return

  try {
    await inventoryCheckApi.updateItem(check.value.id, currentItem.value.id, {
      actual_status: currentItem.value.actual_status,
      actual_location: currentItem.value.actual_location
    })
    ElMessage.success('盘点成功')
    currentItem.value = null
    await loadData()
  } catch (error) {
    ElMessage.error('盘点失败')
  }
}

async function markMissing() {
  if (!currentItem.value) return

  try {
    await inventoryCheckApi.updateItem(check.value.id, currentItem.value.id, {
      check_result: 'missing'
    })
    ElMessage.success('已标记为缺失')
    currentItem.value = null
    await loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

function goBack() {
  router.back()
}

function getResultType(result) {
  const types = { normal: 'success', discrepancy: 'warning', missing: 'danger', extra: 'info' }
  return types[result] || ''
}

function getResultLabel(result) {
  const labels = { normal: '正常', discrepancy: '差异', missing: '缺失', extra: '多出' }
  return labels[result] || '未盘点'
}
</script>

<style scoped>
.scan-check {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .title {
      font-size: 18px;
      font-weight: 600;
    }

    .stats {
      color: #409eff;
      font-weight: 500;
    }
  }

  .scan-card {
    margin-bottom: 20px;

    .scan-area {
      text-align: center;
      padding: 30px 0;

      .scan-icon {
        color: #409eff;
        margin-bottom: 15px;
      }

      .scan-hint {
        color: #909399;
        margin-bottom: 20px;
      }

      .scan-input {
        max-width: 400px;
        margin: 0 auto;
      }
    }
  }

  .current-item {
    margin-bottom: 20px;

    .item-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    .item-actions {
      margin-top: 20px;
      text-align: center;
    }
  }

  .unchecked-list {
    .el-table {
      max-height: 400px;
    }
  }
}
</style>
