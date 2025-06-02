import Vue from "vue";
import VueRouter from "vue-router";

Vue.use(VueRouter);

const routes = [
  {
    path: "/",
    name: "Home",
    component: () => import("../views/Home.vue"),
  },
  {
    path: "/organization",
    name: "Organization",
    component: () => import("../views/Organization.vue"),
  },
  {
    path: "/behavior",
    name: "Behavior",
    component: () => import("../views/Behavior.vue"),
  },
  {
    path: "/threat",
    name: "Threat",
    component: () => import("../views/Threat.vue"),
  },
  {
    path: "/person",
    name: "Person",
    component: () => import("../views/Person.vue"),
  },
];

const router = new VueRouter({
  mode: "history",
  base: process.env.BASE_URL,
  routes,
});

export default router;
