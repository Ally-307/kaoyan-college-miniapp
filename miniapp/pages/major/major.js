const { getMajorById } = require('../../utils/data')

Page({
  data: {
    major: null,
    school: null,
    loading: true,
    error: false,
    activeSection: 'exam'
  },

  onLoad(options) {
    const { schoolId, majorId } = options
    if (schoolId && majorId) {
      this.loadMajor(schoolId, majorId)
    } else {
      this.setData({ loading: false, error: true })
    }
  },

  loadMajor(schoolId, majorId) {
    this.setData({ loading: true, error: false })
    getMajorById(schoolId, majorId).then((res) => {
      if (!res || !res.major || !res.school) {
        this.setData({ loading: false, error: true })
        return
      }
      const major = res.major
      const school = res.school

      if (major.admissionData) {
        major.admissionData = major.admissionData.map((d) => ({
          ...d,
          _reexamRatio: d.reexamCount && d.admissionCount
            ? (d.reexamCount / d.admissionCount).toFixed(1) + ':1'
            : (d.reexam && d.reexam.ratio) || '-',
          _appRatio: d.applicationCount && d.admissionCount
            ? Math.round(d.applicationCount / d.admissionCount) + ':1'
            : '-'
        }))
      }

      wx.setNavigationBarTitle({ title: major.name })
      this.setData({ major, school, loading: false })
    }).catch(() => {
      this.setData({ loading: false, error: true })
    })
  },

  scrollToSection(e) {
    const section = e.currentTarget.dataset.section
    this.setData({ activeSection: section })

    const query = wx.createSelectorQuery()
    query.select(`#section-${section}`).boundingClientRect()
    query.exec((res) => {
      if (res[0]) {
        wx.pageScrollTo({
          scrollTop: res[0].top - 80,
          duration: 300
        })
      }
    })
  },

  onGoBack() {
    wx.navigateBack()
  },

  onShareAppMessage() {
    const major = this.data.major
    const school = this.data.school
    if (!major || !school) return {}
    return {
      title: `${school.name} · ${major.name} 考研信息`,
      path: `/pages/major/major?schoolId=${school.id}&majorId=${major.id}`
    }
  }
})
