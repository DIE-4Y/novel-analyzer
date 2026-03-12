import { createRouter, createWebHistory } from 'vue-router'
import UploadPage from '../views/UploadPage.vue'
import GraphPage from '../views/GraphPage.vue'

const routes = [
  {
    path: '/',
    name: 'Upload',
    component: UploadPage
  },
  {
    path: '/graph',
    name: 'Graph',
    component: GraphPage
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫：确保必须先上传文件才能访问图谱页面
router.beforeEach((to, from, next) => {
  const hasUploadedFile = localStorage.getItem('novelUploaded') === 'true'

  if (to.name === 'Graph' && !hasUploadedFile) {
    next({ name: 'Upload' })
  } else {
    next()
  }
})

export default router
