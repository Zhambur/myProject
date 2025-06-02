import Vue from "vue";
import App from "./App.vue";
import router from "./router";
import store from "./store";
import ElementUI from "element-ui";
import "element-ui/lib/theme-chalk/index.css";
import * as echarts from "echarts";
import "echarts-wordcloud";

// 注册 ElementUI
Vue.use(ElementUI);

// 将 echarts 挂载到 Vue 原型上，方便全局调用
Vue.prototype.$echarts = echarts;

Vue.config.productionTip = false;

new Vue({
  router,
  store,
  render: (h) => h(App),
}).$mount("#app");
