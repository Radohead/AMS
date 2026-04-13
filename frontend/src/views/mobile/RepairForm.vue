<template>
  <div class="mobile-repair-form">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>新建报修</h1>
      <div class="placeholder"></div>
    </div>

    <div class="form-content">
      <!-- 资产选择 -->
      <div class="form-section">
        <div class="section-title">资产信息</div>
        <div class="form-item" v-if="!selectedAsset">
          <div class="input-box" @click="showAssetPicker = true">
            <span class="placeholder-text">请选择报修资产</span>
            <span class="arrow">›</span>
          </div>
        </div>
        <div class="selected-asset" v-else @click="showAssetPicker = true">
          <div class="asset-name">{{ selectedAsset.name }}</div>
          <div class="asset-no">{{ selectedAsset.asset_no }}</div>
        </div>
      </div>

      <!-- 报修信息 -->
      <div class="form-section">
        <div class="section-title">报修信息</div>
        <div class="form-item">
          <div class="item-label">故障描述</div>
          <textarea
            v-model="form.description"
            placeholder="请详细描述故障情况"
            rows="4"
          ></textarea>
        </div>

        <div class="form-item">
          <div class="item-label">紧急程度</div>
          <div class="radio-group">
            <div
              v-for="item in priorityOptions"
              :key="item.value"
              class="radio-item"
              :class="{ active: form.priority === item.value }"
              @click="form.priority = item.value"
            >
              {{ item.label }}
            </div>
          </div>
        </div>

        <div class="form-item">
          <div class="item-label">期望维修时间</div>
          <input
            v-model="form.expected_date"
            type="date"
            class="date-input"
          />
        </div>

        <div class="form-item">
          <div class="item-label">联系电话</div>
          <input
            v-model="form.contact"
            type="tel"
            placeholder="请输入联系电话"
          />
        </div>
      </div>

      <!-- 提交按钮 -->
      <div class="form-actions">
        <button
          class="submit-btn"
          :class="{ loading: submitting }"
          :disabled="submitting"
          @click="handleSubmit"
        >
          <span v-if="!submitting">提交报修</span>
          <span v-else>提交中...</span>
        </button>
      </div>
    </div>

    <!-- 资产选择弹窗 -->
    <div class="picker-overlay" v-if="showAssetPicker" @click="showAssetPicker = false">
      <div class="picker-content" @click.stop>
        <div class="picker-header">
          <span class="picker-cancel" @click="showAssetPicker = false">取消</span>
          <span class="picker-title">选择资产</span>
          <span class="picker-confirm" @click="confirmAsset">确定</span>
        </div>
        <div class="picker-search">
          <input
            v-model="assetKeyword"
            type="text"
            placeholder="搜索资产名称或编码"
            @input="searchAssets"
          />
        </div>
        <div class="picker-list">
          <div
            v-for="asset in assetList"
            :key="asset.id"
            class="picker-item"
            :class="{ selected: selectedAssetId === asset.id }"
            @click="selectedAssetId = asset.id"
          >
            <div class="item-name">{{ asset.name }}</div>
            <div class="item-no">{{ asset.asset_no }}</div>
          </div>
          <div class="picker-empty" v-if="assetList.length === 0 && !assetLoading">
            未找到资产
          </div>
          <div class="picker-loading" v-if="assetLoading">
            加载中...
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { assetApi, repairApi } from '@/api/modules'

const router = useRouter()
const route = useRoute()

const form = reactive({
  asset_id: null,
  description: '',
  priority: 'normal',
  expected_date: '',
  contact: ''
})

const selectedAsset = ref(null)
const showAssetPicker = ref(false)
const assetKeyword = ref('')
const assetList = ref([])
const selectedAssetId = ref(null)
const assetLoading = ref(false)
const submitting = ref(false)

const priorityOptions = [
  { label: '一般', value: 'low' },
  { label: '普通', value: 'normal' },
  { label: '紧急', value: 'urgent' },
  { label: '非常紧急', value: 'critical' }
]

onMounted(() => {
  // 如果有传入资产ID，直接选中
  const assetId = route.query.assetId
  if (assetId) {
    loadAsset(assetId)
  }
  loadAssets()
})

async function loadAsset(id) {
  try {
    const res = await assetApi.get(id)
    selectedAsset.value = res
    form.asset_id = id
  } catch (error) {
    console.error('加载资产失败', error)
  }
}

async function loadAssets() {
  assetLoading.value = true
  try {
    const res = await assetApi.list({
      page: 1,
      page_size: 50,
      keyword: assetKeyword.value
    })
    assetList.value = res.items || []
  } catch (error) {
    console.error('加载资产列表失败', error)
  } finally {
    assetLoading.value = false
  }
}

