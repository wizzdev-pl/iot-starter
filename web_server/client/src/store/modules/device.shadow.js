import Vue from 'vue';

import Actions from "../actions";


const DeviceShadowActions = new Actions('/Device/');


export default {
    namespaced: true,
    state: {items: ({}),},
    getters: {
        getDeviceShadow: (state) => (deviceID) => state.items[deviceID] || undefined,
        getAllDeviceShadows: (state) => state.items
    },
    mutations: {
        ADD_ONE_ITEM: (state, {itemKey, data}) => {
            Vue.set(state.items, itemKey, data);
        }
    },
    actions: {
        loadDeviceShadow: async (context, deviceID) => {
            return 1
            /*DeviceShadowActions.apiHelper.getOne(context, "ADD_ONE_ITEM", deviceID, {
                suffix: deviceID + "/shadow", skipError: true
            })*/
        }
    }
}

