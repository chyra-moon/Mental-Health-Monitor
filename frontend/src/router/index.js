import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/public/LoginView.vue'),
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/public/RegisterView.vue'),
  },
  {
    path: '/student',
    component: () => import('@/views/student/StudentLayout.vue'),
    meta: { role: 'student' },
    children: [
      { path: '', name: 'StudentHome', component: () => import('@/views/student/HomeView.vue') },
      { path: 'emotion', name: 'EmotionDetect', component: () => import('@/views/student/EmotionView.vue') },
    ],
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { role: 'admin' },
    children: [
      { path: '', name: 'AdminHome', component: () => import('@/views/admin/HomeView.vue') },
      { path: 'warnings', name: 'WarningList', component: () => import('@/views/admin/WarningView.vue') },
    ],
  },
  { path: '/:pathMatch(.*)*', redirect: '/login' },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')
  if (to.path !== '/login' && to.path !== '/register' && !token) {
    return '/login'
  }
  if (to.meta.role && to.meta.role !== user.role) {
    return user.role === 'admin' ? '/admin' : '/student'
  }
})

export default router
