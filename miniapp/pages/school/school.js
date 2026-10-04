const { getSchoolById, processSchool } = require('../../utils/data')

Page({
  data: {
    school: null,
    majors: [],
    filteredMajors: [],
    majorKeyword: '',
    loading: true,
    error: false
  },

  onLoad(options) {
    if (options.id) {
      this.loadSchool(options.id)
    } else {
      this.setData({ loading: false, error: true })
    }
  },

  loadSchool(id) {
    this.setData({ loading: true, error: false })
    getSchoolById(id).then((school) => {
      if (!school) {
        this.setData({ loading: false, error: true })
        return
      }
      processSchool(school)
      const majors = school.majors || []
      this.setData({
        school,
        majors,
        filteredMajors: majors,
        loading: false
      })
      wx.setNavigationBarTitle({ title: school.name })
    }).catch(() => {
      this.setData({ loading: false, error: true })
    })
  },

  onMajorSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ majorKeyword: keyword })
    this.filterMajors(keyword)
  },

  onMajorSearchClear() {
    this.setData({
      majorKeyword: '',
      filteredMajors: this.data.majors
    })
  },

  filterMajors(keyword) {
    if (!keyword || !keyword.trim()) {
      this.setData({ filteredMajors: this.data.majors })
      return
    }
    const kw = keyword.trim().toLowerCase()
    const filtered = this.data.majors.filter((m) =>
      m.name.toLowerCase().includes(kw) ||
      m.code.toLowerCase().includes(kw) ||
      (m.category && m.category.toLowerCase().includes(kw)) ||
      (m.degreeType && m.degreeType.toLowerCase().includes(kw))
    )
    this.setData({ filteredMajors: filtered })
  },

  onMajorTap(e) {
    const majorId = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/major/major?schoolId=${this.data.school.id}&majorId=${majorId}`
    })
  },

  onGoBack() {
    wx.navigateBack()
  }
})
