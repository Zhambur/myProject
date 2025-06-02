<template>
  <div class="organization">
    <el-row>
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>公司组织结构分析</span>
            <el-tooltip
              class="item"
              effect="dark"
              content="通过分析邮件往来和登录行为，识别公司各部门结构和人员组成"
              placement="top"
            >
              <i class="el-icon-question" style="margin-left: 10px"></i>
            </el-tooltip>
          </div>
          <p>
            通过对公司内部邮件、登录和打卡数据的分析，我们识别出了HighTech公司的组织结构。
          </p>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="16">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>公司组织架构图</span>
          </div>
          <div id="orgChart" style="width: 100%; height: 600px"></div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>部门人员统计</span>
          </div>
          <div id="deptPieChart" style="width: 100%; height: 350px"></div>
        </el-card>
        <el-card class="box-card" style="margin-top: 20px">
          <div slot="header" class="clearfix">
            <span>职位分布</span>
          </div>
          <div id="positionChart" style="width: 100%; height: 200px"></div>
        </el-card>
      </el-col>
    </el-row>

    <el-row style="margin-top: 20px">
      <el-col :span="24">
        <el-card class="box-card">
          <div slot="header" class="clearfix">
            <span>部门关系网络</span>
            <el-tooltip
              class="item"
              effect="dark"
              content="基于邮件往来数据构建的部门间联系强度图"
              placement="top"
            >
              <i class="el-icon-question" style="margin-left: 10px"></i>
            </el-tooltip>
          </div>
          <div id="deptRelationChart" style="width: 100%; height: 500px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import Papa from "papaparse";
import * as echarts from "echarts";

