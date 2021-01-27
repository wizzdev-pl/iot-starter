<template>
    <LineChart
            :chartData="dataCollection"
            :chartId="chartName"
            :unit="measurementTypeUnit"
    />
</template>

<script>
    import {mapActions, mapGetters} from 'vuex';
    import {LTD} from 'downsample';
    import moment from 'moment';
    import LineChart from "../common/line.chart"
    import config from "../config";
    import colorHelper from "../common/colors.helper"
    import utils from "../common/utils"

    export default {
        name: "MeasurementsChart",
        components: {LineChart},
        props: {
            measurementType: {
                required: true,
                type: String
            },
            measurementTypeUnit: {
                required: true,
                type: String
            },
            deviceId: {
                required: false,
                type: String
            },
            deviceType: {
                required: false,
                type: String
            },
            deviceGroup: {
                required: false,
                type: String
            },
            minTimestamp: {
                required: false,
                type: Number
            },
            maxTimestamp: {
                required: false,
                type: Number
            },
            maxChartPoints: {
                required: false,
                type: Number
            }
        },
        computed: {
            ...mapGetters("device", [
                    "getDevice",
                    "getAllDevices",
                    "getAllDevicesByGroup",
                    "getAllDevicesByType",
                    "getAllDevicesByGroupAndType"
                ]
            ),
            ...mapGetters("measurement", [
                    "getAllMeasurementsFromSelectedTime",
                    "getAllMeasurementsByDeviceFromSelectedTime",
                    "getAllMeasurementsByTypeFromSelectedTime",
                    "getMeasurementsByTypeAndDeviceFromSelectedTime"
                ]
            ),
            maxChartPointsPerLine () {
                if (this.maxChartPoints) return this.maxChartPoints;
                return config.MAX_CHART_POINTS
            },
            minimumTimestamp () {
                if (this.minTimestamp) return this.minTimestamp;
                return utils.getDefaultMinTimestamp();
            },
            maximumTimestamp () {
                if (this.maxTimestamp) return this.maxTimestamp;
                return utils.getCurrentTimestamp();
            },
            dataCollection () {
                let datasets = [];
                this.deviceIds.forEach((deviceId) => {
                    let rawData = this.getMeasurementsByTypeAndDeviceFromSelectedTime(
                        deviceId, this.measurementType, this.minimumTimestamp, this.maximumTimestamp
                    ).map(m => ({x: m.timestamp, y: m.value})).sort((f, s) => f.x < s.x);
                    // let chartData = this.normalizeChartData(rawData);
                    let chartData = LTD(rawData, config.MAX_CHART_POINTS);
                    datasets.push({
                        label: deviceId,
                        data: chartData,
                        borderColor: colorHelper.getColor(deviceId),
                        fill: false,
                        cubicInterpolationMode: 'monotone'
                    });
                });
                return {datasets}
            },
            deviceIds () {
                if (this.deviceId)
                    return [this.deviceId];
                if (this.deviceGroup && this.deviceType)
                    return this.getDeviceIdsFromDeviceObjects(
                        this.getAllDevicesByGroupAndType(this.deviceGroup, this.deviceType)
                    );
                if (this.deviceGroup)
                    return this.getDeviceIdsFromDeviceObjects(
                        this.getAllDevicesByGroup(this.deviceGroup)
                    );
                if (this.deviceType)
                    return this.getDeviceIdsFromDeviceObjects(
                        this.getAllDevicesByType(this.deviceType)
                    );
                return this.getDeviceIdsFromDeviceObjects(this.getAllDevices);
            },
            chartName () {
                return (Number.parseFloat(Math.random()).toFixed(100) * Math.pow(10, 100)).toString()
            }
        },
        methods: {
            ...mapActions("measurementType", {loadMeasurementTypes: "loadItems"}),
            ...mapActions("measurement", {loadMeasurements: "loadItems"}),
            getDeviceIdsFromDeviceObjects (devicesObjects) {
                return devicesObjects.map(d => d.device_id)
            },
            measurementsByDeviceId (deviceID) {
                return this.getAllMeasurementsByDeviceFromSelectedTime(
                    deviceID, this.minimumTimestamp, this.maximumTimestamp
                )
            },
            getDateFromTimestamp (timestamp) {
                let time = moment(timestamp);
                return time.toDate();
            },
            getDateFromTimestampChartFormat (timestamp) {
                let time = moment(timestamp);
                return time.format('MM/DD/YYYY HH:mm')
            },
            normalizeChartData (data) {
                if (data) throw Error("Not implemented");
                let normalizedData = [];
                let normalizedDataSubsets = [];
                let newSubsetIndex = 0;
                for (let i = 1; i < data.length - 1; i++)
                    if (data[i].x + config.BREAK_POINT_VALUE < data[i + 1].x)
                        normalizedDataSubsets.push(data.slice(newSubsetIndex++, i + 1));
                normalizedDataSubsets.push(data.slice(newSubsetIndex++, data.length));
                for (let i = 0; i < normalizedDataSubsets.length; i++) {
                    let subsetData = normalizedDataSubsets[i];
                    let breakElement = subsetData[subsetData.length - 1];
                    breakElement.x += 1;
                    breakElement.y = false;
                    normalizedData = normalizedData.concat(
                        LTD(subsetData, config.MAX_CHART_POINTS / normalizedDataSubsets.length)
                    );
                    normalizedData.push(breakElement);
                }
                return normalizedDataSubsets.flat(1)

            }
        }
    }
</script>