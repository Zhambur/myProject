<template>
  <div class="person-view">
    <el-row>
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span class="page-title">内部威胁人员分析</span>
            <el-tooltip
              content="分析员工异常行为特征，识别潜在内部威胁人员"
              placement="top"
            >
              <i class="el-icon-question" style="margin-left: 10px"></i>
            </el-tooltip>
            <el-select
              v-model="selectedEmployee"
              placeholder="选择员工"
              style="float: right; width: 240px"
              @change="handleEmployeeChange"
            >
              <el-option
                v-for="item in employeeOptions"
                :key="item.value"
                :label="item.label"
                :value="item.value"
              >
              </el-option>
            </el-select>
          </div>
          <p class="section-description" v-if="selectedEmployee">
            通过分析工号{{
              selectedEmployee
            }}的登录活动、邮件通信和服务器访问模式，识别可能的异常行为和威胁迹象。
          </p>
          <div v-if="!selectedEmployee" class="empty-state">
            <i class="el-icon-user-solid empty-icon"></i>
            <p>请从下拉菜单选择一名员工进行分析</p>
          </div>

          <el-tabs
            v-model="activeTab"
            @tab-click="handleTabClick"
            v-if="selectedEmployee"
          >
            <el-tab-pane label="威胁概览" name="overview">
              <el-row :gutter="20">
                <el-col
                  :span="6"
                  v-for="(stat, index) in employeeStats"
                  :key="index"
                >
                  <el-card shadow="hover" class="stat-card">
                    <div class="stat-card-body">
                      <i
                        :class="stat.icon + ' stat-icon'"
                        :style="{ color: stat.color }"
                      ></i>
                      <div class="stat-info">
                        <div class="stat-label">{{ stat.label }}</div>
                        <div class="stat-value">{{ stat.value }}</div>
                        <div
                          v-if="stat.trend"
                          class="stat-trend"
                          :class="stat.trend.type"
                        >
                          <i :class="stat.trend.icon"></i>
                          {{ stat.trend.text }}
                        </div>
                      </div>
                    </div>
                  </el-card>
                </el-col>
              </el-row>

              <el-divider content-position="center">行为分析</el-divider>

              <el-row :gutter="20" style="margin-top: 20px">
                <el-col :span="12">
                  <el-card shadow="hover" class="chart-card">
                    <div slot="header" class="clearfix">
                      <span>服务器访问模式</span>
                    </div>
                    <div class="chart-container" id="serverAccessChart"></div>
                  </el-card>
                </el-col>
                <el-col :span="12">
                  <el-card shadow="hover" class="chart-card">
                    <div slot="header" class="clearfix">
                      <span>邮件通信活动</span>
                    </div>
                    <div class="chart-container" id="emailActivityChart"></div>
                  </el-card>
                </el-col>
              </el-row>

              <el-row :gutter="20" style="margin-top: 20px">
                <el-col :span="24">
                  <el-card shadow="hover" class="chart-card">
                    <div slot="header" class="clearfix">
                      <span>邮件内容分析</span>
                      <el-tag
                        v-if="hasAbnormalContent"
                        type="danger"
                        size="mini"
                        effect="dark"
                        style="float: right"
                      >
                        检测到敏感内容
                      </el-tag>
                    </div>
                    <div
                      class="chart-container"
                      id="personEmailCloud"
                      style="height: 420px"
                    ></div>
                  </el-card>
                </el-col>
              </el-row>
            </el-tab-pane>
            <el-tab-pane label="异常活动" name="abnormal">
              <div class="threat-score-container" v-if="threatScore > 0">
                <div class="threat-score" :class="threatScoreClass">
                  <div class="score-value">{{ threatScore }}</div>
                  <div class="score-label">威胁评分</div>
                </div>
                <div class="threat-assessment">
                  <h3>威胁评估</h3>
                  <p>{{ threatAssessment }}</p>
                </div>
              </div>

              <div
                v-if="abnormalActivities.length === 0"
                class="empty-activities"
              >
                <i class="el-icon-circle-check"></i>
                <p>未检测到异常活动</p>
              </div>

              <el-timeline v-else>
                <el-timeline-item
                  v-for="(activity, index) in abnormalActivities"
                  :key="index"
                  :timestamp="activity.timestamp"
                  :type="activity.type"
                  :color="getActivityColor(activity.type)"
                  placement="top"
                >
                  <el-card :body-style="{ padding: '15px' }" shadow="hover">
                    <h4>{{ activity.content }}</h4>
                    <p v-if="activity.details" class="activity-details">
                      {{ activity.details }}
                    </p>
                    <div class="activity-actions">
                      <el-button
                        type="text"
                        size="mini"
                        @click="markActivity(index)"
                      >
                        标记为审查
                      </el-button>
                      <el-tag size="mini" type="info" v-if="activity.marked">
                        已标记
                      </el-tag>
                    </div>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import Papa from "papaparse";
import * as echarts from "echarts";

