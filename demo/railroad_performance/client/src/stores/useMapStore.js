import { defineStore } from 'pinia';
import mapboxgl from "mapbox-gl";
import 'mapbox-gl/dist/mapbox-gl.css';

export const useMapStore = defineStore('mapdata', {
    state: () => ({
        publicpath: import.meta.env.BASE_URL,
        route_station: undefined,
        route_dataset: undefined,
        station: undefined,
        station_dataset: undefined
    }),
    actions: {
        loadStationData(type, station_name)
        {   
            if (type == 'route'){
                if(! this.route_station) {
                    let file_name = '/public/amtrak-route.geojson'
                    this.route_dataset = file_name
                }
                else {
                    this.route_station = station_name
                }
            }
            else {
                if(! this.station) {
                    let file_name = '/public/amtrak-stations.geojson'
                    this.station_dataset = file_name
                }
                else {
                    this.station = station_name
                }
            }
           
        },
        createMap(map_id) 
        {   
            mapboxgl.accessToken = 'pk.eyJ1Ijoic291bWV5YWsiLCJhIjoiY2w5eW9uZ3J0MDczODNwbzJ4bGN2ZzJsdyJ9.q47T3SNXyRzUNBTpVNQkDQ';
            const map = new mapboxgl.Map({
                    container: map_id,
                    style: 'mapbox://styles/mapbox/streets-v11',
                    center: [-103.5917, 40.6699],
                    zoom: 4
                });
            if (map_id == 'route')
            {
                map.on('load', () => {
            
                    map.addSource('route', {
                    type: 'geojson',
                    data: this.route_dataset,
                    });
                    map.addLayer({
                        'id' : 'route',
                        'type' : 'line',
                        'source' : 'route',
                        'layout': {
                            'line-join': 'round',
                            'line-cap': 'round'
                            },
                        'paint': {
                                'line-color': 'red',
                                'line-width': 1
                                }
                    });
                }); 
            }
            else {
                map.on('load', () => {
                    map.loadImage(
                        'https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png',
                        (error, image) => {
                        if (error) throw error;
                        map.addImage('custom-marker', image);
                        map.addSource('station', {
                            type: 'geojson',
                            data: this.station_dataset,
                            cluster: true,
                            clusterMaxZoom: 14, // Max zoom to cluster points on
                            clusterRadius: 50
                            });
                            map.addLayer({
                                id: 'clusters',
                                type: 'circle',
                                source: 'station',
                                filter: ['has', 'point_count'],
                                paint: {
                                // Use step expressions (https://docs.mapbox.com/mapbox-gl-js/style-spec/#expressions-step)
                                // with three steps to implement three types of circles:
                                //   * Blue, 20px circles when point count is less than 100
                                //   * Yellow, 30px circles when point count is between 100 and 750
                                //   * Pink, 40px circles when point count is greater than or equal to 750
                                'circle-color': [
                                'step',
                                ['get', 'point_count'],
                                '#51bbd6',
                                100,
                                '#f1f075',
                                750,
                                '#f28cb1'
                                ],
                                'circle-radius': [
                                'step',
                                ['get', 'point_count'],
                                20,
                                100,
                                30,
                                750,
                                40
                                ]
                                }
                                });
                                 
                                map.addLayer({
                                id: 'cluster-count',
                                type: 'symbol',
                                source: 'station',
                                filter: ['has', 'point_count'],
                                layout: {
                                'text-field': ['get', 'point_count_abbreviated'],
                                'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
                                'text-size': 12
                                }
                                });
                                 
                                map.addLayer({
                                id: 'unclustered-point',
                                type: 'symbol',
                                source: 'station',
                                filter: ['!', ['has', 'point_count']],
                                'layout': {
                                    'icon-image': 'custom-marker',
                                    // get the title name from the source's "title" property
                                    'text-field': ['get', 'title'],
                                    'text-font': [
                                    'Open Sans Semibold',
                                    'Arial Unicode MS Bold'
                                    ],
                                    'text-offset': [0, 1.25],
                                    'text-anchor': 'top'
                                    }
                                });
                                 
                                // inspect a cluster on click
                                map.on('click', 'clusters', (e) => {
                                const features = map.queryRenderedFeatures(e.point, {
                                layers: ['clusters']
                                });
                                const clusterId = features[0].properties.cluster_id;
                                map.getSource('station').getClusterExpansionZoom(
                                clusterId,
                                (err, zoom) => {
                                if (err) return;
                                 
                                map.easeTo({
                                center: features[0].geometry.coordinates,
                                zoom: zoom
                                });
                                }
                                );
                                });
                                 
                                // When a click event occurs on a feature in
                                // the unclustered-point layer, open a popup at
                                // the location of the feature, with
                                // description HTML from its properties.
                                map.on('click', 'unclustered-point', (e) => {
                                const coordinates = e.features[0].geometry.coordinates.slice();
                                const mag = e.features[0].properties.mag;
                                const tsunami =
                                e.features[0].properties.tsunami === 1 ? 'yes' : 'no';
                                 
                                // Ensure that if the map is zoomed out such that
                                // multiple copies of the feature are visible, the
                                // popup appears over the copy being pointed to.
                                while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
                                }
                                 
                                new mapboxgl.Popup()
                                .setLngLat(coordinates)
                                .setHTML(
                                `magnitude: ${mag}<br>Was there a tsunami?: ${tsunami}`
                                )
                                .addTo(map);
                                });
                                 
                                map.on('mouseenter', 'clusters', () => {
                                map.getCanvas().style.cursor = 'pointer';
                                });
                                map.on('mouseleave', 'clusters', () => {
                                map.getCanvas().style.cursor = '';
                                });       
                        });
                }); 
            }
                    
                    
        }
    }
})