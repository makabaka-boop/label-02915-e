import request from './request'

// ========== 密码加密 ==========
async function sha256(message) {
  const msgBuffer = new TextEncoder().encode(message)
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
}

// ========== 认证 ==========
export const login = async (data) => {
  const hashed = await sha256(data.password)
  return request.post('/auth/login', { ...data, password: hashed })
}

export const logout = () => request.post('/auth/logout')

export const getProfile = () => request.get('/auth/profile')

// ========== 商品 ==========
export const getProducts = (params) => request.get('/products', { params })

export const getProduct = (id) => request.get(`/products/${id}`)

export const createProduct = (data) => request.post('/products', data)

export const updateProduct = (id, data) => request.put(`/products/${id}`, data)

export const deleteProduct = (id) => request.delete(`/products/${id}`)

// ========== 分类 ==========
export const getCategories = (params) => request.get('/categories', { params })

export const getAllCategories = () => request.get('/categories/all')

export const createCategory = (data) => request.post('/categories', data)

export const updateCategory = (id, data) => request.put(`/categories/${id}`, data)

export const deleteCategory = (id) => request.delete(`/categories/${id}`)

// ========== 用户 ==========
export const getUsers = (params) => request.get('/users', { params })

export const createUser = async (data) => {
  const payload = { ...data }
  if (payload.password) {
    payload.password = await sha256(payload.password)
  }
  return request.post('/users', payload)
}

export const updateUser = async (id, data) => {
  const payload = { ...data }
  if (payload.password) {
    payload.password = await sha256(payload.password)
  }
  return request.put(`/users/${id}`, payload)
}

export const deleteUser = (id) => request.delete(`/users/${id}`)

// ========== 日志 ==========
export const getLogs = (params) => request.get('/logs', { params })

// ========== 上传 ==========
export const uploadImage = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
