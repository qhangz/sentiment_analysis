<template>
    <div class="app-container">
        <el-row style="text-align: center; padding-top:20px;padding-bottom:20px;">
            <el-button type="primary" round @click="getPieChart()">pie_chart</el-button>

        </el-row>
        <el-card v-show="1" class="box-card">
            <div ref="pie_chart" class="chart-container"></div>
        </el-card>
    </div>
</template>

<script>
import * as echarts from 'echarts';

export default {
    data() {
        return {
            pieChartRef: null // 用于存储图表实例
        };
    },
    methods: {
        getPieChart() {
            // 检查是否已经存在图表实例，如果存在则销毁
            if (this.pieChartRef !== null) {
                this.pieChartRef.dispose();
            }
            console.log('get pie chart');

            // 初始化新的图表实例
            this.pieChartRef = echarts.init(this.$refs.pie_chart);

            var pie_chart_option = {
                tooltip: {
                    trigger: 'item'
                },
                legend: {
                    top: '5%',
                    left: 'center'
                },
                series: [
                    {
                        name: 'Access From',
                        type: 'pie',
                        radius: ['40%', '70%'],
                        avoidLabelOverlap: false,
                        label: {
                            show: false,
                            position: 'center'
                        },
                        emphasis: {
                            label: {
                                show: true,
                                fontSize: 40,
                                fontWeight: 'bold'
                            }
                        },
                        labelLine: {
                            show: false
                        },
                        data: [
                            { value: 1048, name: 'Search Engine' },
                            { value: 735, name: 'Direct' },
                            { value: 580, name: 'Email' },
                            { value: 484, name: 'Union Ads' },
                            { value: 300, name: 'Video Ads' }
                        ]
                    }
                ]
            };

            // 设置图表的选项
            this.pieChartRef.setOption(pie_chart_option);
            console.log('finish');
        }
    },
    beforeDestroy() {
        // 在组件销毁前销毁图表实例
        if (this.pieChartRef !== null) {
            this.pieChartRef.dispose();
        }
    }
};
</script>

<style scoped>
.chart-container {
    width: 100%;
    height: 400px;
}
</style>