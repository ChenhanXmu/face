//my.js
//获取应用实例
var app = getApp()
Page({
  data: {
    userInfo: {},
    eye: true,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    listData: [
    ],
    max_rank:'',
    hasUserInfo: false
  },
  onLoad: function () {
    var that = this
    wx.getSetting({
      success: function (res) {
        if (res.authSetting['scope.userInfo']) {
          wx.getUserInfo({
            success: function (res) {
              console.log(res.userInfo)
              that.setData({
                userInfo: res.userInfo,
                hasUserInfo: true,
                eye: true
              })
              that.get_my()
              //用户已经授权过
            },
            fail: function (res) {
              console.log("未授权")
              that.setData({
                eye: false
              })
            }
          })
        }
        else {
          console.log("未授权")
          that.setData({
            eye: false
          })
        }
      }
    })
    console.log(that.data.userInfo.nickName)
  },
  get_my: function() {
    var that = this
    wx.request({
      url: '', //get_my接口，请用自己搭建的接口
      method: 'POST',
      data: {
        username: that.data.userInfo.nickName
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
          var max_rank = data.max
          if (max_rank == '1000') max_rank = ''
          that.setData({
            listData: data.listData,
            max_rank: max_rank
          })
        }
      }
    })
  },
  onPullDownRefresh: function () {
    var that = this
    if (that.data.hasUserInfo)
    {
      wx.showLoading({
        title: '拼命刷新中',
      })
      that.get_my()
      setTimeout(function () {
        wx.hideLoading()
        wx.stopPullDownRefresh()
      }, 1000)
    }
  },
  bindGetUserInfo: function (e) {
    var that = this
    console.log(e.detail.userInfo)
    if (e.detail.userInfo) {
      //用户按了允许授权按钮
      that.globalData.userInfo = res.userInfo
      that.setData({
        userInfo: e.detail.userInfo,
        hasUserInfo: true,
        eye: true
      })
      that.get_my()
    } else {
      //用户按了拒绝按钮
      that.setData({
        eye: false
      })
    }
  }
})
