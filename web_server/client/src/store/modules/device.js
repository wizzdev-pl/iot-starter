import Mutations from "../mutations";
import Actions from "../actions";

export default {
    namespaced: true,
    state: {items: [],},
    getters: {
        getDevice: (state) => (deviceID) => state.items.filter(device => device.device_id === deviceID)[0] || null,
        getAllDevices: (state) => state.items,
        getAllDevicesByGroup: (state) => (groupName) => {
            return state.items.filter(device => (device.device_group === groupName))
        },
        getAllDevicesByType: (state) => (typeName) => {
            return state.items.filter(device => (device.device_type === typeName))
        },
        getAllDevicesByGroupAndType: (state) => (groupName, typeName) => {
            return state.items.filter(device => (device.device_type === typeName) && (device.device_group === groupName))
        }
    },
    mutations: (new Mutations()).getCrud(),
    actions: (new Actions('/Device/')).getBase()
}

