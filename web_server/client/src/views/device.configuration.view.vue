<template>
    <DeviceView>
        <div class="m-5">
            <md-empty-state v-if="!configuration"
                            class="md-accent"
                            md-icon="cloud_off"
                            md-label="Getting device shadow error"
                            md-description="Couldn't get device configuration. Please try again letter."
            />
            <b-container>
                <b-row v-if="configuration" id="configuration-list">
                    <b-col sm="6" md="4" v-for="(value, key) in configuration" v-bind:key="key" class="p-1">
                        <strong> {{ key }}: </strong> <br> <span> {{value}} </span>
                    </b-col>
                </b-row>
            </b-container>
        </div>
    </DeviceView>
</template>

<script>
    import {mapActions, mapGetters} from 'vuex';
    import DeviceView from '../views/device.view';

    export default {
        name: "DeviceViewConfiguration",
        components: {DeviceView},
        computed: {
            ...mapGetters("device", ["getDevice"]),
            ...mapGetters("deviceShadow", ["getDeviceShadow"]),
            configuration() {
                if (this.shadow)
                    return this.shadow['config'];
                return null
            },
            deviceId() {
                return this.$route.params.id;
            },
            device() {
                return this.getDevice(this.deviceId);
            },
            shadow() {
                return this.getDeviceShadow(this.deviceId);
            },
            errors() {
                if (this.shadow)
                    return this.shadow['errors'];
                return null
            }
        },
        data: () => ({
            shadowLoadTries: 0,
            deviceLoadTries: 0,
            maxLoadTries: 5,
            _shadow: null
        }),
        methods: {
            ...mapActions("deviceShadow", ["loadDeviceShadow"]),
            ...mapActions("device", {loadDevice: "loadItem"}),
            async loadShadow() {
                Promise.all([() => {
                    let _shadow = this.getDeviceShadow(this.deviceId);
                    while (!_shadow && this.shadowLoadTries++ <= this.maxLoadTries) {
                        this.loadDeviceShadow(this.deviceId).then(() => {
                            _shadow = this.getDeviceShadow(this.deviceId);
                        });
                    }
                    return _shadow
                }]).then(shadow => {
                    this.shadow = shadow
                })
            }
        },
        mounted() {
            this.loadShadow();
        }
    }
</script>

<style lang="css">
    #configuration-list {
        column-count: 4;
    }
</style>
