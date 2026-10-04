const api = require('./api')
const config = api.config

let localData = null
let localFallback = false

const typeStyles = {
  '985': 'background:#FEF2F2;color:#DC2626',
  '211': 'background:#EFF6FF;color:#2563EB',
  '\u53cc\u4e00\u6d41': 'background:#ECFDF5;color:#059669',
  '\u7701\u90e8\u5171\u5efa': 'background:#FFF7ED;color:#D97706',
  '\u666e\u901a': 'background:#F1F5F9;color:#64748B'
}

function getLocal() {
  if (!localData) localData = require('./localData')
  return localData
}

function processSchool(school) {
  if (!school || school._processed) return school
  school.types = (school.type || []).map(function (t) {
    return {
      label: t,
      style: typeStyles[t] || 'background:#F1F5F9;color:#64748B'
    }
  })
  school._processed = true
  return school
}

function stripSchool(school) {
  if (!school) return null
  return {
    id: school.id,
    name: school.name,
    province: school.province,
    city: school.city,
    region: school.region,
    type: school.type || [],
    types: school.types || [],
    intro: school.intro ? school.intro.slice(0, 100) : '',
    majorsCount: (school.majors || []).length,
    _processed: true
  }
}

function withFallback(remoteFn, localFn) {
  if (!config.USE_SERVER || localFallback) return Promise.resolve(localFn())
  return remoteFn().catch((err) => {
    console.warn('[data] API 不可用，切换到本地数据：', err && err.message)
    localFallback = true
    return localFn()
  })
}

function searchSchools(params) {
  return withFallback(
    () => api.request('/schools/search', params),
    () => getLocal().searchSchools(params)
  )
}

function searchMajors(params) {
  return withFallback(
    () => api.request('/majors/search', params),
    () => getLocal().searchMajors(params)
  )
}

function getFilterOptions() {
  return withFallback(
    () => api.request('/filters'),
    () => getLocal().getFilterOptions()
  )
}

function getHotSchools(limit) {
  return withFallback(
    () => api.request('/schools/hot', { limit }),
    () => getLocal().getHotSchools(limit)
  ).then((res) => res.items || res || [])
}

function getSchoolById(id) {
  return withFallback(
    () => api.request(`/schools/${encodeURIComponent(id)}`),
    () => getLocal().getSchoolById(id)
  )
}

function getMajorById(schoolId, majorId) {
  return withFallback(
    () => api.request(`/majors/${encodeURIComponent(schoolId)}/${encodeURIComponent(majorId)}`),
    () => getLocal().getMajorById(schoolId, majorId)
  )
}

module.exports = {
  searchSchools,
  searchMajors,
  getFilterOptions,
  getHotSchools,
  getSchoolById,
  getMajorById,
  processSchool,
  stripSchool
}
