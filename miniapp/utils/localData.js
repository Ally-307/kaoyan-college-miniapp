// 本地数据兜底：服务端不可用时直接读取打包的 schools.js
let cachedSchools = null

function loadSchools() {
  if (!cachedSchools) {
    const data = require('../data/schools')
    cachedSchools = data.schools || []
  }
  return cachedSchools
}

function lightSchool(school) {
  return {
    id: school.id,
    name: school.name,
    province: school.province,
    city: school.city,
    region: school.region,
    type: school.type || [],
    intro: (school.intro || '').slice(0, 120),
    majorsCount: (school.majors || []).length
  }
}

function searchSchools(params) {
  params = params || {}
  const q = (params.q || '').trim().toLowerCase()
  const types = params.type || []
  const regions = params.region || []
  const provinces = params.province || []
  const page = params.page || 1
  const pageSize = params.pageSize || 20

  const result = loadSchools().filter((s) => {
    if (q) {
      const name = (s.name || '').toLowerCase()
      const province = (s.province || '').toLowerCase()
      const city = (s.city || '').toLowerCase()
      if (!name.includes(q) && !province.includes(q) && !city.includes(q)) return false
    }
    if (types.length && !types.some((t) => (s.type || []).includes(t))) return false
    if (regions.length && !regions.includes(s.region)) return false
    if (provinces.length && !provinces.includes(s.province)) return false
    return true
  })

  const total = result.length
  const items = result.slice((page - 1) * pageSize, page * pageSize).map(lightSchool)
  return { items, total, page, pageSize, hasMore: page * pageSize < total }
}

function searchMajors(params) {
  params = params || {}
  const q = (params.q || '').trim().toLowerCase()
  const schoolId = params.schoolId || ''
  const page = params.page || 1
  const pageSize = params.pageSize || 20
  const result = []

  loadSchools().forEach((school) => {
    if (schoolId && school.id !== schoolId) return
    ;(school.majors || []).forEach((major) => {
      if (q) {
        const name = (major.name || '').toLowerCase()
        const code = (major.code || '').toLowerCase()
        const category = (major.category || '').toLowerCase()
        if (!name.includes(q) && !code.includes(q) && !category.includes(q)) return
      }
      result.push({
        ...major,
        schoolId: school.id,
        schoolName: school.name,
        schoolProvince: school.province,
        schoolCity: school.city
      })
    })
  })

  const total = result.length
  const items = result.slice((page - 1) * pageSize, page * pageSize)
  return { items, total, page, pageSize, hasMore: page * pageSize < total }
}

function getFilterOptions() {
  const schools = loadSchools()
  const typeMap = {}
  const regionMap = {}
  const provinceMap = {}
  schools.forEach((s) => {
    ;(s.type || []).forEach((t) => {
      typeMap[t] = (typeMap[t] || 0) + 1
    })
    if (s.region) regionMap[s.region] = (regionMap[s.region] || 0) + 1
    if (s.province) provinceMap[s.province] = (provinceMap[s.province] || 0) + 1
  })
  return {
    types: Object.keys(typeMap).map((label) => ({ label, count: typeMap[label] })),
    regions: Object.keys(regionMap).map((label) => ({ label, count: regionMap[label] })),
    provinces: Object.keys(provinceMap).map((name) => ({ name, count: provinceMap[name] })),
    totalSchools: schools.length,
    totalMajors: schools.reduce((n, s) => n + (s.majors || []).length, 0)
  }
}

function getHotSchools(limit) {
  limit = limit || 6
  return { items: loadSchools().slice(0, limit).map(lightSchool) }
}

function getSchoolById(id) {
  const school = loadSchools().find((s) => s.id === id)
  return school ? JSON.parse(JSON.stringify(school)) : null
}

function getMajorById(schoolId, majorId) {
  const school = getSchoolById(schoolId)
  if (!school) return null
  const major = (school.majors || []).find((m) => m.id === majorId)
  if (!major) return null
  return {
    major: JSON.parse(JSON.stringify(major)),
    school: {
      id: school.id,
      name: school.name,
      province: school.province,
      city: school.city,
      region: school.region,
      type: school.type || []
    }
  }
}

module.exports = {
  searchSchools,
  searchMajors,
  getFilterOptions,
  getHotSchools,
  getSchoolById,
  getMajorById
}
