<template>
  <div class="user-list">
    <div class="page-header">
      <span class="title">用户管理</span>
      <el-button type="primary" @click="showDialog('create')">
        <el-icon><Plus /></el-icon>
        新建用户
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="username" label="用户名" width="150" />
      <el-table-column prop="real_name" label="真实姓名" width="120" />
      <el-table-column prop="email" label="邮箱" width="180" />
      <el-table-column prop="phone" label="电话" width="120" />
      <el-table-column label="角色" min-width="150">
        <template #default="{ row }">
          <el-tag v-for="role in row.roles" :key="role.id" size="small" style="margin-right: 5px">{{ role.name }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="showDialog('edit', row)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)" :disabled="row.is_superuser">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pagination" v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadData" @current-change="loadData" />

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="密码" prop="password" v-if="!isEdit">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="真实姓名">
          <el-input v-model="form.real_name" placeholder="请输入真实姓名" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="电话">
          <el-input v-model="form.phone" placeholder="请输入电话" />
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="form.role_ids" multiple placeholder="请选择角色" style="width: 100%">
            <el-option v-for="role in roleList" :key="role.id" :label="role.name" :value="role.id" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { systemApi } from '@/api/modules'

const loading = ref(false)
const tableData = ref([])
const roleList = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建用户')
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const form = reactive({ username: '', password: '', real_name: '', email: '', phone: '', role_ids: [] })
const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }, { min: 6, message: '密码长度至少6位', trigger: 'blur' }]
}

onMounted(async () => {
  await loadRoles()
  await loadData()
})

async function loadRoles() {
  try { roleList.value = await systemApi.getRoles() }
  catch (error) { console.error('加载角色失败', error) }
}

async function loadData() {
  loading.value = true
  try {
    const res = await systemApi.getUsers({ page: pagination.page, page_size: pagination.page_size })
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

function showDialog(type, data = null) {
  dialogTitle.value = type === 'create' ? '新建用户' : '编辑用户'
  isEdit.value = type === 'edit'
  if (data) {
    form.username = data.username
    form.real_name = data.real_name || ''
    form.email = data.email || ''
    form.phone = data.phone || ''
    form.role_ids = data.roles?.map(r => r.id) || []
  }
  dialogVisible.value = true
}

function resetForm() { formRef.value?.resetFields() }

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) { await systemApi.updateUser(form.id, form); ElMessage.success('更新成功') }
    else { await systemApi.createUser(form); ElMessage.success('创建成功') }
    dialogVisible.value = false
    await loadData()
  } catch (error) { ElMessage.error('操作失败') }
  finally { saving.value = false }
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除用户 "${row.username}" 吗？`, '提示', { type: 'warning' })
    await systemApi.deleteUser(row.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) { if (error !== 'cancel') ElMessage.error('删除失败') }
}
</script>

<style scoped>
.user-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
