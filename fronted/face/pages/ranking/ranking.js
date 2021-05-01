var app = getApp() 
Page({
  data: {
    navbar: ['总排行', 'top10'],
    currentTab: 0,
    listData: [
    ],
    topIndex : 1,
    imgUrl: '',
    topInfo: {
      "mark": 72.34,
      "author": "翔要闻闻你敢不敢"
    }
  },
  navbarTap: function (e) {
    this.setData({
      currentTab: e.currentTarget.dataset.idx
    })
  },
  onLoad: function () {
    var that = this
    that.setData({
      topIndex: 1
    })
    that.get_all()
    that.get_top10()
  },
  onPullDownRefresh: function () {
    var that = this
    var current = that.data.currentTab
    wx.showLoading({
      title: '拼命刷新中',
    })
    if (current == 0)  {
      that.get_all()
      setTimeout(function () {
        wx.hideLoading()
        wx.stopPullDownRefresh()
      }, 1000)
    }
    else {
      that.get_top10()
      setTimeout(function () {
        wx.hideLoading()
        wx.stopPullDownRefresh()
      }, 1000)
    }
  },
  preImage: function() {
    var that = this
    var index = that.data.topIndex
    index = index - 1
    if (index == 0) index = 10
    that.setData({
      topIndex: index
    })
    that.get_top10()
  },
  nextImage: function() {
    var that = this
    var index = that.data.topIndex
    index = index + 1
    if (index == 11) index = 1
    that.setData({
      topIndex: index
    })
    that.get_top10()
  },
  get_all: function() {
    var that = this
    console.log("get_all")
    wx.request({
      url: '', //get_all接口，请用自己搭建的接口
      method: 'GET',
      success: function (res) {
        var data = res.data
        console.log("ok")
        console.log(data)
        var success = data.success
        if (success > 0) {
          that.setData({
            listData: data.listData
          })
        }
      }
    })
  },
  get_top10: function() {
    var that = this
    wx.request({
      url: '', //get_top10，请用自己搭建的接口
      method: 'POST',
      data: {
        index: that.data.topIndex
      },
      header: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      success: function (res) {
        var data = res.data
        console.log("ok")
        console.log(data)
        var success = data.success
        if (success > 0) {
          var mark = data.mark
          var author = data.author
          var myurl = data.url
          if (myurl != '') myurl = "https://www.fwx123.xin/media/" + myurl
          console.log(myurl)
          that.setData({
            imgUrl: myurl,
            topInfo: {
              "mark": mark,
              "author": author
            }
          })
        }
      }
    })
  }
})  
