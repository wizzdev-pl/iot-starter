import GenericMutations from "../mutations";
import Actions from "../actions";

export default {
    namespaced: true,
    state: {items: []},
    getters: {
        getAllDeviceTypes: (state) => state.items
    },
    mutations: (new GenericMutations()).getCrud(),
    actions: (new Actions("/DeviceType/")).getBase(),
}