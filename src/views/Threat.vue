<template>
  <div class="threat">
    <el-row>
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>威胁情报分析</span>
            <el-tooltip
              class="item"
              effect="dark"
              content="检测并分析可能存在的内部威胁事件，探究事件间的关联性"
              placement="top"
            >
              <i class="el-icon-question" style="margin-left: 10px"></i>
            </el-tooltip>
          </div>
          <p>
            通过对多维数据的关联分析，我们发现了多起可疑行为并关联成威胁情报，这些情报可能表明有内部人员试图获取或泄露公司核心产品信息。
          </p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>威胁事件关联图</span>
          </div>
          <div
            id="threatRelationChart"
            style="width: 100%; height: 600px"
          ></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>威胁事件列表</span>
          </div>
          <el-table
            :data="threatEvents"
            style="width: 100%"
            max-height="550"
            @row-click="handleEventSelect"
          >
            <el-table-column
              prop="id"
              label="编号"
              width="60"
            ></el-table-column>
            <el-table-column prop="type" label="类型" width="100">
              <template slot-scope="scope">
                <el-tag :type="getEventTypeTag(scope.row.type)">{{
                  scope.row.type
                }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="date"
              label="日期"
              width="100"
            ></el-table-column>
            <el-table-column prop="description" label="描述"></el-table-column>
            <el-table-column prop="level" label="风险等级" width="80">
              <template slot-scope="scope">
                <el-tag :type="getRiskLevelTag(scope.row.level)">{{
                  scope.row.level
                }}</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="box-card" v-if="selectedEvent">
          <div slot="header" class="clearfix">
            <span>事件详情: {{ selectedEvent.description }}</span>
          </div>
          <el-row :gutter="20">
            <el-col :span="12">
              <h4>事件信息</h4>
              <el-descriptions :column="1" border>
                <el-descriptions-item label="事件ID">{{
                  selectedEvent.id
                }}</el-descriptions-item>
                <el-descriptions-item label="类型">{{
                  selectedEvent.type
                }}</el-descriptions-item>
                <el-descriptions-item label="日期">{{
                  selectedEvent.date
                }}</el-descriptions-item>
                <el-descriptions-item label="时间">{{
                  selectedEvent.time
                }}</el-descriptions-item>
                <el-descriptions-item label="相关用户">{{
                  selectedEvent.user
                }}</el-descriptions-item>
                <el-descriptions-item label="风险等级">
                  <el-tag :type="getRiskLevelTag(selectedEvent.level)">{{
                    selectedEvent.level
                  }}</el-tag>
                </el-descriptions-item>
                <el-descriptions-item label="详细描述">{{
                  selectedEvent.detailDescription
                }}</el-descriptions-item>
              </el-descriptions>
            </el-col>
            <el-col :span="12">
              <h4>相关证据</h4>
              <div id="evidenceChart" style="width: 100%; height: 300px"></div>
            </el-col>
          </el-row>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>威胁情报综合分析</span>
          </div>
          <div class="analysis-content">
            <h3>主要威胁情报发现</h3>
            <p>
              通过对公司内部各种日志数据的综合分析，我们发现了以下几个主要的威胁情报：
            </p>

            <h4>1. 大量敏感文件访问与数据外发</h4>
            <p>
              研发2部的员工ID-1103在非常规工作时间（凌晨2:00-4:00）登录公司服务器，访问并下载了大量与新产品相关的文件，同时向外部邮箱发送了多封带有大附件的邮件。
            </p>

            <h4>2. 异常登录行为</h4>
            <p>
              员工ID-1152在11月10日至11月15日期间多次尝试登录其他研发人员的账户，成功率较低但存在成功案例，显示出明显的账户探测行为。
            </p>

            <h4>3. 反常规上班模式</h4>
            <p>
              员工ID-1388在11月5日至11月20日期间，连续多天出现深夜在办公室活动的记录，但第二天通常迟到或缺勤，与其历史工作模式存在显著差异。
            </p>

            <h4>4. 数据库异常查询</h4>
            <p>
              研发3部的员工ID-1307在11月8日至11月12日期间，对公司核心产品数据库进行了大量非常规查询，涉及表数量远超其工作所需。
            </p>

            <h4>5. 可疑外部通信</h4>
            <p>
              员工ID-1204在11月18日至11月25日期间，其工作站与多个未知IP地址建立了加密连接，流量模式表明可能存在数据外传。
            </p>

            <h3>威胁关联分析</h3>
            <p>
              这些异常事件并非相互独立，通过对时间、网络行为和邮件往来的分析，我们发现：
            </p>
            <ul>
              <li>
                员工ID-1103和员工ID-1204有频繁的邮件往来，且邮件内容多涉及新产品的技术细节
              </li>
              <li>
                员工ID-1152与员工ID-1388在同一网段活动，且活动时间有明显的交错模式
              </li>
              <li>
                在员工ID-1307进行异常数据库查询的同一时间段，员工ID-1103的外发邮件数量明显增加
              </li>
              <li>
                所有涉事员工近期都曾访问过相同的外部技术论坛和几个特定IP地址
              </li>
            </ul>

            <h3>分析方法说明</h3>
            <p>本系统采用多维数据关联分析方法发现这些威胁情报：</p>
            <ol>
              <li>
                通过员工打卡记录与登录时间的交叉分析，发现工作时间与系统活动不匹配的异常
              </li>
              <li>
                使用聚类算法对邮件往来建立关系网络，识别出不寻常的沟通模式
              </li>
              <li>对网络流量进行时序分析，发现工作时间之外的异常流量峰值</li>
              <li>分析登录日志中的失败模式，识别可能的账户探测行为</li>
              <li>
                利用关联规则挖掘算法，发现不同异常事件之间的时间和行为关联
              </li>
            </ol>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
export default {
  name: "Threat",
  data() {
    return {
      threatRelationChart: null,
      evidenceChart: null,
      selectedEvent: null,
      threatEvents: [],
      rawRecentAbnormalEvents: [],
      departmentAbnormalCountsData: [],
      employeeAbnormalActivitiesData: {},
      isLoading: false,
    };
  },
  async mounted() {
    await this.loadThreatData();
    this.initThreatRelationChart();
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
    if (this.threatRelationChart) {
      this.threatRelationChart.dispose();
    }
    if (this.evidenceChart) {
      this.evidenceChart.dispose();
    }
  },
  methods: {
    async loadThreatData() {
      this.isLoading = true;
      this.$message.info("正在加载威胁情报数据...");
      try {
        const [recentRes, deptRes, empRes] = await Promise.all([
          fetch("/recent_abnormal_events.json"),
          fetch("/department_abnormal_counts.json"),
          fetch("/employee_abnormal_activities.json"),
        ]);

        if (!recentRes.ok) throw new Error("加载最近异常事件失败");
        this.rawRecentAbnormalEvents = await recentRes.json();

        if (!deptRes.ok) throw new Error("加载部门异常统计失败");
        this.departmentAbnormalCountsData = await deptRes.json();

        if (!empRes.ok) throw new Error("加载员工异常活动失败");
        this.employeeAbnormalActivitiesData = await empRes.json();

        this.processThreatEvents();
        this.updateThreatRelationChart();

        this.$message.success("威胁情报数据加载完成！");
      } catch (error) {
        console.error("加载威胁数据失败:", error);
        this.$message.error(`加载威胁数据失败: ${error.message}`);
        this.processThreatEvents();
        this.updateThreatRelationChart();
      } finally {
        this.isLoading = false;
      }
    },
    processThreatEvents() {
      if (
        this.rawRecentAbnormalEvents &&
        this.rawRecentAbnormalEvents.length > 0
      ) {
        // 限制处理的事件数量，避免性能问题
        const limitedEvents = this.rawRecentAbnormalEvents.slice(0, 50);

        this.threatEvents = limitedEvents.map((event, index) => {
          // 增强威胁类型分类
          const enhancedType = this.classifyThreatType(event);
          // 增强风险等级评估
          const riskLevel = this.assessThreatLevel(event);
          // 增强描述
          const enhancedDesc = this.enhanceDescription(event);

          return {
            id: index + 1,
            type: enhancedType,
            date: event.timestamp ? event.timestamp.split(" ")[0] : "未知日期",
            time: event.timestamp ? event.timestamp.split(" ")[1] : "未知时间",
            user: event.employeeId || "未知用户",
            description: enhancedDesc,
            level: riskLevel,
            detailDescription: this.generateDetailedDescription(event),
            rawEventData: event,
          };
        });

        // 按风险等级排序：高->中->低
        this.threatEvents.sort((a, b) => {
          const levelOrder = { 高: 0, 中: 1, 低: 2 };
          return levelOrder[a.level] - levelOrder[b.level];
        });
      } else {
        this.threatEvents = [];
      }
    },
    classifyThreatType(event) {
      const proto = event.rawEvent?.proto || "";
      const dport = event.rawEvent?.dport || 0;

      if (proto === "ftp" || proto === "sftp") return "文件传输异常";
      if (dport == 22) return "SSH远程访问";
      if (dport == 3389) return "RDP远程桌面";
      if (proto === "tds") return "数据库访问异常";
      if (proto === "mysql" || proto === "postgresql") return "数据库查询异常";
      return event.type || "非工作时间活动";
    },
    assessThreatLevel(event) {
      const proto = event.rawEvent?.proto || "";
      const dport = event.rawEvent?.dport || 0;
      const time = event.timestamp || "";

      // 深夜时间(22:00-06:00)的敏感操作
      const hour = new Date(time).getHours();
      const isDeepNight = hour >= 22 || hour <= 6;

      // 高风险条件
      if ((proto === "ftp" || proto === "sftp") && isDeepNight) return "高";
      if (dport == 22 || dport == 3389) return "高";
      if (proto === "tds" && isDeepNight) return "中";
      if (proto === "mysql" || proto === "postgresql") return "中";

      return "低";
    },
    enhanceDescription(event) {
      const proto = event.rawEvent?.proto || "";
      const dip = event.rawEvent?.dip || "";
      const dport = event.rawEvent?.dport || "";
      const time = event.timestamp || "";

      if (proto === "ftp" || proto === "sftp") {
        return `可疑文件传输: 在${time}通过${proto.toUpperCase()}访问${dip}:${dport}`;
      }
      if (proto === "tds") {
        return `数据库异常访问: 在${time}访问SQL Server ${dip}:${dport}`;
      }
      if (dport == 22) {
        return `SSH远程登录: 在${time}访问服务器${dip}`;
      }

      return event.description || `在${time}检测到异常活动`;
    },
    generateDetailedDescription(event) {
      const details = [
        `事件时间: ${event.timestamp}`,
        `涉及员工: ${event.employeeId} (${event.department})`,
        `访问协议: ${event.rawEvent?.proto || "未知"}`,
        `目标地址: ${event.rawEvent?.dip}:${event.rawEvent?.dport}`,
        `源地址: ${event.rawEvent?.sip}:${event.rawEvent?.sport}`,
        `连接状态: ${event.rawEvent?.state || "未知"}`,
        `风险评估: ${this.assessThreatLevel(event)}`,
        "",
        "详细分析:",
        event.description || "无详细描述",
      ];

      return details.join("\n");
    },
    initThreatRelationChart() {
      if (this.threatRelationChart) {
        this.threatRelationChart.dispose();
      }
      const chartDom = document.getElementById("threatRelationChart");
      if (chartDom) {
        this.threatRelationChart = this.$echarts.init(chartDom);
        this.updateThreatRelationChart();
      } else {
        console.error("Threat relation chart DOM not found.");
      }
    },
    updateThreatRelationChart() {
      if (!this.threatRelationChart) return;

      let nodes = [];
      let links = [];
      const categories = [
        { name: "威胁类型", itemStyle: { color: "#F56C6C" } }, // Category 0
        { name: "部门", itemStyle: { color: "#409EFF" } }, // Category 1
        { name: "风险等级", itemStyle: { color: "#E6A23C" } }, // Category 2
      ];

      // 如果使用rawRecentAbnormalEvents数据（更小规模）
      if (
        !this.rawRecentAbnormalEvents ||
        this.rawRecentAbnormalEvents.length === 0
      ) {
        this.threatRelationChart.setOption({
          title: {
            text: "暂无威胁事件数据以生成关联图",
            left: "center",
            top: "center",
          },
          series: [],
        });
        return;
      }

      // 数据聚合：按威胁类型、部门、风险等级进行统计
      const threatTypeStats = new Map();
      const departmentStats = new Map();
      const riskLevelStats = new Map();
      const relationStats = new Map(); // 关系统计

      // 只处理前100个事件，避免性能问题
      const limitedEvents = this.rawRecentAbnormalEvents.slice(0, 100);

      limitedEvents.forEach((event) => {
        const threatType = this.classifyThreatType(event);
        const department = event.department || "未知部门";
        const riskLevel = this.assessThreatLevel(event);

        // 统计各维度数据
        threatTypeStats.set(
          threatType,
          (threatTypeStats.get(threatType) || 0) + 1
        );
        departmentStats.set(
          department,
          (departmentStats.get(department) || 0) + 1
        );
        riskLevelStats.set(riskLevel, (riskLevelStats.get(riskLevel) || 0) + 1);

        // 记录关系
        const threatDeptKey = `${threatType}-${department}`;
        const deptRiskKey = `${department}-${riskLevel}`;
        const threatRiskKey = `${threatType}-${riskLevel}`;

        relationStats.set(
          threatDeptKey,
          (relationStats.get(threatDeptKey) || 0) + 1
        );
        relationStats.set(
          deptRiskKey,
          (relationStats.get(deptRiskKey) || 0) + 1
        );
        relationStats.set(
          threatRiskKey,
          (relationStats.get(threatRiskKey) || 0) + 1
        );
      });

      // 创建威胁类型节点（最多显示前5个）
      const topThreatTypes = Array.from(threatTypeStats.entries())
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);

      topThreatTypes.forEach(([type, count]) => {
        nodes.push({
          id: `threat_${type}`,
          name: `${type}\n(${count}次)`,
          category: 0,
          symbolSize: Math.max(20, Math.min(60, count * 2)),
          value: count,
          draggable: true,
        });
      });

      // 创建部门节点
      Array.from(departmentStats.entries()).forEach(([dept, count]) => {
        nodes.push({
          id: `dept_${dept}`,
          name: `${dept}\n(${count}次)`,
          category: 1,
          symbolSize: Math.max(25, Math.min(50, count * 1.5)),
          value: count,
          draggable: true,
        });
      });

      // 创建风险等级节点
      Array.from(riskLevelStats.entries()).forEach(([level, count]) => {
        nodes.push({
          id: `risk_${level}`,
          name: `${level}风险\n(${count}次)`,
          category: 2,
          symbolSize: Math.max(20, Math.min(45, count * 1.2)),
          value: count,
          draggable: true,
        });
      });

      // 创建关系连接（只显示较强的关联）
      relationStats.forEach((count, key) => {
        if (count < 2) return; // 过滤掉弱关联

        const [source, target] = key.split("-");
        let sourceId, targetId;

        // 确定连接的源和目标ID
        if (threatTypeStats.has(source)) {
          sourceId = `threat_${source}`;
        } else if (departmentStats.has(source)) {
          sourceId = `dept_${source}`;
        } else if (riskLevelStats.has(source)) {
          sourceId = `risk_${source}`;
        }

        if (threatTypeStats.has(target)) {
          targetId = `threat_${target}`;
        } else if (departmentStats.has(target)) {
          targetId = `dept_${target}`;
        } else if (riskLevelStats.has(target)) {
          targetId = `risk_${target}`;
        }

        if (sourceId && targetId && sourceId !== targetId) {
          links.push({
            source: sourceId,
            target: targetId,
            value: count,
            lineStyle: {
              width: Math.max(1, Math.min(8, count * 0.5)),
              opacity: Math.max(0.3, Math.min(1, count * 0.1)),
            },
          });
        }
      });

      // 限制节点数量，避免过于复杂
      if (nodes.length > 20) {
        nodes = nodes.slice(0, 20);
        // 重新过滤连接，只保留存在的节点
        const nodeIds = new Set(nodes.map((n) => n.id));
        links = links.filter(
          (l) => nodeIds.has(l.source) && nodeIds.has(l.target)
        );
      }

      const option = {
        title: {
          text: "威胁事件关联分析（聚合视图）",
          subtext: `基于${limitedEvents.length}个威胁事件的关联分析`,
          left: "center",
        },
        tooltip: {
          formatter: function (params) {
            if (params.dataType === "node") {
              return `${params.data.name}<br/>事件数量: ${
                params.data.value || "N/A"
              }`;
            } else if (params.dataType === "edge") {
              return `关联强度: ${params.data.value}`;
            }
            return params.name;
          },
        },
        legend: [
          {
            data: categories.map(function (a) {
              return a.name;
            }),
            bottom: 10,
          },
        ],
        animationDurationUpdate: 1500,
        animationEasingUpdate: "quinticInOut",
        series: [
          {
            type: "graph",
            layout: "force",
            data: nodes,
            links: links,
            categories: categories,
            roam: true,
            label: {
              show: true,
              position: "inside",
              formatter: "{b}",
              fontSize: 10,
            },
            edgeSymbol: ["none", "arrow"],
            edgeSymbolSize: [4, 8],
            force: {
              repulsion: 100,
              edgeLength: [50, 100],
              gravity: 0.05,
            },
            emphasis: {
              focus: "adjacency",
              lineStyle: {
                width: 4,
              },
            },
          },
        ],
      };

      this.threatRelationChart.setOption(option, true);
    },
    handleEventSelect(event) {
      this.selectedEvent = event;
      this.$nextTick(() => {
        this.initEvidenceChart();
      });
    },
    initEvidenceChart() {
      if (this.evidenceChart) {
        this.evidenceChart.dispose();
      }
      if (!this.selectedEvent) return;

      const chartDom = document.getElementById("evidenceChart");
      if (chartDom) {
        this.evidenceChart = this.$echarts.init(chartDom);
        this.updateEvidenceChart();
      } else {
        console.error("Evidence chart DOM not found.");
      }
    },
    updateEvidenceChart() {
      if (
        !this.evidenceChart ||
        !this.selectedEvent ||
        !this.selectedEvent.rawEventData
      ) {
        // Clear chart or show placeholder if no event or no raw data
        if (this.evidenceChart) {
          this.evidenceChart.setOption({
            title: {
              text: this.selectedEvent
                ? "选择的事件缺少原始数据"
                : "未选择事件",
              left: "center",
              top: "center",
            },
            series: [], // Clear series
          });
        }
        return;
      }

      const eventType = this.selectedEvent.type;
      const rawEvent = this.selectedEvent.rawEventData.rawEvent; // Assuming rawEventData contains the original rawEvent object
      let option = {};

      if (eventType === "邮件敏感词" && rawEvent && rawEvent.subject) {
        // 为邮件敏感词显示主题和关键词
        const keywordsFound = [];
        // SENSITIVE_EMAIL_KEYWORDS is not directly available here,
        // but we can infer from the description or rawEvent if it was stored.
        // For now, just display the subject.
        // A more advanced version could highlight keywords in the subject.
        option = {
          title: {
            text: `证据: ${eventType}`,
            subtext: `邮件主题: ${rawEvent.subject.substring(0, 100)}${
              rawEvent.subject.length > 100 ? "..." : ""
            }`,
            left: "center",
            textStyle: { fontSize: 14 },
            subtextStyle: { fontSize: 12, color: "#555" },
          },
          // We could use a graphic element to display text if no chart is suitable
          graphic: {
            type: "text",
            left: "center",
            top: "middle",
            style: {
              text: `相关邮件主题与描述中提到的敏感词有关。\n详细信息请查看事件描述。`,
              textAlign: "center",
              font: "14px Microsoft YaHei",
            },
          },
          series: [],
        };
      } else if (
        eventType === "非工作时间登录" &&
        this.selectedEvent.rawEventData
      ) {
        // 为非工作时间登录显示登录时间戳
        option = {
          title: {
            text: `证据: ${eventType}`,
            subtext: `登录时间: ${this.selectedEvent.rawEventData.timestamp}`,
            left: "center",
            textStyle: { fontSize: 14 },
            subtextStyle: { fontSize: 12, color: "#555" },
          },
          graphic: {
            type: "text",
            left: "center",
            top: "middle",
            style: {
              text: `该登录事件发生在非工作时段。\n具体时间点: ${this.selectedEvent.rawEventData.timestamp}`,
              textAlign: "center",
              font: "14px Microsoft YaHei",
            },
          },
          series: [],
        };
      } else {
        // 其他事件类型或缺少具体信息
        option = {
          title: {
            text: `事件证据 (类型: ${eventType})`,
            subtext: "此事件类型的详细证据展示待实现",
            left: "center",
            top: "center",
            textStyle: { fontSize: 14 },
            subtextStyle: { fontSize: 12, color: "#888" },
          },
          series: [],
        };
      }
      this.evidenceChart.setOption(option, true);
    },
    getEventTypeTag(type) {
      const typeMap = {
        数据外发: "danger",
        账户探测: "warning",
        异常行为: "warning",
        数据库异常: "danger",
        可疑通信: "danger",
      };
      return typeMap[type] || "info";
    },
    getRiskLevelTag(level) {
      const levelMap = {
        高: "danger",
        中: "warning",
        低: "info",
      };
      return levelMap[level] || "info";
    },
    handleResize() {
      this.threatRelationChart && this.threatRelationChart.resize();
      this.evidenceChart && this.evidenceChart.resize();
    },
  },
};
</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
}

.analysis-content {
  line-height: 1.6;
  text-align: justify;
}

.analysis-content h3 {
  margin-top: 20px;
  color: #303133;
  border-bottom: 1px solid #ebeef5;
  padding-bottom: 8px;
}

.analysis-content h4 {
  margin-top: 15px;
  color: #409eff;
}

.analysis-content ul,
.analysis-content ol {
  padding-left: 20px;
  margin: 10px 0;
}

.analysis-content li {
  margin-bottom: 5px;
}
</style>
