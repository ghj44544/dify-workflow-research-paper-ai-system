import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 120000
})

request.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
)

request.interceptors.response.use(
  (response) => {
    const result = response.data

    if (!result || typeof result.code === 'undefined') {
      return result
    }

    if (result.code !== 200) {
      ElMessage.error(result.message || '请求失败')
      return Promise.reject(result)
    }

    if (result.data && typeof result.data === 'object' && !Array.isArray(result.data)) {
      Object.defineProperty(result.data, '__message', {
        value: result.message,
        enumerable: false
      })
    }

    return result.data
  },
  (error) => {
    const message = error.response?.data?.message || '网络请求失败，请检查后端服务是否启动'
    ElMessage.error(message)
    return Promise.reject(error)
  }
)

export default request
