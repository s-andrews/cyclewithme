$( document ).ready(function() {
    load_map()
});


function load_map() {

    let map = new OpenLayers.Map("map1");

    let mapnik = new OpenLayers.Layer.OSM();

    let fromProjection = new OpenLayers.Projection("EPSG:4326");   // Transform from WGS 1984
    let toProjection   = new OpenLayers.Projection("EPSG:900913"); // to Spherical Mercator Projection
    let position       = new OpenLayers.LonLat(0.32,52.27).transform( fromProjection, toProjection);
    let zoom           = 12; 

    map.addLayer(mapnik);

    // Add the Layer with the GPX Track
    let lgpx = new OpenLayers.Layer.Vector("Route", {
        strategies: [new OpenLayers.Strategy.Fixed()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "example.gpx",
            format: new OpenLayers.Format.GPX()
        }),
        style: {strokeColor: "red", strokeWidth: 5, strokeOpacity: 0.5},
        projection: new OpenLayers.Projection("EPSG:4326")
    });
    map.addLayer(lgpx);

    map.setCenter(position, zoom );
}