<template>
  <div class="mobile-profile">
    <div class="header">
      <button class="back-btn" @click="goBack">←</button>
      <h1>个人中心</h1>
      <div class="placeholder"></div>
    </div>

    <div class="profile-content">
      <!-- 用户信息卡片 -->
      <div class="user-card">
        <div class="avatar">{{ userStore.userInfo?.real_name?.charAt(0) || 'U' }}</div>
        <div class="user-info">
          <div class="user-name">{{ userStore.userInfo?.real_name || '用户' }}</div>
          <div class="user-role">{{ userStore.userInfo?.role?.name || '普通用户' }}</div>
        </div>
      </div>

      <!-- 快捷操作 -->
      <div class="action-section">
        <div class="section-title">我的任务</div>
        <div class="action-list">
          <div class="action-item" @click="goToMyRepairs">
            <div class="action-icon">🔧</div>
            <div class="action-text">我的报修</div>
            <div class="action-arrow">›</div>
          </div>
          <div class="action-item" @click="goToMyChecks">
            <div class="action-icon">📋</div>
            <div class="action-text">我的盘点</div>
            <div class="action-arrow">›</div>
          </div>
        </div>
      </div>

      <!-- 系统设置 -->
      <div class="action-section">
        <div class="section-title">系统</div>
        <div class="action-list">
          <div class="action-item" @click="goToSettings">
            <div class="action-icon">⚙️</div>
            <div class="action-text">设置</div>
            <div class="action-arrow">›</div>
          </div>
          <div class="action-item" @click="showAbout">
            <div class="action-icon">ℹ️</div>
            <div class="action-text">关于</div>
            <div class="action-arrow">›</div>
          </div>
        </div>
      </div>

      <!-- 退出登录 -->
      <div class="logout-section">
        <button class="logout-btn" @click="handleLogout">退出登录</button>
      </div>

      <!-- 版本信息 -->
      <div class="version-info">
        AMS 资产管理系统 v1.0.0
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

function goToMyRepairs() {
  router.push('/mobile/repair')
}

function goToMyChecks() {
  router.push('/mobile/check')
}

function goToSettings() {
  alert('设置功能开发中')
}

function showAbout() {
  alert('AMS 资产管理系统\n版本: v1.0.0\n\n一款面向公司内部的资产全生命周期管理软件')
}

function handleLogout() {
  if (confirm('确定要退出登录吗？')) {
    userStore.logout()
    router.push('/mobile/login')
  }
}

function goBack() {
  router.back()
}
</script>

<style scoped>
.mobile-profile {
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

.profile-content {
  padding: 16px;
}

.user-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.avatar {
  width: 64px;
  height: 64px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  color: #fff;
}

.user-info {
  color: #fff;
}

.user-name {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 4px;
}

.user-role {
  font-size: 14px;
  opacity: 0.8;
}

.action-section {
  background: #fff;
  border-radius: 12px;
  margin-bottom: 16px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.section-title {
  padding: 16px 16px 8px;
  font-size: 13px;
  color: #909399;
}

.action-list {
  padding-bottom: 4px;
}

.action-item {
  display: flex;
  align-items: center;
  padding: 14px 16px;
  cursor: pointer;
}

.action-item:active {
  background: #f5f7fa;
}

.action-icon {
  width: 32px;
  height: 32px;
  background: #f5f7fa;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-right: 12px;
}

.action-text {
  flex: 1;
  font-size: 15px;
  color: #303133;
}

.action-arrow {
  color: #c0c4cc;
  font-size: 18px;
}

.logout-section {
  margin-top: 20px;
}

.logout-btn {
  width: 100%;
  height: 48px;
  background: #fff;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  color: #ff4d4f;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.logout-btn:active {
  background: #f5f7fa;
}

.version-info {
  text-align: center;
  font-size: 12px;
  color: #c0c4cc;
  margin-top: 24px;
}
</style>
