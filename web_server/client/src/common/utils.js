import moment from "moment";
import config from "../config";

export default {
    getTimezoneOffset() {
        // Return timezone offset in milliseconds
        return (new Date()).getTimezoneOffset() * 60 * 1000;
    },
    getCurrentTimestamp () {
        // Return current unix utc timestamp
        return moment().utc().valueOf()
    },
    getDefaultMinTimestamp () {
        return this.getCurrentTimestamp() - config.DEFAULT_MIN_TIMESTAMP_RANGE
    },
    prettyPrint (string) {
        // Change underscore string into nice looking sentence with all words capitalized
        if (!string) return "";
        return string
            .split('_')
            .map(word => word.toLowerCase())
            .map(word => word.charAt(0).toUpperCase() + word.slice(1))
            .join(" ");
    },
}