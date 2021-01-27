import ApiHelper from "../common/api.helper";

class Actions {
    constructor (baseURL) {
        this.apiHelper = new ApiHelper(baseURL);
    }

    getBase () {
        return {
            loadItems: async (context) => this.apiHelper.getList(context, "ADD_ITEMS"),
            loadItem: async (context, itemID) => this.apiHelper.getList(context, "ADD_ITEM", {suffix: itemID})
        };
    }
}

export default Actions;
