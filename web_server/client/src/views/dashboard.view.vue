<template>
    <div>
        <div class="md-layout md-gutter mt-3">
            <div class="md-layout-item">
                <b class="md-headline mb-5 p-3 text-center"> Measurements - Charts </b>
                <MeasurementTypesCharts class="mt-2"/>
            </div>
        </div>
        <div class="md-layout md-gutter mt-5">
            <div class="md-layout-item">
                <b class="md-headline p-3 text-center"> All Devices
                    <router-link to="/devices/">
                        <md-icon class="pb-1">launch</md-icon>
                    </router-link>
                </b>
                <DevicesList class="mt-2"/>
            </div>
            <div class="md-layout-item">
                <b class="md-headline p-3 text-center"> Last Measurements </b>
                <MeasurementsList class="mt-2"/>
            </div>
        </div>
    </div>
</template>

<script>
    import DevicesList from "../components/devices.table"
    import MeasurementsList from "../components/measurements.table"
    import MeasurementTypesCharts from "../components/measurement_types.charts"

    export default {
        name: "DashboardView",
        components: {DevicesList, MeasurementsList, MeasurementTypesCharts}
    }
</script>

<style scoped>

</style>