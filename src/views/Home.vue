<template>
  <div class="home">
    <div class="dashboard-header">
      <el-row :gutter="20">
        <el-col
          :span="6"
          v-for="(card, index) in computedStatCards"
          :key="index"
        >
          <el-card shadow="hover" class="stat-card">
            <div class="stat-card-content">
              <div
                class="stat-card-icon"
                :style="{ backgroundColor: card.bgColor }"
              >
                <i :class="card.icon"></i>
              </div>
              <div class="stat-card-info">
                <div class="stat-card-title">{{ card.title }}</div>
                <div class="stat-card-value">{{ card.value }}</div>
                <div class="stat-card-trend" :class="card.trend.type">
                  <i :class="card.trend.icon"></i>
                  <span>{{ card.trend.value }}</span>
                </div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-row :gutter="20" class="main-charts">
      <el-col :span="16">
        <el-card shadow="hover" class="chart-card">
          <div slot="header" class="clearfix">
            <span>系统活动总览</span>
            <el-radio-group
              v-model="activityType"
              size="mini"
              @change="handleActivityTypeChange"
              style="float: right"
            >
              <el-radio-button label="login">登录活动</el-radio-button>
              <el-radio-button label="web">网页访问</el-radio-button>
              <el-radio-button label="email">邮件活动</el-radio-button>
            </el-radio-group>
          </div>
          <div id="activityChart" style="width: 100%; height: 400px"></div>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card shadow="hover" class="chart-card">
          <div slot="header" class="clearfix">
            <span>威胁分布</span>
            <el-dropdown
              trigger="click"
              @command="handleThreatChartChange"
              style="float: right; cursor: pointer"
            >
              <span class="el-dropdown-link">
                筛选 <i class="el-icon-arrow-down el-icon--right"></i>
              </span>
              <el-dropdown-menu slot="dropdown">
                <el-dropdown-item command="all">全部</el-dropdown-item>
                <el-dropdown-item command="high">高风险</el-dropdown-item>
                <el-dropdown-item command="medium">中风险</el-dropdown-item>
                <el-dropdown-item command="low">低风险</el-dropdown-item>
              </el-dropdown-menu>
            </el-dropdown>
          </div>
          <div id="threatChart" style="width: 100%; height: 400px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="detail-charts">
      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <div slot="header" class="clearfix">
            <span>部门异常活动统计</span>
          </div>
          <div
            id="departmentAbnormalChart"
            style="width: 100%; height: 320px"
          ></div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card shadow="hover" class="chart-card">
          <div slot="header" class="clearfix">
            <span>最近异常事件</span>
            <el-button type="text" style="float: right" @click="goToThreatPage"
              >查看全部</el-button
            >
          </div>
          <el-table
            :data="actualRecentEvents"
            style="width: 100%"
            :row-class-name="getEventRowClass"
            @row-click="handleEventClick"
          >
            <el-table-column
              prop="time"
              label="时间"
              width="180"
            ></el-table-column>
            <el-table-column prop="type" label="类型" width="120">
              <template slot-scope="scope">
                <el-tag :type="getEventTypeTag(scope.row.type)">{{
                  scope.row.type
                }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述"></el-table-column>
            <el-table-column prop="level" label="风险等级" width="100">
              <template slot-scope="scope">
                <el-tag :type="getRiskLevelTag(scope.row.level)" size="mini">
                  {{ scope.row.level }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      globalStats: null,
      dailyActivitySummary: null,
      departmentAbnormalCounts: [],
      actualRecentEvents: [],
      isLoading: true,

      activityType: "login",
      activityChart: null,
      threatChart: null,
      departmentAbnormalChart: null,
      threatFilter: "all",
    };
  },
  computed: {
    computedStatCards() {
      if (!this.globalStats) {
        const defaultCards = [
          {
            title: "总员工数",
            value: "-",
            icon: "el-icon-user-solid",
            bgColor: "#409EFF",
            trend: {
              type: "steady",
              icon: "el-icon-minus",
              value: "加载中...",
            },
          },
          {
            title: "登录事件",
            value: "-",
            icon: "el-icon-s-platform",
            bgColor: "#67C23A",
            trend: {
              type: "steady",
              icon: "el-icon-minus",
              value: "加载中...",
            },
          },
          {
            title: "网页访问",
            value: "-",
            icon: "el-icon-reading",
            bgColor: "#E6A23C",
            trend: {
              type: "steady",
              icon: "el-icon-minus",
              value: "加载中...",
            },
          },
          {
            title: "异常事件",
            value: "-",
            icon: "el-icon-warning-outline",
            bgColor: "#F56C6C",
            trend: {
              type: "steady",
              icon: "el-icon-minus",
              value: "加载中...",
            },
          },
        ];
        return defaultCards;
      }
      return [
        {
          title: "总员工数",
          value: this.globalStats.totalEmployees?.toLocaleString() || "0",
          icon: "el-icon-user-solid",
          bgColor: "#409EFF",
          trend: { type: "steady", icon: "el-icon-minus", value: "-" },
        },
        {
          title: "登录事件总数",
          value: this.globalStats.totalLoginEvents?.toLocaleString() || "0",
          icon: "el-icon-s-platform",
          bgColor: "#67C23A",
          trend: { type: "steady", icon: "el-icon-minus", value: "-" },
        },
        {
          title: "网页访问总数",
          value: this.globalStats.totalWeblogEvents?.toLocaleString() || "0",
          icon: "el-icon-reading",
          bgColor: "#E6A23C",
          trend: { type: "steady", icon: "el-icon-minus", value: "-" },
        },
        {
          title: "异常事件总数",
          value:
            this.globalStats.totalAbnormalActivities?.toLocaleString() || "0",
          icon: "el-icon-warning-outline",
          bgColor: "#F56C6C",
          trend: { type: "steady", icon: "el-icon-minus", value: "-" },
        },
      ];
    },
  },
  async mounted() {
    await this.loadDashboardData();
  },
  methods: {
    async loadDashboardData() {
      this.isLoading = true;
      this.$message.info("正在加载仪表盘数据...");
      try {
        const [
          globalStatsRes,
          dailyActivityRes,
          deptAbnormalRes,
          recentEventsRes,
        ] = await Promise.all([
          fetch("/global_stats.json"),
          fetch("/daily_activity_summary.json"),
          fetch("/department_abnormal_counts.json"),
          fetch("/recent_abnormal_events.json"),
        ]);

        if (!globalStatsRes.ok)
          throw new Error(`获取全局统计失败: ${globalStatsRes.status}`);
        if (!dailyActivityRes.ok)
          throw new Error(`获取每日活动总结失败: ${dailyActivityRes.status}`);
        if (!deptAbnormalRes.ok)
          throw new Error(`获取部门异常统计失败: ${deptAbnormalRes.status}`);
        if (!recentEventsRes.ok)
          throw new Error(`获取最近异常事件失败: ${recentEventsRes.status}`);

        this.globalStats = await globalStatsRes.json();
        this.dailyActivitySummary = await dailyActivityRes.json();
        this.departmentAbnormalCounts = await deptAbnormalRes.json();
        const rawRecentEvents = await recentEventsRes.json();

        this.actualRecentEvents = rawRecentEvents.map((event) => ({
          time: event.timestamp,
          type: event.type,
          description: event.description,
          level: event.level,
          employeeId: event.employeeId,
          department: event.department,
        }));

        console.log("全局统计:", this.globalStats);
        console.log("每日活动:", this.dailyActivitySummary);
        console.log("部门异常统计:", this.departmentAbnormalCounts);
        console.log("最近异常事件 (转换后):", this.actualRecentEvents);

        this.$message.success("仪表盘数据加载完成！");
        this.initCharts();
      } catch (error) {
        console.error("加载仪表盘数据失败:", error);
        this.$message.error(`加载仪表盘数据失败: ${error.message}`);
      } finally {
        this.isLoading = false;
      }
    },
    initCharts() {
      this.$nextTick(() => {
        this.initActivityChart();
        this.initThreatChart();
        this.initDepartmentAbnormalChart();
      });
    },
    handleActivityTypeChange() {
      if (this.dailyActivitySummary) {
        this.initActivityChart();
      } else {
        this.$message.warning("活动数据仍在加载中，请稍候...");
      }
    },
    handleThreatChartChange(command) {
      this.threatFilter = command;
      this.initThreatChart();
    },
    goToThreatPage() {
      this.$router.push("/threat");
    },
    initActivityChart() {
      if (!this.dailyActivitySummary) {
        console.warn(
          "initActivityChart: dailyActivitySummary is not loaded yet."
        );
        return;
      }
      if (this.activityChart) {
        this.activityChart.dispose();
      }
      this.activityChart = this.$echarts.init(
        document.getElementById("activityChart")
      );

      let seriesData = [];
      let dates = [];
      let yAxisName = "";

      if (
        this.activityType === "login" &&
        this.dailyActivitySummary.loginsByDay
      ) {
        seriesData = this.dailyActivitySummary.loginsByDay.map(
          (item) => item.count
        );
        dates = this.dailyActivitySummary.loginsByDay.map((item) => item.date);
        yAxisName = "登录次数";
      } else if (
        this.activityType === "web" &&
        this.dailyActivitySummary.weblogsByDay
      ) {
        seriesData = this.dailyActivitySummary.weblogsByDay.map(
          (item) => item.count
        );
        dates = this.dailyActivitySummary.weblogsByDay.map((item) => item.date);
        yAxisName = "网页访问次数";
      } else if (
        this.activityType === "email" &&
        this.dailyActivitySummary.emailsByDay
      ) {
        seriesData = this.dailyActivitySummary.emailsByDay.map(
          (item) => item.count
        );
        dates = this.dailyActivitySummary.emailsByDay.map((item) => item.date);
        yAxisName = "邮件数量";
      }

      if (!dates.length || !seriesData.length) {
        console.warn(
          `initActivityChart: No data for activityType '${this.activityType}'`
        );
        this.activityChart.setOption({
          title: {
            text: `暂无'${yAxisName || this.activityType}'数据`,
            left: "center",
            top: "center",
            textStyle: { color: "#909399" },
          },
        });
        return;
      }

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          top: 10,
          data: [yAxisName],
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: [
          {
            type: "category",
            boundaryGap: true,
            data: dates,
            axisLabel: {
              formatter: function (value) {
                return value.substring(5);
              },
              rotate: 45,
              interval: "auto",
            },
          },
        ],
        yAxis: [
          {
            type: "value",
            name: "数量",
            axisLabel: {
              formatter: "{value}",
            },
          },
        ],
        dataZoom: [
          {
            type: "inside",
            start: 0,
            end: 100,
          },
          {
            start: 0,
            end: 100,
          },
        ],
        series: [
          {
            name: yAxisName,
            type: "line",
            smooth: true,
            data: seriesData,
            areaStyle: {},
            emphasis: {
              focus: "series",
            },
          },
        ],
      };
      this.activityChart.setOption(option);
    },
    initThreatChart() {
      console.warn("ThreatChart 仍在使用模拟数据。");
      if (this.threatChart) {
        this.threatChart.dispose();
      }
      this.threatChart = this.$echarts.init(
        document.getElementById("threatChart")
      );

      let data = [];
      if (this.threatFilter === "all" || this.threatFilter === "high") {
        data.push(
          { value: 8, name: "数据泄露", itemStyle: { color: "#F56C6C" } },
          { value: 5, name: "异常通信", itemStyle: { color: "#F56C6C" } }
        );
      }

      if (this.threatFilter === "all" || this.threatFilter === "medium") {
        data.push(
          { value: 6, name: "异常登录", itemStyle: { color: "#E6A23C" } },
          { value: 4, name: "非常规操作", itemStyle: { color: "#E6A23C" } }
        );
      }

      if (this.threatFilter === "all" || this.threatFilter === "low") {
        data.push(
          { value: 3, name: "审计失败", itemStyle: { color: "#909399" } },
          { value: 2, name: "权限异常", itemStyle: { color: "#909399" } }
        );
      }

      const option = {
        tooltip: {
          trigger: "item",
          formatter: "{a} <br/>{b}: {c} ({d}%)",
        },
        legend: {
          orient: "vertical",
          right: 10,
          top: "center",
          data: data.map((item) => item.name),
        },
        series: [
          {
            name: "威胁类型",
            type: "pie",
            radius: ["40%", "70%"],
            center: ["40%", "50%"],
            avoidLabelOverlap: false,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
            label: {
              show: false,
              position: "center",
            },
            labelLine: {
              show: false,
            },
            data: data,
          },
        ],
      };

      this.threatChart.setOption(option);

      this.threatChart.on("click", (params) => {
        this.$notify({
          title: "威胁详情",
          message: `${params.name}类型威胁共有${params.value}个事件，点击查看详情`,
          type: "warning",
          duration: 3000,
        });
      });
    },
    initDepartmentAbnormalChart() {
      if (
        !this.departmentAbnormalCounts ||
        this.departmentAbnormalCounts.length === 0
      ) {
        console.warn(
          "initDepartmentAbnormalChart: departmentAbnormalCounts is not loaded or empty."
        );
        if (this.departmentAbnormalChart)
          this.departmentAbnormalChart.dispose();
        this.departmentAbnormalChart = this.$echarts.init(
          document.getElementById("departmentAbnormalChart")
        );
        this.departmentAbnormalChart.setOption({
          title: {
            text: "暂无部门异常数据",
            left: "center",
            top: "center",
            textStyle: { color: "#909399" },
          },
        });
        return;
      }
      if (this.departmentAbnormalChart) {
        this.departmentAbnormalChart.dispose();
      }
      this.departmentAbnormalChart = this.$echarts.init(
        document.getElementById("departmentAbnormalChart")
      );

      const departmentNames = this.departmentAbnormalCounts.map(
        (item) => item.department
      );
      const abnormalCounts = this.departmentAbnormalCounts.map(
        (item) => item.count
      );

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          data: ["高风险", "中风险", "低风险"],
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "value",
          boundaryGap: [0, 0.01],
        },
        yAxis: {
          type: "category",
          data: departmentNames,
        },
        series: [
          {
            name: "高风险",
            type: "bar",
            data: abnormalCounts.map((count) => (count > 0 ? count : 0)),
            itemStyle: {
              color: "#F56C6C",
            },
          },
          {
            name: "中风险",
            type: "bar",
            data: abnormalCounts.map((count) => (count > 0 ? count : 0)),
            itemStyle: {
              color: "#E6A23C",
            },
          },
          {
            name: "低风险",
            type: "bar",
            data: abnormalCounts.map((count) => (count > 0 ? count : 0)),
            itemStyle: {
              color: "#909399",
            },
          },
        ],
      };

      this.departmentAbnormalChart.setOption(option);
    },
    handleEventClick(row) {
      this.$router.push("/threat");
    },
    getEventRowClass({ row }) {
      if (row.level === "高风险") {
        return "high-risk-row";
      }
      return "";
    },
    getEventTypeTag(type) {
      const typeMap = {
        数据泄露: "danger",
        异常登录: "warning",
        异常流量: "danger",
        非常规操作: "warning",
        数据库异常: "danger",
      };
      return typeMap[type] || "info";
    },
    getRiskLevelTag(level) {
      const levelMap = {
        高风险: "danger",
        中风险: "warning",
        低风险: "info",
      };
      return levelMap[level] || "info";
    },
  },
  beforeDestroy() {
    this.activityChart && this.activityChart.dispose();
    this.threatChart && this.threatChart.dispose();
    this.departmentAbnormalChart && this.departmentAbnormalChart.dispose();
  },
  watch: {
    "$store.state.app.sidebar.opened"() {
      this.$nextTick(() => {
        this.activityChart && this.activityChart.resize();
        this.threatChart && this.threatChart.resize();
        this.departmentAbnormalChart && this.departmentAbnormalChart.resize();
      });
    },
  },
};
</script>

