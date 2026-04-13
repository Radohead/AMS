<template>
  <div class="qrcode-generator">
    <div class="header">
      <el-button @click="goBack">
        <el-icon><Back /></el-icon> 返回
      </el-button>
      <h2>二维码批量生成</h2>
      <div class="header-tip">请在右侧选择资产后生成二维码</div>
    </div>

    <div class="content">
      <el-row :gutter="20">
        <!-- 左侧：资产选择 -->
        <el-col :span="14">
          <el-card class="filter-card">
            <template #header>
              <span>选择资产</span>
            </template>

            <!-- 筛选条件 -->
            <div class="filter-form">
              <el-form :inline="true">
                <el-form-item label="分类">
                  <el-select
                    v-model="filters.categoryId"
                    placeholder="请选择分类"
                    clearable
                    @change="handleFilterChange"
                  >
                    <el-option
                      v-for="cat in categories"
                      :key="cat.id"
                      :label="cat.name"
                      :value="cat.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="部门">
                  <el-select
                    v-model="filters.departmentId"
                    placeholder="请选择部门"
                    clearable
                    @change="handleFilterChange"
                  >
                    <el-option
                      v-for="dept in departments"
                      :key="dept.id"
                      :label="dept.name"
                      :value="dept.id"
                    />
                  </el-select>
                </el-form-item>

                <el-form-item label="状态">
                  <el-select
                    v-model="filters.status"
                    placeholder="请选择状态"
                    clearable
                    @change="handleFilterChange"
                  >
                    <el-option label="在库" value="stock" />
                    <el-option label="使用中" value="in_use" />
                    <el-option label="维修中" value="repair" />
                  </el-select>
                </el-form-item>
              </el-form>

              <el-input
                v-model="filters.keyword"
                placeholder="搜索资产名称/编码"
                clearable
                @input="debounceSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>

            <!-- 资产列表 -->
            <div class="asset-list">
              <el-table
                ref="assetTable"
                :data="assets"
                v-loading="loading"
                @selection-change="handleSelectionChange"
                height="400"
              >
                <el-table-column type="selection" width="50" />
                <el-table-column prop="name" label="资产名称" min-width="150" />
                <el-table-column prop="asset_no" label="资产编码" width="150" />
                <el-table-column prop="category_name" label="分类" width="100" />
                <el-table-column prop="status_text" label="状态" width="80">
                  <template #default="{ row }">
                    <el-tag :type="getStatusType(row.status)" size="small">
                      {{ row.status_text }}
                    </el-tag>
                  </template>
                </el-table-column>
              </el-table>

              <el-pagination
                v-model:current-page="pagination.page"
                v-model:page-size="pagination.pageSize"
                :total="pagination.total"
                :page-sizes="[20, 50, 100]"
                layout="total, sizes, prev, pager, next"
                @size-change="loadAssets"
                @current-change="loadAssets"
                class="pagination"
              />
            </div>

            <div class="selection-info">
              已选择 <strong>{{ selectedAssets.length }}</strong> 项资产
              <el-button type="text" @click="selectAll">全选当前页</el-button>
              <el-button type="text" @click="clearSelection">清空</el-button>
            </div>
          </el-card>
        </el-col>

        <!-- 右侧：二维码设置和预览 -->
        <el-col :span="10">
          <el-card class="settings-card">
            <template #header>
              <span>二维码设置</span>
            </template>

            <el-form label-width="100px">
              <el-form-item label="二维码尺寸">
                <el-radio-group v-model="settings.size">
                  <el-radio value="2cm">2cm</el-radio>
                  <el-radio value="3cm">3cm</el-radio>
                  <el-radio value="4cm">4cm</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="每页数量">
                <el-radio-group v-model="settings.perPage">
                  <el-radio :value="6">6个/页</el-radio>
                  <el-radio :value="9">9个/页</el-radio>
                  <el-radio :value="12">12个/页</el-radio>
                  <el-radio :value="16">16个/页</el-radio>
                </el-radio-group>
              </el-form-item>

              <el-form-item label="包含信息">
                <el-checkbox-group v-model="settings.includes">
                  <el-checkbox label="name">资产名称</el-checkbox>
                  <el-checkbox label="asset_no">资产编码</el-checkbox>
                  <el-checkbox label="category">分类</el-checkbox>
                  <el-checkbox label="location">位置</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="显示规格">
                <el-checkbox-group v-model="settings.includes">
                  <el-checkbox label="brand">品牌</el-checkbox>
                  <el-checkbox label="model">型号</el-checkbox>
                  <el-checkbox label="spec">规格</el-checkbox>
                </el-checkbox-group>
              </el-form-item>

              <el-form-item label="打印模板">
                <el-select v-model="settings.template">
                  <el-option label="标准模板" value="standard" />
                  <el-option label="紧凑模板" value="compact" />
                  <el-option label="带Logo模板" value="withLogo" />
                </el-select>
              </el-form-item>

              <el-form-item label="样式">
                <el-color-picker v-model="settings.color" />
                <span class="color-label">前景色</span>
                <el-color-picker v-model="settings.bgColor" />
                <span class="color-label">背景色</span>
              </el-form-item>
            </el-form>
          </el-card>

          <el-card class="preview-card">
            <template #header>
              <span>预览</span>
            </template>

            <div class="preview-container">
              <div class="preview-grid" :style="previewStyle">
                <div
                  v-for="i in Math.min(selectedAssets.length, 4)"
                  :key="i"
                  class="preview-item"
                >
                  <div class="qr-placeholder">
                    <el-icon :size="40"><Document /></el-icon>
                  </div>
                  <div class="preview-label" v-if="settings.includes.includes('name')">
                    {{ selectedAssets[i-1]?.name || '示例资产' }}
                  </div>
                  <div class="preview-label small" v-if="settings.includes.includes('asset_no')">
                    {{ selectedAssets[i-1]?.asset_no || 'AS20240101XXX' }}
                  </div>
                </div>
              </div>
            </div>

            <div class="preview-actions">
              <el-button type="success" @click="handleGenerate" :disabled="selectedAssets.length === 0" :loading="generating">
                生成二维码
              </el-button>
              <el-button @click="handlePreview" :disabled="selectedAssets.length === 0">
                详细预览
              </el-button>
              <el-button type="primary" @click="handleExport" :disabled="selectedAssets.length === 0">
                导出 PDF
              </el-button>
              <el-button @click="handlePrint" :disabled="selectedAssets.length === 0">
                直接打印
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 预览弹窗 -->
    <el-dialog
      v-model="previewVisible"
      title="二维码预览"
      width="90%"
      :close-on-click-modal="false"
    >
      <div class="preview-dialog-content" ref="previewContent">
        <div class="qr-page" v-for="(page, pageIndex) in previewPages" :key="pageIndex">
          <div
            v-for="asset in page"
            :key="asset.id"
            class="qr-item"
            :style="qrItemStyle"
          >
            <canvas :ref="el => setCanvasRef(el, asset.id)"></canvas>
            <div class="qr-info">
              <div v-if="settings.includes.includes('name')" class="info-name">
                {{ asset.name }}
              </div>
              <div v-if="settings.includes.includes('asset_no')" class="info-no">
                {{ asset.asset_no }}
              </div>
              <div v-if="settings.includes.includes('category')" class="info-category">
                {{ asset.category?.name || '-' }}
              </div>
              <div v-if="settings.includes.includes('location')" class="info-location">
                {{ asset.location || '-' }}
              </div>
              <div v-if="asset.brand || asset.model" class="info-spec">
                {{ [asset.brand, asset.model].filter(Boolean).join(' ') }}
              </div>
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <el-button @click="previewVisible = false">关闭</el-button>
        <el-button type="primary" @click="handleExport">导出 PDF</el-button>
        <el-button @click="handlePrint">直接打印</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Document } from '@element-plus/icons-vue'
