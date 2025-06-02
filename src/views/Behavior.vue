<template>
  <div class="behavior">
    <el-row>
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>员工日常工作行为分析</span>
            <el-tooltip
              class="item"
              effect="dark"
              content="分析各部门员工的正常工作模式和行为特征"
              placement="top"
            >
              <i class="el-icon-question" style="margin-left: 10px"></i>
            </el-tooltip>
          </div>
          <p>
            通过对监控数据的分析，我们总结了公司不同部门员工的工作行为模式，包括工作时间、网络活动、邮件沟通等。
          </p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>员工打卡时间分析</span>
            <el-select
              v-model="selectedDepartment"
              size="mini"
              style="float: right; margin-right: 10px"
              placeholder="选择部门"
              @change="handleDepartmentChangeForCheckTime"
            >
              <el-option
                v-for="dept in allDepartments"
                :key="dept"
                :label="dept"
                :value="dept"
              ></el-option>
            </el-select>
          </div>
          <div ref="checkTimeChartRef" style="width: 100%; height: 350px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>员工工作时长分布</span>
          </div>
          <div ref="workHoursChartRef" style="width: 100%; height: 350px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>员工网页访问类别分析</span>
            <el-radio-group
              v-model="webVisitTimeRange"
              size="mini"
              style="float: right; margin-right: 10px"
              @change="handleWebTimeRangeChange"
            >
              <el-radio-button label="workHours">工作时间</el-radio-button>
              <el-radio-button label="afterHours">非工作时间</el-radio-button>
              <el-radio-button label="allDay">全天</el-radio-button>
            </el-radio-group>
          </div>
          <div
            ref="webCategoryChartRef"
            style="width: 100%; height: 350px"
          ></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>服务器/数据库访问频率</span>
          </div>
          <div
            ref="serverAccessChartRef"
            style="width: 100%; height: 350px"
          ></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>网络流量时序分析</span>
            <el-date-picker
              v-model="selectedDate"
              type="date"
              format="yyyy-MM-dd"
              value-format="yyyy-MM-dd"
              placeholder="选择日期"
              :picker-options="pickerOptions"
              style="float: right; margin-right: 10px; width: 150px"
              size="mini"
              @change="handleDateChangeForNetworkFlow"
            >
            </el-date-picker>
          </div>
          <div
            ref="networkFlowChartRef"
            style="width: 100%; height: 400px"
          ></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>邮件通信频率（按部门）</span>
          </div>
          <div
            ref="emailFrequencyChartRef"
            style="width: 100%; height: 300px"
          ></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>登录成功率</span>
          </div>
          <div
            ref="loginSuccessChartRef"
            style="width: 100%; height: 300px"
          ></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>TCP协议使用分布</span>
          </div>
          <div
            ref="tcpProtocolChartRef"
            style="width: 100%; height: 300px"
          ></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: "Behavior",
  data() {
    return {
      checkTimeChart: null,
      workHoursChart: null,
      webCategoryChart: null,
      serverAccessChart: null,
      networkFlowChart: null,
      emailFrequencyChart: null,
      loginSuccessChart: null,
      tcpProtocolChart: null,
      selectedDepartment: "",
      webVisitTimeRange: "workHours",
      selectedDate: "2017-11-01",
      pickerOptions: {
        disabledDate(time) {
          const start = new Date("2017-11-01").getTime();
          const end = new Date("2017-11-30").getTime();
          return time.getTime() < start || time.getTime() > end;
        },
      },
      isLoading: true,
      allDepartments: [],
      departmentCheckTimeData: null,
      workDurationDistributionData: null,
      webCategoryData: null,
      departmentEmailActivityData: null,
      loginSuccessFailData: null,
      tcpProtocolData: null,
      serverDBAccessData: [],
      dailyNetworkTrafficData: [],
    };
  },
  async mounted() {
    console.log("Behavior.vue mounted: Starting data load...");
    await this.loadBehaviorData();
    console.log(
      "Behavior.vue mounted: Data load complete. Scheduling chart initializations."
    );
    this.$nextTick(() => {
      console.log("Behavior.vue mounted/$nextTick: Initializing charts...");
      this.initAllCharts();
    });
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    this.disposeAllCharts();
  },
  watch: {
    selectedDepartment(newVal, oldVal) {
      if (newVal !== oldVal && this.departmentCheckTimeData) {
        console.log(
          `Watcher: selectedDepartment changed to ${newVal}. Re-initializing checkTimeChart.`
        );
        this.initCheckTimeChart();
      }
    },
    webVisitTimeRange(newVal, oldVal) {
      if (newVal !== oldVal && this.webCategoryData) {
        console.log(
          `Watcher: webVisitTimeRange changed to ${newVal}. Re-initializing webCategoryChart.`
        );
        this.initWebCategoryChart();
      }
    },
    selectedDate(newVal, oldVal) {
      if (newVal !== oldVal && this.dailyNetworkTrafficData) {
        // check specific data for this chart
        console.log(
          `Watcher: selectedDate changed to ${newVal}. Re-initializing networkFlowChart.`
        );
        this.initNetworkFlowChart();
      }
    },
  },
  methods: {
    initAllCharts() {
      this.initCheckTimeChart();
      this.initWorkHoursChart();
      this.initWebCategoryChart();
      this.initServerAccessChart();
      this.initNetworkFlowChart();
      this.initEmailFrequencyChart();
      this.initLoginSuccessChart();
      this.initTcpProtocolChart();
    },
    disposeAllCharts() {
      if (this.checkTimeChart) {
        this.checkTimeChart.dispose();
        this.checkTimeChart = null;
      }
      if (this.workHoursChart) {
        this.workHoursChart.dispose();
        this.workHoursChart = null;
      }
      if (this.webCategoryChart) {
        this.webCategoryChart.dispose();
        this.webCategoryChart = null;
      }
      if (this.serverAccessChart) {
        this.serverAccessChart.dispose();
        this.serverAccessChart = null;
      }
      if (this.networkFlowChart) {
        this.networkFlowChart.dispose();
        this.networkFlowChart = null;
      }
      if (this.emailFrequencyChart) {
        this.emailFrequencyChart.dispose();
        this.emailFrequencyChart = null;
      }
      if (this.loginSuccessChart) {
        this.loginSuccessChart.dispose();
        this.loginSuccessChart = null;
      }
      if (this.tcpProtocolChart) {
        this.tcpProtocolChart.dispose();
        this.tcpProtocolChart = null;
      }
      console.log("All charts disposed.");
    },
    showEmptyChart(chartInstance, chartRefName, message = "暂无数据") {
      const chartDom = this.$refs[chartRefName];
      if (chartInstance) {
        try {
          chartInstance.clear();
          chartInstance.setOption({
            title: {
              text: message,
              left: "center",
              top: "center",
              textStyle: { color: "#888", fontSize: 16 },
            },
            xAxis: {},
            yAxis: {},
            series: [],
          });
        } catch (e) {
          console.error(
            `Error setting empty chart option for ${chartRefName}:`,
            e,
            chartInstance
          );
          if (chartDom)
            chartDom.innerHTML = `<div style=\"text-align: center; padding-top: 50px; color: #888;\">${message} (Error displaying chart)</div>`;
        }
      } else if (chartDom) {
        chartDom.innerHTML = `<div style=\"text-align: center; padding-top: 50px; color: #888;\">${message}</div>`;
        console.log(
          `showEmptyChart: ${chartRefName} instance was null, set HTML directly.`
        );
      } else {
        console.error(
          `showEmptyChart: Cannot find DOM element for ${chartRefName} and chart instance is null.`
        );
      }
    },

    async loadBehaviorData() {
      this.isLoading = true;
      this.$message.info("正在加载行为分析数据...");
      try {
        // 首先加载所有部门名称
        const allDeptsResponse = await fetch("/all_department_names.json");
        if (allDeptsResponse.ok) {
          this.allDepartments = await allDeptsResponse.json();
          console.log("已加载所有部门:", this.allDepartments);
          if (this.allDepartments.length > 0 && !this.selectedDepartment) {
            this.selectedDepartment = this.allDepartments[0];
          }
        }

        const results = await Promise.allSettled([
          fetch("/department_check_time_approx.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load department_check_time_approx.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/work_duration_distribution.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load work_duration_distribution.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/web_category_distribution.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load web_category_distribution.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/department_email_activity.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load department_email_activity.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/login_success_fail.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load login_success_fail.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/tcp_protocol_distribution.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load tcp_protocol_distribution.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/server_database_access_frequency.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load server_database_access_frequency.json: ${res.statusText}`
                  )
                )
          ),
          fetch("/daily_network_traffic.json").then((res) =>
            res.ok
              ? res.json()
              : Promise.reject(
                  new Error(
                    `Failed to load daily_network_traffic.json: ${res.statusText}`
                  )
                )
          ),
        ]);

        if (results[0].status === "fulfilled" && results[0].value) {
          this.departmentCheckTimeData = results[0].value;
          // 不再从这里更新 allDepartments，因为已经从 all_department_names.json 加载
        } else {
          console.error(
            "Failed to load department check time data:",
            results[0].reason
          );
          this.departmentCheckTimeData = [];
        }
        this.workDurationDistributionData =
          results[1].status === "fulfilled" ? results[1].value : [];
        this.webCategoryData =
          results[2].status === "fulfilled" ? results[2].value : null;
        this.departmentEmailActivityData =
          results[3].status === "fulfilled" ? results[3].value : [];
        this.loginSuccessFailData =
          results[4].status === "fulfilled" ? results[4].value : {};
        this.tcpProtocolData =
          results[5].status === "fulfilled" ? results[5].value : [];
        this.serverDBAccessData =
          results[6].status === "fulfilled" ? results[6].value : [];
        this.dailyNetworkTrafficData =
          results[7].status === "fulfilled" ? results[7].value : [];

        console.log(
          "Department Check Time Data Loaded:",
          this.departmentCheckTimeData
        );
        console.log("Login Success/Fail Data:", this.loginSuccessFailData);

        this.$message.success("行为分析数据加载完成!");
      } catch (error) {
        console.error("加载行为数据失败:", error);
        this.$message.error(`加载行为数据失败: ${error.message || "未知错误"}`);
        // Initialize with empty data to prevent errors
        this.departmentCheckTimeData = [];
        this.workDurationDistributionData = [];
        this.webCategoryData = null;
        this.departmentEmailActivityData = [];
        this.loginSuccessFailData = {};
        this.tcpProtocolData = [];
        this.serverDBAccessData = [];
        this.dailyNetworkTrafficData = [];
      } finally {
        this.isLoading = false;
      }
    },

    initCheckTimeChart() {
      const chartDom = this.$refs.checkTimeChartRef;
      if (!chartDom) {
        console.error(
          "initCheckTimeChart: DOM element 'checkTimeChartRef' not found."
        );
        return;
      }
      if (this.checkTimeChart) {
        this.checkTimeChart.dispose();
      }
      this.checkTimeChart = this.$echarts.init(chartDom);
      console.log(
        "initCheckTimeChart: Initialized for department:",
        this.selectedDepartment
      );

      if (
        !this.departmentCheckTimeData ||
        this.departmentCheckTimeData.length === 0
      ) {
        this.showEmptyChart(
          this.checkTimeChart,
          "checkTimeChartRef",
          "打卡时间数据正在加载或无可用数据"
        );
        console.log(
          "initCheckTimeChart: No departmentCheckTimeData available."
        );
        return;
      }

      const selectedDeptData = this.departmentCheckTimeData.find(
        (d) => d.department === this.selectedDepartment
      );

      if (
        !selectedDeptData ||
        !selectedDeptData.checkInDistribution ||
        !selectedDeptData.checkOutDistribution
      ) {
        this.showEmptyChart(
          this.checkTimeChart,
          "checkTimeChartRef",
          `部门 [${this.selectedDepartment}] 无打卡数据`
        );
        console.log(
          `initCheckTimeChart: No data for selected department: ${this.selectedDepartment}`
        );
        return;
      }

      const checkInTimes = selectedDeptData.checkInDistribution.map(
        (item) => item.timeBin
      );
      const checkInCounts = selectedDeptData.checkInDistribution.map(
        (item) => item.count
      );
      const checkOutTimes = selectedDeptData.checkOutDistribution.map(
        (item) => item.timeBin
      );
      const checkOutCounts = selectedDeptData.checkOutDistribution.map(
        (item) => item.count
      );

      // Ensure unique time bins for x-axis, sorted
      const allTimeBins = [
        ...new Set([...checkInTimes, ...checkOutTimes]),
      ].sort();

      const option = {
        title: {
          text: `${this.selectedDepartment} 打卡时间分布`,
          left: "center",
          textStyle: { fontSize: 16 },
        },
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        legend: { data: ["上班打卡", "下班打卡"], top: 30 },
        grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
        xAxis: {
          type: "category",
          data: allTimeBins,
          axisLabel: { rotate: 45, interval: "auto" },
        }, // Ensure allTimeBins is populated
        yAxis: { type: "value", name: "次数" },
        series: [
          {
            name: "上班打卡",
            type: "bar",
            stack: "time",
            emphasis: { focus: "series" },
            data: allTimeBins.map((bin) => {
              const index = checkInTimes.indexOf(bin);
              return index !== -1 ? checkInCounts[index] : 0;
            }),
            itemStyle: { color: "#67C23A" },
          },
          {
            name: "下班打卡",
            type: "bar",
            stack: "time",
            emphasis: { focus: "series" },
            data: allTimeBins.map((bin) => {
              const index = checkOutTimes.indexOf(bin);
              return index !== -1 ? checkOutCounts[index] : 0;
            }),
            itemStyle: { color: "#409EFF" },
          },
        ],
      };
      try {
        this.checkTimeChart.setOption(option);
        console.log(
          "initCheckTimeChart: Chart option set successfully for",
          this.selectedDepartment
        );
      } catch (e) {
        console.error("Error setting chart option for checkTimeChart:", e);
      }
    },

    initWorkHoursChart() {
      const chartDom = this.$refs.workHoursChartRef;
      if (!chartDom) {
        console.error(
          "initWorkHoursChart: DOM element 'workHoursChartRef' not found."
        );
        return;
      }
      if (this.workHoursChart) {
        this.workHoursChart.dispose();
      }
      this.workHoursChart = this.$echarts.init(chartDom);

      if (
        !this.workDurationDistributionData ||
        this.workDurationDistributionData.length === 0
      ) {
        this.showEmptyChart(
          this.workHoursChart,
          "workHoursChartRef",
          "工时数据正在加载或无可用数据"
        );
        return;
      }
      const durationRanges = this.workDurationDistributionData.map(
        (item) => item.durationRange
      );
      const counts = this.workDurationDistributionData.map(
        (item) => item.count
      );
      const option = {
        title: {
          text: "员工工作时长分布",
          left: "center",
          textStyle: { fontSize: 16 },
        },
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        grid: { left: "3%", right: "4%", bottom: "10%", containLabel: true }, // Adjusted bottom for labels
        xAxis: {
          type: "category",
          data: durationRanges,
          axisLabel: { rotate: 45, interval: 0 },
        }, // Show all labels
        yAxis: { type: "value", name: "次数" },
        series: [
          {
            name: "工作时长",
            type: "bar",
            data: counts,
            itemStyle: { color: "#F56C6C" },
            barMaxWidth: 50,
          },
        ],
      };
      this.workHoursChart.setOption(option);
    },

    initWebCategoryChart() {
      const chartDom = this.$refs.webCategoryChartRef;
      if (!chartDom) {
        console.error(
          "initWebCategoryChart: DOM element 'webCategoryChartRef' not found."
        );
        return;
      }
      if (this.webCategoryChart) {
        this.webCategoryChart.dispose();
      }
      this.webCategoryChart = this.$echarts.init(chartDom);

      if (
        !this.webCategoryData ||
        !this.webCategoryData[this.webVisitTimeRange] ||
        this.webCategoryData[this.webVisitTimeRange].length === 0
      ) {
        this.showEmptyChart(
          this.webCategoryChart,
          "webCategoryChartRef",
          `网页访问数据(${this.webVisitTimeRange})正在加载或无可用数据`
        );
        return;
      }

      const currentData = this.webCategoryData[this.webVisitTimeRange];
      const categories = currentData.map((item) => item.category);
      const counts = currentData.map((item) => item.count);

      const option = {
        title: {
          text: `网页访问类别 (${
            this.webVisitTimeRange === "workHours"
              ? "工作时间"
              : this.webVisitTimeRange === "afterHours"
              ? "非工作时间"
              : "全天"
          })`,
          left: "center",
          textStyle: { fontSize: 16 },
        },
        tooltip: { trigger: "item", formatter: "{b} : {c} ({d}%)" }, // Tooltip for pie chart
        legend: {
          orient: "vertical",
          left: "left",
          data: categories,
          type: "scroll",
          top: 30,
          bottom: 20,
        },
        series: [
          {
            name: "访问类别",
            type: "pie",
            radius: "65%",
            center: ["60%", "55%"], // Adjusted center for legend
            data: currentData.map((item) => ({
              name: item.category,
              value: item.count,
            })),
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
          },
        ],
      };
      this.webCategoryChart.setOption(option);
    },

    initServerAccessChart() {
      const chartDom = this.$refs.serverAccessChartRef;
      if (!chartDom) {
        console.error(
          "initServerAccessChart: DOM element 'serverAccessChartRef' not found."
        );
        return;
      }
      if (this.serverAccessChart) {
        this.serverAccessChart.dispose();
      }
      this.serverAccessChart = this.$echarts.init(chartDom);

      // serverDBAccessData is for tcplog based KNOWN_SERVERS_DATABASES.
      // For login.csv based data, you might have another data property or need to fetch/process `employee_database_access.json` / `database_server_summary.json`
      const dataToDisplay = this.serverDBAccessData; // This currently uses server_database_access_frequency.json

      if (!dataToDisplay || dataToDisplay.length === 0) {
        this.showEmptyChart(
          this.serverAccessChart,
          "serverAccessChartRef",
          "服务器/数据库访问数据正在加载或无可用数据"
        );
        return;
      }

      const serverNames = dataToDisplay.map((item) => item.name); // 'name' from server_database_access_frequency.json
      const accessCounts = dataToDisplay.map((item) => item.count); // 'count'

      const option = {
        title: {
          text: "服务器/数据库访问频率 (基于预定义列表)",
          left: "center",
          textStyle: { fontSize: 16 },
        },
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
        xAxis: {
          type: "category",
          data: serverNames,
          axisLabel: { rotate: 30, interval: 0 },
        }, // Show all labels if few enough
        yAxis: { type: "value", name: "访问次数" },
        series: [
          {
            name: "访问次数",
            type: "bar",
            data: accessCounts,
            itemStyle: { color: "#E6A23C" },
            barMaxWidth: 50,
          },
        ],
      };
      this.serverAccessChart.setOption(option);
    },

    initNetworkFlowChart() {
      const chartDom = this.$refs.networkFlowChartRef;
      if (!chartDom) {
        console.error("networkFlowChartRef not found");
        return;
      }
      if (this.networkFlowChart) {
        this.networkFlowChart.dispose();
      }
      this.networkFlowChart = this.$echarts.init(chartDom);

      if (
        !this.dailyNetworkTrafficData ||
        this.dailyNetworkTrafficData.length === 0
      ) {
        this.showEmptyChart(
          this.networkFlowChart,
          "networkFlowChartRef",
          "网络流量数据正在加载或无可用数据"
        );
        return;
      }

      // Filter data for selectedDate if necessary, or show all if selectedDate is not used for filtering here
      // For simplicity, this example assumes dailyNetworkTrafficData is an array of {date, bytes_in, bytes_out}
      // and we plot all of it or a selected portion based on selectedDate (if you add filtering logic)

      const dates = this.dailyNetworkTrafficData.map((d) => d.date);
      const bytesIn = this.dailyNetworkTrafficData.map((d) => d.bytes_in);
      const bytesOut = this.dailyNetworkTrafficData.map((d) => d.bytes_out);

      const option = {
        title: {
          text: `每日网络流量 (${this.selectedDate || "所有日期"})`,
          left: "center",
          textStyle: { fontSize: 16 },
        },
        tooltip: {
          trigger: "axis",
          axisPointer: { type: "cross", label: { backgroundColor: "#6a7985" } },
        },
        legend: { data: ["流入字节数", "流出字节数"], top: 30 },
        grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
        xAxis: [{ type: "category", boundaryGap: false, data: dates }],
        yAxis: [
          {
            type: "value",
            name: "字节数",
            axisLabel: {
              formatter: function (value) {
                return value / 1024 / 1024 + " MB";
              },
            },
          },
        ], // Example formatter
        series: [
          {
            name: "流入字节数",
            type: "line",
            stack: "总量入",
            areaStyle: {},
            emphasis: { focus: "series" },
            data: bytesIn,
            smooth: true,
            itemStyle: { color: "#5470C6" },
          },
          {
            name: "流出字节数",
            type: "line",
            stack: "总量出",
            areaStyle: {},
            emphasis: { focus: "series" },
            data: bytesOut,
            smooth: true,
            itemStyle: { color: "#91CC75" },
          },
        ],
      };
      this.networkFlowChart.setOption(option);
    },

    initEmailFrequencyChart() {
      const chartDom = this.$refs.emailFrequencyChartRef;
      if (!chartDom) {
        console.error("emailFrequencyChartRef not found");
        return;
      }
      if (this.emailFrequencyChart) {
        this.emailFrequencyChart.dispose();
      }
      this.emailFrequencyChart = this.$echarts.init(chartDom);

      if (
        !this.departmentEmailActivityData ||
        this.departmentEmailActivityData.length === 0
      ) {
        this.showEmptyChart(
          this.emailFrequencyChart,
          "emailFrequencyChartRef",
          "邮件频率数据正在加载或无可用数据"
        );
        return;
      }
      const departmentNames = this.departmentEmailActivityData.map(
        (item) => item.department
      );
      const emailCounts = this.departmentEmailActivityData.map(
        (item) => item.emailCount
      );
      const option = {
        title: {
          text: "部门邮件通信频率",
          left: "center",
          textStyle: { fontSize: 14 },
          top: 5,
        },
        tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
        grid: { left: "3%", right: "4%", bottom: "3%", containLabel: true },
        xAxis: { type: "value", boundaryGap: [0, 0.01] },
        yAxis: {
          type: "category",
          data: departmentNames.slice(0, 10).reverse(),
        }, // Show top 10, reversed for horizontal bar
        series: [
          {
            name: "邮件数量",
            type: "bar",
            data: emailCounts.slice(0, 10).reverse(),
            itemStyle: { color: "#EE6666" },
          },
        ],
      };
      this.emailFrequencyChart.setOption(option);
    },

    initLoginSuccessChart() {
      const chartDom = this.$refs.loginSuccessChartRef;
      if (!chartDom) {
        console.error("loginSuccessChartRef not found");
        return;
      }
      if (this.loginSuccessChart) {
        this.loginSuccessChart.dispose();
      }
      this.loginSuccessChart = this.$echarts.init(chartDom);

      if (
        !this.loginSuccessFailData ||
        Object.keys(this.loginSuccessFailData).length === 0
      ) {
        this.showEmptyChart(
          this.loginSuccessChart,
          "loginSuccessChartRef",
          "登录成功率数据正在加载或无可用数据"
        );
        return;
      }

      // 只获取部门数据，排除顶层的success和fail字段
      const departments = Object.keys(this.loginSuccessFailData).filter(
        (key) => key !== "success" && key !== "fail"
      );

      const seriesData = departments.map((dept) => {
        const deptData = this.loginSuccessFailData[dept];
        let rate = 0;
        if (
          deptData &&
          typeof deptData === "object" &&
          deptData.success !== undefined &&
          deptData.fail !== undefined
        ) {
          const total = deptData.success + deptData.fail;
          if (total > 0) {
            rate = (deptData.success / total) * 100;
          }
        }
        return {
          name: dept,
          value: parseFloat(rate.toFixed(2)), // Ensure value is a number, rounded
        };
      });

      const option = {
        title: {
          text: "各部门登录成功率",
          left: "center",
          textStyle: { fontSize: 14 },
          top: 5,
        },
        tooltip: {
          trigger: "item",
          formatter: function (params) {
            // params.data will be an object like {name: '研发部', value: 95.55}
            if (params.data && typeof params.data.value === "number") {
              return `${params.data.name} : ${params.data.value.toFixed(2)}%`;
            }
            return `${params.name} : N/A`; // Fallback
          },
        },
        series: [
          {
            type: "funnel",
            left: "10%",
            top: 40,
            bottom: 10,
            width: "80%",
            min: 0,
            max: 100,
            minSize: "0%",
            maxSize: "100%",
            sort: "descending",
            gap: 2,
            label: {
              show: true,
              position: "inside",
              formatter: function (params) {
                if (params.data && typeof params.data.value === "number") {
                  return `${params.data.name}\n${params.data.value.toFixed(
                    0
                  )}%`;
                }
                return `${params.data.name}\nN/A`; // Fallback
              },
            },
            labelLine: { length: 10, lineStyle: { width: 1, type: "solid" } },
            itemStyle: { borderColor: "#fff", borderWidth: 1 },
            emphasis: { label: { fontSize: 16 } },
            data: seriesData.sort((a, b) => b.value - a.value), // Sort for funnel
          },
        ],
      };
      this.loginSuccessChart.setOption(option);
    },

    initTcpProtocolChart() {
      const chartDom = this.$refs.tcpProtocolChartRef;
      if (!chartDom) {
        console.error("tcpProtocolChartRef not found");
        return;
      }
      if (this.tcpProtocolChart) {
        this.tcpProtocolChart.dispose();
      }
      this.tcpProtocolChart = this.$echarts.init(chartDom);

      if (!this.tcpProtocolData || this.tcpProtocolData.length === 0) {
        this.showEmptyChart(
          this.tcpProtocolChart,
          "tcpProtocolChartRef",
          "TCP协议数据正在加载或无可用数据"
        );
        return;
      }
      // Take top N protocols for clarity, e.g., top 7
      const topN = 7;
      const displayData = this.tcpProtocolData.slice(0, topN);
      const otherCount = this.tcpProtocolData
        .slice(topN)
        .reduce((sum, item) => sum + item.count, 0);
      if (otherCount > 0) {
        displayData.push({ protocol: "其他", count: otherCount });
      }

      const option = {
        title: {
          text: "TCP协议使用分布",
          left: "center",
          textStyle: { fontSize: 14 },
          top: 5,
        },
        tooltip: { trigger: "item", formatter: "{b} : {c} ({d}%)" },
        legend: {
          orient: "vertical",
          left: 10,
          top: 30,
          data: displayData.map((item) => item.protocol),
          type: "scroll",
        },
        series: [
          {
            name: "协议",
            type: "pie",
            radius: ["40%", "70%"],
            center: ["60%", "55%"],
            avoidLabelOverlap: false,
            label: { show: false, position: "center" },
            emphasis: {
              label: { show: true, fontSize: "16", fontWeight: "bold" },
            },
            labelLine: { show: false },
            data: displayData.map((item) => ({
              name: item.protocol,
              value: item.count,
            })),
          },
        ],
      };
      this.tcpProtocolChart.setOption(option);
    },

    // Watcher handlers for re-initialization
    handleDepartmentChangeForCheckTime() {
      if (this.departmentCheckTimeData) this.initCheckTimeChart();
    },
    handleWebTimeRangeChange() {
      if (this.webCategoryData) this.initWebCategoryChart();
    },
    handleDateChangeForNetworkFlow() {
      // Assuming network flow chart might need re-init or update based on selectedDate
      if (this.dailyNetworkTrafficData) this.initNetworkFlowChart();
    },

    handleResize() {
      if (this.checkTimeChart) this.checkTimeChart.resize();
      if (this.workHoursChart) this.workHoursChart.resize();
      if (this.webCategoryChart) this.webCategoryChart.resize();
      if (this.serverAccessChart) this.serverAccessChart.resize();
      if (this.networkFlowChart) this.networkFlowChart.resize();
      if (this.emailFrequencyChart) this.emailFrequencyChart.resize();
      if (this.loginSuccessChart) this.loginSuccessChart.resize();
      if (this.tcpProtocolChart) this.tcpProtocolChart.resize();
    },
  },
};
</script>

<style scoped>
.behavior {
  padding: 20px;
}
.box-card {
  margin-bottom: 20px;
}
.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}
.clearfix:after {
  clear: both;
}
</style>
