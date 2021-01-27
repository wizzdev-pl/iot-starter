<template>
    <div class="page-container">
        <md-app md-mode="reveal">
            <md-app-toolbar class="md-primary">
                <span class="md-title">{{ $t("title") }}</span>
                <b-nav class="ml-2" pills>
                    <b-nav-item>
                        <router-link to="/">
                            <span class="text-white">
                                <md-icon class="pb-1">dashboard</md-icon>
                                Dashboard
                            </span>
                        </router-link>
                    </b-nav-item>
                    <b-nav-item>
                        <router-link to="/devices/">
                            <span class="text-white">Devices</span>
                        </router-link>
                    </b-nav-item>
                </b-nav>
                <div class="ml-auto d-inline-flex">
                    <div class="mt-auto mb-auto mr-2">{{time}}</div>
                    <md-button id="refreshButton" class="md-fab md-mini md-plain" v-on:click="loadData(true)">
                        <md-icon>refresh</md-icon>
                    </md-button>
                </div>
            </md-app-toolbar>

            <md-app-content>
                <router-view/>
            </md-app-content>

        </md-app>
    </div>
</template>

<script>
    import 'vue-material/dist/vue-material.min.css'

    import Vue from "vue";
    import {mapActions, mapGetters} from 'vuex';
    import moment from "moment";

    import Configuration from "./config";
    import router from "./router";

    export default {
        name: "App",
        computed: {
            ...mapGetters("device", {devices: "getAllDevices"})
        },
        methods: {
            ...mapActions("measurement", {loadMeasurements: "loadItems"}),
            ...mapActions("measurementType", {loadMeasurementTypes: "loadItems"}),
            ...mapActions("device", {loadDevices: "loadItems"}),
            ...mapActions("deviceGroup", {loadDeviceGroups: "loadItems"}),
            ...mapActions("deviceType", {loadDeviceTypes: "loadItems"}),
            ...mapActions("deviceShadow", ["loadDeviceShadow", "loadDeviceShadows"]),
            loadData: async function (goToDashboard) {
                let object = this;
                Vue.toasted.clear();
                Vue.toasted.show("Loading data ... ", {
                    duration: 1500,
                });
                this.loadDeviceGroups();
                this.loadDeviceTypes();
                this.loadMeasurements();
                this.loadMeasurementTypes();
                this.loadDevices().then(async function () {
                    // TODO: Find a better way while devices from API would be added to vuex;
                    await new Promise(r => setTimeout(r, 1000));
                    object.devices.forEach(device => object.loadDeviceShadow(device.device_id));
                });
                if (goToDashboard && router.currentRoute !== "/") {
                    try {
                        router.push({path: "/"});
                    } catch (e) {
                        if (Configuration.DEBUG)
                            console.log("Cannot change current location. " + e)
                    }
                }
            }
        },
        data: () => ({
            time: ""
        }),
        async mounted() {
            this.loadData();
            window.document.title = "Wizzdev Iot";
            setInterval(() => this.time = moment().format('HH:mm:ss DD-MM-YYYY'), 1000);
        },
    };
</script>

<style lang="css">
    #refreshButton {
        background-color: #007bff !important;
    }

    #refreshButton .md-icon {
        color: white !important;
    }
</style>