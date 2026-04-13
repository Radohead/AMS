<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside :width="isCollapse ? '64px' : '220px'" class="aside">
      <div class="logo">
        <el-icon v-if="isCollapse"><Box /></el-icon>
        <span v-else>AMS 资产管理系统</span>
      </div>

      <el-menu
        :default-active="activeMenu"
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        class="aside-menu"
      >
        <el-menu-item index="/dashboard">
          <el-icon><Odometer /></el-icon>
          <template #title>首页</template>
        </el-menu-item>

        <el-sub-menu index="/assets">
          <template #title>
            <el-icon><Box /></el-icon>
            <span>资产管理</span>
          </template>
          <el-menu-item index="/assets">资产列表</el-menu-item>
          <el-menu-item index="/assets/create">新建资产</el-menu-item>
          <el-menu-item index="/categories">资产分类</el-menu-item>
          <el-menu-item index="/qrcodes">二维码管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/people">
          <template #title>
            <el-icon><User /></el-icon>
            <span>人员管理</span>
          </template>
          <el-menu-item index="/employees">员工管理</el-menu-item>
          <el-menu-item index="/departments">部门管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/inventory">
          <template #title>
            <el-icon><Shop /></el-icon>
            <span>库存管理</span>
          </template>
          <el-menu-item index="/consumables">易耗品管理</el-menu-item>
          <el-menu-item index="/inventory-check">盘点管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/process">
          <template #title>
            <el-icon><Tools /></el-icon>
            <span>流程管理</span>
          </template>
          <el-menu-item index="/repair">报修管理</el-menu-item>
          <el-menu-item index="/scrap">报废管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/system" v-if="isAdmin">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/users">用户管理</el-menu-item>
          <el-menu-item index="/roles">角色管理</el-menu-item>
          <el-menu-item index="/logs">操作日志</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航 -->
      <el-header class="header">
        <div class="header-left">
          <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
            <Expand v-if="isCollapse" />
            <Fold v-else />
          </el-icon>
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="route.meta.title">
              {{ route.meta.title }}
            </el-breadcrumb-item>
          </el-breadcrumb>
        </div>

        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><UserFilled /></el-icon>
              <span>{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                <el-dropdown-item command="changePassword">修改密码</el-dropdown-item>
                <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>

  <!-- 修改密码对话框 -->
  <el-dialog v-model="changePasswordDialogVisible" title="修改密码" width="400px">
    <el-form :model="passwordForm" label-width="100px">
      <el-form-item label="原密码">
        <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" show-password />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" show-password />
      </el-form-item>
      <el-form-item label="确认密码">
        <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请再次输入新密码" show-password />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="changePasswordDialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitPasswordChange">确定</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessageBox, ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const isCollapse = ref(false)
const changePasswordDialogVisible = ref(false)
const passwordForm = ref({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const activeMenu = computed(() => route.path)
const isAdmin = computed(() => userStore.userInfo?.is_superuser)

onMounted(async () => {
  if (userStore.token && !userStore.userInfo) {
    await userStore.getUserInfo()
  }
})

function handleCommand(command) {
  switch (command) {
    case 'logout':
      ElMessageBox.confirm('确定要退出登录吗？', '提示', {
        type: 'warning',
        confirmButtonText: '确定',
        cancelButtonText: '取消'
      }).then(() => {
        userStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      }).catch(() => {
        // 用户取消，不做任何操作
      })
      break
    case 'changePassword':
      passwordForm.value = { oldPassword: '', newPassword: '', confirmPassword: '' }
      changePasswordDialogVisible.value = true
      break
    case 'profile':
      ElMessage.info('个人中心功能开发中')
      break
  }
}

async function submitPasswordChange() {
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    ElMessage.error('两次输入的密码不一致')
    return
  }
  if (passwordForm.value.newPassword.length < 6) {
    ElMessage.error('新密码长度不能少于6位')
    return
  }

  try {
    await userStore.changePassword(passwordForm.value.oldPassword, passwordForm.value.newPassword)
    ElMessage.success('密码修改成功，请重新登录')
    changePasswordDialogVisible.value = false
    userStore.logout()
    router.push('/login')
  } catch (error) {
    ElMessage.error(error.message || '密码修改失败')
  }
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}

.aside {
  background: #304156;
  transition: width 0.3s;

  .logo {
    height: 60px;
    line-height: 60px;
    text-align: center;
    color: #fff;
    font-size: 18px;
    font-weight: 600;
    background: #263445;
  }

  .aside-menu {
    border-right: none;
    background: #304156;

    :deep(.el-menu-item),
    :deep(.el-sub-menu__title) {
      color: #bfcbd9;

      &:hover {
        background: #263445;
      }

      &.is-active {
        color: #409eff;
        background: #263445;
      }
    }
  }
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);

  .header-left {
    display: flex;
    align-items: center;
    gap: 15px;

    .collapse-btn {
      font-size: 20px;
      cursor: pointer;
      color: #606266;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      padding: 0 10px;

      &:hover {
        background: #f5f7fa;
      }
    }
  }
}

.main {
  background: #f0f2f5;
  padding: 20px;
}
</style>
