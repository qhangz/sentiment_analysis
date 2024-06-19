<template>
  <div class="app-container">
    <el-card class="box-card">
      <div class="tip">
        请输入您感兴趣的视频:
      </div>
      <el-input v-model="textarea" type="textarea" :disabled="stage" :rows="1" placeholder="请输入您感兴趣的视频的链接" clearable />
    </el-card>

    <el-row style="text-align: center; padding-top:20px; padding-bottom:20px;">
      <el-button type="info" round @click="clear()">清空内容</el-button>
      <el-button type="primary" round @click="recommend()">推荐视频</el-button>
    </el-row>

    <el-card v-show="visible" class="box-card">
      <div v-show="visible" class="tip">
        推荐结果:
      </div>
      <el-input v-model="resarea" type="textarea" :disabled="stage" :rows="20" placeholder="推荐结果加载中..." clearable />

    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      textarea: '', // 用户输入框内输入内容
      recommendResults: '', // 情感分析结果
      stage: false,
      visible: false, // 设置情感分析结果的可见性
      resarea: ''
    }
  },
  methods: {
    clear() {
      var that = this
      that.textarea = ''
      that.resarea = ''
      that.recommendResults = ''
      that.visible = false
      that.$message({
        showClose: true,
        message: '选择内容已清空！',
        type: 'success'
      })
    },
    recommend() {
      var that = this
      that.resarea = ''
      // 获取用户输入框输入的要进行情感分析的文本
      if (that.textarea === '') {
        this.$message({
          showClose: true,
          message: '输入视频链接不能为空',
          type: 'warning'
        })
        that.analysisResult = ''
        that.visible = false
        return
      }

      that.visible = true
      that.$message({
        showClose: true,
        message: '个性化推荐开始！请稍等！',
        type: 'success'
      })
      // 请求后端数据库推荐接口，请求方法为POST，请求体格式为JSON
      let formData = new FormData();
      formData.append('url', that.textarea);
      axios.post('http://localhost:5000/api/recommend/video', formData)
        .then((response) => {
          console.log(response.data)
          // 获取接口返回的推荐结果并更新界面数据
          that.resarea = response.data.data.result
          that.visible = true
          that.$message({
            showClose: true,
            message: '成功为您个性化推荐视频！',
            type: 'success'
          })
        }).catch((error) => {
          // 捕获异常并弹窗提示
          console.log(error)
          that.recommendResults = ''
          that.visible = false
          that.$message({
            showClose: true,
            message: '请求异常，请检查后端服务模块！',
            type: 'error'
          })
        })
    }
  }
}
</script>

<style scoped>
.tip {
  font-family: 宋体;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 10px;
}
</style>
