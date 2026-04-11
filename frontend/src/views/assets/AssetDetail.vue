<template>
  <div class="asset-detail" v-loading="loading">
    <div class="page-header">
      <span class="title">资产详情</span>
      <div class="actions">
        <el-button @click="goBack">返回</el-button>
        <el-button type="primary" @click="goEdit">编辑</el-button>
        <el-button @click="showQrCode">二维码</el-button>
        <el-dropdown @command="handleAction">
          <el-button type="primary">
            更多操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="assign">分配</el-dropdown-item>
              <el-dropdown-item command="transfer">调拨</el-dropdown-item>
              <el-dropdown-item command="return">退库</el-dropdown-item>
              <el-dropdown-item command="repair">报修</el-dropdown-item>
              <el-dropdown-item command="scrap">报废</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <el-row :gutter="20">
      <!-- 基本信息 -->
      <el-col :span="16">
        <el-card class="info-card">
          <template #header>
            <span>基本信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="资产编码">{{ asset.asset_no }}</el-descriptions-item>
            <el-descriptions-item label="资产名称">{{ asset.name }}</el-descriptions-item>
            <el-descriptions-item label="分类">{{ asset.category?.name }}</el-descriptions-item>
            <el-descriptions-item label="类型">
              <el-tag :class="'type-tag type-' + asset.asset_type" size="small">
                {{ asset.asset_type === 'fixed' ? '固定资产' : asset.asset_type === 'consumable' ? '易耗品' : asset.asset_type === 'real_estate' ? '房地产' : asset.asset_type }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="品牌">{{ asset.brand || '-' }}</el-descriptions-item>
            <el-descriptions-item label="型号">{{ asset.model || '-' }}</el-descriptions-item>
            <el-descriptions-item label="序列号">{{ asset.serial_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="状态">
              <el-tag :class="'status-tag status-' + asset.status" size="small">
                {{ getStatusLabel(asset.status) }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="存放位置">{{ asset.location || '-' }}</el-descriptions-item>
            <el-descriptions-item label="使用部门">{{ asset.department?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="使用人">{{ asset.user?.name || '-' }}</el-descriptions-item>
            <el-descriptions-item label="保管人">{{ asset.keeper?.name || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="info-card">
          <template #header>
            <span>财务信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="购买日期">{{ asset.purchase_date || '-' }}</el-descriptions-item>
            <el-descriptions-item label="购买价格">¥{{ asset.purchase_price?.toFixed(2) || '0.00' }}</el-descriptions-item>
            <el-descriptions-item label="保修截止">{{ asset.warranty_end || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <el-card class="info-card" v-if="asset.asset_type === 'consumable'">
          <template #header>
            <span>库存信息</span>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="单位">{{ asset.unit || '-' }}</el-descriptions-item>
            <el-descriptions-item label="当前库存">
              <el-text :type="asset.current_stock <= asset.min_stock ? 'danger' : 'success'">
                {{ asset.current_stock }}
              </el-text>
            </el-descriptions-item>
            <el-descriptions-item label="最低库存">{{ asset.min_stock || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 变动记录 -->
        <el-card class="info-card">
          <template #header>
            <span>变动记录</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="record in records"
              :key="record.id"
              :timestamp="record.created_at"
              placement="top"
            >
              <el-card>
                <p><strong>{{ getActionLabel(record.action_type) }}</strong></p>
                <p v-if="record.description">{{ record.description }}</p>
              </el-card>
            </el-timeline-item>
            <el-empty v-if="!records.length" description="暂无变动记录" />
          </el-timeline>
        </el-card>
      </el-col>

      <!-- 右侧信息 -->
      <el-col :span="8">
        <el-card class="info-card">
          <template #header>
            <span>资产图片</span>
            <el-button type="primary" size="small" @click="showUploadPhotoDialog">
              上传照片
            </el-button>
          </template>
          <div class="image-list">
            <el-empty v-if="!images.length" description="暂无图片" />
            <div v-else class="image-grid">
              <div v-for="(img, index) in images" :key="index" class="image-item">
                <el-image
                  :src="img"
                  :preview-src-list="images"
                  fit="cover"
                  class="asset-image"
                />
                <div class="image-overlay">
                  <el-button type="danger" size="small" circle @click="handleDeletePhoto(img)">
                    <el-icon><Delete /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </div>
        </el-card>

        <el-card class="info-card">
          <template #header>
            <span>资产附件</span>
            <el-button type="primary" size="small" @click="showUploadAttachmentDialog">
              上传附件
            </el-button>
          </template>
          <el-table :data="attachments" empty-text="暂无附件">
            <el-table-column prop="name" label="文件名" show-overflow-tooltip />
            <el-table-column prop="type" label="类型" width="80">
              <template #default="{ row }">
                <el-tag size="small">{{ row.type?.toUpperCase() }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="size" label="大小" width="100">
              <template #default="{ row }">
                {{ formatFileSize(row.size) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" width="120">
              <template #default="{ row }">
                <el-button type="primary" size="small" link @click="downloadAttachment(row)">下载</el-button>
                <el-button type="danger" size="small" link @click="handleDeleteAttachment(row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card class="info-card">
          <template #header>
            <span>其他信息</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="创建时间">{{ asset.created_at }}</el-descriptions-item>
            <el-descriptions-item label="更新时间">{{ asset.updated_at }}</el-descriptions-item>
            <el-descriptions-item label="描述">{{ asset.description || '-' }}</el-descriptions-item>
            <el-descriptions-item label="备注">{{ asset.remarks || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>

        <!-- 房地产专用信息 -->
        <el-card class="info-card" v-if="asset.asset_type === 'real_estate'">
          <template #header>
            <span>房地产信息</span>
          </template>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="详细地址">{{ asset.address || '-' }}</el-descriptions-item>
            <el-descriptions-item label="建筑面积">{{ asset.area ? asset.area + ' m²' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="占地面积">{{ asset.land_area ? asset.land_area + ' m²' : '-' }}</el-descriptions-item>
            <el-descriptions-item label="建成年份">{{ asset.build_year || '-' }}</el-descriptions-item>
            <el-descriptions-item label="产权类型">{{ asset.property_type || '-' }}</el-descriptions-item>
            <el-descriptions-item label="产权证号">{{ asset.property_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="土地证号">{{ asset.land_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="楼栋号">{{ asset.building_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="楼层">{{ asset.floor || '-' }}</el-descriptions-item>
            <el-descriptions-item label="房间号">{{ asset.room_no || '-' }}</el-descriptions-item>
            <el-descriptions-item label="用途">{{ asset.usage || '-' }}</el-descriptions-item>
            <el-descriptions-item label="建筑结构">{{ asset.structure || '-' }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>

    <!-- 二维码对话框 -->
    <el-dialog v-model="qrDialogVisible" title="资产二维码" width="350px" center>
      <div class="qr-code-wrapper">
        <img :src="qrCodeUrl" alt="二维码" />
        <p class="asset-no">{{ asset.asset_no }}</p>
        <p class="asset-name">{{ asset.name }}</p>
      </div>
      <template #footer>
        <el-button @click="printQrCode">打印</el-button>
      </template>
    </el-dialog>

    <!-- 分配对话框 -->
    <el-dialog v-model="assignDialogVisible" title="分配资产" width="500px">
      <el-form :model="assignForm" label-width="100px">
        <el-form-item label="使用人">
          <el-select v-model="assignForm.user_id" placeholder="请选择使用人" filterable style="width: 100%">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="保管人">
          <el-select v-model="assignForm.keeper_id" placeholder="请选择保管人" filterable clearable style="width: 100%">
            <el-option v-for="emp in employeeList" :key="emp.id" :label="emp.name" :value="emp.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="使用部门">
          <el-select v-model="assignForm.department_id" placeholder="请选择部门" clearable style="width: 100%">
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="存放位置">
          <el-input v-model="assignForm.location" placeholder="请输入存放位置" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="assignDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitAssign">确定</el-button>
      </template>
    </el-dialog>

    <!-- 报修对话框 -->
    <el-dialog v-model="repairDialogVisible" title="报修申请" width="500px">
      <el-form :model="repairForm" label-width="100px">
        <el-form-item label="故障描述" required>
          <el-input v-model="repairForm.description" type="textarea" :rows="4" placeholder="请描述故障情况" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="repairForm.priority" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="普通" value="normal" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="repairDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitRepair">提交</el-button>
      </template>
    </el-dialog>

    <!-- 调拨对话框 -->
    <el-dialog v-model="transferDialogVisible" title="调拨资产" width="500px">
      <el-form :model="transferForm" label-width="100px">
        <el-form-item label="调入部门" required>
          <el-select v-model="transferForm.department_id" placeholder="请选择调入部门" style="width: 100%">
            <el-option v-for="dept in departmentList" :key="dept.id" :label="dept.name" :value="dept.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="调入位置">
          <el-input v-model="transferForm.location" placeholder="请输入调入位置" />
        </el-form-item>
        <el-form-item label="调拨原因">
          <el-input v-model="transferForm.reason" type="textarea" :rows="3" placeholder="请输入调拨原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="transferDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitTransfer">提交</el-button>
      </template>
    </el-dialog>

    <!-- 报废对话框 -->
    <el-dialog v-model="scrapDialogVisible" title="报废申请" width="500px">
      <el-form :model="scrapForm" label-width="100px">
        <el-form-item label="报废原因" required>
          <el-input v-model="scrapForm.reason" type="textarea" :rows="3" placeholder="请输入报废原因" />
        </el-form-item>
        <el-form-item label="详细说明">
          <el-input v-model="scrapForm.description" type="textarea" :rows="4" placeholder="请详细描述资产状况" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="scrapDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitScrap">提交</el-button>
      </template>
    </el-dialog>

    <!-- 上传照片对话框 -->
    <el-dialog v-model="uploadPhotoDialogVisible" title="上传资产照片" width="500px">
      <el-upload
        ref="photoUploadRef"
        :auto-upload="false"
        :on-change="handlePhotoFileChange"
        :file-list="pendingPhotoFiles"
        accept="image/jpeg,image/png,image/jpg"
        list-type="picture-card"
        :limit="10"
        multiple
      >
        <el-icon><Plus /></el-icon>
      </el-upload>
      <div class="upload-tip">支持 JPG/PNG，单张不超过10MB，最多10张</div>
      <template #footer>
        <el-button @click="uploadPhotoDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUploadPhotos">上传</el-button>
      </template>
    </el-dialog>

    <!-- 上传附件对话框 -->
    <el-dialog v-model="uploadAttachmentDialogVisible" title="上传资产附件" width="500px">
      <el-upload
        ref="attachmentUploadRef"
        :auto-upload="false"
        accept=".pdf,.doc,.docx,.xls,.xlsx,.jpg,.jpeg,.png"
        :limit="20"
        multiple
        drag
      >
        <el-icon><UploadFilled /></el-icon>
        <div>将文件拖到此处，或<em>点击上传</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 PDF、Word、Excel、图片，单文件不超过 20MB，最多20个</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="uploadAttachmentDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitUploadAttachments">上传</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { assetApi, departmentApi, employeeApi, repairApi, scrapApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const loading = ref(false)
const asset = ref({})
const records = ref([])
const images = ref([])
const attachments = ref([])
const departmentList = ref([])
const employeeList = ref([])

const qrDialogVisible = ref(false)
const assignDialogVisible = ref(false)
const uploadPhotoDialogVisible = ref(false)
const uploadAttachmentDialogVisible = ref(false)
const photoUploadRef = ref()
const attachmentUploadRef = ref()
const pendingPhotoFiles = ref([])
const repairDialogVisible = ref(false)
const transferDialogVisible = ref(false)
const scrapDialogVisible = ref(false)

const assignForm = reactive({
  user_id: null,
  keeper_id: null,
  department_id: null,
  location: ''
})

const repairForm = reactive({
  description: '',
  priority: 'normal'
})

const transferForm = reactive({
  department_id: null,
  location: '',
  reason: ''
})

const scrapForm = reactive({
  reason: '',
  description: ''
})

const qrCodeUrl = computed(() => {
  return asset.value.id ? `/api/assets/${asset.value.id}/qrcode` : ''
})

onMounted(async () => {
  await loadData()
  await loadDepartments()
  await loadEmployees()
})

async function loadData() {
  loading.value = true
  try {
    const id = route.params.id
    asset.value = await assetApi.get(id)
    records.value = await assetApi.getRecords(id)
    images.value = asset.value.images ? JSON.parse(asset.value.images) : []
    // 加载附件
    attachments.value = await assetApi.getAttachments(id)
  } catch (error) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

async function loadDepartments() {
  try {
    departmentList.value = await departmentApi.list()
  } catch (error) {
    console.error('加载部门失败', error)
  }
}

async function loadEmployees() {
  try {
    const res = await employeeApi.list({ page_size: 1000 })
    employeeList.value = res.items
  } catch (error) {
    console.error('加载员工失败', error)
  }
}

function goBack() {
  router.back()
}

function goEdit() {
  router.push(`/assets/${route.params.id}/edit`)
}

function showQrCode() {
  qrDialogVisible.value = true
}

function handleAction(command) {
  switch (command) {
    case 'assign':
      assignDialogVisible.value = true
      break
    case 'transfer':
      transferDialogVisible.value = true
      break
    case 'return':
      handleReturn()
      break
    case 'repair':
      repairDialogVisible.value = true
      break
    case 'scrap':
      scrapDialogVisible.value = true
      break
  }
}

async function submitAssign() {
  try {
    await assetApi.assign(route.params.id, assignForm)
    ElMessage.success('分配成功')
    assignDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('分配失败')
  }
}

async function handleReturn() {
  try {
    await assetApi.return(route.params.id)
    ElMessage.success('退库成功')
    loadData()
  } catch (error) {
    ElMessage.error('退库失败')
  }
}

async function submitRepair() {
  try {
    await repairApi.create({
      asset_id: parseInt(route.params.id),
      description: repairForm.description,
      priority: repairForm.priority
    })
    ElMessage.success('报修提交成功')
    repairDialogVisible.value = false
  } catch (error) {
    ElMessage.error('报修提交失败')
  }
}

async function submitTransfer() {
  try {
    await assetApi.transfer(route.params.id, transferForm)
    ElMessage.success('调拨申请已提交')
    transferDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('调拨提交失败')
  }
}

async function submitScrap() {
  try {
    await scrapApi.create({
      asset_id: parseInt(route.params.id),
      reason: scrapForm.reason,
      description: scrapForm.description
    })
    ElMessage.success('报废申请已提交')
    scrapDialogVisible.value = false
  } catch (error) {
    ElMessage.error('报废提交失败')
  }
}

function showUploadPhotoDialog() {
  pendingPhotoFiles.value = []
  photoUploadRef.value?.clearFiles()
  uploadPhotoDialogVisible.value = true
}

function showUploadAttachmentDialog() {
  attachmentUploadRef.value?.clearFiles()
  uploadAttachmentDialogVisible.value = true
}

function handlePhotoFileChange(file, fileList) {
  pendingPhotoFiles.value = fileList
}

async function submitUploadPhotos() {
  if (!pendingPhotoFiles.value.length) {
    ElMessage.warning('请选择照片')
    return
  }
  const files = pendingPhotoFiles.value.map(f => f.raw).filter(Boolean)
  try {
    await assetApi.uploadPhotos(route.params.id, files)
    ElMessage.success('照片上传成功')
    uploadPhotoDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

async function handleDeletePhoto(url) {
  try {
    await assetApi.deletePhoto(route.params.id, url)
    ElMessage.success('照片已删除')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

async function submitUploadAttachments() {
  const fileInput = attachmentUploadRef.value?.$el?.querySelector('input[type=file]')
  if (!fileInput?.files?.length) {
    ElMessage.warning('请选择文件')
    return
  }
  const files = Array.from(fileInput.files)
  try {
    await assetApi.uploadAttachments(route.params.id, files)
    ElMessage.success('附件上传成功')
    uploadAttachmentDialogVisible.value = false
    loadData()
  } catch (error) {
    ElMessage.error('上传失败')
  }
}

async function handleDeleteAttachment(att) {
  try {
    const filename = att.url.split('/').pop()
    await assetApi.deleteAttachment(route.params.id, filename)
    ElMessage.success('附件已删除')
    loadData()
  } catch (error) {
    ElMessage.error('删除失败')
  }
}

function downloadAttachment(att) {
  window.open(att.url, '_blank')
}

function formatFileSize(bytes) {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function printQrCode() {
  window.print()
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

function getActionLabel(action) {
  const labels = {
    create: '创建资产',
    update: '更新信息',
    assign: '分配资产',
    transfer: '调拨资产',
    return: '退库',
    repair: '提交报修',
    scrap: '提交报废'
  }
  return labels[action] || action
}
</script>

<style scoped>
.asset-detail {
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    .title {
      font-size: 18px;
      font-weight: 600;
    }

    .actions {
      display: flex;
      gap: 10px;
    }
  }

  .info-card {
    margin-bottom: 20px;
  }

  .image-list {
    .image-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
      gap: 10px;
    }

    .image-item {
      position: relative;
      height: 140px;
      border-radius: 4px;
      overflow: hidden;

      .asset-image {
        width: 100%;
        height: 100%;
      }

      .image-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;
      }

      &:hover .image-overlay {
        opacity: 1;
      }
    }
  }

  .upload-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 10px;
  }

  .qr-code-wrapper {
    text-align: center;

    img {
      width: 250px;
      height: 250px;
      margin-bottom: 15px;
    }

    .asset-no {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }

    .asset-name {
      color: #909399;
      margin-top: 5px;
    }
  }
}
</style>
