<template>
    <div class="w-100 h-100">
        <div class="layout">
            <div class="md-layout mt-5 mr-5 ml-5" v-if="device">
                <div class="float-left p-2">
                    <b class="md-display-1">{{ prettyPrint(deviceId) }}</b>
                    <b class="md-headline ml-4">{{ prettyPrint(device ? device.device_group : "" ) }}</b>
                    <b class="md-headline ml-4">{{ prettyPrint(device ? device.device_type : "" ) }}</b>
                </div>
                <div class="float-left p-2 mt-1">

                    <router-link :to="'/devices/' + deviceId + '/measurements'">
                        <md-button id="btn-measurements">
                            <md-icon class="mb-1 mr-1">insert_chart_outlined</md-icon>
                            Measurements
                        </md-button>
                    </router-link>

                    <router-link :to="'/devices/' + deviceId + '/configuration'">
                        <md-button id="btn-configuration">
                            <md-icon class="mb-1 mr-1">settings</md-icon>
                            Configuration
                        </md-button>
                    </router-link>

                </div>
            </div>
        </div>
        <md-divider class="m-1 mb-5"/>
        <div class="layout">
            <slot></slot>
        </div>
    </div>
</template>

<script>
    import {mapGetters} from 'vuex';
    import utils from "../common/utils";

    export default {
        name: "DeviceView",
        computed: {
            ...mapGetters("device", ["getDevice"]),
            deviceId() { return this.$route.params.id; },
            device() { return this.getDevice(this.deviceId); }
        },
        methods: {
            prettyPrint: utils.prettyPrint,
        }
    }
</script>
