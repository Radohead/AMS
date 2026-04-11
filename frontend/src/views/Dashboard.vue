<template>
  <div class="dashboard">
    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card" v-for="stat in stats" :key="stat.label">
        <div class="stat-icon" :style="{ background: stat.color }">
          <el-icon :size="24"><component :is="stat.icon" /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
      </div>
    </div>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="chart-row">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>资产类型分布</span>
          </template>
          <div ref="typeChartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>资产状态分布</span>
          </template>
          <div ref="statusChartRef" class="chart"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 待处理事项 -->
    <el-row :gutter="20" class="todo-row">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>待处理报修</span>
          </template>
          <div class="todo-list">
            <div v-for="item in pendingRepairs" :key="item.id" class="todo-item">
              <span class="todo-title">{{ item.asset_name }}</span>
              <el-tag size="small" :type="getPriorityType(item.priority)">
                {{ getPriorityLabel(item.priority) }}
              </el-tag>
            </div>
            <el-empty v-if="!pendingRepairs.length" description="暂无待处理" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>待审批报废</span>
          </template>
          <div class="todo-list">
            <div v-for="item in pendingScraps" :key="item.id" class="todo-item">
              <span class="todo-title">{{ item.asset_name }}</span>
              <el-tag size="small" type="warning">待审批</el-tag>
            </div>
            <el-empty v-if="!pendingScraps.length" description="暂无待处理" />
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>库存预警</span>
          </template>
          <div class="todo-list">
            <div v-for="item in lowStockItems" :key="item.id" class="todo-item">
              <span class="todo-title">{{ item.name }}</span>
              <el-tag size="small" type="danger">
                库存: {{ item.current_stock }}/{{ item.min_stock }}
              </el-tag>
            </div>
            <el-empty v-if="!lowStockItems.length" description="暂无预警" />
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { assetApi, repairApi, scrapApi, consumableApi } from '@/api/modules'

const stats = ref([
  { label: '资产总数', value: 0, icon: 'Box', color: '#409eff' },
  { label: '使用中', value: 0, icon: 'Check', color: '#67c23a' },
  { label: '空闲中', value: 0, icon: 'Clock', color: '#909399' },
  { label: '维修中', value: 0, icon: 'Tools', color: '#e6a23c' }
])

const pendingRepairs = ref([])
const pendingScraps = ref([])
const lowStockItems = ref([])

const typeChartRef = ref()
const statusChartRef = ref()

onMounted(async () => {
  await loadStats()
  await loadTodos()
})

async function loadStats() {
  try {
    const res = await assetApi.getStats()
    stats.value[0].value = res.total
    stats.value[1].value = res.in_use
    stats.value[2].value = res.in_stock
    stats.value[3].value = res.in_repair
  } catch (error) {
    console.error('加载统计失败', error)
  }
}

async function loadTodos() {
  try {
    // 待处理报修
    const repairRes = await repairApi.list({ status: 'pending', page_size: 5 })
    pendingRepairs.value = repairRes.items || []

    // 待审批报废
    const scrapRes = await scrapApi.list({ status: 'pending', page_size: 5 })
    pendingScraps.value = scrapRes.items || []

    // 库存预警
    lowStockItems.value = await consumableApi.getLowStock()
  } catch (error) {
    console.error('加载待办失败', error)
  }
}

function getPriorityType(priority) {
  const types = { low: 'info', normal: '', high: 'warning', urgent: 'danger' }
  return types[priority] || ''
}

function getPriorityLabel(priority) {
  const labels = { low: '低', normal: '普通', high: '高', urgent: '紧急' }
  return labels[priority] || priority
}
</script>

<style scoped>
.dashboard {
  .stat-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 20px;
    margin-bottom: 20px;
  }

  .stat-card {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    display: flex;
    align-items: center;
    gap: 20px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.05);

    .stat-icon {
      width: 60px;
      height: 60px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: #fff;
    }

    .stat-value {
      font-size: 28px;
      font-weight: 600;
      color: #303133;
    }

    .stat-label {
      color: #909399;
      margin-top: 4px;
    }
  }

  .chart-row,
  .todo-row {
    margin-bottom: 20px;
  }

  .chart-card {
    .chart {
      height: 300px;
    }
  }

  .todo-list {
    .todo-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }
    }

    .todo-title {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}
</style>
