<template>
  <el-container class="layout-container">
    <!-- 移动端遮罩 -->
    <div class="mobile-overlay" :class="{ visible: sidebarOpen }" @click="sidebarOpen = false"></div>

    <el-aside class="layout-aside" :class="{ 'sidebar-open': sidebarOpen }" width="240px">
      <div class="sidebar-logo">
        <div class="logo-icon">P</div>
        <span class="logo-text">商品管理</span>
      </div>
      <el-menu
        :default-active="route.path"
        router
        @select="sidebarOpen = false"
      >
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Grid /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/logs">
          <el-icon><Document /></el-icon>
          <span>操作日志</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <div style="display: flex; align-items: center; gap: 12px;">
          <button class="mobile-menu-btn" @click="sidebarOpen = !sidebarOpen" aria-label="菜单">
            ☰
          </button>
          <span class="header-title">{{ route.meta.title }}</span>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand" trigger="click">
            <div class="user-dropdown-trigger">
              <div class="user-avatar">{{ avatarText }}</div>
              <span>{{ userStore.nickname || userStore.username }}</span>
              <el-icon :size="12"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">
                  <el-icon><SwitchButton /></el-icon>
                  退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view v-slot="{ Component }">
          <transition name="slide-fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Goods, Grid, User, Document, ArrowDown, SwitchButton } from '@element-plus/icons-vue'
import { useUserStore } from '../stores/user'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const sidebarOpen = ref(false)

const avatarText = computed(() => {
  const name = userStore.nickname || userStore.username || ''
  return name.charAt(0).toUpperCase()
})

// 路由切换时关闭侧边栏
watch(() => route.path, () => {
  sidebarOpen.value = false
})

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    userStore.clearLogin()
    ElMessage.success('已退出')
    router.push('/login')
  }
}
</script>
