import Vue from "vue";
import Vuex from "vuex";

import device from './modules/device';
import measurement from './modules/measurement';
import measurementType from './modules/measurement.type';
import deviceGroup from './modules/device.group';
import deviceType from './modules/device.type';
import deviceShadow from './modules/device.shadow';

Vue.use(Vuex);

export default new Vuex.Store({
    modules: {device, measurement, measurementType, deviceGroup, deviceType, deviceShadow},
});
