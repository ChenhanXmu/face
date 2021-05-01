//index.js
//获取应用实例
var app = getApp()
Page({
  data: {
    eye: true,
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    isUploaded: 0,
    imageInfo: {},
    filepath: '',
    mark: 0,
    userInfo: {},
    ranking_tip: '',
    inRange: 0,
    hasUserInfo: false
  },
  //事件处理函数
  uploadRanking: function (e) {
    var that = this
    var file = that.data.filepath
    var mark = that.data.mark
    var username
    if (that.data.hasUserInfo) username = that.data.userInfo.nickName
    else username = '匿名用户'
    console.log(username)
    wx.uploadFile({
      header: { 'content-type': 'application/x-www-form-urlencoded;charset=utf-8' },
      url: '', //upload接口，请用自己搭建的接口
      filePath: file,
      name: 'file',
      formData: {
        'username': username,
        'mark': mark
      },
      success: function (res) {
        var data = res.data
        var json_data = JSON.parse(data)
        that.setData({
          ranking_tip: json_data['msg']
        })
        console.log(json_data['msg'])
      },
      fail: function (res) {
        console.log("not ok!")
        console.log(res)
        that.setData({
          ranking_tip: '网络错误，请重试'
        })
      }
    })
  },
  uploadImage: function (e) {
    var that = this
    var source = e.currentTarget.dataset.source
    wx.chooseImage({
      count: 1,
      sourceType: [source],
      success: function (res) {
        var tempFilePaths = res.tempFilePaths
        var tempFiles = res.tempFiles
        that.setData({
          imageInfo: {
            avatarUrl: tempFilePaths[0],
            tips: '检测中，请稍候',
          }
        })
        wx.showLoading({
          title: '检测中，请稍候',
        })
        var file = tempFiles[0]
        wx.uploadFile({
          header: { 'content-type': 'application/x-www-form-urlencoded' },
          url: '', //face接口，请用自己搭建接口
          filePath: tempFilePaths[0],
          name: 'file',
          success: function (res) {
            var data = res.data
            var json_data = JSON.parse(data)
            var success = json_data['success']
            if (success < 0) {
              that.setData({
                ranking_tip: '',
                isUploaded: 0,
                imageInfo: {
                  avatarUrl: tempFilePaths[0],
                  tips: json_data['msg'],
                }
              })
              wx.hideLoading()
            }
            else if (success > 0) {
              var age = json_data['age']
              var sex = json_data['sex']
              var emotion = json_data['emotion']
              var smile = json_data['smile']
              var beauty = json_data['beauty']
              var health = json_data['health']
              var in_range = json_data['in_range']
              var result = '这是一位' + age + '岁' + emotion + '的' + sex
              console.log("ok!")
              console.log(data)

              that.setData({
                isUploaded: 1,
                inRange: 1,
                filepath: tempFilePaths[0],
                mark: beauty,
                imageInfo: {
                  avatarUrl: tempFilePaths[0],
                  tips: result,
                  smile: '微笑：' + smile + '分',
                  beauty: '颜值：' + beauty + '分'
                }
              })

              if (in_range == 1) {
                if (that.data.hasUserInfo) {
                  that.setData({
                    ranking_tip: '已登录，将以"' + that.data.userInfo.nickName + '"身份上传'
                  })
                }
                else {
                  that.setData({
                    ranking_tip: '未登陆，将以"匿名用户"身份上榜'
                  })
                }
              }
              else {
                that.setData({
                  inRange: 0,
                  ranking_tip: '颜值还差点，再努力吧~'
                })
              }
              wx.hideLoading()
            }
          },
          fail: function (res) {
            console.log("not ok!")
            console.log(res)
            that.setData({
              isUploaded: 0,
              imageInfo: {
                avatarUrl: tempFilePaths[0],
                tips: '网络错误，请重试',
              }
            })
          }
        })
      }
    })
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
              //用户已经授权过
            },
            fail: function(res) {
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
  },
  bindGetUserInfo: function (e) {
    var that = this
    console.log(e.detail.userInfo)
    if (e.detail.userInfo) {
      //用户按了允许授权按钮
      that.setData({
        userInfo: e.detail.userInfo,
        hasUserInfo: true,
        eye: true
      })
      var ranking_tips = that.data.ranking_tip
      if (ranking_tips == '未登陆，将以"匿名用户"身份上榜')
        that.setData({
          ranking_tip: '已登录，将以"' + that.data.userInfo.nickName + '"身份上榜'
        })
    } else {
      //用户按了拒绝按钮
      that.setData({
        eye: false
      })
    }
  }
})