<style lang="scss" scoped>
.home {
  padding: 20px;
}

.dashboard-header {
  margin-bottom: 20px;
}

.stat-card {
  background-color: #fff;
  border-radius: 4px;
  height: 120px;
  overflow: hidden;

  .stat-card-content {
    display: flex;
    align-items: center;
    height: 100%;
  }

  .stat-card-icon {
    width: 80px;
    height: 80px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    margin-left: 16px;

    i {
      font-size: 32px;
      color: #fff;
    }
  }

  .stat-card-info {
    flex: 1;
  }

  .stat-card-title {
    font-size: 14px;
    color: #909399;
    margin-bottom: 5px;
  }

  .stat-card-value {
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 5px;
  }

  .stat-card-trend {
    font-size: 12px;
    display: flex;
    align-items: center;

    i {
      margin-right: 4px;
    }

    &.up {
      color: #f56c6c;
    }

    &.down {
      color: #67c23a;
    }

    &.steady {
      color: #909399;
    }
  }
}

.main-charts {
  margin-bottom: 20px;
}

.detail-charts {
  margin-bottom: 20px;
}

.chart-card {
  .el-card__header {
    padding: 12px 20px;
  }
}

.high-risk-row {
  background-color: rgba(245, 108, 108, 0.1);
}

::v-deep .el-table__body tr:hover > td {
  background-color: rgba(236, 245, 255, 0.8) !important;
  cursor: pointer;
}
</style>
