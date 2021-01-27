export default {
    getColor (id) {
        const colorId = "color-" + id;
        let color = localStorage.getItem(colorId);
        if (!color) {
            color = "#"+((1<<24)*Math.random()|0).toString(16);
            localStorage.setItem(colorId, color);
        }
        return color;
    }
}