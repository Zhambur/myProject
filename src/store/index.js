import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    employeeData: null,
    departmentData: null,
    selectedEmployee: null,
    selectedDate: "2017-11-01",
    threatEvents: [],
  },
  mutations: {
    SET_EMPLOYEE_DATA(state, data) {
      state.employeeData = data;
    },
    SET_DEPARTMENT_DATA(state, data) {
      state.departmentData = data;
    },
    SET_SELECTED_EMPLOYEE(state, employee) {
      state.selectedEmployee = employee;
    },
    SET_SELECTED_DATE(state, date) {
      state.selectedDate = date;
    },
    ADD_THREAT_EVENT(state, event) {
      state.threatEvents.push(event);
    },
  },
  actions: {
    fetchEmployeeData({ commit }) {
      // 实际项目中，这里应该是API请求
      // 模拟数据
      const data = {
        departments: {
          研发: { count: 280, subDepartments: ["研发1", "研发2", "研发3"] },
          财务: { count: 25, subDepartments: [] },
          人力资源: { count: 15, subDepartments: [] },
        },
      };
      commit("SET_DEPARTMENT_DATA", data);
    },
  },
  modules: {},
});
