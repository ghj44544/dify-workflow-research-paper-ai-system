<template>
  <el-container class="app-shell">
    <el-aside class="app-aside" width="220px">
      <div class="brand">
        <div class="brand-logo">
          <el-icon><Reading /></el-icon>
        </div>
        <div class="brand-title">科研文献智能分析系统</div>
        <div class="brand-subtitle">Dify Workflow + FastAPI</div>
      </div>
      <el-menu :default-active="activeMenu" router class="app-menu">
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/papers">
          <el-icon><Files /></el-icon>
          <span>文献管理</span>
        </el-menu-item>
        <el-menu-item index="/assistant">
          <el-icon><MagicStick /></el-icon>
          <span>智能科研助手</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-title">
          <el-icon><DataAnalysis /></el-icon>
          基于 Dify Workflow 的科研文献智能分析系统
        </div>
      </el-header>
      <el-main class="app-main" :class="{ 'is-assistant-main': route.path.startsWith('/assistant') }">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { DataAnalysis, Files, House, MagicStick, Reading } from '@element-plus/icons-vue'

const route = useRoute()

const activeMenu = computed(() => {
  if (route.path.startsWith('/assistant')) {
    return '/assistant'
  }
  if (route.path.startsWith('/papers')) {
    return '/papers'
  }
  return '/'
})
</script>

<style scoped>
.app-shell {
  height: 100vh;
  background:
    radial-gradient(circle at 15% 0%, rgb(64 158 255 / 9%), transparent 28%),
    radial-gradient(circle at 92% 8%, rgb(103 194 58 / 9%), transparent 24%),
    #f5f7fb;
  overflow: hidden;
}

.app-shell > .el-container {
  min-width: 0;
  min-height: 0;
}

.app-aside {
  border-right: 1px solid rgb(229 231 235 / 86%);
  background: rgb(255 255 255 / 92%);
  backdrop-filter: blur(12px);
}

.brand {
  padding: 24px 18px 18px;
  border-bottom: 1px solid #eef0f4;
}

.brand-logo {
  display: grid;
  width: 42px;
  height: 42px;
  margin-bottom: 12px;
  place-items: center;
  border-radius: 14px;
  background: #111827;
  color: #ffffff;
  font-size: 22px;
  box-shadow: 0 12px 28px rgb(17 24 39 / 16%);
}

.brand-title {
  color: #1f2d3d;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.45;
}

.brand-subtitle {
  margin-top: 6px;
  color: #8492a6;
  font-size: 12px;
}

.app-menu {
  border-right: none;
}

.app-header {
  flex: 0 0 60px;
  display: flex;
  align-items: center;
  border-bottom: 1px solid rgb(229 231 235 / 86%);
  background: rgb(255 255 255 / 82%);
  backdrop-filter: blur(10px);
}

.header-title {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #1f2d3d;
  font-size: 18px;
  font-weight: 600;
}

.app-main {
  height: calc(100vh - 60px);
  padding: 24px;
  overflow: auto;
  box-sizing: border-box;
}

.app-main.is-assistant-main {
  padding: 0;
  overflow: hidden;
}

@media (max-width: 760px) {
  .app-shell {
    display: block;
    height: 100vh;
  }

  .app-aside {
    width: 100% !important;
  }

  .app-header {
    display: none;
  }

  .app-main {
    height: calc(100vh - 152px);
    padding: 16px;
  }

  .app-main.is-assistant-main {
    height: calc(100vh - 152px);
    padding: 0;
  }
}

:global(html),
:global(body),
:global(#app) {
  height: 100%;
  margin: 0;
  overflow: hidden;
}
</style>
