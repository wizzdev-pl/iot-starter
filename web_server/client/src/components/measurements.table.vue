<template>
    <md-card>
        <b-pagination
                v-model="currentPage"
                :total-rows="measurements.length"
                :per-page="pageSize"
                aria-controls="measurements-table"
                align="fill"
                v-if="measurements.length !== 0"
        />

        <b-table striped hover small
                 id="measurements-table"
                 :items="measurements"
                 :per-page="pageSize"
                 :current-page="currentPage"
                 :busy="isBusy && measurements.length === 0"
        >
            <template v-slot:table-busy>
                <div class="text-center text-danger my-2 p-5">
                    <b-spinner class="align-middle"></b-spinner>
                    <strong class="ml-1">Loading ...</strong>
                </div>
            </template>

            <template v-slot:cell(timestamp)="data">
                {{ getDateFromTimestamp(data.value) }}
            </template>

            <template v-slot:cell(device_id)="data">
                <md-icon :style="'color: ' + getColor(data.value)">label</md-icon>
                <router-link :to="'/devices/' + data.value" class="link">
                    {{ (data.value) }}
                </router-link>
            </template>

            <template v-slot:cell(measurement_type)="data">
                {{ getMeasurementTypeLabel(data.value) }}
            </template>

            <template v-slot:cell(value)="data">
                {{ getNormalizedFloat(data.value) }}
            </template>

        </b-table>
    </md-card>
</template>

<script>
    import moment from 'moment'
    import config from "../config";
    import {mapActions, mapGetters} from 'vuex';
    import measurement from "../store/modules/measurement";
    import colorsHelper from "../common/colors.helper"

    export default {
        name: "MeasurementsList",
        props: ["deviceId", "measurementType"],
        computed: {
            ...mapGetters("measurement", {allMeasurements: "getAllMeasurements"}),
            ...mapGetters("measurementType", {getMeasurementTypeLabel: "getMeasurementTypeLabel"}),
            measurements () {
                let measurements = null;
                if (this.deviceId && this.measurementType)
                    measurements = this.getMeasurementsByTypeAndDevice(this.deviceId, this.measurementType);
                else if (this.deviceId)
                    measurements = this.getAllMeasurementsByDevice(this.deviceId);
                else if (this.measurementType)
                    measurements = this.getAllMeasurementsByType(this.measurementType);
                else measurements = this.allMeasurements;
                return measurements.sort((a, b) => b.timestamp - a.timestamp);
            }
        },
        methods: {
            ...mapGetters("measurement", ["getMeasurementsByTypeAndDevice", "getAllMeasurementsByDevice", "getAllMeasurementsByType"]),
            getDateFromTimestamp: (timestamp) => moment(timestamp).local().format('HH:mm DD-MM-YYYY'),
            getNormalizedFloat: (value) => value.toFixed(2),
            getColor: colorsHelper.getColor
        },
        mounted () {
            setTimeout(() => this.isBusy = false, 40000);
        },
        data () {
            return ({
                isBusy: true,
                currentPage: 1,
                pageSize: config.PAGE_SIZE
            })
        },
    }
</script>