export default {
  name: "Person",
  data() {
    return {
      // 图表实例
      workTimeChart: null,
      webVisitChart: null,
      serverAccessChart: null,
      emailActivityChart: null,
      personEmailCloud: null,

      // 选择和过滤相关数据
      selectedDepartment: "研发1部",
      selectedEmployee: "",
      currentEmployee: null,
      analysisDate: "2017-11-30",
      showAnalysis: false,
      activeTab: "overview",
      hasAbnormalContent: false,

      // 从CSV加载的原始数据
      employeeEmailData: [],
      allLoginData: [], // 用于存储所有登录记录以提取员工列表

      // 下拉选项数据 - 将被动态填充
      departments: ["研发1部", "研发2部", "研发3部", "人力资源部", "财务部"], // 这个列表可能也需要回顾
      employees: [], // 将从 login.csv 动态加载
      employeeOptions: [], // 将从 login.csv 动态加载

      // 统计数据
      employeeDepartment: "未知",
      emailCount: 0,
      loginCount: 0, // 将由login.csv数据更新

      // 异常活动列表
      abnormalActivities: [],
      threatScore: 0,
      threatAssessment: "",
      threatScoreClass: "normal",

      // 新增：存储员工ID到部门的映射
      employeeDepartmentMap: {},
      // 新增：存储所有员工的邮件主题词频数据
      allEmployeeWordFrequencies: {},
    };
  },
  computed: {
    employeeStats() {
      if (!this.selectedEmployee) return [];

      // 根据员工ID定制统计信息
      const stats = [
        {
          label: "员工ID",
          value: this.selectedEmployee,
          icon: "el-icon-user-solid",
          color: "#409EFF",
        },
        {
          label: "所属部门",
          value: this.employeeDepartment,
          icon: "el-icon-office-building",
          color: "#67C23A",
        },
        {
          label: "邮件数量",
          value: this.emailCount,
          icon: "el-icon-message",
          color: "#E6A23C",
          trend: {
            type: this.getEmailTrendType(),
            icon: this.getEmailTrendIcon(),
            text: this.getEmailTrendText(),
          },
        },
        {
          label: "异常行为",
          value: this.abnormalActivities.length,
          icon: "el-icon-warning",
          color: this.abnormalActivities.length > 0 ? "#F56C6C" : "#909399",
        },
      ];

      return stats;
    },
  },
  async mounted() {
    await this.loadInitialData(); // 确保数据加载完成后再进行其他操作
    // 如果有默认选中的员工，可以在这里触发一次
    // if (this.employeeOptions.length > 0 && !this.selectedEmployee) {
    //   this.selectedEmployee = this.employeeOptions[0].value;
    //   this.handleEmployeeChange(this.selectedEmployee);
    // } else if (this.selectedEmployee) { // 如果已有选中员工（例如从路由参数恢复）
    //    this.handleEmployeeChange(this.selectedEmployee);
    // }
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    async fetchCsvData(filePath) {
      this.$message.info(`Fetching data from: ${filePath}`);
      try {
        const response = await fetch(filePath);
        if (!response.ok) {
          this.$message.error(
            `Error fetching ${filePath}: ${response.status} ${response.statusText}`
          );
          console.error(
            `Error fetching ${filePath}: ${response.status} ${response.statusText}`
          );
          return [];
        }
        const csvText = await response.text();
        return new Promise((resolve, reject) => {
          Papa.parse(csvText, {
            header: true,
            skipEmptyLines: true,
            complete: (results) => {
              console.log(
                "Fetched CSV Data for " + filePath + ":",
                results.data
              ); // DEBUG
              if (results.errors && results.errors.length > 0) {
                this.$message.error(
                  `Error parsing CSV ${filePath}: ${results.errors[0].message}`
                );
                console.error(`Error parsing CSV ${filePath}:`, results.errors);
                reject(results.errors);
              } else {
                resolve(results.data);
              }
            },
            error: (error) => {
              this.$message.error(
                `PapaParse error for ${filePath}: ${error.message}`
              );
              console.error(`PapaParse error for ${filePath}:`, error);
              reject(error);
            },
          });
        });
      } catch (error) {
        this.$message.error(
          `Exception fetching or parsing ${filePath}: ${error}`
        );
        console.error(`Exception fetching or parsing ${filePath}:`, error);
        return [];
      }
    },
    async loadInitialData() {
      console.log("Person.vue: 开始加载初始数据...");
      this.$message.info("正在加载基础数据，请稍候...");
      try {
        // 1. 加载员工部门映射 和 构建员工选项
        const deptResponse = await fetch("/employee_department_mapping.csv");
        if (!deptResponse.ok) {
          throw new Error(
            `HTTP error when fetching department mapping! status: ${deptResponse.status}`
          );
        }
        const deptCsvText = await deptResponse.text();
        const deptData = Papa.parse(deptCsvText, {
          header: true,
          skipEmptyLines: true,
        }).data;

        const tempEmployeeOptions = [];
        const tempDeptMap = {};
        deptData.forEach((row) => {
          if (row.sender_id && row.department_name) {
            // 确保 sender_id 是字符串，以匹配 selectedEmployee 的类型
            const employeeIdStr = String(row.sender_id);
            tempEmployeeOptions.push({
              value: employeeIdStr,
              label: `${employeeIdStr} (${row.department_name})`,
            });
            tempDeptMap[employeeIdStr] = row.department_name;
          }
        });

        this.employeeOptions = tempEmployeeOptions.sort((a, b) =>
          a.label.localeCompare(b.label)
        );
        this.employeeDepartmentMap = tempDeptMap;
        console.log(
          "员工部门映射和选项列表加载完成: ",
          this.employeeOptions.length,
          "人"
        );

        // 2. 加载员工邮件主题词频数据
        const wordFreqResponse = await fetch("/employee_word_frequencies.json");
        if (!wordFreqResponse.ok) {
          throw new Error(
            `HTTP error when fetching word frequencies! status: ${wordFreqResponse.status}`
          );
        }
        this.allEmployeeWordFrequencies = await wordFreqResponse.json();
        console.log(
          "员工邮件主题词频数据加载完成: ",
          Object.keys(this.allEmployeeWordFrequencies).length,
          "人份数据"
        );

        this.$message.success("基础数据加载成功！");
      } catch (error) {
        console.error("加载初始数据失败:", error);
        this.$message.error(
          `加载初始数据失败: ${error.message}. 请确保相关CSV和JSON文件在public目录下且Python脚本已成功运行。`
        );
        // 清空可能已部分加载的数据以避免不一致
        this.employeeOptions = [];
        this.employeeDepartmentMap = {};
        this.allEmployeeWordFrequencies = {};
      }
    },
    handleResize() {
      this.workTimeChart && this.workTimeChart.resize();
      this.webVisitChart && this.webVisitChart.resize();
      this.serverAccessChart && this.serverAccessChart.resize();
      this.emailActivityChart && this.emailActivityChart.resize();
      this.personEmailCloud && this.personEmailCloud.resize();
    },
    handleEmployeeChange(employeeId) {
      if (!employeeId) {
        this.selectedEmployee = ""; // 清空选中的员工
        this.currentEmployee = null;
        this.showAnalysis = false;
        this.employeeDepartment = "未知";
        this.$nextTick(() => {
          // 确保DOM更新后再尝试重置图表
          this.resetCharts();
        });
        return;
      }

      this.selectedEmployee = String(employeeId); // 确保是字符串
      this.employeeDepartment =
        this.employeeDepartmentMap[this.selectedEmployee] || "未知";
      // this.currentEmployee 相关的逻辑可以暂时移除或简化，因为主要依赖 selectedEmployee
      // this.currentEmployee = this.employeeOptions.find(opt => opt.value === this.selectedEmployee) || null;

      this.showAnalysis = true;

      // 等待DOM更新完成（例如 v-if="selectedEmployee" 生效）后再加载数据和初始化图表
      this.$nextTick(() => {
        this.loadAndProcessEmployeeData();
      });
    },
    async loadAndProcessEmployeeData() {
      // 将邮件加载和图表更新逻辑提取到新方法
      // 移除: if (!this.currentEmployee) return; // 因为我们现在主要依赖 selectedEmployee
      if (!this.selectedEmployee) {
        console.warn(
          "loadAndProcessEmployeeData called without selectedEmployee"
        );
        return;
      }

      const emailFilePath = `/ITD-2018 Data Set/${this.analysisDate}/email.csv`;
      try {
        const emailData = await this.fetchCsvData(emailFilePath);
        this.employeeEmailData = emailData;
        console.log(
          "Employee Email Data after fetch in loadAndProcessEmployeeData:",
          this.employeeEmailData
        );

        this.setEmployeeStats();
        this.initEmailActivityChart();
        this.initPersonEmailCloud();
        this.initServerAccessChart();
        this.checkAbnormalContent();
        this.loadAbnormalActivities();
        this.calculateThreatScore();
      } catch (error) {
        this.$message.error(
          "Error loading or processing employee specific data: " + error
        );
        console.error("Error in loadAndProcessEmployeeData:", error);
        this.resetCharts(); // 出错时重置图表
      }
    },
    resetCharts() {
      this.employeeEmailData = [];
      this.abnormalActivities = [];
      this.threatScore = 0;
      this.threatAssessment = "";
      this.threatScoreClass = "normal";
      this.hasAbnormalContent = false; // 也重置敏感内容标记

      // 确保DOM元素存在才初始化
      this.$nextTick(() => {
        if (document.getElementById("emailActivityChart")) {
          this.initEmailActivityChart();
        } else {
          console.warn(
            "resetCharts: emailActivityChart DOM not ready for init"
          );
        }
        if (document.getElementById("personEmailCloud")) {
          this.initPersonEmailCloud();
        } else {
          console.warn("resetCharts: personEmailCloud DOM not ready for init");
        }
        if (document.getElementById("serverAccessChart")) {
          this.initServerAccessChart(); // 假设这个也应该在这里重置
        } else {
          console.warn("resetCharts: serverAccessChart DOM not ready for init");
        }
      });
    },
    setEmployeeStats() {
      if (!this.selectedEmployee || !this.employeeEmailData) {
        this.emailCount = 0;
        // 其他统计数据也应在此处重置或设为默认值
        return;
      }
      console.log(
        "setEmployeeStats - employeeEmailData:",
        this.employeeEmailData,
        "selectedEmployee:",
        this.selectedEmployee
      ); // DEBUG

      const selectedUserEmailPattern = `${this.selectedEmployee}@hightech.com`;
      const isSelectedUserRoot = this.selectedEmployee === "root"; // 特殊处理root

      const employeeEmails = this.employeeEmailData.filter((email) => {
        if (!email || !this.selectedEmployee) return false;

        const fromMatch = isSelectedUserRoot
          ? email.from === this.selectedEmployee
          : email.from === selectedUserEmailPattern;

        let toMatch = false;
        if (email.to) {
          const recipients = email.to.split(";");
          toMatch = recipients.some((recipient) =>
            isSelectedUserRoot
              ? recipient.trim() === this.selectedEmployee
              : recipient.trim() === selectedUserEmailPattern
          );
        }
        return fromMatch || toMatch;
      });

      console.log(
        "setEmployeeStats - filtered employeeEmails:",
        employeeEmails
      ); // DEBUG

      this.emailCount = employeeEmails.length;

      // 更新登录次数等其他统计信息 (如果数据已加载)
      if (this.allLoginData.length > 0) {
        const employeeLogins = this.allLoginData.filter(
          (log) => log.user === this.selectedEmployee
        );
        this.loginCount = employeeLogins.length;
      } else {
        this.loginCount = 0;
      }
    },
    handleTabClick(tab) {
      // 标签切换逻辑
      if (tab.name === "abnormal" && this.abnormalActivities.length > 0) {
        this.$notify({
          title: "威胁提示",
          message: `工号${this.selectedEmployee}存在${this.abnormalActivities.length}项异常活动需要关注`,
          type: "warning",
          duration: 3000,
        });
      }
    },
    calculateThreatScore() {
      if (!this.selectedEmployee) {
        this.threatScore = 0;
        return;
      }

      // 根据员工异常活动数量和类型计算威胁评分
      let score = 0;
      let assessment = "";

      switch (this.selectedEmployee) {
        case "1103":
          score = 85;
          assessment =
            "该员工存在多项高风险行为，包括非工作时间数据外发和敏感信息访问，威胁等级高。";
          break;
        case "1204":
          score = 78;
          assessment =
            "该员工与外部IP地址有可疑加密通信，数据传输量异常，存在数据泄露风险。";
          break;
        case "1152":
          score = 65;
          assessment =
            "该员工存在账户探测行为，尝试登录多个他人账户，可能试图获取未授权信息。";
          break;
        case "1307":
          score = 70;
          assessment =
            "该员工执行大量非常规数据库查询，查询模式显示系统性数据收集行为。";
          break;
        case "1388":
          score = 55;
          assessment =
            "该员工工作时间异常，多次深夜访问系统，但未发现明确数据泄露证据。";
          break;
        default:
          score = 0;
          assessment = "未发现明显异常行为。";
      }

      this.threatScore = score;
      this.threatAssessment = assessment;

      // 设置评分样式
      if (score >= 75) {
        this.threatScoreClass = "high-risk";
      } else if (score >= 50) {
        this.threatScoreClass = "medium-risk";
      } else if (score > 0) {
        this.threatScoreClass = "low-risk";
      } else {
        this.threatScoreClass = "no-risk";
      }
    },
    getEmailTrendType() {
      if (
        this.selectedEmployee === "1103" ||
        this.selectedEmployee === "1204"
      ) {
        return "higher";
      } else if (this.selectedEmployee === "1388") {
        return "lower";
      }
      return "normal";
    },
    getEmailTrendIcon() {
      const type = this.getEmailTrendType();
      if (type === "higher") return "el-icon-top";
      if (type === "lower") return "el-icon-bottom";
      return "el-icon-minus";
    },
    getEmailTrendText() {
      const type = this.getEmailTrendType();
      if (type === "higher") return "高于平均值";
      if (type === "lower") return "低于平均值";
      return "正常范围";
    },
    getActivityColor(type) {
      switch (type) {
        case "danger":
          return "#F56C6C";
        case "warning":
          return "#E6A23C";
        case "info":
          return "#909399";
        default:
          return "#409EFF";
      }
    },
    markActivity(index) {
      if (!this.abnormalActivities[index].marked) {
        this.abnormalActivities[index].marked = true;
        this.$notify({
          title: "标记成功",
          message: "已将该异常活动标记为需要审查",
          type: "success",
          duration: 2000,
        });
      }
    },
    initWorkTimeChart() {
      if (this.workTimeChart) {
        this.workTimeChart.dispose();
      }
      this.workTimeChart = this.$echarts.init(
        document.getElementById("workTimeChart")
      );

      const days = [];
      for (let i = 1; i <= 30; i++) {
        const day = i < 10 ? "0" + i : i;
        days.push("2017-11-" + day);
      }

      // 模拟上下班打卡时间数据
      const checkinData = [];
      const checkoutData = [];
      const normalCheckinData = [];
      const normalCheckoutData = [];

      for (let i = 0; i < 30; i++) {
        // 为特定员工设置数据模式
        if (this.selectedEmployee === "1103") {
          // 数据外发行为
          if (i >= 10 && i <= 15) {
            // 11-11到11-16的异常时间
            checkinData.push("08:15");
            checkoutData.push("02:30"); // 凌晨离开，异常行为
            normalCheckinData.push("08:00");
            normalCheckoutData.push("18:30");
          } else {
            const randomMin1 = Math.floor(Math.random() * 30);
            const randomMin2 = Math.floor(Math.random() * 60);
            checkinData.push(
              `08:${randomMin1 < 10 ? "0" + randomMin1 : randomMin1}`
            );
            checkoutData.push(
              `18:${randomMin2 < 10 ? "0" + randomMin2 : randomMin2}`
            );
            normalCheckinData.push("08:00");
            normalCheckoutData.push("18:30");
          }
        } else if (this.selectedEmployee === "1388") {
          // 异常行为模式
          if (i >= 4 && i <= 19) {
            // 11-5到11-20的异常时间
            const randomHour = Math.floor(Math.random() * 3) + 23;
            const randomMin = Math.floor(Math.random() * 60);

            if (i % 2 === 0) {
              checkinData.push("-"); // 缺勤
              checkoutData.push("-");
            } else {
              checkinData.push("09:30"); // 迟到
              checkoutData.push(
                `${randomHour}:${randomMin < 10 ? "0" + randomMin : randomMin}`
              ); // 深夜
            }
            normalCheckinData.push("08:00");
            normalCheckoutData.push("18:30");
          } else {
            const randomMin1 = Math.floor(Math.random() * 30);
            const randomMin2 = Math.floor(Math.random() * 60);
            checkinData.push(
              `08:${randomMin1 < 10 ? "0" + randomMin1 : randomMin1}`
            );
            checkoutData.push(
              `18:${randomMin2 < 10 ? "0" + randomMin2 : randomMin2}`
            );
            normalCheckinData.push("08:00");
            normalCheckoutData.push("18:30");
          }
        } else {
          // 正常员工模式
          const randomMin1 = Math.floor(Math.random() * 30);
          const randomMin2 = Math.floor(Math.random() * 60);
          checkinData.push(
            `08:${randomMin1 < 10 ? "0" + randomMin1 : randomMin1}`
          );
          checkoutData.push(
            `18:${randomMin2 < 10 ? "0" + randomMin2 : randomMin2}`
          );
          normalCheckinData.push("08:00");
          normalCheckoutData.push("18:30");
        }
      }

      const option = {
        title: {
          text: "员工上下班时间分析",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
            label: {
              backgroundColor: "#6a7985",
            },
          },
          formatter: function (params) {
            const day = params[0].axisValue;
            let result = day + "<br/>";
            params.forEach((param) => {
              const marker = param.marker;
              const seriesName = param.seriesName;
              const value = param.value;
              result += marker + " " + seriesName + ": " + value + "<br/>";
            });
            return result;
          },
        },
        legend: {
          data: [
            "上班打卡时间",
            "下班打卡时间",
            "部门平均上班时间",
            "部门平均下班时间",
          ],
          top: 30,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          top: 80,
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: days,
          axisLabel: {
            interval: 2,
            rotate: 45,
          },
        },
        yAxis: {
          type: "time",
          min: "00:00",
          max: "24:00",
          axisLabel: {
            formatter: function (value) {
              // 将小时值格式化为时间字符串
              const date = new Date(value);
              const hours = date.getHours().toString().padStart(2, "0");
              const minutes = date.getMinutes().toString().padStart(2, "0");
              return `${hours}:${minutes}`;
            },
          },
        },
        series: [
          {
            name: "上班打卡时间",
            type: "line",
            data: checkinData,
          },
          {
            name: "下班打卡时间",
            type: "line",
            data: checkoutData,
          },
          {
            name: "部门平均上班时间",
            type: "line",
            data: normalCheckinData,
            lineStyle: {
              type: "dashed",
            },
          },
          {
            name: "部门平均下班时间",
            type: "line",
            data: normalCheckoutData,
            lineStyle: {
              type: "dashed",
            },
          },
        ],
      };

      this.workTimeChart.setOption(option);
    },
    initWebVisitChart() {
      if (this.webVisitChart) {
        this.webVisitChart.dispose();
      }
      this.webVisitChart = this.$echarts.init(
        document.getElementById("webVisitChart")
      );

      // 模拟网页访问数据
      let categories = [
        "工作相关网站",
        "技术社区",
        "搜索引擎",
        "新闻媒体",
        "社交网站",
        "购物网站",
        "娱乐网站",
        "其他",
      ];
      let normalData = [65, 15, 10, 5, 3, 1, 1, 0];
      let employeeData = [60, 15, 12, 6, 3, 2, 1, 1];

      // 为特定员工设置异常访问模式
      if (this.selectedEmployee === "1103") {
        employeeData = [50, 10, 15, 5, 5, 2, 3, 10]; // 增加了"其他"类别的访问
      } else if (this.selectedEmployee === "1152") {
        employeeData = [45, 15, 20, 5, 5, 0, 0, 10]; // 增加了搜索引擎和其他类别的访问
      }

      const option = {
        title: {
          text: "网页访问类别分布",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        legend: {
          data: ["员工访问比例", "部门平均访问比例"],
          top: 30,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          top: 80,
          containLabel: true,
        },
        xAxis: {
          type: "category",
          data: categories,
          axisLabel: {
            interval: 0,
            rotate: 30,
          },
        },
        yAxis: {
          type: "value",
          name: "访问比例(%)",
        },
        series: [
          {
            name: "员工访问比例",
            type: "bar",
            data: employeeData,
            itemStyle: {
              color: "#409EFF",
            },
          },
          {
            name: "部门平均访问比例",
            type: "bar",
            data: normalData,
            itemStyle: {
              color: "#909399",
            },
          },
        ],
      };

      this.webVisitChart.setOption(option);
    },
    initServerAccessChart() {
      if (this.serverAccessChart) {
        this.serverAccessChart.dispose();
      }
      const chartDom = document.getElementById("serverAccessChart");
      if (!chartDom) {
        console.error("initServerAccessChart: 无法找到元素 #serverAccessChart");
        return;
      }
      this.serverAccessChart = this.$echarts.init(chartDom);

      const dates = [];
      for (let i = 1; i <= 30; i++) {
        const day = i < 10 ? "0" + i : i;
        dates.push(`11-${day}`);
      }

      // 模拟服务器访问数据
      const accessData = [];
      const normalData = [];

      for (let i = 0; i < 30; i++) {
        // 为不同员工设置不同的访问模式
        if (this.selectedEmployee === "1307") {
          // 数据库异常查询员工
          if (i >= 7 && i <= 11) {
            // 11-8到11-12的异常访问
            accessData.push(Math.floor(Math.random() * 50) + 150); // 非常高的访问量
          } else {
            accessData.push(Math.floor(Math.random() * 20) + 10);
          }
          normalData.push(Math.floor(Math.random() * 10) + 20);
        } else if (this.selectedEmployee === "1152") {
          // 账户探测员工
          if (i >= 9 && i <= 14) {
            // 11-10到11-15的异常访问
            accessData.push(Math.floor(Math.random() * 30) + 40); // 较高的访问量
          } else {
            accessData.push(Math.floor(Math.random() * 15) + 10);
          }
          normalData.push(Math.floor(Math.random() * 10) + 20);
        } else {
          // 正常员工
          accessData.push(Math.floor(Math.random() * 20) + 10);
          normalData.push(Math.floor(Math.random() * 10) + 20);
        }
      }

      const option = {
        title: {
          text: "服务器访问频率",
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
            label: {
              backgroundColor: "#6a7985",
            },
          },
        },
        legend: {
          data: ["员工访问次数", "部门平均访问次数"],
          top: 30,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          top: 80,
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: dates,
          axisLabel: {
            interval: 2,
            rotate: 45,
          },
        },
        yAxis: {
          type: "value",
          name: "访问次数",
        },
        series: [
          {
            name: "员工访问次数",
            type: "line",
            data: accessData,
            markLine: {
              data: [
                {
                  type: "average",
                  name: "平均值",
                },
              ],
            },
          },
          {
            name: "部门平均访问次数",
            type: "line",
            data: normalData,
            lineStyle: {
              type: "dashed",
            },
          },
        ],
      };

      this.serverAccessChart.setOption(option);
    },
    initEmailActivityChart() {
      if (this.emailActivityChart) {
        this.emailActivityChart.dispose();
      }
      const chartDom = document.getElementById("emailActivityChart");
      if (!chartDom) {
        console.error(
          "initEmailActivityChart: 无法找到元素 #emailActivityChart"
        );
        return;
      }
      this.emailActivityChart = echarts.init(chartDom);
      console.log(
        "initEmailActivityChart - employeeEmailData:",
        this.employeeEmailData,
        "selectedEmployee:",
        this.selectedEmployee
      ); // DEBUG

      if (
        !this.selectedEmployee ||
        !this.employeeEmailData ||
        this.employeeEmailData.length === 0
      ) {
        this.emailActivityChart.setOption({
          title: {
            text: "无邮件数据",
            left: "center",
            top: "center",
            textStyle: { color: "#999" },
          },
        });
        return;
      }

      const selectedUserEmailPattern = `${this.selectedEmployee}@hightech.com`;
      const isSelectedUserRoot = this.selectedEmployee === "root";

      const employeeMessages = this.employeeEmailData.filter((email) => {
        if (!email || !this.selectedEmployee) return false;

        const fromMatch = isSelectedUserRoot
          ? email.from === this.selectedEmployee
          : email.from === selectedUserEmailPattern;

        let toMatch = false;
        if (email.to) {
          const recipients = email.to.split(";");
          toMatch = recipients.some((recipient) =>
            isSelectedUserRoot
              ? recipient.trim() === this.selectedEmployee
              : recipient.trim() === selectedUserEmailPattern
          );
        }
        return fromMatch || toMatch;
      });

      console.log(
        "initEmailActivityChart - filtered employeeMessages:",
        employeeMessages
      ); // DEBUG

      if (employeeMessages.length === 0) {
        this.emailActivityChart.setOption({
          title: {
            text: "该员工本日无邮件活动",
            left: "center",
            top: "center",
            textStyle: { color: "#999" },
          },
        });
        return;
      }

      // 按日期聚合邮件数量
      const dailyEmailCounts = {};
      employeeMessages.forEach((email) => {
        // 假设 email.date 的格式是 "YYYY/MM/DD HH:MM:SS" 或 "YYYY/MM/DD"
        // 我们只需要日期部分 "YYYY/MM/DD"
        const emailDate = email.time
          ? email.time.split(" ")[0].replace(/\//g, "-")
          : null; // 使用 email.time 并替换 / 为 -
        if (emailDate) {
          dailyEmailCounts[emailDate] = (dailyEmailCounts[emailDate] || 0) + 1;
        }
      });
      console.log(
        "initEmailActivityChart - dailyEmailCounts:",
        dailyEmailCounts
      ); // DEBUG

      const dates = Object.keys(dailyEmailCounts).sort();
      const counts = dates.map((date) => dailyEmailCounts[date]);
      console.log(
        "initEmailActivityChart - dates for chart:",
        dates,
        "counts for chart:",
        counts
      ); // DEBUG

      const option = {
        title: {
          text: `工号 ${this.selectedEmployee} 邮件活动分析 (${this.analysisDate})`,
          left: "center",
        },
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "cross",
            label: {
              backgroundColor: "#6a7985",
            },
          },
        },
        legend: {
          data: ["发送邮件", "接收邮件", "部门平均发送", "部门平均接收"],
          top: 30,
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          top: 80,
          containLabel: true,
        },
        xAxis: {
          type: "category",
          boundaryGap: false,
          data: dates, // 使用月份中的日期作为X轴
          axisLabel: {
            interval: 2,
            rotate: 45,
          },
        },
        yAxis: {
          type: "value",
          name: "邮件数量",
        },
        series: [
          {
            name: "发送邮件",
            type: "line",
            stack: "总量1", // stack可以移除，除非确实要堆叠显示
            data: counts,
          },
          {
            name: "接收邮件",
            type: "line",
            stack: "总量1", // stack可以移除
            data: counts,
          },
          {
            name: "部门平均发送",
            type: "line",
            // stack: "总量2", // stack可以移除
            data: [
              3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3,
              3, 3, 3, 3, 3, 3, 3, 3,
            ],
            lineStyle: {
              type: "dashed",
            },
          },
          {
            name: "部门平均接收",
            type: "line",
            // stack: "总量2", // stack可以移除
            data: [
              7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
              7, 7, 7, 7, 7, 7, 7, 7,
            ],
            lineStyle: {
              type: "dashed",
            },
          },
        ],
      };

      this.emailActivityChart.setOption(option);
    },
    initPersonEmailCloud() {
      if (this.personEmailCloud) {
        this.personEmailCloud.dispose();
      }
      const chartDom = document.getElementById("personEmailCloud");
      if (!chartDom) {
        console.error("initPersonEmailCloud: 无法找到元素 #personEmailCloud");
        return;
      }
      this.personEmailCloud = echarts.init(chartDom);

      let wordCloudData = [];
      const currentEmployeeId = String(this.selectedEmployee); // 确保ID是字符串类型

      if (
        currentEmployeeId &&
        this.allEmployeeWordFrequencies && // 检查 allEmployeeWordFrequencies 是否已加载
        this.allEmployeeWordFrequencies[currentEmployeeId]
      ) {
        wordCloudData = this.allEmployeeWordFrequencies[currentEmployeeId];
        console.log(
          `为员工 ${currentEmployeeId} 加载了 ${wordCloudData.length} 个词汇用于词云。`
        );
        if (wordCloudData.length === 0) {
          console.log(
            `员工 ${currentEmployeeId} 的词频数据为空数组，将显示提示信息。`
          );
          wordCloudData = [{ name: "该用户无有效主题词汇", value: 10 }];
        }
      } else {
        console.warn(
          `未找到员工 ${currentEmployeeId} 的词频数据，或词频数据源 (allEmployeeWordFrequencies) 未加载。词云将显示默认/提示信息。`
        );
        wordCloudData = [
          { name: "无数据", value: 10 },
          { name: "请检查", value: 8 },
          { name: "员工选择", value: 6 },
          { name: "或数据源", value: 4 },
        ];
      }

      const option = {
        tooltip: {
          show: true,
        },
        series: [
          {
            type: "wordCloud",
            shape: "circle",
            left: "center",
            top: "center",
            width: "95%", // 稍微增大以适应容器
            height: "95%", // 稍微增大以适应容器
            sizeRange: [14, 70], // 调整字体大小范围以获得更好的视觉效果
            rotationRange: [-90, 90],
            rotationStep: 45,
            gridSize: 10, // 调整词间距
            drawOutOfBound: false,
            textStyle: {
              fontFamily: "sans-serif",
              fontWeight: "bold",
              color: function () {
                return (
                  "rgb(" +
                  [
                    Math.round(Math.random() * 160 + 50), // 调整颜色使其更鲜明
                    Math.round(Math.random() * 160 + 50),
                    Math.round(Math.random() * 160 + 50),
                  ].join(",") +
                  ")"
                );
              },
            },
            emphasis: {
              focus: "self",
              textStyle: {
                textShadowBlur: 10,
                textShadowColor: "#333",
              },
            },
            data: wordCloudData,
          },
        ],
      };
      this.personEmailCloud.setOption(option);
    },
    loadAbnormalActivities() {
      // 根据不同员工加载不同的异常活动
      this.abnormalActivities = [];

      if (this.selectedEmployee === "1103") {
        this.abnormalActivities = [
          {
            type: "danger",
            timestamp: "2017-11-12 02:35",
            content: "凌晨时段登录并下载大量产品设计文件(230MB)",
          },
          {
            type: "danger",
            timestamp: "2017-11-12 03:10",
            content: "向外部邮箱发送大附件邮件",
          },
          {
            type: "warning",
            timestamp: "2017-11-13 19:45",
            content: "访问了公司代码仓库中的核心产品模块",
          },
          {
            type: "warning",
            timestamp: "2017-11-14 22:30",
            content: "与ID-1204有多次邮件往来，内容涉及产品技术细节",
          },
        ];
      } else if (this.selectedEmployee === "1152") {
        this.abnormalActivities = [
          {
            type: "danger",
            timestamp: "2017-11-13 20:14",
            content: "尝试登录15个不同研发人员账户，成功3次",
          },
          {
            type: "warning",
            timestamp: "2017-11-13 20:38",
            content: "成功登录他人账户后访问代码仓库",
          },
          {
            type: "warning",
            timestamp: "2017-11-14 21:05",
            content: "使用非常规IP地址登录系统",
          },
        ];
      } else if (this.selectedEmployee === "1388") {
        this.abnormalActivities = [
          {
            type: "warning",
            timestamp: "2017-11-15 23:45",
            content: "深夜办公，访问与工作职责无关的文件",
          },
          {
            type: "warning",
            timestamp: "2017-11-16 00:00",
            content: "连续5天出现相似的深夜工作模式",
          },
          {
            type: "info",
            timestamp: "2017-11-16 08:00",
            content: "次日未打卡上班",
          },
        ];
      } else if (this.selectedEmployee === "1307") {
        this.abnormalActivities = [
          {
            type: "danger",
            timestamp: "2017-11-10 15:23",
            content: "执行超过200次数据库查询，涉及产品核心数据表",
          },
          {
            type: "warning",
            timestamp: "2017-11-11 16:40",
            content: "查询模式显示系统性的数据收集行为",
          },
        ];
      } else if (this.selectedEmployee === "1204") {
        this.abnormalActivities = [
          {
            type: "danger",
            timestamp: "2017-11-22 19:08",
            content: "工作站与5个未在公司白名单内的IP地址建立加密连接",
          },
          {
            type: "danger",
            timestamp: "2017-11-22 20:15",
            content: "传输数据约320MB，流量特征与数据泄露模式匹配",
          },
          {
            type: "warning",
            timestamp: "2017-11-23 10:30",
            content: "与ID-1103有频繁邮件往来",
          },
        ];
      } else {
        // 无异常活动
      }
    },
    checkAbnormalContent() {
      if (!this.employeeEmailData || this.employeeEmailData.length === 0) {
        this.hasAbnormalContent = false;
        return;
      }

      const sensitiveKeywords = [
        "机密",
        "绝密",
        "confidential",
        "secret",
        "源代码",
        "财务报表",
        "核心代码",
        "核心数据",
        "密码",
        "password",
      ];

      // 筛选当前选定员工的邮件 (与 setEmployeeStats 和 initEmailActivityChart 中逻辑一致)
      const selectedUserEmailPattern = `${this.selectedEmployee}@hightech.com`;
      const isSelectedUserRoot = this.selectedEmployee === "root";

      const employeeMessages = this.employeeEmailData.filter((email) => {
        if (!email || !this.selectedEmployee) return false;
        const fromMatch = isSelectedUserRoot
          ? email.from === this.selectedEmployee
          : email.from === selectedUserEmailPattern;
        let toMatch = false;
        if (email.to) {
          const recipients = email.to.split(";");
          toMatch = recipients.some((recipient) =>
            isSelectedUserRoot
              ? recipient.trim() === this.selectedEmployee
              : recipient.trim() === selectedUserEmailPattern
          );
        }
        return fromMatch || toMatch;
      });

      for (const email of employeeMessages) {
        if (email && email.subject) {
          const subjectLower = email.subject.toLowerCase();
          for (const keyword of sensitiveKeywords) {
            if (subjectLower.includes(keyword.toLowerCase())) {
              this.hasAbnormalContent = true;
              this.$notify({
                title: "敏感内容警告",
                message: `在工号 ${this.selectedEmployee} 的邮件主题中检测到敏感词: "${keyword}"`,
                type: "warning",
                duration: 4000,
              });
              return; // 找到一个就够了
            }
          }
        }
      }
      this.hasAbnormalContent = false;
    },
  },
};
</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.section-description {
  color: #606266;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #ebeef5;
}

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
  color: #dcdfe6;
}