import QRCode from 'qrcode'
import { categoryApi, departmentApi, assetApi } from '@/api/modules'

const router = useRouter()

// 资产数据
const assets = ref([])
const selectedAssets = ref([])
const loading = ref(false)
const assetTable = ref(null)

// 筛选条件
const filters = reactive({
  categoryId: null,
  departmentId: null,
  status: '',
  keyword: ''
})

const categories = ref([])
const departments = ref([])

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 50,
  total: 0
})

// 二维码设置
const settings = reactive({
  size: '3cm',
  perPage: 9,
  includes: ['name', 'asset_no'],
  template: 'standard',
  color: '#000000',
  bgColor: '#ffffff'
})

// 生成状态
const generating = ref(false)

// 预览
const previewVisible = ref(false)
const previewContent = ref(null)
const canvasRefs = reactive({})

// 计算预览样式
const previewStyle = computed(() => {
  const perRow = settings.perPage <= 6 ? 2 : settings.perPage <= 9 ? 3 : 4
  return {
    gridTemplateColumns: `repeat(${perRow}, 1fr)`
  }
})

// 计算二维码尺寸
const qrItemStyle = computed(() => {
  const size = parseInt(settings.size) * 37.8 // px
  return {
    width: `${size}px`,
    height: `${size + 40}px`
  }
})

