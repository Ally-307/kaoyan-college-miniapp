// 格式化工具函数

// 格式化分数线展示
function formatScore(score) {
  if (score === undefined || score === null || score === 0) return '暂无数据'
  return score.toString()
}

// 格式化复录比
function formatRatio(ratio) {
  if (!ratio) return '暂无数据'
  return ratio
}

// 格式化年份
function formatYear(year) {
  return `${year}年`
}

// 格式化院校类型标签
function formatSchoolTypes(types) {
  if (!types || types.length === 0) return []
  return types.map(t => ({
    label: t,
    className: `tag-${t}`
  }))
}

// 格式化日期（用于日志等）
function formatDate(date) {
  const d = date || new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

// 将百分数转为小数显示
function percentToDisplay(p) {
  if (p === undefined || p === null) return '暂无'
  return `${p}%`
}

module.exports = {
  formatScore,
  formatRatio,
  formatYear,
  formatSchoolTypes,
  formatDate,
  percentToDisplay
}
