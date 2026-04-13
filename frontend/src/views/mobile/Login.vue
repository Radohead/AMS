<template>
  <div class="mobile-login">
    <div class="login-content">
      <div class="logo-section">
        <div class="logo">AMS</div>
        <h1>资产管理系统</h1>
        <p>移动端</p>
      </div>

      <div class="form-section">
        <div class="input-group">
          <div class="input-icon">
            <span>👤</span>
          </div>
          <input
            v-model="form.username"
            type="text"
            placeholder="请输入用户名"
            @keyup.enter="handleLogin"
          />
        </div>

        <div class="input-group">
          <div class="input-icon">
            <span>🔒</span>
          </div>
          <input
            v-model="form.password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="请输入密码"
            @keyup.enter="handleLogin"
          />
          <div class="toggle-password" @click="showPassword = !showPassword">
            {{ showPassword ? '🙈' : '👁️' }}
          </div>
        </div>

        <button
          class="login-btn"
          :class="{ loading: loading }"
          :disabled="loading"
          @click="handleLogin"
        >
          <span v-if="!loading">登 录</span>
          <span v-else>登录中...</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'

const router = useRouter()
const userStore = useUserStore()

const showPassword = ref(false)
const loading = ref(false)

const form = reactive({
  username: '',
  password: ''
})

async function handleLogin() {
  if (!form.username || !form.password) {
    alert('请输入用户名和密码')
    return
  }

  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    // 获取用户信息
    await userStore.getUserInfo()
    router.push('/mobile')
  } catch (error) {
    alert('登录失败，请检查用户名和密码')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.mobile-login {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.login-content {
  width: 100%;
  max-width: 360px;
}

.logo-section {
  text-align: center;
  margin-bottom: 40px;
  color: #fff;
}

.logo {
  width: 80px;
  height: 80px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: bold;
  margin: 0 auto 16px;
  backdrop-filter: blur(10px);
}

.logo-section h1 {
  font-size: 24px;
  margin-bottom: 8px;
}

.logo-section p {
  font-size: 14px;
  opacity: 0.8;
}

.form-section {
  background: #fff;
  border-radius: 16px;
  padding: 30px 24px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
}

.input-group {
  display: flex;
  align-items: center;
  background: #f5f7fa;
  border-radius: 12px;
  margin-bottom: 16px;
  padding: 0 16px;
  height: 50px;
}

.input-icon {
  margin-right: 12px;
  font-size: 18px;
}

.input-group input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 16px;
  outline: none;
  color: #303133;
}

.input-group input::placeholder {
  color: #909399;
}

.toggle-password {
  cursor: pointer;
  font-size: 18px;
  padding: 4px;
}

.login-btn {
  width: 100%;
  height: 50px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  border-radius: 12px;
  color: #fff;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  margin-top: 8px;
  transition: opacity 0.3s;
}

.login-btn:active {
  opacity: 0.8;
}

.login-btn.loading {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
