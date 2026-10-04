// 小程序运行配置：本地开发默认走 API，服务不可用时自动回退本地数据
module.exports = {
  USE_SERVER: true,
  API_BASE_URL: 'http://127.0.0.1:8010/api',
  REQUEST_TIMEOUT: 8000,
  PAGE_SIZE: 20
}
