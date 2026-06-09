<template>
  <el-container class="app-shell">
    <el-aside class="app-aside" width="220px">
      <div class="brand">
        <div class="brand-title">科研文献智能分析系统</div>
        <div class="brand-subtitle">Dify Workflow + FastAPI</div>
      </div>
      <el-menu :default-active="activeMenu" router class="app-menu">
        <el-menu-item index="/">
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/papers">
          <span>文献管理</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="app-header">
        <div class="header-title">基于 Dify Workflow 的科研文献智能分析系统</div>
      </el-header>
      <el-main class="app-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const activeMenu = computed(() => {
  if (route.path.startsWith('/papers')) {
    return '/papers'
  }
  return '/'
})
</script>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: #f5f7fb;
}

.app-aside {
  border-right: 1px solid #e5e7eb;
  background: #ffffff;
}

.brand {
  padding: 22px 18px 18px;
  border-bottom: 1px solid #eef0f4;
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
  display: flex;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  background: #ffffff;
}

.header-title {
  color: #1f2d3d;
  font-size: 18px;
  font-weight: 600;
}

.app-main {
  padding: 24px;
}

@media (max-width: 760px) {
  .app-shell {
    display: block;
  }

  .app-aside {
    width: 100% !important;
  }

  .app-header {
    display: none;
  }

  .app-main {
    padding: 16px;
  }
}
</style>