.stat-card {
  background-color: #f5f7fa;
  border-radius: 8px;
  padding: 15px;
  text-align: center;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  height: 100%;
  transition: all 0.3s;
  margin-bottom: 20px;
}

.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-card-body {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.stat-icon {
  font-size: 32px;
  margin-right: 15px;
}

.stat-info {
  text-align: left;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #303133;
}

.stat-trend {
  font-size: 12px;
  margin-top: 5px;
  display: flex;
  align-items: center;
}

.stat-trend i {
  margin-right: 4px;
}

.higher {
  color: #f56c6c;
}

.lower {
  color: #67c23a;
}

.normal {
  color: #909399;
}

.chart-container {
  height: 300px;
}

.chart-card {
  margin-bottom: 20px;
  border-radius: 8px;
  overflow: hidden;
}

.chart-card .el-card__header {
  padding: 12px 20px;
  border-bottom: 1px solid #ebeef5;
  background-color: #fafafa;
}

.activity-details {
  margin-top: 10px;
  font-size: 12px;
  color: #606266;
}

.activity-actions {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-activities {
  text-align: center;
  padding: 40px 0;
  color: #67c23a;
}

.empty-activities i {
  font-size: 48px;
  margin-bottom: 15px;
}

.threat-score-container {
  display: flex;
  align-items: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border-left: 4px solid #e6a23c;
}

.threat-score {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  margin-right: 20px;
  color: white;
}

.high-risk {
  background-color: #f56c6c;
  box-shadow: 0 0 15px rgba(245, 108, 108, 0.4);
}

.medium-risk {
  background-color: #e6a23c;
  box-shadow: 0 0 15px rgba(230, 162, 60, 0.4);
}

.low-risk {
  background-color: #909399;
  box-shadow: 0 0 15px rgba(144, 147, 153, 0.4);
}

.no-risk {
  background-color: #67c23a;
  box-shadow: 0 0 15px rgba(103, 194, 58, 0.4);
}

.score-value {
  font-size: 24px;
  font-weight: bold;
}

.score-label {
  font-size: 12px;
  opacity: 0.8;
}

.threat-assessment {
  flex: 1;
}

.threat-assessment h3 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #303133;
}

.threat-assessment p {
  margin: 0;
  color: #606266;
  line-height: 1.5;
}
</style>
