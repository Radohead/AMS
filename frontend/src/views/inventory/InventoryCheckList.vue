<template>
  <div class="inventory-check-list">
    <div class="page-header">
      <span class="title">盘点管理</span>
      <el-button type="primary" @click="showDialog('create')">
        <el-icon><Plus /></el-icon>
        新建盘点
      </el-button>
    </div>

    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="计划中" value="planning" />
            <el-option label="进行中" value="in_progress" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="name" label="盘点名称" min-width="150" />
      <el-table-column prop="start_date" label="开始日期" width="120" />
      <el-table-column prop="end_date" label="结束日期" width="120" />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="250" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
          <template v-if="row.status === 'planning'">
            <el-button type="success" link @click="startCheck(row)">开始盘点</el-button>
          </template>
          <template v-if="row.status === 'in_progress'">
            <el-button type="success" link @click="scanCheck(row)">扫码盘点</el-button>
            <el-button type="warning" link @click="completeCheck(row)">完成盘点</el-button>
          </template>
          <template v-if="row.status === 'completed'">
            <el-button type="primary" link @click="showReport(row)">查看报告</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pagination" v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadData" @current-change="loadData" />

    <!-- 新建盘点对话框 -->
    <el-dialog v-model="dialogVisible" title="新建盘点计划" width="500px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="盘点名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入盘点名称" />
        </el-form-item>
        <el-form-item label="开始日期" prop="start_date">
          <el-date-picker v-model="form.start_date" type="datetime" placeholder="选择开始日期" style="width: 100%" format="YYYY-MM-DD HH:mm" />
        </el-form-item>
        <el-form-item label="盘点分类">
          <el-cascader v-model="form.categories" :options="categoryTree" :props="{ multiple: true, emitPath: false, label: 'name', value: 'id' }" placeholder="可多选分类" clearable style="width: 100%" />
        </el-form-item>
        <el-form-item label="盘点部门">
          <el-select v-model="form.departments" multiple placeholder="可多选部门" clearable style="width: 100%">
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>

    <!-- 报告对话框 -->
    <el-dialog v-model="reportDialogVisible" title="盘点报告" width="700px">
      <el-descriptions :column="2" border v-if="reportData.check">
        <el-descriptions-item label="盘点名称">{{ reportData.check.name }}</el-descriptions-item>
        <el-descriptions-item label="盘点时间">{{ reportData.check.start_date }} ~ {{ reportData.check.end_date }}</el-descriptions-item>
      </el-descriptions>
      <el-divider />
      <el-row :gutter="20" class="report-summary">
        <el-col :span="6"><el-statistic title="总资产数" :value="reportData.summary?.total || 0" /></el-col>
        <el-col :span="6"><el-statistic title="正常" :value="reportData.summary?.normal || 0" /></el-col>
        <el-col :span="6"><el-statistic title="差异" :value="reportData.summary?.discrepancy || 0" /></el-col>
        <el-col :span="6"><el-statistic title="未盘点" :value="reportData.summary?.unchecked || 0" /></el-col>
      </el-row>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { inventoryCheckApi, categoryApi, departmentApi } from '@/api/modules'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const categoryTree = ref([])
const departmentList = ref([])
const searchForm = reactive({ status: '' })
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const dialogVisible = ref(false)
const reportDialogVisible = ref(false)
const saving = ref(false)
const formRef = ref()
const reportData = ref({})

const form = reactive({ name: '', start_date: null, categories: [], departments: [] })
const rules = {
  name: [{ required: true, message: '请输入盘点名称', trigger: 'blur' }],
  start_date: [{ required: true, message: '请选择开始日期', trigger: 'change' }]
}

onMounted(async () => {
  await Promise.all([loadCategories(), loadDepartments()])
  await loadData()
})

async function loadCategories() {
  try { categoryTree.value = await categoryApi.getTree() }
  catch (error) { console.error('加载分类失败', error) }
}

async function loadDepartments() {
  try { departmentList.value = await departmentApi.list() }
  catch (error) { console.error('加载部门失败', error) }
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (searchForm.status) params.status = searchForm.status
    const res = await inventoryCheckApi.list(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { searchForm.status = ''; pagination.page = 1; loadData() }
function goDetail(id) { router.push(`/inventory-check/${id}`) }

function showDialog() { dialogVisible.value = true }
function resetForm() { formRef.value?.resetFields() }

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    await inventoryCheckApi.create(form)
    ElMessage.success('创建成功')
    dialogVisible.value = false
    loadData()
  } catch (error) { ElMessage.error('创建失败') }
  finally { saving.value = false }
}

async function startCheck(row) {
  try {
    await ElMessageBox.confirm('确定要开始盘点吗？', '提示', { type: 'info' })
    await inventoryCheckApi.start(row.id)
    ElMessage.success('盘点已开始')
    loadData()
  } catch (error) { if (error !== 'cancel') ElMessage.error('操作失败') }
}

function scanCheck(row) { router.push(`/inventory-check/${row.id}/scan`) }

async function completeCheck(row) {
  try {
    await ElMessageBox.confirm('确定要完成盘点吗？', '提示', { type: 'info' })
    await inventoryCheckApi.complete(row.id)
    ElMessage.success('盘点已完成')
    loadData()
  } catch (error) { if (error !== 'cancel') ElMessage.error('操作失败') }
}

async function showReport(row) {
  try { reportData.value = await inventoryCheckApi.getReport(row.id); reportDialogVisible.value = true }
  catch (error) { ElMessage.error('加载报告失败') }
}

function getStatusType(s) { return { planning: 'info', in_progress: 'primary', completed: 'success' }[s] || '' }
function getStatusLabel(s) { return { planning: '计划中', in_progress: '进行中', completed: '已完成' }[s] || s }
</script>

<style scoped>
.inventory-check-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .search-form { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
  .pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
  .report-summary { margin-top: 20px; }
}
</style>
