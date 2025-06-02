<template>
  <div id="app">
    <el-container>
      <el-header height="60px">
        <div class="header-container">
          <div class="logo-area">
            <i class="el-icon-data-analysis logo-icon"></i>
            <div class="title-container">
              <h1 class="main-title">内部威胁情报分析系统</h1>
              <div class="sub-title">Internal Threat Intelligence Analysis</div>
            </div>
          </div>
          <div class="header-right">
            <span class="time">开发者：张宏彬，高宇润，曹家赫，王宇</span>
          </div>
        </div>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu
            default-active="1"
            class="el-menu-vertical"
            background-color="#545c64"
            text-color="#fff"
            active-text-color="#ffd04b"
            router
          >
            <el-menu-item index="/">
              <i class="el-icon-s-home"></i>
              <span slot="title">首页</span>
            </el-menu-item>
            <el-menu-item index="/organization">
              <i class="el-icon-s-custom"></i>
              <span slot="title">组织结构</span>
            </el-menu-item>
            <el-menu-item index="/behavior">
              <i class="el-icon-s-data"></i>
              <span slot="title">行为分析</span>
            </el-menu-item>
            <el-menu-item index="/threat">
              <i class="el-icon-warning"></i>
              <span slot="title">威胁检测</span>
            </el-menu-item>
            <el-menu-item index="/person">
              <i class="el-icon-user"></i>
              <span slot="title">个人分析</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script>
export default {
  name: "App",
};
</script>

<style>
#app {
  font-family: "Microsoft YaHei", Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  height: 100vh;
}

body {
  margin: 0;
  padding: 0;
}

.el-header {
  background: linear-gradient(to right, #1e5eff, #3e7fff);
  color: white;
  line-height: 60px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
  padding: 0 20px;
}

.header-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}

.logo-area {
  display: flex;
  align-items: center;
}

.logo-icon {
  font-size: 32px;
  margin-right: 15px;
  background: rgba(255, 255, 255, 0.2);
  padding: 8px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(255, 255, 255, 0.3);
}

.title-container {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.main-title {
  font-size: 20px;
  font-weight: bold;
  margin: 0;
  line-height: 1.2;
  letter-spacing: 1px;
  text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
}

.sub-title {
  font-size: 12px;
  opacity: 0.8;
  letter-spacing: 0.5px;
  line-height: 1;
}

.header-right {
  display: flex;
  align-items: center;
}

.time {
  font-size: 14px;
  padding: 4px 10px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
}

.el-aside {
  background-color: #545c64;
  color: white;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
}

.el-menu-vertical {
  border-right: 0;
}

.el-main {
  background-color: #f0f2f5;
  padding: 20px;
}
</style>
