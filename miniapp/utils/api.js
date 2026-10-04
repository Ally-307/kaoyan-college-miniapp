const config = require('../config')

function buildQuery(params) {
  const parts = []
  Object.keys(params || {}).forEach((key) => {
    const value = params[key]
    if (value === undefined || value === null || value === '') return
    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== undefined && item !== null && item !== '') {
          parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(item)}`)
        }
      })
    } else {
      parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    }
  })
  return parts.length ? `?${parts.join('&')}` : ''
}

function request(path, params, options) {
  options = options || {}
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${config.API_BASE_URL}${path}${buildQuery(params)}`,
      method: options.method || 'GET',
      timeout: options.timeout || config.REQUEST_TIMEOUT,
      header: options.header || {},
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300 && res.data && res.data.code === 0) {
          resolve(res.data.data || {})
        } else {
          const message = res.data && res.data.message ? res.data.message : `HTTP ${res.statusCode}`
          reject(new Error(message))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

module.exports = { request, config }
