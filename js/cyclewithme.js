$( document ).ready(function() {
    get_ride()
});


function get_ride() {
    // Check the URL for ride=XXXXXX to get the ride event ID
    
    let sections = window.location.href.split("ride=");
    if (sections.length == 2) {
        ride_id = sections[1];
        update_ride(null);
    }
}


function update_ride(json) {

    // Either request the json for this ride, or parse it to update the view
    if (json == null) {
        // Send an ajax request for the json file
        $.ajax(
            {
                url: "/rides/"+ride_id+"/ride.json",
                success: function(x) {
                    update_ride(x)
                }
            }
        )

        return
    }
    
    // Parse the json to populate the page.
    $("#eventtitle").html(json.name)
    $("#eventdate").html(json.date)

    // Clear any existing route data
    $("#routes").html("")

    for (i in json.routes) {
        let route = json.routes[i];
        console.log(route)
        $("#routes").append(`
        <div class="row">
        <div class="col-lg-12">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-5">
                            <h3 class="card-title">${route.name}</h3>
                            <p class="card-text">${route.description}</p>
                            <ul>
                                <li><strong>Start Time:</strong> ${route.start_time}</li>
                                <li><strong>Departs:</strong> ${route.departs}</li>
                                <li><strong>Distance:</strong> ${route.distance} miles</li>
                                <li><strong>Pace:</strong> ${route.pace}</li>
                                <li><strong>Stop: </strong> ${route.stop}</li>
                                <li><strong>Leader:</strong> ${route.leader}</li>
                                <li><strong>Spaces:</strong> ${route.spaces} (${route.joined.length} taken)</li>
                            </ul>
                            <div class="text-center">
                                <a href="#" class="btn btn-primary signup">Sign up</a>
                            </div>

                        </div>
                        <div class="col-md-7">
                            <div id="map${route.number}" class="map"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
        `)
        load_map(route.number)
    }


}


function load_map(route_number) {

    console.log("Loading map for route "+route_number)

    let map = new OpenLayers.Map("map"+route_number);

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
            url: "/rides/"+ride_id+"/route"+route_number+".gpx",
            format: new OpenLayers.Format.GPX()
        }),
        style: {strokeColor: "red", strokeWidth: 5, strokeOpacity: 0.5},
        projection: new OpenLayers.Projection("EPSG:4326")
    });
    map.addLayer(lgpx);

    map.setCenter(position, zoom );
}