<template>
  <div class="department-list">
    <div class="page-header">
      <span class="title">部门管理</span>
      <el-button type="primary" @click="showDialog('create')">
        <el-icon><Plus /></el-icon>
        新建部门
      </el-button>
    </div>

    <el-card>
      <el-tree :data="treeData" :props="{ label: 'name', children: 'children' }" node-key="id" default-expand-all>
        <template #default="{ data }">
          <span class="tree-node">
            <span>{{ data.name }}</span>
            <span class="node-actions">
              <el-button type="primary" link size="small" @click.stop="showDialog('edit', data)">编辑</el-button>
              <el-button type="danger" link size="small" @click.stop="handleDelete(data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px" @closed="resetForm">
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="部门名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入部门名称" />
        </el-form-item>
        <el-form-item label="部门编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入部门编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="上级部门">
          <el-cascader v-model="form.parent_id" :options="treeData" :props="{ checkStrictly: true, emitPath: false, label: 'name', value: 'id' }" placeholder="请选择上级部门" clearable style="width: 100%" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="3" placeholder="请输入描述" />
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
import { departmentApi } from '@/api/modules'

const treeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建部门')
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const form = reactive({ name: '', code: '', parent_id: null, description: '' })
const rules = {
  name: [{ required: true, message: '请输入部门名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入部门编码', trigger: 'blur' }]
}

onMounted(async () => { await loadData() })

async function loadData() {
  try { treeData.value = await departmentApi.getTree() }
  catch (error) { ElMessage.error('加载数据失败') }
}

function showDialog(type, data = null) {
  dialogTitle.value = type === 'create' ? '新建部门' : '编辑部门'
  isEdit.value = type === 'edit'
  if (data) { Object.keys(form).forEach(key => { form[key] = data[key] || null }) }
  dialogVisible.value = true
}

function resetForm() { formRef.value?.resetFields() }

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  saving.value = true
  try {
    if (isEdit.value) { await departmentApi.update(form.id, form); ElMessage.success('更新成功') }
    else { await departmentApi.create(form); ElMessage.success('创建成功') }
    dialogVisible.value = false
    await loadData()
  } catch (error) { ElMessage.error('操作失败') }
  finally { saving.value = false }
}

async function handleDelete(data) {
  try {
    await ElMessageBox.confirm(`确定要删除部门 "${data.name}" 吗？`, '提示', { type: 'warning' })
    await departmentApi.delete(data.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) { if (error !== 'cancel') ElMessage.error('删除失败') }
}
</script>

<style scoped>
.department-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .tree-node { display: flex; justify-content: space-between; align-items: center; width: 100%; padding-right: 20px; .node-actions { display: flex; gap: 10px; } }
}
</style>
