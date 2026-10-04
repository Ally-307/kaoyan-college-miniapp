const {
  searchSchools,
  getFilterOptions,
  getHotSchools,
  processSchool
} = require('../../utils/data')

const config = require('../../config')

Page({
  data: {
    keyword: '',
    filteredSchools: [],
    filterOptions: { types: [], regions: [] },
    selectedTypes: [],
    selectedRegions: [],
    showFilter: false,
    hasSearched: false,
    hotSchools: [],
    loading: true,
    loadingMore: false,
    regionStats: [],
    page: 1,
    pageSize: config.PAGE_SIZE || 20,
    total: 0,
    hasMore: false
  },

  onLoad() {
    this.initData()
  },

  onShow() {
    if (typeof this.getTabBar === 'function' && this.getTabBar()) {
      this.getTabBar().setData({ selected: 0 })
    }
  },

  initData() {
    this.setData({ loading: true })
    Promise.all([getFilterOptions(), getHotSchools(6)])
      .then(([filterOptions, hotSchools]) => {
        const regionStats = (filterOptions.regions || []).map((r) => ({
          region: r.label,
          count: r.count
        }))
        this.setData({
          filterOptions: {
            types: (filterOptions.types || []).map((t) => t.label),
            regions: regionStats.map((r) => r.region)
          },
          hotSchools: hotSchools.map(processSchool),
          regionStats,
          loading: false
        })
      })
      .catch(() => {
        this.setData({ loading: false })
      })
  },

  onSearchInput(e) {
    const keyword = e.detail.value
    this.setData({ keyword })
    if (this._searchTimer) clearTimeout(this._searchTimer)
    this._searchTimer = setTimeout(() => {
      this.doSearch(keyword)
    }, 250)
  },

  onSearchConfirm(e) {
    const keyword = e.detail.value
    this.setData({ keyword })
    if (this._searchTimer) clearTimeout(this._searchTimer)
    this.doSearch(keyword)
  },

  onSearchClear() {
    if (this._searchTimer) clearTimeout(this._searchTimer)
    this.setData({
      keyword: '',
      filteredSchools: [],
      total: 0,
      page: 1,
      hasMore: false,
      hasSearched: false
    })
  },

  doSearch(keyword, page, append) {
    page = page || 1
    append = append || false
    const kw = (keyword || '').trim()
    const hasFilters = this.data.selectedTypes.length > 0 || this.data.selectedRegions.length > 0
    this.setData({
      loading: page === 1,
      loadingMore: page > 1
    })

    searchSchools({
      q: kw,
      type: this.data.selectedTypes,
      region: this.data.selectedRegions,
      page,
      pageSize: this.data.pageSize
    }).then((res) => {
      const items = (res.items || []).map(processSchool)
      this.setData({
        filteredSchools: append ? this.data.filteredSchools.concat(items) : items,
        total: res.total || items.length,
        page: res.page || page,
        hasMore: !!res.hasMore,
        hasSearched: kw.length > 0 || hasFilters,
        loading: false,
        loadingMore: false
      })
    }).catch(() => {
      this.setData({ loading: false, loadingMore: false })
      wx.showToast({ title: '加载失败，请检查服务', icon: 'none' })
    })
  },

  onReachBottom() {
    if (this.data.hasMore && !this.data.loading && !this.data.loadingMore) {
      this.doSearch(this.data.keyword, this.data.page + 1, true)
    }
  },

  toggleFilter() {
    this.setData({ showFilter: !this.data.showFilter })
  },

  onSelectType(e) {
    const type = e.currentTarget.dataset.type
    let selected = [...this.data.selectedTypes]
    const idx = selected.indexOf(type)
    if (idx > -1) {
      selected.splice(idx, 1)
    } else {
      selected.push(type)
    }
    this.setData({ selectedTypes: selected })
    this.doSearch(this.data.keyword)
  },

  onSelectRegion(e) {
    const region = e.currentTarget.dataset.region
    let selected = [...this.data.selectedRegions]
    const idx = selected.indexOf(region)
    if (idx > -1) {
      selected.splice(idx, 1)
    } else {
      selected.push(region)
    }
    this.setData({ selectedRegions: selected })
    this.doSearch(this.data.keyword)
  },

  clearFilters() {
    this.setData({
      selectedTypes: [],
      selectedRegions: [],
      showFilter: false
    })
    this.doSearch(this.data.keyword)
  },

  onSchoolTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/school/school?id=${id}`
    })
  },

  onHotSchoolTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/school/school?id=${id}`
    })
  }
})
