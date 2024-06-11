<template>
    <div class="app-container">
        <el-card class="box-card">
            <div class="tip">
                给ChatGPT发送消息:
            </div>
            <el-input v-model="textarea" type="textarea" :disabled="stage" :rows="6" placeholder="请输入与ChatGPT的对话"
                clearable />
        </el-card>
        <el-row style="text-align: center; padding-top:20px; padding-bottom:20px;">
            <el-button type="info" round @click="clear()">清空内容</el-button>
            <el-button type="success" round @click="gptChat()">发送消息</el-button>
            <el-button type="primary" round @click="gptAnalysis()">情感分析</el-button>
        </el-row>
        <!-- 发送消息框 -->
        <el-card v-show="chatVisible" class="box-card">
            <div v-show="chatVisible" class="tip">
                ChatGPT回复:
            </div>
            <el-input v-model="resarea" type="textarea" :disabled="stage" :rows="6" placeholder="ChatGPT回复" clearable />
        </el-card>
        <!-- 情感分析框 -->
        <el-card v-show="anaVisible" class="box-card">
            <div v-show="anaVisible" class="tip">
                ChatGPT情感分析结果:
            </div>
            <el-input v-model="resultarea" type="textarea" :disabled="stage" :rows="6" placeholder="ChatGPT情感分析结果"
                clearable />
        </el-card>
    </div>
</template>

<script>
import axios from 'axios'
export default {
    data() {
        return {
            textarea: '', // 用户输入框内输入内容
            resarea: '', // ChatGPT回复
            resultarea:'',
            stage: false,
            anaVisible: false, // 设置情感分析结果的可见性
            chatVisible: false, // 设置ChatGPT回复的可见性
        }
    },
    methods: {
        clear() {
            var that = this
            that.textarea = ''
            that.resarea = ''
            that.resultarea = ''
            that.anaVisible = false
            that.chatVisible = false
            that.$message({
                showClose: true,
                message: '文本内容已清空！',
                type: 'success'
            })
        },
        gptAnalysis() {
            var that = this
            // 获取用户输入框输入的要进行情感分析的文本
            var context = that.textarea
            if (context === '') {
                this.$message({
                    showClose: true,
                    message: '输入文本内容不能为空',
                    type: 'warning'
                })
                that.anaVisible = false
            } else {
                let formData = new FormData();
                formData.append('text', that.textarea);

                axios.post('http://localhost:5000/api/gpt/analyse', formData)
                    .then((response) => {
                        console.log(response.data);
                        // 获取接口返回的情感分析预测结果并更新界面数据
                        that.resultarea = response.data.data.result;
                        that.anaVisible = true;
                    })
                    .catch((error) => {
                        // 捕获异常并弹窗提示
                        console.log(error);
                        that.resultarea = '';
                        that.anaVisible = false;
                        that.$message({
                            showClose: true,
                            message: '请求异常，请检查后端服务模块！',
                            type: 'error'
                        });
                    });

            }
        },
        gptChat() {
            var that = this
            // 获取用户输入框输入的要进行情感分析的文本
            var context = that.textarea
            if (context === '') {
                this.$message({
                    showClose: true,
                    message: '输入文本内容不能为空',
                    type: 'warning'
                })
                that.chatVisible = false
            } else {
                let formData = new FormData();
                formData.append('text', that.textarea);

                axios.post('http://localhost:5000/api/gpt/chat', formData)
                    .then((response) => {
                        console.log(response.data);
                        // 获取接口返回的情感分析预测结果并更新界面数据
                        that.resarea = response.data.data.result;
                        that.chatVisible = true;
                    })
                    .catch((error) => {
                        // 捕获异常并弹窗提示
                        console.log(error);
                        that.resarea = '';
                        that.chatVisible = false;
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
.box-card{
    margin-bottom: 10px;
}
</style>