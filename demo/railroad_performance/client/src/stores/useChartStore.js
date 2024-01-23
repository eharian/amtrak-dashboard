import { defineStore } from 'pinia';
import { displayTop10 } from '../views/station/js/barchart';
import { avgDelayLine } from '../views/station/js/linechart';
import { displayStack } from '../views/route/js/stackchart';
import * as d3 from 'd3';

export const useChartStore = defineStore('chart', {
  state: () => ({
    otp: undefined,
    otpcause: undefined,
    delaycause: undefined,
    ridership: undefined,
    amtrak: undefined,
    avgDelay: undefined,
    comp: undefined,
    line: undefined
  }),
  actions: {
    displayOTP() {
      const spec = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Amtrak Ontime Performance",
        "description": "Amtrak Ontime Performance from 2013 - 20121",
        "data": { "url": this.otp },
        "encoding": {
          "x": { "field": "Year", "type": "temporal" },
          "y": { "field": "Performance", "type": "quantitative" },
          "color": { "field": "Name", "type": "nominal" }
        },
        "width": 400,
        "height": 400,
        "layer": [
          {
            "encoding": {
              "x": { "field": "Year", "type": "temporal" },
              "y": { "field": "Performance", "type": "quantitative" },
              "color": { "field": "Name", "type": "nominal" }
            },
            "layer": [
              { "mark": "line" },
              {
                "params": [{
                  "name": "label",
                  "select": {
                    "type": "point",
                    "encodings": ["x"],
                    "nearest": true,
                    "on": "mouseover"
                  }
                }],
                "mark": "point",
                "encoding": {
                  "opacity": {
                    "condition": {
                      "param": "label",
                      "empty": false,
                      "value": 1
                    },
                    "value": 0
                  }
                }
              }
            ]
          },
          {
            "transform": [{ "filter": { "param": "label", "empty": false } }],
            "layer": [
              {
                "mark": { "type": "rule", "color": "gray" },
                "encoding": {
                  "x": { "type": "temporal", "field": "Year", "aggregate": "min" }
                }
              },
              {
                "encoding": {
                  "text": { "type": "quantitative", "field": "Performance" },
                  "x": { "type": "temporal", "field": "Year" },
                  "y": { "type": "quantitative", "field": "Performance" }
                },
                "layer": [
                  {
                    "mark": {
                      "type": "text",
                      "stroke": "white",
                      "strokeWidth": 2,
                      "align": "left",
                      "dx": 5,
                      "dy": -5
                    }
                  },
                  {
                    "mark": { "type": "text", "align": "left", "dx": 5, "dy": -5 },
                    "encoding": {
                      "color": { "type": "nominal", "field": "symbol" }
                    }
                  }
                ]
              }
            ]
          }
        ]

      };
      vegaEmbed("#vis", spec, { mode: "vega-lite" }).then(console.log).catch(console.warn);

    },
    displayOTPCause() {
      const spec2 = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Amtrak Ontime Performance Cause",
        "data": { "url": this.otpcause },
        "params": [
          {
            "name": "highlight",
            "select": {"type": "point", "on": "mouseover"}
          },
          {"name": "select", "select": "point"}
        ],
        "mark": {
          "type": "bar",
          "stroke": "black",
          "cursor": "pointer",
          "tooltip": true,
        },
        "encoding": {
          "x": {"field": "Year" },
          "y": { "field": "Hours", "type": "quantitative" },
          "xOffset": { "field": "Cause" },
          "color": { "field": "Cause" },
          "fillOpacity": {
            "condition": {"param": "select", "value": 1},
            "value": 0.3
          },
          "strokeWidth": {
            "condition": [
              {
                "param": "select",
                "empty": false,
                "value": 2
              },
              {
                "param": "highlight",
                "empty": false,
                "value": 1
              }
            ],
            "value": 0
          }
        },
        "width": 500,
        "height": 400
      };

      vegaEmbed("#vis-2", spec2, { mode: "vega-lite" }).then(console.log).catch(console.warn);

    },
    displayComp() {
      const spec3 = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Comparison of OTP on NorthBound and SouthBound Long distance trains",
        "data": { "url": this.comp },
        "params": [
          {
            "name": "highlight",
            "select": {"type": "point", "on": "mouseover"}
          },
          {"name": "select", "select": "point"}
        ],
        "mark": {
          "type": "bar",
          "stroke": "black",
          "cursor": "pointer",
          "tooltip": true,
        },
        "encoding": {
          "x": {"field": "Train" },
          "y": { "field": "OTP", "type": "quantitative" },
          "xOffset": { "field": "Direction" },
          "color": { "field": "Direction" },
          "fillOpacity": {
            "condition": {"param": "select", "value": 1},
            "value": 0.3
          },
          "strokeWidth": {
            "condition": [
              {
                "param": "select",
                "empty": false,
                "value": 2
              },
              {
                "param": "highlight",
                "empty": false,
                "value": 1
              }
            ],
            "value": 0
          }
        },
        "width": 500,
        "height": 400
      };

      vegaEmbed("#comp", spec3, { mode: "vega-lite" }).then(console.log).catch(console.warn);

    },
    displayDelayCause() {
      const spec4 = {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "title": "Reasons for Train Delay",
        "data": {"url": this.delaycause},
        "mark": "bar",
        "encoding": {
          "x": {
            "field": "Year",
            "type": "ordinal",
            "title": "Year"
          },
          "y": { "field": "Hours", "type": "quantitative" },
          "color": {
            "field": "Cause",
            "type": "nominal", 
          }
        },
        "width": 500,
        "height": 400
      }
      vegaEmbed("#vis-4", spec4, { mode: "vega-lite" }).then(console.log).catch(console.warn);
    },
    displayBarChart(id, reset_id, alpha, top5_id, bottom5_id, asc_id, des_id, all_id) {
      displayTop10(this.ridership, id, reset_id, alpha, top5_id, bottom5_id, asc_id, des_id, all_id);
    },
    displayLineChart(id, button_id) {
      avgDelayLine(this.amtrak, id, button_id)
    },
    displayStackedBar(id){
      displayStack(this.line, id)
    }
  }
});