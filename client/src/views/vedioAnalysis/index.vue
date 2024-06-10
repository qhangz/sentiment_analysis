<!-- eslint-disable indent -->
<template>
  <div class="app-container">

    <el-card class="box-card">
      <div class="tip">
        请输入要进行情感分析的视频:
      </div>
      <el-input v-model="textarea" type="textarea" :disabled="stage" :rows="1" placeholder="请输入要进行情感分析的视频链接"
        clearable />
    </el-card>
    <el-row style="text-align: center; padding-top:20px;padding-bottom:20px;">
      <el-button type="info" round @click="clear()">清空内容</el-button>
      <el-button type="primary" round @click="vedioEmotionAnalysis()">情感分析</el-button>
    </el-row>

    <el-card v-show="sp_visible" class="box-card">
      <div v-show="sp_visible" class="tip">
        数据爬取结果（评论部分）：
      </div>
      <el-table :data="spiderResults" height="290" border style="width: 100%">
        <el-table-column prop="comment" label="评论" />
      </el-table>
    </el-card>

    <!-- <el-card v-show="visible" class="box-card">
      <div v-show="visible" class="tip"> -->
    <el-card v-show="visible" class="box-card">
      <div v-show="visible" class="tip">
        视频情感分析结果：
      </div>
      <el-table id="excel" :data="analysisResults" height="290" border style="width: 100%">
        <el-table-column prop="key" label="关键词" />
        <el-table-column prop="textrank" label="权重值" />
        <el-table-column prop="probability" label="情感得分" />
        <el-table-column prop="sentiment" label="情感倾向" />
      </el-table>
      <el-row style="text-align: center; padding-top:20px;padding-bottom:20px;">
        <el-button type="primary" round @click="videoVisualize()">弹幕数据可视化</el-button>
        <el-button type="primary" round @click="videoSentiment()">可视化情感趋势图</el-button>
        <el-button type="primary" round @click="videoWordcloud()">弹幕词云图</el-button>
      </el-row>
    </el-card>
    <el-row style="text-align: center; padding-top:10px;padding-bottom:10px;"></el-row>
    <!--分析结果可视化-->

    <el-card v-show="vis_visible" class="box-card">
      <img class="vis-img" :src="visImg" alt="Result Image" />
    </el-card>

    <el-card v-show="sen_visible" class="box-card">
      <img class="sen-img" :src="senImg" alt="Result Image" />
    </el-card>

    <el-card v-show="wc_visible" class="box-card">
      <img class="wc-img" :src="wcImg" alt="Result Image" />
    </el-card>


  </div>
</template>

<script>
import axios from 'axios'
import * as echarts from 'echarts'
import 'echarts-wordcloud'
import { getVisualize, test, getImage } from '@/api/image'
export default {
  data() {
    return {
      textarea: '',  // 用户输入的视频链接
      analysisResults: '',

      visible: false,
      vis_visible: false,
      wc_visible: false,
      sen_visible: false,

      vis_notready: true,

      visImg: null,
      senImg: null,
      wcImg: null,
    }
  },
  methods: {
    clear() {
      var that = this
      that.textarea = ''

      that.analysisResults = ''

      that.visible = false
      that.vis_visible = false
      that.sen_visible = false
      that.wc_visible = false

      that.vis_notready = true

      that.visImg = null,
        that.senImg = null,
        that.wcImg = null

      that.$message({
        showClose: true,
        message: '选择内容已清空！',
        type: 'success'
      })
    },
    // 视频关键词情感分析
    vedioEmotionAnalysis() {
      var that = this
      // 判断用户是否已经选择要进行数据库情感分析的视频
      if (that.textarea === '') {
        this.$message({
          showClose: true,
          message: '请先选择要进行情感分析的视频！',
          type: 'warning'
        })
        that.analysisResults = ''
        that.visible = false
        return
      }
      that.visible = true
      that.$message({
        showClose: true,
        message: '情感分析开始！请稍等！',
        type: 'success'
      })
      let formData = new FormData();
      formData.append('url', that.textarea);

      axios.post('http://localhost:5000/api/analyse/toptext', formData)
        .then((response) => {
          // 获取接口返回的关键词情感分析预测结果并更新界面数据
          that.analysisResults = response.data.data
          that.visible = true
          that.$message({
            showClose: true,
            message: '情感分析完成！',
            type: 'success'
          })
        }).catch((error) => {
          console.log(error)
          that.analysisResults = ''
          that.visible = false
          that.$message({
            showClose: true,
            message: '请求异常，请检查后端服务模块！',
            type: 'error'
          })
        })
      this.preVideoVisualize()
      this.preVideoSentiment()
      this.preVideoWordcloud()
    },
    // 弹幕数据可视化
    preVideoVisualize() {
      var that = this

      let formData = new FormData();
      formData.append('url', that.textarea);
      // console.log('vedio visualize:');

      axios.post('http://localhost:5000/api/analyse/visualize', formData, { responseType: 'blob' })
        .then((response) => {
          // Convert response to blob
          const blob = new Blob([response.data], { type: 'image/png' });
          const imageUrl = window.URL.createObjectURL(blob);
          // Display the image
          // console.log('imageUrl:', imageUrl);
          that.visImg = imageUrl;
          console.log('pre visualize');
          that.vis_notready = false
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    },
    // 可视化情感趋势图
    preVideoSentiment() {
      var that = this

      let formData = new FormData();
      formData.append('url', that.textarea);
      // console.log('vedio sentiment:');

      axios.post('http://localhost:5000/api/analyse/sentiment', formData, { responseType: 'blob' })
        .then((response) => {
          // Convert response to blob
          const blob = new Blob([response.data], { type: 'image/png' });
          const imageUrl = window.URL.createObjectURL(blob);
          // Display the image
          // console.log('imageUrl:', imageUrl);
          that.senImg = imageUrl;
          console.log('pre sentiment');
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    },
    // 弹幕词云图
    preVideoWordcloud() {
      var that = this

      let formData = new FormData();
      formData.append('url', that.textarea);
      // console.log('vedio wordcloud:');

      axios.post('http://localhost:5000/api/analyse/wordcloud', formData, { responseType: 'blob' })
        .then((response) => {
          // Convert response to blob
          const blob = new Blob([response.data], { type: 'image/png' });
          const imageUrl = window.URL.createObjectURL(blob);
          // Display the image
          // console.log('imageUrl:', imageUrl);
          that.wcImg = imageUrl;
          console.log('pre wordcloud');
        })
        .catch((error) => {
          console.error('Error:', error);
        });
    },
    videoVisualize() {
      var that = this
      that.vis_visible = true;
      that.wc_visible = false;
      that.sen_visible = false;
    },
    videoSentiment() {
      var that = this
      that.vis_visible = false;
      that.wc_visible = false;
      that.sen_visible = true;
    },
    videoWordcloud() {
      var that = this
      that.vis_visible = false;
      that.wc_visible = true;
      that.sen_visible = false;
    },
  }
}
</script>

<style scoped>
.tip {
  font-family: 宋体;
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  margin-bottom: 10px;
  text-align: left;
}

.chart-container {
  width: 500%;
  height: 400px;
  margin-left: 400px;
}

.vis-img {
  width: 50%;
  height: 50%;
  margin: 0 auto;
  display: block;
}

.wc-img {
  width: 50%;
  height: 50%;
  margin: 0 auto;
  display: block;
}

.sen-img {
  width: 50%;
  height: 50%;
  margin: 0 auto;
  display: block;
}
</style>