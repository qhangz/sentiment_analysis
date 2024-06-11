<template>
  <div class="app-container">
    <el-card class="box-card">
      <div class="tip">
        请输入要进行情感分析的评论:
      </div>
      <el-input v-model="textarea" type="textarea" :disabled="stage" :rows="6" placeholder="请输入要进行情感分析的文本"
        clearable />
    </el-card>
    <el-row style="text-align: center; padding-top:20px; padding-bottom:20px;">
      <el-button type="info" round @click="clear()">清空内容</el-button>
      <el-button type="primary" round @click="emotionAnalysis()">情感分析</el-button>
    </el-row>
    <el-card v-show="visible" class="box-card">
      <div v-show="visible" class="tip">
        情感分析结果:  {{ analysisResult.sentiment }}, {{ analysisResult.probability }}
      </div>
    </el-card>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  data() {
    return {
      textarea: '', // 用户输入框内输入内容
      analysisResult: '', // 情感分析结果
      stage: false,
      visible: false, // 设置情感分析结果的可见性
    }
  },
  methods: {
    clear() {
      var that = this
      that.textarea = ''
      that.analysisResult = ''
      that.visible = false
      that.$message({
        showClose: true,
        message: '文本内容已清空！',
        type: 'success'
      })
    },
    emotionAnalysis() {
      var that = this
      // 获取用户输入框输入的要进行情感分析的文本
      var context = that.textarea
      if (context === '') {
        this.$message({
          showClose: true,
          message: '输入文本内容不能为空',
          type: 'warning'
        })
        that.analysisResult = ''
        that.visible = false
      } else {
        let formData = new FormData();
        formData.append('text', that.textarea);

        axios.post('http://localhost:5000/api/analyse/text', formData)
          .then((response) => {
            console.log(response.data.data.probability);
            // 获取接口返回的情感分析预测结果并更新界面数据
            that.analysisResult = response.data.data;
            that.visible = true;
            that.$message({
              showClose: true,
              message: '情感分析完成！',
              type: 'success'
            });
          })
          .catch((error) => {
            // 捕获异常并弹窗提示
            console.log(error);
            that.analysisResult = '';
            that.visible = false;
            that.$message({
              showClose: true,
              message: '请求异常，请检查后端服务模块！',
              type: 'error'
            });
          });
      }
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
