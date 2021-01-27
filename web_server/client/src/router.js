import Vue from "vue";
import VueRouter from "vue-router";

import DashboardView from "./views/dashboard.view"
import DeviceTableView from "./views/devices.table.view"
import DeviceViewMeasurements from "./views/device.measurements.view"
import DeviceViewConfiguration from "./views/device.configuration.view"


Vue.use(VueRouter);


const routes = [
    {
        path: "/",
        name: "Dashboard",
        component: DashboardView,
    },
    {
        path: "/devices/",
        name: "Devices",
        component: DeviceTableView,
    },
        {
        path: "/devices/:id",
        redirect: "/devices/:id/measurements"
    },
    {
        path: "/devices/:id/measurements",
        name: "Device-Measurements",
        component: DeviceViewMeasurements,
    },
    {
        path: "/devices/:id/configuration",
        name: "Device-Configuration",
        component: DeviceViewConfiguration,
    }
];
const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes,
});

export default router;
