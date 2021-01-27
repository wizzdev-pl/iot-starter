<template>
    <div>
        <div class="mb-3 w-100">
            <b class="md-headline p-3 text-center"> Devices </b>
        </div>

        <md-card class="p-2">
            <b> Filters </b>
            <div class="md-layout md-gutter">
                <div class="md-layout-item">
                    <b-select v-model="deviceGroup" :options="deviceGroupSelectOptions"/>
                </div>
                <div class="md-layout-item">
                    <b-select v-model="deviceType" :options="deviceTypeSelectOptions"/>
                </div>
            </div>
        </md-card>
        <div class="md-layout md-gutter mt-5">
            <div class="md-layout-item">
                <DevicesList :device-group="deviceGroup" :device-type="deviceType" :pageSize="pageSize" class="mt-2"/>
            </div>
        </div>
    </div>
</template>

<script>
    import {mapActions, mapGetters} from 'vuex';
    import DevicesList from "../components/devices.table"
    import utils from "../common/utils";

    export default {
        name: "DashboardView",
        components: {DevicesList},
        computed: {
            ...mapGetters("deviceGroup", {deviceGroups: "getAllDeviceGroups"}),
            ...mapGetters("deviceType", {deviceTypes: "getAllDeviceTypes"}),
            deviceGroupSelectOptions () {
                return [{value: null, text: "Select device group"}].concat(
                    this.deviceGroups.map(g => ({value: g.device_group, text: utils.prettyPrint(g.device_group)}))
                )
            },
            deviceTypeSelectOptions () {
                return [{value: null, text: "Select device type"}].concat(
                    this.deviceTypes.map(t => ({value: t.device_type, text: utils.prettyPrint(t.device_type)}))
                )
            }
        },
        data () {
            return ({
                deviceGroup: null,
                deviceType: null,
                pageSize: 15
            })
        },
    }
</script>

<style scoped>

</style>