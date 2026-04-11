<template>
  <div class="repair-list">
    <div class="page-header">
      <span class="title">报修管理</span>
    </div>

    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待处理" value="pending" />
            <el-option label="已指派" value="assigned" />
            <el-option label="处理中" value="processing" />
            <el-option label="已完成" value="completed" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="searchForm.priority" placeholder="请选择优先级" clearable>
            <el-option label="低" value="low" />
            <el-option label="普通" value="normal" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="order_no" label="工单编号" width="150" />
      <el-table-column prop="asset_name" label="资产名称" min-width="150" />
      <el-table-column prop="description" label="故障描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="优先级" width="80">
        <template #default="{ row }">
          <el-tag :type="getPriorityType(row.priority)" size="small">{{ getPriorityLabel(row.priority) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="160" />
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
          <template v-if="row.status === 'pending'">
            <el-button type="primary" link @click="showAssignDialog(row)">指派</el-button>
          </template>
          <template v-if="row.status === 'assigned'">
            <el-button type="primary" link @click="showCompleteDialog(row)">完成</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pagination" v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadData" @current-change="loadData" />

    <!-- 指派对话框 -->
    <el-dialog v-model="assignDialogVisible" title="指派维修人员" width="400px">
      <el-form label-width="100px">
        <el-form-item label="选择维修人员">
          <el-select v-model="assignForm.handler_id" placeholder="请选择" style="width: 100%">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAssign">确定</el-button>
      </template>
    </el-dialog>

    <!-- 完成对话框 -->
    <el-dialog v-model="completeDialogVisible" title="完成维修" width="500px">
      <el-form :model="completeForm" label-width="100px">
        <el-form-item label="维修结果" required>
          <el-input v-model="completeForm.repair_result" type="textarea" :rows="3" placeholder="请输入维修结果" />
        </el-form-item>
        <el-form-item label="维修费用">
          <el-input-number v-model="completeForm.repair_cost" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="使用的配件">
          <el-input v-model="completeForm.parts_used" placeholder="请输入使用的配件" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="completeDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitComplete">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { repairApi, employeeApi } from '@/api/modules'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const employeeList = ref([])
const searchForm = reactive({ status: '', priority: '' })
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const assignDialogVisible = ref(false)
const completeDialogVisible = ref(false)
const currentOrder = ref(null)
const assignForm = reactive({ handler_id: null })
const completeForm = reactive({ repair_result: '', repair_cost: 0, parts_used: '' })

onMounted(async () => {
  await loadEmployees()
  await loadData()
})

async function loadEmployees() {
  try { const res = await employeeApi.list({ page_size: 1000 }); employeeList.value = res.items }
  catch (error) { console.error('加载员工失败', error) }
}

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    Object.assign(params, searchForm)
    Object.keys(params).forEach(key => { if (!params[key]) delete params[key] })
    const res = await repairApi.list(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { Object.keys(searchForm).forEach(key => { searchForm[key] = '' }); pagination.page = 1; loadData() }
function goDetail(id) { router.push(`/repair/${id}`) }

function showAssignDialog(row) { currentOrder.value = row; assignForm.handler_id = null; assignDialogVisible.value = true }

async function submitAssign() {
  if (!assignForm.handler_id) { ElMessage.warning('请选择维修人员'); return }
  try { await repairApi.assign(currentOrder.value.id, assignForm.handler_id); ElMessage.success('指派成功'); assignDialogVisible.value = false; loadData() }
  catch (error) { ElMessage.error('指派失败') }
}

function showCompleteDialog(row) { currentOrder.value = row; completeForm.repair_result = ''; completeForm.repair_cost = 0; completeForm.parts_used = ''; completeDialogVisible.value = true }

async function submitComplete() {
  if (!completeForm.repair_result) { ElMessage.warning('请输入维修结果'); return }
  try { await repairApi.complete(currentOrder.value.id, completeForm); ElMessage.success('操作成功'); completeDialogVisible.value = false; loadData() }
  catch (error) { ElMessage.error('操作失败') }
}

function getPriorityType(p) { return { low: 'info', normal: '', high: 'warning', urgent: 'danger' }[p] || '' }
function getPriorityLabel(p) { return { low: '低', normal: '普通', high: '高', urgent: '紧急' }[p] || p }
function getStatusType(s) { return { pending: 'warning', assigned: 'primary', processing: 'primary', completed: 'success' }[s] || '' }
function getStatusLabel(s) { return { pending: '待处理', assigned: '已指派', processing: '处理中', completed: '已完成' }[s] || s }
</script>

<style scoped>
.repair-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .search-form { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
  .pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
