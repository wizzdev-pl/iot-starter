<template>
    <DeviceView>
        <div class="ml-5 mr-5">

            <!-- Datetime Select -->
            <b-container v-if="!isBusy && device" class="mt-3" fluid>
                <b-row v-if="isSelectChosen">
                    <b-col md="11" sm="10" cols="9" class="p-1">
                        <b-select v-model="minTimestampTemp"
                                  :options="selectTimeRangeOptions"
                        />
                    </b-col>
                    <b-col md="1" sm="2" cols="3">
                        <md-button class="md-primary md-raised" v-on:click="isSelectChosen = !isSelectChosen">
                            <md-icon>compare_arrows</md-icon>
                        </md-button>
                    </b-col>
                </b-row>
                <b-row v-if="!isSelectChosen">
                    <b-col md="11" sm="10" cols="9" class="p-1">
                        <b-row>
                            <b-col>
                                From:
                                <DataPicker v-model="minTimestampDate" :format="datetimeFormat"/>
                            </b-col>
                            <b-col>
                                To:
                                <DataPicker v-model="maxTimestampDate" :format="datetimeFormat"/>
                            </b-col>
                        </b-row>
                        <b-row class="pr-3 pl-3 pt-2">
                            <md-button class="w-100 m-auto md-raised" v-on:click="acceptSelectedDateFromDatePicker()">
                                <strong>Update chart</strong>
                            </md-button>
                        </b-row>
                    </b-col>
                    <b-col md="1" sm="2" cols="3">
                        <md-button class="md-primary md-raised" v-on:click="isSelectChosen = !isSelectChosen">
                            <md-icon>compare_arrows</md-icon>
                        </md-button>
                    </b-col>
                </b-row>
            </b-container>

            <!-- Loading -->
            <div class="md-layout mt-3" v-if="isBusy  || !device">
                <div class="md-layout-item text-center text-danger">
                    <b-spinner class="align-middle mb-2"></b-spinner>
                    <br>
                    <strong> Loading... </strong>
                </div>
            </div>

            <!-- Charts -->
            <div class="md-layout mt-4" v-if="!isBusy">
                <div class="md-layout-item">
                    <MeasurementTypesChart :device-id="deviceId"
                                           :min-timestamp="minTimestamp"
                                           :max-timestamp="maxTimestamp"
                                           :height-in-v-h="50"/>
                </div>
            </div>
        </div>
    </DeviceView>
</template>

<script>
    import moment from "moment"
    import DataPicker from 'vuejs-datetimepicker';
    import {mapGetters, mapActions} from 'vuex';

    import utils from "../common/utils";
    import MeasurementTypesChart from '../components/measurement_types.charts';
    import DeviceView from "../views/device.view";

    export default {
        name: "DeviceViewMeasurements",
        components: {MeasurementTypesChart, DeviceView, DataPicker},
        props: {"view": Number},
        computed: {
            ...mapGetters("device", ["getDevice"]),
            deviceId() {
                return this.$route.params.id;
            },
            device() {
                return this.getDevice(this.deviceId)
            }
        },
        methods: {
            ...mapActions("measurement", ["loadMeasurementsForDevice"]),
            getHoursInMilliseconds(hours) {
                return hours * 60 * 60 * 1000;
            },
            acceptSelectedDateFromDatePicker() {
                debugger;
                this.minTimestamp = moment(this.minTimestampDate, this.datetimeFormatForMoment).valueOf();
                this.maxTimestamp = moment(this.maxTimestampDate, this.datetimeFormatForMoment).valueOf();
                return this.loadNewDataSet();
            },
            loadNewDataSet() {
                if (this.device) {
                    this.isBusy = true;
                    this.loadMeasurementsForDevice({
                        deviceId: this.deviceId,
                        minTimestamp: this.minTimestamp,
                        maxTimestamp: this.maxTimestamp
                    }).then(() => setTimeout(() => this.isBusy = false, 1000));
                }
            },
        },
        data() {
            let datetimeFormatForMoment = "DD/MM/YYYY H:m:s";
            return ({
                isSelectChosen: true,
                isBusy: false,
                datetimeFormat: datetimeFormatForMoment.replace('m', 'i'),
                datetimeFormatForMoment: datetimeFormatForMoment,
                minTimestamp: utils.getDefaultMinTimestamp(),
                maxTimestamp: utils.getCurrentTimestamp(),
                minTimestampDate: moment(utils.getDefaultMinTimestamp()).format(datetimeFormatForMoment),
                maxTimestampDate: moment().format(datetimeFormatForMoment),
                minTimestampTemp: utils.getDefaultMinTimestamp(),
                selectTimeRangeOptions: [
                    {value: utils.getCurrentTimestamp() - this.getHoursInMilliseconds(6), text: "Last 6 hours"},
                    {value: utils.getCurrentTimestamp() - this.getHoursInMilliseconds(24), text: "Last day"},
                    {value: utils.getCurrentTimestamp() - this.getHoursInMilliseconds(24 * 7), text: "Last 7 days"},
                    {
                        value: utils.getCurrentTimestamp() - this.getHoursInMilliseconds(24 * 30),
                        text: "Last 30 days"
                    },
                ]
            })
        },
        watch: {
            minTimestampTemp(newMinTimestamp) {
                this.minTimestamp = newMinTimestamp;
                this.minTimestampTemp = newMinTimestamp;
                this.loadNewDataSet();
            }
        }
    }
</script>

<style lang="css">
    #tab-measurements {
        min-height: 700px;
    }

    div.datetime-picker {
        float: right;
        width: calc(100% - 45px)
    }
</style>