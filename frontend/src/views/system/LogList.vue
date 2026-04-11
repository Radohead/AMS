<template>
  <div class="log-list">
    <div class="page-header">
      <span class="title">操作日志</span>
    </div>

    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="登录日志" name="login" />
      <el-tab-pane label="操作日志" name="operation" />
    </el-tabs>

    <div class="search-form" v-if="activeTab === 'operation'">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="用户名">
          <el-input v-model="searchForm.username" placeholder="请输入用户名" clearable />
        </el-form-item>
        <el-form-item label="资源类型">
          <el-select v-model="searchForm.resource" placeholder="请选择" clearable>
            <el-option label="资产" value="asset" />
            <el-option label="分类" value="category" />
            <el-option label="员工" value="employee" />
            <el-option label="部门" value="department" />
            <el-option label="报修" value="repair" />
            <el-option label="报废" value="scrap" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column v-if="activeTab === 'login'" prop="username" label="用户名" width="150" />
      <el-table-column v-if="activeTab === 'login'" prop="ip_address" label="IP地址" width="150" />
      <el-table-column v-if="activeTab === 'login'" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'success' ? 'success' : 'danger'" size="small">
            {{ row.status === 'success' ? '成功' : '失败' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column v-if="activeTab === 'login'" prop="created_at" label="登录时间" width="180" />

      <template v-if="activeTab === 'operation'">
        <el-table-column prop="username" label="用户名" width="120" />
        <el-table-column prop="action" label="操作" width="150" />
        <el-table-column prop="resource" label="资源类型" width="120">
          <template #default="{ row }">{{ getResourceName(row.resource) }}</template>
        </el-table-column>
        <el-table-column prop="resource_id" label="资源ID" width="100" />
        <el-table-column prop="path" label="请求路径" min-width="200" show-overflow-tooltip />
        <el-table-column prop="ip_address" label="IP地址" width="150" />
        <el-table-column prop="created_at" label="操作时间" width="180" />
      </template>
    </el-table>

    <el-pagination class="pagination" v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadData" @current-change="loadData" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { systemApi } from '@/api/modules'

const loading = ref(false)
const tableData = ref([])
const activeTab = ref('login')
const searchForm = reactive({ username: '', resource: '' })
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const resourceNames = {
  asset: '资产', category: '分类', employee: '员工', department: '部门',
  repair: '报修', scrap: '报废', user: '用户', role: '角色'
}

function getResourceName(resource) { return resourceNames[resource] || resource }

onMounted(async () => { await loadData() })

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    let res
    if (activeTab.value === 'login') { res = await systemApi.getLoginLogs(params) }
    else { Object.assign(params, searchForm); Object.keys(params).forEach(key => { if (!params[key]) delete params[key] }); res = await systemApi.getOperationLogs(params) }
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

function handleTabChange() { pagination.page = 1; loadData() }
function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { Object.keys(searchForm).forEach(key => { searchForm[key] = '' }); pagination.page = 1; loadData() }
</script>

<style scoped>
.log-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .search-form { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
  .pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
