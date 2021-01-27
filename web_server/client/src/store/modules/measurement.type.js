import GenericMutations from "../mutations";
import Actions from "../actions";

export default {
    namespaced: true,
    state: {items: []},
    getters: {
        getAllMeasurementTypes: (state) => state.items.sort((m1, m2) => m2.priority - m1.priority),
        getMeasurementTypeLabel: (state) => (measurementTypeName) => {
                let label = state.items.filter(mt => mt.name === measurementTypeName)[0].label;
                if (label) return label;
                return measurementTypeName;
            }
    },
    mutations: (new GenericMutations()).getCrud(),
    actions: (new Actions("/MeasurementType/")).getBase(),
}