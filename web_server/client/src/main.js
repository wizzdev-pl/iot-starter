import 'vue-material/dist/vue-material.min.css'
import 'vue-material/dist/theme/black-green-light.css'
import '../static/material_icons.css'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

import Vue from "vue";
import Vuex from "vuex";
import VueMaterial from 'vue-material';
import { BootstrapVue, IconsPlugin } from 'bootstrap-vue'
import Toasted from "vue-toasted";

import Configuration from "./config";
import App from "./App.vue";
import i18n from "./i18n";
import store from "./store";
import router from "./router";

Vue.config.productionTip = false;

Vue.use(Vuex);
Vue.use(VueMaterial);
Vue.use(BootstrapVue);
Vue.use(IconsPlugin);
Vue.use(Toasted);

new Vue({
    router, store, i18n, render: (h) => h(App),
}).$mount("#app");