<template>
    <div>
        <md-card v-if="measurementTypes.length === 0 || measurements.length === 0" style="background-color: rgba(0,0,0,0.05); " >
            <div class="text-center text-danger my-2 p-5" style="opacity: 0.6">
                <b-spinner class="align-middle mr-1"></b-spinner>
                <strong>Loading ...</strong>
            </div>
        </md-card>
        <md-card v-if="measurementTypes.length > 0 && measurements.length > 0">
            <md-tabs id="measurements-menu"
                     class="md-accent"
                     md-alignment="centered"
                     :md-active-tab="measurementTypes[0].name">
                <md-tab v-for="measurementType in measurementTypes"
                        :md-label="measurementType.label"
                        :key="measurementType.name"
                        :id="measurementType.name"
                >
                    <MeasurementsChart
                            :id="measurementType.name"
                            :max-chart-points="maxChartPoints"
                            :measurement-type="measurementType.name"
                            :measurement-type-unit="measurementType.unit"
                            :device-id="deviceId"
                            :device-type="deviceType"
                            :min-timestamp="minTimestamp"
                            :style="`height: ${heightInVH}vh; position: relative`"
                    />
                </md-tab>
            </md-tabs>
        </md-card>
    </div>
</template>

<script>
    import {mapActions, mapGetters} from 'vuex';
    import MeasurementsChart from './measurements.chart'
    import Configuration from "../config";

    export default {
        name: "MeasurementTypesCharts",
        components: {MeasurementsChart},
        props: {
            deviceId: {required: false, type: String},
            deviceType: {required: false, type: String},
            minTimestamp: {required: false, type: Number},
            maxTimestamp: {required: false, type: Number},
            heightInVH: {default: 35, type: Number},
        },
        computed: {
            ...mapGetters("measurementType", {measurementTypes: "getAllMeasurementTypes"}),
            ...mapGetters("measurement", {measurements: "getAllMeasurements"})
        },
        data () {
            return ({
                maxChartPoints: Configuration.MAX_CHART_POINTS
            })
        }
    }
</script>

<style lang="css">
    #measurements-menu .md-tabs-navigation {
        background-color: #007bff !important;
    }

    #measurements-menu .md-tabs-navigation .md-button-content {
        color: white !important;
    }
</style>