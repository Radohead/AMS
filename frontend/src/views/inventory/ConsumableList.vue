<template>
  <div class="consumable-list">
    <div class="page-header">
      <span class="title">易耗品管理</span>
    </div>

    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="资产名称" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="asset_no" label="资产编码" width="150" />
      <el-table-column prop="name" label="名称" min-width="150" />
      <el-table-column prop="unit" label="单位" width="80" />
      <el-table-column prop="current_stock" label="当前库存" width="100" align="center">
        <template #default="{ row }">
          <el-text :type="row.current_stock <= row.min_stock ? 'danger' : 'success'">
            {{ row.current_stock }}
          </el-text>
        </template>
      </el-table-column>
      <el-table-column prop="min_stock" label="最低库存" width="100" align="center" />
      <el-table-column prop="location" label="存放位置" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.current_stock <= row.min_stock ? 'danger' : 'success'" size="small">
            {{ row.current_stock <= row.min_stock ? '需要补货' : '正常' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="showConsumeDialog(row)">领用</el-button>
          <el-button type="success" link @click="showRestockDialog(row)">补货</el-button>
          <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pagination" v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadData" @current-change="loadData" />

    <!-- 领用对话框 -->
    <el-dialog v-model="consumeDialogVisible" title="领用易耗品" width="400px">
      <el-form :model="consumeForm" label-width="80px">
        <el-form-item label="资产">{{ currentItem?.name }}</el-form-item>
        <el-form-item label="当前库存">{{ currentItem?.current_stock }} {{ currentItem?.unit }}</el-form-item>
        <el-form-item label="领用数量" required>
          <el-input-number v-model="consumeForm.quantity" :min="1" :max="currentItem?.current_stock || 1" />
        </el-form-item>
        <el-form-item label="领用人">
          <el-select v-model="consumeForm.employee_id" placeholder="请选择领用人" filterable style="width: 100%">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="用途">
          <el-input v-model="consumeForm.purpose" type="textarea" :rows="2" placeholder="请输入用途" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="consumeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitConsume">确定</el-button>
      </template>
    </el-dialog>

    <!-- 补货对话框 -->
    <el-dialog v-model="restockDialogVisible" title="补充库存" width="400px">
      <el-form :model="restockForm" label-width="80px">
        <el-form-item label="资产">{{ currentItem?.name }}</el-form-item>
        <el-form-item label="当前库存">{{ currentItem?.current_stock }} {{ currentItem?.unit }}</el-form-item>
        <el-form-item label="补货数量" required>
          <el-input-number v-model="restockForm.quantity" :min="1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="restockDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRestock">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { consumableApi, employeeApi } from '@/api/modules'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const employeeList = ref([])
const searchForm = reactive({ keyword: '' })
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const consumeDialogVisible = ref(false)
const restockDialogVisible = ref(false)
const currentItem = ref(null)
const consumeForm = reactive({ quantity: 1, employee_id: null, purpose: '' })
const restockForm = reactive({ quantity: 1 })

onMounted(async () => {
  await loadEmployees()
  await loadData()
})

async function loadEmployees() {
  try {
    const res = await employeeApi.list({ page_size: 1000 })
    employeeList.value = res.items
  } catch (error) { console.error('加载员工失败', error) }
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (searchForm.keyword) params.keyword = searchForm.keyword
    const res = await consumableApi.getStock(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { searchForm.keyword = ''; pagination.page = 1; loadData() }
function goDetail(id) { router.push(`/assets/${id}`) }

function showConsumeDialog(row) {
  currentItem.value = row
  consumeForm.quantity = 1
  consumeForm.employee_id = null
  consumeForm.purpose = ''
  consumeDialogVisible.value = true
}

async function submitConsume() {
  if (!consumeForm.employee_id) { ElMessage.warning('请选择领用人'); return }
  try {
    await consumableApi.consume({ asset_id: currentItem.value.id, ...consumeForm })
    ElMessage.success('领用成功')
    consumeDialogVisible.value = false
    loadData()
  } catch (error) { ElMessage.error('领用失败') }
}

function showRestockDialog(row) {
  currentItem.value = row
  restockForm.quantity = 1
  restockDialogVisible.value = true
}

async function submitRestock() {
  try {
    await consumableApi.restock(currentItem.value.id, restockForm.quantity)
    ElMessage.success('补货成功')
    restockDialogVisible.value = false
    loadData()
  } catch (error) { ElMessage.error('补货失败') }
}
</script>

<style scoped>
.consumable-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .search-form { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
  .pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
