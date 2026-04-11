<template>
  <div class="role-list">
    <div class="page-header">
      <span class="title">角色管理</span>
      <el-button type="primary" @click="showDialog('create')">
        <el-icon><Plus /></el-icon>
        新建角色
      </el-button>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="name" label="角色名称" width="150" />
      <el-table-column prop="code" label="角色编码" width="150" />
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column label="权限" min-width="300">
        <template #default="{ row }">
          <el-tag v-for="perm in row.permissions?.slice(0, 5)" :key="perm.id" size="small" style="margin-right: 5px; margin-bottom: 2px">{{ perm.name }}</el-tag>
          <el-tag v-if="row.permissions?.length > 5" size="small">+{{ row.permissions.length - 5 }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="showDialog('edit', row)" :disabled="row.is_system">编辑</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入角色名称" />
        </el-form-item>
        <el-form-item label="角色编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入角色编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="权限">
          <div class="permission-group">
            <el-checkbox-group v-model="form.permission_ids">
              <el-descriptions :column="2" border>
                <el-descriptions-item v-for="(perms, resource) in groupedPermissions" :key="resource" :label="getResourceName(resource)" :span="2">
                  <el-checkbox v-for="perm in perms" :key="perm.id" :label="perm.id" style="margin: 5px 10px">{{ perm.name }}</el-checkbox>
                </el-descriptions-item>
              </el-descriptions>
            </el-checkbox-group>
          </div>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { systemApi } from '@/api/modules'

const loading = ref(false)
const tableData = ref([])
const groupedPermissions = ref({})
const dialogVisible = ref(false)
const dialogTitle = ref('新建角色')
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const form = reactive({ name: '', code: '', description: '', permission_ids: [] })
const rules = {
  name: [{ required: true, message: '请输入角色名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入角色编码', trigger: 'blur' }]
}

const resourceNames = {
  asset: '资产管理', category: '资产分类', employee: '员工管理', department: '部门管理',
  repair: '报修管理', scrap: '报废管理', inventory: '库存管理', inventory_check: '盘点管理',
  user: '用户管理', role: '角色管理', permission: '权限管理'
}

function getResourceName(resource) { return resourceNames[resource] || resource }

onMounted(async () => {
  await Promise.all([loadRoles(), loadPermissions()])
})

async function loadRoles() {
  loading.value = true
  try { tableData.value = await systemApi.getRoles() }
  catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

async function loadPermissions() {
  try { groupedPermissions.value = await systemApi.getPermissionsGrouped() }
  catch (error) { console.error('加载权限失败', error) }
}

function showDialog(type, data = null) {
  dialogTitle.value = type === 'create' ? '新建角色' : '编辑角色'
  isEdit.value = type === 'edit'
  if (data) {
    form.id = data.id
    form.name = data.name
    form.code = data.code
    form.description = data.description || ''
    form.permission_ids = data.permissions?.map(p => p.id) || []
  }
  dialogVisible.value = true
}

function resetForm() { formRef.value?.resetFields() }

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) { await systemApi.updateRole(form.id, form); ElMessage.success('更新成功') }
    else { await systemApi.createRole(form); ElMessage.success('创建成功') }
    dialogVisible.value = false
    await loadRoles()
  } catch (error) { ElMessage.error('操作失败') }
  finally { saving.value = false }
}
</script>

<style scoped>
.role-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .permission-group { max-height: 400px; overflow-y: auto; width: 100%; }
}
</style>
