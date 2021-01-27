import {Line} from 'vue-chartjs'
import "chartjs-plugin-zoom"

export default {
    extends: Line,
    props: ['chartData', "unit"],
    computed: {
        dates: function () {
            return this.chartData.datasets.map(dataset => dataset.data).flat().map(entry => entry.x);
        },
        values: function () {
            return this.chartData.datasets.map(dataset => dataset.data).flat().map(entry => entry.y);
        },
        xMin: function () {
            return Math.min(...this.dates)
        },
        xMax: function () {
            return Math.max(...this.dates)
        },
        yMin: function () {
            return Math.min(...this.values)
        },
        yMax: function () {
            return Math.max(...this.values)

        },
        options: function () {
            const measurementTypeUnit = this.unit;
            return {
                normalized: true,
                responsive: true,
                maintainAspectRatio: false,
                animation: {duration: 0},
                legend: {
                    position: 'bottom',
                },
                scales: {
                    xAxes: [{
                        type: 'time',
                        display: true,
                        scaleLabel: {
                            display: true,
                            labelString: 'Date'
                        },
                        time: {
                            tooltipFormat: 'YYYY-MM-DD HH:mm',
                            displayFormats: {
                                millisecond: 'HH:mm:ss.SSS',
                                second: 'HH:mm:ss',
                                minute: 'HH:mm',
                                hour: 'MMM D HH:mm',
                                day: "MMM D HH:mm"
                            }
                        },
                        ticks: {
                            maxTicksLimit: 30,
                            source: 'auto',
                            major: {
                                fontStyle: 'bold',
                                fontColor: '#FF0000'
                            }
                        }
                    }],
                    yAxes: [{
                        display: true,
                        ticks: {
                            callback: function (value, index, values) {
                                if (measurementTypeUnit) return value + measurementTypeUnit;
                                return value;
                            }
                        },
                        scaleLabel: {
                            display: true,
                        }
                    }]
                },
                plugins: {
                    zoom: {
                        pan: {
                            enabled: true,
                            mode: 'xy',
                            rangeMin: {x: this.xMin - 1000, y: this.yMin - 10},
                            rangeMax: {x: this.xMax + 1000, y: this.yMax + 10}
                        },
                        zoom: {
                            enabled: true,
                            mode: "xy",
                            threshold: 0.1,
                            speed: 0.1,
                            rangeMin: {x: this.xMin - 1000, y: this.yMin - 10},
                            rangeMax: {x: this.xMax, y: this.yMax}
                        }
                    }
                }
            }
        }
    },
    watch: {
        chartData (newData, oldData) {
            this.renderChart(newData, this.options)
        }
    },
    mounted () {
        this.renderChart(this.chartData, this.options)
    },
}