// 计算预览页面
const previewPages = computed(() => {
  const pages = []
  for (let i = 0; i < selectedAssets.value.length; i += settings.perPage) {
    pages.push(selectedAssets.value.slice(i, i + settings.perPage))
  }
  return pages.length > 0 ? pages : [[]]
})

onMounted(() => {
  loadCategories()
  loadDepartments()
  loadAssets()
})

async function loadCategories() {
  try {
    const res = await categoryApi.getTree()
    categories.value = flattenTree(res)
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

async function loadDepartments() {
  try {
    const res = await departmentApi.getTree()
    departments.value = flattenTree(res)
  } catch (error) {
    console.error('加载部门失败', error)
  }
}

function flattenTree(tree) {
  const result = []
  function traverse(nodes) {
    for (const node of nodes) {
      result.push({ id: node.id, name: node.name })
      if (node.children?.length) {
        traverse(node.children)
      }
    }
  }
  traverse(tree)
  return result
}

async function loadAssets() {
  loading.value = true
  try {
    const params = {
      page: pagination.page,
      page_size: pagination.pageSize
    }
    if (filters.keyword) params.keyword = filters.keyword
    if (filters.categoryId) params.category_id = filters.categoryId
    if (filters.departmentId) params.department_id = filters.departmentId
    if (filters.status) params.status = filters.status

    const res = await assetApi.list(params)
    assets.value = (res.items || []).map(asset => ({
      ...asset,
      status_text: getStatusText(asset.status)
    }))
    pagination.total = res.total || 0
  } catch (error) {
    console.error('加载资产失败', error)
  } finally {
    loading.value = false
  }
}

let searchTimer = null
function debounceSearch() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    pagination.page = 1
    loadAssets()
  }, 300)
}

function handleFilterChange() {
  pagination.page = 1
  loadAssets()
}

function handleSelectionChange(selection) {
  selectedAssets.value = selection
}

function selectAll() {
  assets.value.forEach(asset => {
    assetTable.value?.toggleRowSelection(asset, true)
  })
}

function clearSelection() {
  assetTable.value?.clearSelection()
}

function getStatusText(status) {
  const map = {
    stock: '在库',
    in_use: '使用中',
    repair: '维修中',
    scrapped: '已报废',
    lost: '丢失'
  }
  return map[status] || status
}

function getStatusType(status) {
  const map = {
    stock: '',
    in_use: 'success',
    repair: 'warning',
    scrapped: 'info',
    lost: 'danger'
  }
  return map[status] || ''
}

async function handleGenerate() {
  if (selectedAssets.value.length === 0) {
    ElMessage.warning('请先选择资产')
    return
  }

  generating.value = true
  try {
    // 生成二维码
    await generateQRCodes()
    ElMessage.success(`已生成 ${selectedAssets.value.length} 个二维码`)
  } catch (error) {
    ElMessage.error('生成失败')
    console.error(error)
  } finally {
    generating.value = false
  }
}

async function generateQRCodes() {
  // 使用与资产详情一致的URL格式
  const baseUrl = window.location.origin

  for (const asset of selectedAssets.value) {
    const canvas = canvasRefs[asset.id]
    if (!canvas) continue

    // 与资产详情页保持一致：/mobile/assets/{id}
    const qrData = `${baseUrl}/mobile/assets/${asset.id}`

    await QRCode.toCanvas(canvas, qrData, {
      width: 200,
      margin: 1,
      color: {
        dark: settings.color,
        light: settings.bgColor
      }
    })
  }
}

function setCanvasRef(el, id) {
  if (el) {
    canvasRefs[id] = el
  }
}

