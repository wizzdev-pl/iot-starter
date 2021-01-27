import axios from "axios";
import Vue from "vue";

import Configuration from "../config";


export default class ApiHelper {
    constructor (base_url) {
        this.base_url = base_url
    }

    /* Save gathered items from API to items array
    * Available options:
    * queryParams: {name=value} - get arguments
    * suffix: string - added to url after base url
    * skipError: boolean - do not toast error message
    */
    async getList (context, action, options) {
        options = (options || {});
        let url = Configuration.API_BASE_URL + this.base_url + (options.suffix || "");
        axios.get(url, {params: (options.queryParams)})
            .then(response => {
                context.commit(action, ApiHelper.normalizeData(response.data['data']));
                return response.data['data'];
            })
            .catch(error => {
                if (options.skipError !== true) this.toastApiError(undefined, error);
                return null;
            });
    }

    /* Save gathered item from API to items object under selected key
    * Available options:
    * queryParams: {name=value} - get arguments
    * suffix: string - added to url after base url
    * skipError: boolean - do not toast error message
    */
    async getOne (context, action, itemKey, options) {
        options = (options || {});
        let url = Configuration.API_BASE_URL + this.base_url + (options.suffix || "");
        axios.get(url, {params: (options.queryParams)})
            .then(response => {
                context.commit(action, {itemKey: itemKey, data: response.data['data']});
                return response.data['data'];
            })
            .catch(error => {
                if (options.skipError !== true) this.toastApiError(undefined, error);
                return null
            });
    }

    /* Create notification for user about error */
    toastApiError (message, error) {
        Vue.toasted.error(
            message ? message : this.createStandardApiErrorMessage() + '<br>' + error, {
                duration: Configuration.TOAST_DISPLAY_TIME_IN_MS, // How long it would be displayed in milliseconds
                action: {
                    text: 'Hide',
                    onClick: (e, toastObject) => {
                        toastObject.goAway(0);
                    }
                },
            });
        if (Configuration.DEBUG) console.log(error);
    }

    /* Create standard generic api error message for user
    *  Argument "customUrl" is optional, if empty, the base_url would be taken */
    createStandardApiErrorMessage (customUrl) {
        let url = customUrl || this.base_url;
        return url + ": Cannot communicate with API. Please try again later."
    }

    /* Removes deleted files and 'is_delete' property from provided array of objects */
    static normalizeData (data) {
        return data.filter((i) => !i.is_removed).map((i) => {
            delete i.is_removed;
            return i
        });
    }
}