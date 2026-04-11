<template>
  <div class="scrap-list">
    <div class="page-header">
      <span class="title">报废管理</span>
    </div>

    <div class="search-form">
      <el-form :inline="true" :model="searchForm">
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" placeholder="请选择状态" clearable>
            <el-option label="待审批" value="pending" />
            <el-option label="已通过" value="approved" />
            <el-option label="已驳回" value="rejected" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </div>

    <el-table :data="tableData" v-loading="loading" stripe>
      <el-table-column prop="order_no" label="申请编号" width="150" />
      <el-table-column prop="asset_name" label="资产名称" min-width="150" />
      <el-table-column prop="reason" label="报废原因" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)" size="small">{{ getStatusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="申请时间" width="160" />
      <el-table-column prop="reviewed_at" label="审批时间" width="160" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" link @click="goDetail(row.id)">详情</el-button>
          <template v-if="row.status === 'pending'">
            <el-button type="primary" link @click="showReviewDialog(row)">审批</el-button>
          </template>
        </template>
      </el-table-column>
    </el-table>

    <el-pagination class="pagination" v-model:current-page="pagination.page" v-model:page-size="pagination.page_size" :total="pagination.total" :page-sizes="[10, 20, 50, 100]" layout="total, sizes, prev, pager, next, jumper" @size-change="loadData" @current-change="loadData" />

    <!-- 审批对话框 -->
    <el-dialog v-model="reviewDialogVisible" title="审批报废申请" width="500px">
      <el-form :model="reviewForm" label-width="100px">
        <el-form-item label="审批结果" required>
          <el-radio-group v-model="reviewForm.status">
            <el-radio label="approved">通过</el-radio>
            <el-radio label="rejected">驳回</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="审批意见">
          <el-input v-model="reviewForm.review_comment" type="textarea" :rows="3" placeholder="请输入审批意见" />
        </el-form-item>
        <template v-if="reviewForm.status === 'approved'">
          <el-form-item label="处置方式">
            <el-select v-model="reviewForm.disposal_method" placeholder="请选择" style="width: 100%">
              <el-option label="回收" value="recycle" />
              <el-option label="报废" value="discard" />
              <el-option label="变卖" value="sell" />
            </el-select>
          </el-form-item>
          <el-form-item label="残值">
            <el-input-number v-model="reviewForm.residual_value" :min="0" :precision="2" />
          </el-form-item>
        </template>
      </el-form>
      <template #footer>
        <el-button @click="reviewDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { scrapApi } from '@/api/modules'

const router = useRouter()
const loading = ref(false)
const tableData = ref([])
const searchForm = reactive({ status: '' })
const pagination = reactive({ page: 1, page_size: 20, total: 0 })

const reviewDialogVisible = ref(false)
const currentOrder = ref(null)
const reviewForm = reactive({ status: 'approved', review_comment: '', disposal_method: '', residual_value: 0 })

onMounted(async () => { await loadData() })

async function loadData() {
  loading.value = true
  try {
    const params = { page: pagination.page, page_size: pagination.page_size }
    if (searchForm.status) params.status = searchForm.status
    const res = await scrapApi.list(params)
    tableData.value = res.items
    pagination.total = res.total
  } catch (error) { ElMessage.error('加载数据失败') }
  finally { loading.value = false }
}

function handleSearch() { pagination.page = 1; loadData() }
function handleReset() { searchForm.status = ''; pagination.page = 1; loadData() }
function goDetail(id) { router.push(`/scrap/${id}`) }

function showReviewDialog(row) { currentOrder.value = row; reviewForm.status = 'approved'; reviewForm.review_comment = ''; reviewForm.disposal_method = ''; reviewForm.residual_value = 0; reviewDialogVisible.value = true }

async function submitReview() {
  try { await scrapApi.approve(currentOrder.value.id, reviewForm); ElMessage.success('审批成功'); reviewDialogVisible.value = false; loadData() }
  catch (error) { ElMessage.error('审批失败') }
}

function getStatusType(s) { return { pending: 'warning', approved: 'success', rejected: 'danger' }[s] || '' }
function getStatusLabel(s) { return { pending: '待审批', approved: '已通过', rejected: '已驳回' }[s] || s }
</script>

<style scoped>
.scrap-list {
  .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; .title { font-size: 18px; font-weight: 600; } }
  .search-form { background: #fff; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
  .pagination { margin-top: 20px; display: flex; justify-content: flex-end; }
}
</style>
