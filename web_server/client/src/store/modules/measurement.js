import Actions from "../actions";
import utils from "../../common/utils";

const MeasurementsActions = new Actions('/Measurement/');

export default {
    namespaced: true,
    state: {items: []},
    getters: {
        getAllMeasurements: (state) => state.items,
        getAllMeasurementsByDevice: (state, getters) => (deviceID) => {
            return getters.getAllMeasurements.filter(m => m.device_id === deviceID)
        },
        getAllMeasurementsByType: (state, getters) => (measurementType) => {
            return getters.getAllMeasurements.filter(m => {
                return m.measurement_type === measurementType
            })
        },
        getMeasurementsByTypeAndDevice: (state, getters) => (deviceID, measurementType) => {
            return getters.getAllMeasurements.filter(m => (m.device_id === deviceID && m.measurement_type === measurementType))
        },
        getAllMeasurementsFromSelectedTime: (state, getters) => (minTimestamp, maxTimestamp) => {
            return getters.getAllMeasurements.filter(m => (minTimestamp < m.timestamp) && (m.timestamp < maxTimestamp))
        },
        getAllMeasurementsByDeviceFromSelectedTime: (state, getters) => (deviceID, minTimestamp, maxTimestamp) => {
            return getters.getAllMeasurementsByDevice(deviceID).filter(m => (minTimestamp < m.timestamp) && (m.timestamp < maxTimestamp));
        },
        getAllMeasurementsByTypeFromSelectedTime: (state, getters) => (measurementType, minTimestamp, maxTimestamp) => {
            return getters.getAllMeasurementsByType(measurementType).filter(m => (minTimestamp < m.timestamp) && (m.timestamp < maxTimestamp))
        },
        getMeasurementsByTypeAndDeviceFromSelectedTime: (state, getters) => (deviceID, measurementType, minTimestamp, maxTimestamp) => {
            return getters.getMeasurementsByTypeAndDevice(deviceID, measurementType).filter(m => (minTimestamp < m.timestamp) && (m.timestamp < maxTimestamp))
        }
    },
    mutations: {
        ADD_ITEM: (state, newItem) => state.items.push(newItem),
        ADD_ITEMS: (state, newItems) => state.items = newItems,
        ADD_ITEMS_FOR_DEVICE: (state, newItems) => {
            if (newItems.length > 0) {
                let device_id = newItems[0].device_id;
                state.items = state.items
                    .filter(item => item.device_id !== device_id)
                    .concat(newItems);
            }
        }
    },
    actions: {
        loadItems: async (context) => {
            const minTimestamp = utils.getDefaultMinTimestamp();
            return MeasurementsActions.apiHelper.getList(context, "ADD_ITEMS", {queryParams: {minTimestamp}})
        },
        loadMeasurementsForDevice: async (context, {deviceId, minTimestamp, maxTimestamp}) => {
            return MeasurementsActions.apiHelper.getList(context, "ADD_ITEMS_FOR_DEVICE", {
                queryParams: {minTimestamp: minTimestamp, maxTimestamp: maxTimestamp},
                suffix: deviceId + "/",
                skipFilter: true
            })
        }
    }
}


