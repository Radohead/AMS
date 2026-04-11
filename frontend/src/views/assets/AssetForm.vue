<template>
  <div class="asset-form">
    <div class="page-header">
      <span class="title">{{ isEdit ? '编辑资产' : '新建资产' }}</span>
    </div>

    <el-card>
      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-width="120px"
        class="asset-form-content"
      >
        <el-divider content-position="left">基本信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="资产名称" prop="name">
              <el-input v-model="form.name" placeholder="请输入资产名称" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="资产分类" prop="category_id">
              <el-cascader
                v-model="form.category_id"
                :options="categoryTree"
                :props="{ checkStrictly: true, emitPath: false, label: 'name', value: 'id' }"
                placeholder="请选择分类"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="资产类型" prop="asset_type">
              <el-radio-group v-model="form.asset_type">
                <el-radio label="fixed">固定资产</el-radio>
                <el-radio label="consumable">易耗品</el-radio>
                <el-radio label="real_estate">房地产</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="品牌">
              <el-input v-model="form.brand" placeholder="请输入品牌" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="型号">
              <el-input v-model="form.model" placeholder="请输入型号" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="序列号">
              <el-input v-model="form.serial_no" placeholder="请输入序列号" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">财务信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="购买日期">
              <el-date-picker
                v-model="form.purchase_date"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="购买价格">
              <el-input-number
                v-model="form.purchase_price"
                :min="0"
                :precision="2"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="保修截止">
              <el-date-picker
                v-model="form.warranty_end"
                type="date"
                placeholder="选择日期"
                style="width: 100%"
                format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-divider content-position="left">使用信息</el-divider>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="使用部门">
              <el-select v-model="form.department_id" placeholder="请选择部门" clearable style="width: 100%">
                <el-option
                  v-for="dept in departmentList"
                  :key="dept.id"
                  :label="dept.name"
                  :value="dept.id"
                />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="存放位置">
              <el-input v-model="form.location" placeholder="请输入存放位置" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="form.asset_type === 'consumable'">
          <el-col :span="8">
            <el-form-item label="单位">
              <el-input v-model="form.unit" placeholder="如: 个/箱/支" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="当前库存">
              <el-input-number v-model="form.current_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最低库存">
              <el-input-number v-model="form.min_stock" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 房地产专用字段 -->
        <template v-if="form.asset_type === 'real_estate'">
          <el-divider content-position="left">房地产信息</el-divider>
          <el-row :gutter="20">
            <el-col :span="24">
              <el-form-item label="详细地址">
                <el-input v-model="form.address" placeholder="请输入详细地址（省市区街道门牌）" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="建筑面积(m²)">
                <el-input-number v-model="form.area" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="占地面积(m²)">
                <el-input-number v-model="form.land_area" :min="0" :precision="2" style="width: 100%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="建成年份">
                <el-input-number v-model="form.build_year" :min="1900" :max="2100" style="width: 100%" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="产权类型">
                <el-select v-model="form.property_type" placeholder="请选择" clearable style="width: 100%">
                  <el-option label="商品房" value="商品房" />
                  <el-option label="经济适用房" value="经济适用房" />
                  <el-option label="公房" value="公房" />
                  <el-option label="自建房" value="自建房" />
                </el-select>
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="产权证号">
                <el-input v-model="form.property_no" placeholder="不动产权证编号" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="土地证号">
                <el-input v-model="form.land_no" placeholder="土地证号" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="6">
              <el-form-item label="楼栋号">
                <el-input v-model="form.building_no" placeholder="楼栋号" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="楼层">
                <el-input v-model="form.floor" placeholder="如: 1-3层" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="房间号">
                <el-input v-model="form.room_no" placeholder="房间号" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="用途">
                <el-select v-model="form.usage" placeholder="请选择" clearable style="width: 100%">
                  <el-option label="办公" value="办公" />
                  <el-option label="生产" value="生产" />
                  <el-option label="仓储" value="仓储" />
                  <el-option label="住宅" value="住宅" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="建筑结构">
                <el-select v-model="form.structure" placeholder="请选择" clearable style="width: 100%">
                  <el-option label="钢结构" value="钢结构" />
                  <el-option label="钢筋混凝土" value="钢筋混凝土" />
                  <el-option label="砖混结构" value="砖混结构" />
                  <el-option label="砖木结构" value="砖木结构" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <el-divider content-position="left">资产照片</el-divider>
        <el-form-item label="上传照片">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :limit="10"
            :on-change="handlePhotoChange"
            :on-remove="handlePhotoRemove"
            :file-list="photoFileList"
            accept="image/jpeg,image/png,image/jpg"
            list-type="picture-card"
            :before-remove="beforePhotoRemove"
          >
            <el-icon><Plus /></el-icon>
          </el-upload>
          <div class="upload-tip">支持 JPG/PNG 格式，单张不超过 10MB，最多10张</div>
        </el-form-item>

        <el-divider content-position="left">其他信息</el-divider>

        <el-form-item label="资产描述">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            placeholder="请输入资产描述"
          />
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="form.remarks"
            type="textarea"
            :rows="2"
            placeholder="请输入备注"
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="saving" @click="handleSubmit">
            {{ isEdit ? '保存' : '创建' }}
          </el-button>
          <el-button @click="goBack">取消</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { assetApi, categoryApi, departmentApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const formRef = ref()
const uploadRef = ref()
const saving = ref(false)
const uploading = ref(false)
const categoryTree = ref([])
const departmentList = ref([])
const photoFileList = ref([])
const pendingPhotos = ref([]) // 待上传的新照片文件

const isEdit = computed(() => !!route.params.id)

const form = reactive({
  name: '',
  category_id: null,
  asset_type: 'fixed',
  brand: '',
  model: '',
  serial_no: '',
  purchase_date: null,
  purchase_price: 0,
  warranty_end: null,
  department_id: null,
  location: '',
  unit: '',
  current_stock: 0,
  min_stock: 0,
  description: '',
  remarks: '',
  // 房地产专用字段
  address: '',
  area: null,
  land_area: null,
  property_type: '',
  property_no: '',
  land_no: '',
  building_no: '',
  floor: '',
  room_no: '',
  usage: '',
  build_year: null,
  structure: ''
})

const rules = {
  name: [{ required: true, message: '请输入资产名称', trigger: 'blur' }],
  category_id: [{ required: true, message: '请选择资产分类', trigger: 'change' }],
  asset_type: [{ required: true, message: '请选择资产类型', trigger: 'change' }]
}

onMounted(async () => {
  await loadCategories()
  await loadDepartments()

  if (isEdit.value) {
    await loadData()
  }
})

async function loadCategories() {
  try {
    categoryTree.value = await categoryApi.getTree()
  } catch (error) {
    console.error('加载分类失败', error)
  }
}

async function loadDepartments() {
  try {
    departmentList.value = await departmentApi.list()
  } catch (error) {
    console.error('加载部门失败', error)
  }
}

async function loadData() {
  try {
    const res = await assetApi.get(route.params.id)
    Object.keys(form).forEach(key => {
      if (res[key] !== undefined) {
        form[key] = res[key]
      }
    })
    // 加载已有图片
    if (res.images) {
      const existingImages = typeof res.images === 'string' ? JSON.parse(res.images) : res.images
      photoFileList.value = existingImages.map(url => ({ url, name: url.split('/').pop() }))
    }
  } catch (error) {
    ElMessage.error('加载数据失败')
  }
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    let assetId = route.params.id
    if (isEdit.value) {
      await assetApi.update(route.params.id, form)
      ElMessage.success('保存成功')
    } else {
      const created = await assetApi.create(form)
      assetId = created.id
      ElMessage.success('创建成功')
    }
    // 上传待上传的新照片
    if (pendingPhotos.value.length > 0 && assetId) {
      uploading.value = true
      await assetApi.uploadPhotos(assetId, pendingPhotos.value)
      uploading.value = false
      ElMessage.success('照片上传成功')
    }
    router.push('/assets')
  } catch (error) {
    ElMessage.error('操作失败')
  } finally {
    saving.value = false
  }
}

function handlePhotoChange(file, fileList) {
  pendingPhotos.value = fileList.filter(f => !f.url)
}

function handlePhotoRemove(file, fileList) {
  pendingPhotos.value = fileList.filter(f => !f.url)
}

async function beforePhotoRemove(file) {
  // 已上传的照片，需要调用后端删除
  if (file.url) {
    try {
      await assetApi.deletePhoto(route.params.id, file.url)
      return true
    } catch (error) {
      ElMessage.error('删除照片失败')
      return false
    }
  }
  return true
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.asset-form {
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

  .asset-form-content {
    max-width: 900px;
  }

  .upload-tip {
    font-size: 12px;
    color: #909399;
    margin-top: 8px;
  }
}
</style>