async function handlePreview() {
  if (selectedAssets.value.length === 0) {
    ElMessage.warning('请先选择资产')
    return
  }

  previewVisible.value = true
  await nextTick()

  // 延迟生成二维码
  setTimeout(async () => {
    await generateQRCodes()
  }, 100)
}

async function handleExport() {
  if (selectedAssets.value.length === 0) {
    ElMessage.warning('请先选择资产')
    return
  }

  try {
    // 使用 html2canvas 和 jsPDF 导出
    const { default: html2canvas } = await import('html2canvas')
    const { default: jsPDF } = await import('jspdf')

    const pages = previewContent.value.querySelectorAll('.qr-page')

    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    for (let i = 0; i < pages.length; i++) {
      if (i > 0) {
        pdf.addPage()
      }

      const canvas = await html2canvas(pages[i], {
        scale: 2,
        useCORS: true,
        backgroundColor: '#ffffff'
      })

      const imgData = canvas.toDataURL('image/png')
      const pdfWidth = pdf.internal.pageSize.getWidth()
      const pdfHeight = (canvas.height * pdfWidth) / canvas.width

      pdf.addImage(imgData, 'PNG', 0, 0, pdfWidth, pdfHeight)
    }

    pdf.save(`资产二维码_${new Date().toISOString().split('T')[0]}.pdf`)
    ElMessage.success('PDF 导出成功')
  } catch (error) {
    ElMessage.error('导出失败')
    console.error(error)
  }
}

function handlePrint() {
  if (selectedAssets.value.length === 0) {
    ElMessage.warning('请先选择资产')
    return
  }

  handlePreview().then(() => {
    setTimeout(() => {
      window.print()
    }, 500)
  })
}

function goBack() {
  router.back()
}

// 简单的 fetch 封装
async function fetch(url, options = {}) {
  const token = localStorage.getItem('token')
  const res = await fetch(url, {
    ...options,
    headers: {
      'Authorization': token ? `Bearer ${token}` : '',
      ...options.headers
    }
  })

  if (!res.ok) {
    throw new Error(res.statusText)
  }

  return res.json()
}
</script>

<style scoped>
.qrcode-generator {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  font-size: 18px;
}

.header-tip {
  color: #909399;
  font-size: 13px;
}

.content {
  min-height: calc(100vh - 140px);
}

.filter-card, .settings-card, .preview-card {
  height: 100%;
}

.filter-form {
  margin-bottom: 16px;
}

.asset-list {
  margin-top: 16px;
}

.pagination {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
}

.selection-info {
  margin-top: 12px;
  padding: 8px 12px;
  background: #f5f7fa;
  border-radius: 4px;
  font-size: 14px;
}

.selection-info strong {
  color: #409eff;
}

.settings-card {
  margin-bottom: 16px;
}

.color-label {
  margin-left: 8px;
  margin-right: 16px;
  font-size: 12px;
  color: #909399;
}

.preview-container {
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-grid {
  display: grid;
  gap: 16px;
}

.preview-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.qr-placeholder {
  width: 80px;
  height: 80px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px dashed #dcdfe6;
  border-radius: 4px;
}

.preview-label {
  margin-top: 8px;
  font-size: 12px;
  text-align: center;
  max-width: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.preview-label.small {
  font-size: 10px;
  color: #909399;
}

.preview-actions {
  margin-top: 16px;
  display: flex;
  gap: 12px;
  justify-content: center;
}

/* 预览弹窗 */
.preview-dialog-content {
  max-height: 70vh;
  overflow-y: auto;
}

.qr-page {
  display: flex;
  flex-wrap: wrap;
  gap: 10mm;
  padding: 10mm;
  background: #fff;
  page-break-after: always;
}

.qr-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 5mm;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.qr-item canvas {
  max-width: 100%;
}

.qr-info {
  text-align: center;
  margin-top: 4px;
}

.info-name {
  font-size: 12px;
  font-weight: 500;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.info-no {
  font-size: 10px;
  color: #666;
}

.info-category {
  font-size: 9px;
  color: #999;
}

.info-location {
  font-size: 9px;
  color: #999;
}

.info-spec {
  font-size: 9px;
  color: #666;
  margin-top: 2px;
}

@media print {
  .qr-page {
    page-break-after: always;
  }
}
</style>
