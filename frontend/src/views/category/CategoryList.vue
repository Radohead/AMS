<template>
  <div class="category-list">
    <div class="page-header">
      <span class="title">资产分类</span>
      <el-button type="primary" @click="showDialog('create')">
        <el-icon><Plus /></el-icon>
        新建分类
      </el-button>
    </div>

    <el-card>
      <el-tree
        :data="treeData"
        :props="{ label: 'name', children: 'children' }"
        node-key="id"
        default-expand-all
      >
        <template #default="{ node, data }">
          <span class="tree-node">
            <span>{{ data.name }}</span>
            <span class="node-actions">
              <el-tag size="small" :type="data.asset_type === 'fixed' ? '' : 'warning'">
                {{ data.asset_type === 'fixed' ? '固定资产' : '易耗品' }}
              </el-tag>
              <el-button type="primary" link size="small" @click.stop="showDialog('edit', data)">编辑</el-button>
              <el-button type="danger" link size="small" @click.stop="handleDelete(data)">删除</el-button>
            </span>
          </span>
        </template>
      </el-tree>
    </el-card>

    <!-- 新建/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="500px"
      @closed="resetForm"
    >
      <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类编码" prop="code">
          <el-input v-model="form.code" placeholder="请输入分类编码" :disabled="isEdit" />
        </el-form-item>
        <el-form-item label="上级分类">
          <el-cascader
            v-model="form.parent_id"
            :options="treeData"
            :props="{ checkStrictly: true, emitPath: false, label: 'name', value: 'id' }"
            placeholder="请选择上级分类（可选）"
            clearable
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="资产类型" prop="asset_type">
          <el-radio-group v-model="form.asset_type">
            <el-radio label="fixed">固定资产</el-radio>
            <el-radio label="consumable">易耗品</el-radio>
          </el-radio-group>
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { categoryApi } from '@/api/modules'

const treeData = ref([])
const dialogVisible = ref(false)
const dialogTitle = ref('新建分类')
const isEdit = ref(false)
const saving = ref(false)
const formRef = ref()

const form = reactive({
  name: '',
  code: '',
  parent_id: null,
  asset_type: 'fixed',
  description: ''
})

const rules = {
  name: [{ required: true, message: '请输入分类名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入分类编码', trigger: 'blur' }],
  asset_type: [{ required: true, message: '请选择资产类型', trigger: 'change' }]
}

onMounted(async () => {
  await loadData()
})

async function loadData() {
  try {
    treeData.value = await categoryApi.getTree()
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

function showDialog(type, data = null) {
  if (type === 'create') {
    dialogTitle.value = '新建分类'
    isEdit.value = false
  } else {
    dialogTitle.value = '编辑分类'
    isEdit.value = true
    Object.keys(form).forEach(key => {
      form[key] = data[key] || null
    })
  }
  dialogVisible.value = true
}

function resetForm() {
  formRef.value?.resetFields()
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (isEdit.value) {
      await categoryApi.update(form.id, form)
      ElMessage.success('更新成功')
    } else {
      await categoryApi.create(form)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await loadData()
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

async function handleDelete(data) {
  try {
    await ElMessageBox.confirm(`确定要删除分类 "${data.name}" 吗？`, '提示', {
      type: 'warning'
    })
    await categoryApi.delete(data.id)
    ElMessage.success('删除成功')
    await loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}
</script>

<style scoped>
.category-list {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .title {
      font-size: 18px;
      font-weight: 600;
    }
  }

  .tree-node {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    padding-right: 20px;

    .node-actions {
      display: flex;
      gap: 10px;
      align-items: center;
    }
  }
}
</style>
