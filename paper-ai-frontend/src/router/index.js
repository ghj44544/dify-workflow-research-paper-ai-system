import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/papers',
    name: 'papers',
    component: () => import('../views/PaperListView.vue')
  },
  {
    path: '/papers/:id',
    name: 'paper-detail',
    component: () => import('../views/PaperDetailView.vue')
  },
  {
    path: '/papers/:id/ask',
    name: 'paper-ask',
    component: () => import('../views/PaperAskView.vue')
  },
  {
    path: '/papers/:id/notes',
    name: 'paper-notes',
    component: () => import('../views/PaperNoteView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
