/**
 * 图片工具函数
 */

// 获取完整的图片URL
export function getImageUrl(imagePath) {
  if (!imagePath) return null

  // 如果已经是完整URL（http/https开头），直接返回
  if (imagePath.startsWith('http://') || imagePath.startsWith('https://')) {
    return imagePath
  }

  // 相对路径直接返回，由前端代理处理
  // vite.config.js 中配置了 /api 和 /uploads 代理到后端
  return imagePath
}

// 获取资产类型对应的占位图
export function getAssetPlaceholder(assetType) {
  const placeholders = {
    fixed: '/images/placeholder-fixed.svg',
    consumable: '/images/placeholder-consumable.svg',
    real_estate: '/images/placeholder-real-estate.svg'
  }
  return placeholders[assetType] || '/images/placeholder-default.svg'
}

// 获取资产图片（优先使用第一张，否则使用类型占位图）
export function getAssetImage(asset, thumbnail = false) {
  // 尝试获取第一张图片
  let images = []

  if (asset.images) {
    try {
      images = typeof asset.images === 'string' ? JSON.parse(asset.images) : asset.images
    } catch (e) {
      console.error('解析图片失败:', e)
    }
  }

  // 如果有图片，返回第一张
  if (images && images.length > 0) {
    return getImageUrl(images[0])
  }

  // 否则返回类型占位图
  return getAssetPlaceholder(asset.asset_type)
}

// 解析资产图片列表
export function parseAssetImages(imagesField) {
  if (!imagesField) return []

  try {
    if (typeof imagesField === 'string') {
      return JSON.parse(imagesField)
    }
    return Array.isArray(imagesField) ? imagesField : []
  } catch (e) {
    console.error('解析图片列表失败:', e)
    return []
  }
}

// 获取所有资产图片的完整URL列表
export function getAllAssetImageUrls(imagesField) {
  const images = parseAssetImages(imagesField)
  return images.map(img => getImageUrl(img))
}
