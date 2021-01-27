import GenericMutations from "../mutations";
import Actions from "../actions";

export default {
    namespaced: true,
    state: {items: []},
    getters: {
        getAllDeviceGroups: (state) => state.items
    },
    mutations: (new GenericMutations()).getCrud(),
    actions: (new Actions("/DeviceGroup/")).getBase(),
}