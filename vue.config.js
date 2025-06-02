const { defineConfig } = require("@vue/cli-service");

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  devServer: {
    allowedHosts: "all",
    host: "0.0.0.0",
    headers: {
      "Access-Control-Allow-Origin": "*", // 添加 CORS 支持
    },
    client: {
      overlay: false,
      webSocketURL: "auto://0.0.0.0:0/ws",
    },
  },
  css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "@/assets/styles/variables.scss";`,
      },
    },
  },
});
