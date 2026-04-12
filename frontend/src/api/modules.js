import api from './index'

// 资产相关API
export const assetApi = {
  // 获取资产列表
  list: (params) => api.get('/assets/', { params }),

  // 获取资产详情
  get: (id) => api.get(`/assets/${id}`),

  // 通过编码获取资产
  getByNo: (assetNo) => api.get(`/assets/no/${assetNo}`),

  // 创建资产
  create: (data) => api.post('/assets/', data),

  // 更新资产
  update: (id, data) => api.put(`/assets/${id}`, data),

  // 删除资产
  delete: (id) => api.delete(`/assets/${id}`),

  // 分配资产
  assign: (id, data) => api.post(`/assets/${id}/assign`, data),

  // 调拨资产
  transfer: (id, data) => api.post(`/assets/${id}/transfer`, data),

  // 退库资产
  return: (id, remarks) => api.post(`/assets/${id}/return`, { remarks }),

  // 获取资产变动记录
  getRecords: (id) => api.get(`/assets/${id}/records`),

  // 获取资产二维码
  getQrCode: (id) => `/api/assets/${id}/qrcode`,

  // 上传资产照片
  uploadPhotos: (id, files) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    return api.post(`/assets/${id}/photos`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 删除资产照片
  deletePhoto: (id, url) => {
    return api.delete(`/assets/${id}/photos`, { params: { url } })
  },

  // 上传资产附件
  uploadAttachments: (id, files) => {
    const formData = new FormData()
    files.forEach(file => formData.append('files', file))
    return api.post(`/assets/${id}/attachments`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 获取资产附件列表
  getAttachments: (id) => api.get(`/assets/${id}/attachments`),

  // 删除资产附件
  deleteAttachment: (id, filename) => api.delete(`/assets/${id}/attachments/${filename}`),

  // 获取资产统计
  getStats: () => api.get('/assets/stats/overview')
}

// 分类相关API
export const categoryApi = {
  list: (params) => api.get('/categories/', { params }),
  getTree: () => api.get('/categories/tree'),
  get: (id) => api.get(`/categories/${id}`),
  create: (data) => api.post('/categories/', data),
  update: (id, data) => api.put(`/categories/${id}`, data),
  delete: (id) => api.delete(`/categories/${id}`)
}

// 部门相关API
export const departmentApi = {
  list: (params) => api.get('/departments/', { params }),
  getTree: () => api.get('/departments/tree'),
  get: (id) => api.get(`/departments/${id}`),
  create: (data) => api.post('/departments/', data),
  update: (id, data) => api.put(`/departments/${id}`, data),
  delete: (id) => api.delete(`/departments/${id}`)
}

// 员工相关API
export const employeeApi = {
  list: (params) => api.get('/employees/', { params }),
  get: (id) => api.get(`/employees/${id}`),
  create: (data) => api.post('/employees/', data),
  update: (id, data) => api.put(`/employees/${id}`, data),
  delete: (id) => api.delete(`/employees/${id}`)
}

// 易耗品相关API
export const consumableApi = {
  getStock: (params) => api.get('/inventory/stock', { params }),
  getLowStock: () => api.get('/inventory/stock/low'),
  consume: (data) => api.post('/inventory/consume', data),
  restock: (id, quantity) => api.post(`/inventory/${id}/restock?quantity=${quantity}`),
  getRecords: (params) => api.get('/inventory/records', { params })
}

// 报修相关API
export const repairApi = {
  list: (params) => api.get('/repair/', { params }),
  get: (id) => api.get(`/repair/${id}`),
  create: (data) => api.post('/repair/', data),
  update: (id, data) => api.put(`/repair/${id}`, data),
  assign: (id, handlerId) => api.post(`/repair/${id}/assign`, { handler_id: handlerId }),
  complete: (id, data) => api.post(`/repair/${id}/complete`, data)
}

// 报废相关API
export const scrapApi = {
  list: (params) => api.get('/scrap/', { params }),
  get: (id) => api.get(`/scrap/${id}`),
  create: (data) => api.post('/scrap/', data),
  approve: (id, data) => api.post(`/scrap/${id}/approve`, data),
  dispose: (id, data) => api.post(`/scrap/${id}/dispose`, data)
}

// 盘点相关API
export const inventoryCheckApi = {
  list: (params) => api.get('/inventory-check/', { params }),
  get: (id) => api.get(`/inventory-check/${id}`),
  create: (data) => api.post('/inventory-check/', data),
  update: (id, data) => api.put(`/inventory-check/${id}`, data),
  start: (id) => api.post(`/inventory-check/${id}/start`),
  getItems: (id, params) => api.get(`/inventory-check/${id}/items`, { params }),
  updateItem: (id, itemId, data) => api.put(`/inventory-check/items/${itemId}`, data),
  complete: (id) => api.post(`/inventory-check/${id}/complete`),
  getReport: (id) => api.get(`/inventory-check/${id}/report`)
}

// 系统管理API
export const systemApi = {
  // 用户
  getUsers: (params) => api.get('/permissions/users', { params }),
  createUser: (data) => api.post('/permissions/users', data),
  updateUser: (id, data) => api.put(`/permissions/users/${id}`, data),
  deleteUser: (id) => api.delete(`/permissions/users/${id}`),

  // 角色
  getRoles: () => api.get('/permissions/roles'),
  createRole: (data) => api.post('/permissions/roles', data),
  updateRole: (id, data) => api.put(`/permissions/roles/${id}`, data),

  // 权限
  getPermissions: () => api.get('/permissions/permissions'),
  getPermissionsGrouped: () => api.get('/permissions/permissions/grouped'),

  // 日志
  getLoginLogs: (params) => api.get('/permissions/logs/login', { params }),
  getOperationLogs: (params) => api.get('/permissions/logs/operation', { params })
}

// 文件上传API
export const uploadApi = {
  uploadImage: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  uploadFile: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/file', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  delete: (filename) => api.delete(`/upload/${filename}`)
}
