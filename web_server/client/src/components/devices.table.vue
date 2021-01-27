<template>
    <md-card>
        <b-pagination
                v-model="currentPage"
                :total-rows="devices.length"
                :per-page="pageSize"
                aria-controls="devices-table"
                align="fill"
                v-if="devices.length !== 0"
        />
        <b-table striped hover small
                 id="devices-table"
                 :items="devices"
                 :per-page="pageSize"
                 :current-page="currentPage"
                 :fields="fields"
                 :busy="isBusy && devices.length === 0"
        >
            <template v-slot:table-busy>
                <div class="text-center text-danger my-2 p-5">
                    <b-spinner class="align-middle"></b-spinner>
                    <strong class="ml-1">Loading ...</strong>
                </div>
            </template>

            <template v-slot:cell(device_id)="data">
                <md-icon :style="'color: ' + getColor(data.value)">label</md-icon>
                <router-link :to="'/devices/' + data.value" class="link">
                    {{ (data.value) }}
                </router-link>
            </template>

        </b-table>
    </md-card>
</template>

<script>
    import {mapActions, mapGetters} from 'vuex';
    import config from "../config";
    import colorsHelper from "../common/colors.helper"

    export default {
        name: "DevicesList",
        props: {
            deviceGroup: {required: false, type: String},
            deviceType: {required: false, type: String},
            pageSize: {type: Number, default: config.PAGE_SIZE}
        },
        computed: {
            ...mapGetters("device", ["getAllDevices", "getAllDevicesByType", "getAllDevicesByGroup", "getAllDevicesByGroupAndType"]),
            devices () {
                if (this.deviceGroup && this.deviceType)
                    return this.getAllDevicesByGroupAndType(this.deviceGroup, this.deviceType);
                if (this.deviceGroup)
                    return this.getAllDevicesByGroup(this.deviceGroup);
                if (this.deviceType)
                    return this.getAllDevicesByType(this.deviceType);
                return this.getAllDevices;
            },
            fields () {
                if (this.devices.length > 0) return ['device_id', 'device_group', 'device_type'];
                return [];
            }
        },
        methods: {
            getColor: colorsHelper.getColor
        },
        data () {
            return ({
                isBusy: true,
                currentPage: 1,
            })
        },
        mounted () {
            setTimeout(() => this.isBusy = false, 15000);
        }
    }
</script>