let searchTimer = null
function searchAssets() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    loadAssets()
  }, 300)
}

function confirmAsset() {
  const asset = assetList.value.find(a => a.id === selectedAssetId.value)
  if (asset) {
    selectedAsset.value = asset
    form.asset_id = asset.id
  }
  showAssetPicker.value = false
}

async function handleSubmit() {
  // 验证
  if (!form.asset_id) {
    alert('请选择报修资产')
    return
  }
  if (!form.description.trim()) {
    alert('请描述故障情况')
    return
  }

  submitting.value = true
  try {
    await repairApi.create({
      asset_id: form.asset_id,
      title: selectedAsset.value.name + ' 报修',
      description: form.description,
      priority: form.priority,
      expected_date: form.expected_date || null,
      contact: form.contact || null
    })

    alert('提交成功')
    router.back()
  } catch (error) {
    console.error('提交失败', error)
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-repair-form {
  min-height: 100vh;
  background: #f5f7fa;
  padding-bottom: 100px;
}

.header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
}

.back-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 24px;
  cursor: pointer;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header h1 {
  color: #fff;
  font-size: 18px;
  margin: 0;
}

.placeholder {
  width: 40px;
}

.form-content {
  padding: 16px;
}

.form-section {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  padding: 16px 16px 8px;
  font-size: 14px;
  font-weight: 500;
  color: #909399;
}

.form-item {
  padding: 0 16px 16px;
}

.input-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 44px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 0 12px;
  cursor: pointer;
}

.input-box:active {
  border-color: #667eea;
}

.placeholder-text {
  color: #909399;
  font-size: 14px;
}

.arrow {
  color: #909399;
  font-size: 18px;
}

.selected-asset {
  background: #f5f7fa;
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
}

.asset-name {
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
}

.asset-no {
  font-size: 12px;
  color: #909399;
}

.item-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 8px;
}

textarea {
  width: 100%;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 12px;
  font-size: 14px;
  resize: none;
  outline: none;
  font-family: inherit;
}

textarea:focus {
  border-color: #667eea;
}

.radio-group {
  display: flex;
  gap: 8px;
}

.radio-item {
  flex: 1;
  height: 36px;
  line-height: 36px;
  text-align: center;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
  cursor: pointer;
}

.radio-item.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
}

.date-input {
  width: 100%;
  height: 44px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

.date-input:focus {
  border-color: #667eea;
}

input[type="tel"],
input[type="text"] {
  width: 100%;
  height: 44px;
  border: 1px solid #dcdfe6;
  border-radius: 8px;
  padding: 0 12px;
  font-size: 14px;
  outline: none;
}

input:focus {
  border-color: #667eea;
}

.form-actions {
  padding: 16px;
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background: #fff;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.08);
}

.submit-btn {
  width: 100%;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 24px;
  color: #fff;
  font-size: 16px;
  cursor: pointer;
}

.submit-btn:active {
  opacity: 0.9;
}

.submit-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 资产选择弹窗 */
.picker-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: flex-end;
}

.picker-content {
  width: 100%;
  height: 70vh;
  background: #fff;
  border-radius: 16px 16px 0 0;
  display: flex;
  flex-direction: column;
}

.picker-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #f5f7fa;
}

.picker-cancel {
  color: #909399;
  font-size: 14px;
  cursor: pointer;
}

.picker-title {
  font-size: 16px;
  font-weight: 500;
  color: #303133;
}

.picker-confirm {
  color: #667eea;
  font-size: 14px;
  cursor: pointer;
}

.picker-search {
  padding: 12px 16px;
  border-bottom: 1px solid #f5f7fa;
}

.picker-search input {
  width: 100%;
  height: 40px;
  border: 1px solid #dcdfe6;
  border-radius: 20px;
  padding: 0 16px;
  font-size: 14px;
  outline: none;
}

.picker-search input:focus {
  border-color: #667eea;
}

.picker-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.picker-item {
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  cursor: pointer;
}

.picker-item:active {
  background: #f5f7fa;
}

.picker-item.selected {
  background: #e6f0ff;
  border: 1px solid #667eea;
}

.picker-item .item-name {
  font-size: 15px;
  color: #303133;
  margin-bottom: 4px;
}

.picker-item .item-no {
  font-size: 12px;
  color: #909399;
}

.picker-empty,
.picker-loading {
  text-align: center;
  padding: 40px 0;
  color: #909399;
  font-size: 14px;
}
</style>
