<template>
  <div class="asset-list">
    <div class="page-header">
      <span class="title">资产管理</span>
      <el-button type="primary" @click="goCreate">
        <el-icon><Plus /></el-icon>
        新建资产
      </el-button>
    </div>

    <!-- 搜索表单 -->
    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="关键词">
          <el-input v-model="searchForm.keyword" placeholder="资产名称/编码/序列号" clearable />
        </el-form-item>
        <el-form-item label="分类">
          <el-cascader
            v-model="searchForm.category_id"
            :options="categoryTree"
            :props="{ checkStrictly: true, emitPath: false }"
            placeholder="请选择分类"
            clearable
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="空闲" value="stock" />
            <el-option label="使用中" value="in_use" />
            <el-option label="维修中" value="repair" />
            <el-option label="已报废" value="scrapped" />
          </el-select>
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="searchForm.asset_type" placeholder="请选择类型" clearable>
            <el-option label="固定资产" value="fixed" />
            <el-option label="易耗品" value="consumable" />
            <el-option label="房地产" value="real_estate" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 数据表格 -->
    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column label="缩略图" width="80">
        <template #default="{ row }">
          <el-image
            v-if="getFirstImage(row)"
            :src="getFirstImage(row)"
            fit="cover"
            style="width: 50px; height: 50px; border-radius: 4px;"
          />
          <div v-else class="no-thumb">
            <el-icon><Picture /></el-icon>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="asset_no" label="资产编码" width="150" />
      <el-table-column prop="name" label="资产名称" min-width="150" show-overflow-tooltip />
      <el-table-column label="分类" width="120">
        <template #default="{ row }">
          {{ row.category?.name || '-' }}
        </template>
      </el-table-column>
      <el-table-column prop="brand" label="品牌" width="100" />
      <el-table-column prop="model" label="型号" width="120" />
      <el-table-column label="类型" width="90">
        <template #default="{ row }">
          <el-tag :class="'type-tag type-' + row.asset_type" size="small">
            {{ row.asset_type === 'fixed' ? '固定资产' : row.asset_type === 'consumable' ? '易耗品' : row.asset_type === 'real_estate' ? '房地产' : row.asset_type }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag :class="'status-tag status-' + row.status" size="small">
            {{ getStatusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="location" label="位置" width="120" show-overflow-tooltip />
      <el-table-column prop="purchase_price" label="价格" width="100" align="right">
        <template #default="{ row }">
          ¥{{ row.purchase_price?.toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
          <el-button type="primary" link @click="goEdit(row.id)">编辑</el-button>
          <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 分页 -->
    <el-pagination
      class="pagination"
      v-model:current-page="pagination.page"
      v-model:page-size="pagination.page_size"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="loadData"
      @current-change="loadData"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { assetApi, categoryApi } from '@/api/modules'

const router = useRouter()

const loading = ref(false)
const tableData = ref([])
const categoryTree = ref([])

const searchForm = reactive({
  keyword: '',
  category_id: null,
  status: '',
  asset_type: ''
})

const pagination = reactive({
  page: 1,
  page_size: 20,
  total: 0
})

onMounted(async () => {
  await loadCategories()
  await loadData()
})

async function loadCategories() {
  try {
    categoryTree.value = await categoryApi.getTree()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

async function loadData() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.page_size,
      ...searchForm
    }
    Object.keys(params).forEach(key => {
      if (!params[key]) delete params[key]
    })

    const res = await assetApi.list(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  pagination.page = 1
  loadData()
}

function handleReset() {
  Object.keys(searchForm).forEach(key => {
    searchForm[key] = key === 'category_id' ? null : ''
  })
  pagination.page = 1
  loadData()
}

function goCreate() {
  router.push('/assets/create')
}

function goDetail(id) {
  router.push(`/assets/${id}`)
}

function goEdit(id) {
  router.push(`/assets/${id}/edit`)
}

async function handleDelete(row) {
  try {
    await ElMessageBox.confirm(`确定要删除资产 "${row.name}" 吗？`, '提示', {
      type: 'warning'
    })
    await assetApi.delete(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

function getStatusLabel(status) {
  const labels = {
    stock: '空闲',
    in_use: '使用中',
    repair: '维修中',
    scrapped: '已报废',
    lost: '丢失'
  }
  return labels[status] || status
}

function getFirstImage(row) {
  if (!row.images) return null
  try {
    const images = typeof row.images === 'string' ? JSON.parse(row.images) : row.images
    return images.length > 0 ? images[0] : null
  } catch {
    return null
  }
}
</script>

<style scoped>
.asset-list {
  .no-thumb {
    width: 50px;
    height: 50px;
    border-radius: 4px;
    background: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #c0c4cc;
    font-size: 20px;
  }
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

  .search-form {
    background: #fff;
    padding: 20px;
    border-radius: 8px;
    margin-bottom: 20px;
  }

  .pagination {
    margin-top: 20px;
    display: flex;
    justify-content: flex-end;
  }
}
</style>
