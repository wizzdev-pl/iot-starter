import Vue from 'vue'
import VueI18n from 'vue-i18n'


Vue.use(VueI18n);


const messages = {
    en: {
        title: "Wizzdev IoT",
        loadingInfo: "Still loading data. Please wait ...",
        cannotAddNewDevice: "Cannot add new device",
        cannotGetList: "Cannot communicate with API. Please try again later.",
        devices: "Devices",
        deviceID: "Device ID",
        deviceDescription: "Description",
        deviceGroup: "Group",
        deviceType: "Type",
        deviceGroups: "Device Groups",
        deviceTypes: "Device Types",
        deviceGroupDescription: "Device Group Description",
        deviceTypeDescription: "Device Type Description",
        cannotGetListOfDeviceGroups: "Cannot get list of device groups. Please try again later.",
        measurements: "Measurements",
        measurementType: "Measurement Type",
        measurementDate: "Read Date",
        measurementValue: "Read Value",
    }
};
const i18n = new VueI18n({
    locale: 'en', messages
});


export default i18n