export default {
  name: "Organization",
  data() {
    return {
      orgChart: null,
      deptPieChart: null,
      positionChart: null,
      deptRelationChart: null,
      organizationData: [],
      departmentCounts: [],
      deptRelationNodes: [],
      deptRelationLinks: [],
    };
  },
  async mounted() {
    await this.loadOrganizationData();
    this.initAllCharts();
    window.addEventListener("resize", this.handleResize);
  },
  beforeDestroy() {
    window.removeEventListener("resize", this.handleResize);
  },
  methods: {
    handleResize() {
      this.orgChart && this.orgChart.resize();
      this.deptPieChart && this.deptPieChart.resize();
      this.positionChart && this.positionChart.resize();
      this.deptRelationChart && this.deptRelationChart.resize();
    },
    initAllCharts() {
      this.initOrgChart();
      this.initDeptPieChart();
      this.initPositionChart();
      this.initDeptRelationChart();
    },
    async loadOrganizationData() {
      console.log("Organization.vue: 开始加载组织数据...");
      this.$message.info("正在加载组织架构数据...");
      try {
        const response = await fetch("/employee_department_mapping.csv");
        if (!response.ok) {
          throw new Error(
            `HTTP error! status: ${response.status} while fetching employee_department_mapping.csv`
          );
        }
        const csvText = await response.text();
        const parsedData = Papa.parse(csvText, {
          header: true,
          skipEmptyLines: true,
        }).data;

        this.organizationData = parsedData.filter(
          (row) => row.sender_id && row.department_name
        );
        console.log(
          "组织数据加载完成: ",
          this.organizationData.length,
          "条记录"
        );

        const counts = {};
        this.organizationData.forEach((item) => {
          counts[item.department_name] =
            (counts[item.department_name] || 0) + 1;
        });
        this.departmentCounts = Object.entries(counts).map(([name, value]) => ({
          name,
          value,
        }));
        console.log("部门人数统计: ", this.departmentCounts);

        // 新增：加载部门关系数据
        const nodesResponse = await fetch("/department_relation_nodes.json");
        if (!nodesResponse.ok) {
          throw new Error(
            `HTTP error! status: ${nodesResponse.status} while fetching department_relation_nodes.json`
          );
        }
        this.deptRelationNodes = await nodesResponse.json();
        console.log(
          "部门关系节点数据加载完成: ",
          this.deptRelationNodes.length,
          "个部门"
        );

        const linksResponse = await fetch("/department_relation_links.json");
        if (!linksResponse.ok) {
          throw new Error(
            `HTTP error! status: ${linksResponse.status} while fetching department_relation_links.json`
          );
        }
        this.deptRelationLinks = await linksResponse.json();
        console.log(
          "部门关系连接数据加载完成: ",
          this.deptRelationLinks.length,
          "条关系"
        );

        this.$message.success("组织架构及关系数据加载成功！");
      } catch (error) {
        console.error("加载组织数据失败:", error);
        this.$message.error(`加载组织数据失败: ${error.message}`);
        this.organizationData = [];
        this.departmentCounts = [];
        this.deptRelationNodes = []; // 清空
        this.deptRelationLinks = []; // 清空
      }
    },
    initOrgChart() {
      if (this.orgChart) {
        this.orgChart.dispose();
      }
      const chartDom = document.getElementById("orgChart");
      if (!chartDom) {
        console.error("initOrgChart: 无法找到DOM元素 #orgChart");
        return;
      }
      this.orgChart = echarts.init(chartDom);

      const nodes = [];
      const links = [];
      let nodeIdCounter = 0;

      if (this.organizationData.length === 0) {
        console.warn("组织数据为空，无法生成组织架构图。");
        this.orgChart.setOption({
          title: {
            text: "组织数据加载失败或为空",
            left: "center",
            top: "center",
          },
        });
        return;
      }

      const companyRootId = `company-${nodeIdCounter++}`;
      nodes.push({
        id: companyRootId,
        name: "HighTech 公司",
        category: "公司",
        symbolSize: 70,
        itemStyle: { color: "#A30000" },
        label: { show: true, fontSize: 16, fontWeight: "bold" },
        fixed: true,
        x: this.orgChart.getWidth() / 2,
        y: 50,
      });

      const departments = {};
      this.organizationData.forEach((employee) => {
        const departmentName = employee.department_name;
        const employeeId = String(employee.sender_id);

        if (!departments[departmentName]) {
          const deptId = `dept-${departmentName}-${nodeIdCounter++}`;
          departments[departmentName] = deptId;
          nodes.push({
            id: deptId,
            name: departmentName,
            category: "部门",
            symbolSize: 50,
            itemStyle: { color: "#00529B" },
            label: { show: true, fontSize: 14, position: "bottom" },
          });
          links.push({
            source: companyRootId,
            target: deptId,
            lineStyle: { width: 2 },
          });
        }

        const empNodeId = `emp-${employeeId}-${nodeIdCounter++}`;
        nodes.push({
          id: empNodeId,
          name: employeeId,
          category: "员工",
          department: departmentName,
          symbolSize: 30,
          itemStyle: { color: "#409EFF" },
          label: { show: true, position: "right", formatter: "{b}" },
        });

        links.push({
          source: departments[departmentName],
          target: empNodeId,
        });
      });

      const option = {
        title: {
          text: "公司组织结构图 (基于推断数据)",
          subtext: "点击节点可拖动，滚轮可缩放",
          left: "center",
        },
        tooltip: {
          trigger: "item",
          formatter: function (params) {
            if (params.dataType === "node") {
              const data = params.data;
              let res = `<div style="font-weight:bold;margin-bottom:5px;">${data.category}: ${data.name}</div>`;
              if (data.department) {
                res += `所属部门: ${data.department}<br/>`;
              }
              return res;
            }
            return params.data.source && params.data.target ? "层级关系" : "";
          },
        },
        legend: [
          {
            data: ["公司", "部门", "员工"],
            top: 50,
            textStyle: { fontSize: 12 },
            icon: "circle",
            itemWidth: 10,
            itemHeight: 10,
          },
        ],
        animationDurationUpdate: 1500,
        animationEasingUpdate: "quinticInOut",
        series: [
          {
            type: "graph",
            layout: "force",
            force: {
              repulsion: [300, 400],
              gravity: 0.15,
              edgeLength: [80, 150],
              layoutAnimation: true,
              friction: 0.6,
            },
            roam: true,
            draggable: true,
            label: {
              show: true,
              position: "right",
              fontSize: 10,
            },
            edgeSymbol: ["none", "arrow"],
            edgeSymbolSize: [0, 8],
            nodes: nodes,
            links: links,
            categories: [
              { name: "公司", itemStyle: { color: "#A30000" } },
              { name: "部门", itemStyle: { color: "#00529B" } },
              { name: "员工", itemStyle: { color: "#409EFF" } },
            ],
            lineStyle: {
              opacity: 0.9,
              width: 1.5,
              curveness: 0,
            },
          },
        ],
      };
      this.orgChart.setOption(option);
    },
    initDeptPieChart() {
      if (this.deptPieChart) {
        this.deptPieChart.dispose();
      }
      const chartDom = document.getElementById("deptPieChart");
      if (!chartDom) {
        console.error("initDeptPieChart: 无法找到DOM元素 #deptPieChart");
        return;
      }
      this.deptPieChart = echarts.init(chartDom);

      if (this.departmentCounts.length === 0) {
        console.warn("部门统计数据为空，无法生成饼图。");
        this.deptPieChart.setOption({
          title: {
            text: "部门人数数据加载失败或为空",
            left: "center",
            top: "center",
          },
        });
        return;
      }

      const option = {
        title: {
          text: "各部门人员数量占比",
          left: "center",
        },
        tooltip: {
          trigger: "item",
          formatter: "{a} <br/>{b}: {c}人 ({d}%)",
        },
        legend: {
          orient: "vertical",
          left: 10,
          top: 30,
          data: this.departmentCounts.map((item) => item.name),
        },
        series: [
          {
            name: "部门人数",
            type: "pie",
            radius: "70%",
            center: ["55%", "60%"],
            data: this.departmentCounts,
            emphasis: {
              itemStyle: {
                shadowBlur: 10,
                shadowOffsetX: 0,
                shadowColor: "rgba(0, 0, 0, 0.5)",
              },
            },
            label: {
              show: true,
              formatter: "{b}: {c}人\n({d}%)",
            },
            labelLine: {
              show: true,
            },
          },
        ],
      };
      this.deptPieChart.setOption(option);
    },
    initPositionChart() {
      this.positionChart = this.$echarts.init(
        document.getElementById("positionChart")
      );

      const option = {
        tooltip: {
          trigger: "axis",
          axisPointer: {
            type: "shadow",
          },
        },
        grid: {
          left: "3%",
          right: "4%",
          bottom: "3%",
          containLabel: true,
        },
        xAxis: {
          type: "value",
        },
        yAxis: {
          type: "category",
          data: ["总经理", "部长", "组长", "普通员工"],
        },
        series: [
          {
            name: "职位人数",
            type: "bar",
            data: [1, 5, 17, 297],
          },
        ],
      };

      this.positionChart.setOption(option);
    },
    initDeptRelationChart() {
      if (this.deptRelationChart) {
        this.deptRelationChart.dispose();
      }
      const chartDom = document.getElementById("deptRelationChart");
      if (!chartDom) {
        console.error(
          "initDeptRelationChart: 无法找到DOM元素 #deptRelationChart"
        );
        return;
      }
      this.deptRelationChart = echarts.init(chartDom);

      if (
        this.deptRelationNodes.length === 0 ||
        this.deptRelationLinks.length === 0
      ) {
        console.warn("部门关系数据为空，无法生成关系网络图。");
        this.deptRelationChart.setOption({
          title: {
            text: "部门关系数据加载失败或为空",
            left: "center",
            top: "center",
          },
        });
        return;
      }

      // 为节点数据添加symbolSize和category（如果需要，可以基于memberCount或value）
      const processedNodes = this.deptRelationNodes.map((node) => ({
        ...node,
        symbolSize: Math.max(
          20,
          Math.min(80, node.memberCount * 2 + node.value / 50)
        ), // 示例：根据成员数和邮件量调整大小
        category: node.name, // 每个部门一个类别，用于图例和颜色区分
        draggable: true,
      }));

      const categories = this.deptRelationNodes.map((node) => ({
        name: node.name,
      }));

      const option = {
        title: {
          text: "部门间邮件往来关系 (真实数据)",
          left: "center",
          textStyle: {
            fontSize: 18,
            fontWeight: "bold",
          },
          subtext: "基于 전체邮件数据分析",
        },
        tooltip: {
          trigger: "item",
          formatter: function (params) {
            if (params.dataType === "edge") {
              return `${params.data.source} → ${params.data.target}<br/>邮件往来: ${params.data.value}封`;
            }
            // params.dataType === 'node'
            return `${params.data.name}<br/>总邮件活跃度: ${
              params.data.value || "-"
            }<br/>成员数: ${params.data.memberCount || "-"}人`;
          },
        },
        legend: {
          type: "scroll",
          orient: "vertical",
          right: 10,
          top: 50,
          data: categories.map((c) => c.name), // 从节点动态生成图例
        },
        animationDuration: 1500,
        animationEasingUpdate: "quinticInOut",
        series: [
          {
            name: "部门关系网络",
            type: "graph",
            layout: "force",
            data: processedNodes, // 使用处理后的节点数据
            links: this.deptRelationLinks, // 使用加载的连接数据
            categories: categories, // 用于图例和颜色
            roam: true,
            draggable: true,
            label: {
              show: true,
              position: "right",
              formatter: "{b}", // 显示节点名称 (b 代表 name)
              fontSize: 10,
            },
            force: {
              repulsion: 400, // 节点间斥力因子
              gravity: 0.1, // 引力因子
              edgeLength: [80, 150], // 边的理想长度范围
              layoutAnimation: true,
              friction: 0.6,
            },
            lineStyle: {
              opacity: 0.7,
              width: 1.5,
              curveness: 0.1, // 边的弯曲度
              color: "source", // 边颜色跟随源节点
            },
            edgeSymbol: ["none", "arrow"],
            edgeSymbolSize: [0, 7],
            emphasis: {
              focus: "adjacency",
              lineStyle: {
                width: 4, // 高亮时边的宽度
              },
              label: {
                show: true, // 高亮时也显示标签
                fontSize: 12,
              },
            },
          },
        ],
      };

      this.deptRelationChart.setOption(option);

      // 可以保留或移除原有的点击事件，根据新数据结构调整
      this.deptRelationChart.off("click"); // 先移除旧的监听器
      this.deptRelationChart.on("click", (params) => {
        if (params.dataType === "edge") {
          console.log(
            `点击了边: ${params.data.source} -> ${params.data.target}, 往来数: ${params.data.value}`
          );
          this.$message.info(
            `部门 ${params.data.source} 与 ${params.data.target} 间邮件往来 ${params.data.value} 封`
          );
        } else if (params.dataType === "node") {
          console.log(
            `点击了部门节点: ${params.name}, 成员数: ${params.data.memberCount}, 邮件活跃度: ${params.data.value}`
          );
        }
      });
    },
  },
};
</script>

<style scoped>
.box-card {
  margin-bottom: 20px;
}
</style>
