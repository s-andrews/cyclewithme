$( document ).ready(function() {
    get_ride()

    // Add a handler for the signup submission
    $("#modalsignupbutton").click(complete_signup)
});


function complete_signup() {
    // Get the route number from the data attribute 
    // on the submit button

    let route_number = $("#modalsignupbutton").data("routenumber")

    // Get their name from the input form
    let name = $("#signupnamefield").val()

    // Update the cookie with the name they've provided
    Cookies.set("cwmname",name,{ 'samesite': 'strict' })

    console.log("Set name to "+name)

    // Submit this to the back end.

    //TODO
}


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

    // Format the date nicely
    date_sections = json.date.split("-")
    // We subtract 1 from the month as they are zero indexed for some stupid reason
    let d = new Date(date_sections[0], date_sections[1]-1, date_sections[2]);
    let ye = new Intl.DateTimeFormat('en', { year: 'numeric' }).format(d);
    let mo = new Intl.DateTimeFormat('en', { month: 'short' }).format(d);
    let da = new Intl.DateTimeFormat('en', { day: '2-digit' }).format(d);
    let wd = new Intl.DateTimeFormat('en', { weekday: 'long' }).format(d);

    $("#eventdate").html(`${wd}, ${da} ${mo}, ${ye}`)

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
                                <li><strong>Spaces:</strong> ${route.spaces} total, ${route.joined.length} taken <button type="button" class="btn btn-sm btn-secondary" data-html="true" data-container="body" data-toggle="popover" data-placement="right" data-content="${route.joined.join("<br>")}">Who?</button></li>
                            </ul>
                            <div class="text-center">
                                <a href="#" data-routenumber="${route.number}" class="btn btn-primary signup">Sign up</a>
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
        load_map(route.number, route.lat, route.lon)
    }

    // Enable the popovers for the list of riders
    $('[data-toggle="popover"]').popover()

    // Enable the signup buttons
    $(".signup").click(function(e) {
        e.preventDefault();
        $("#modalsignupbutton").data("routenumber",$(this).data("routenumber"))
        let name = Cookies.get("cwmname")
        $("#signupnamefield").val(name)
        $("#signupmodal").modal("show")
    })

}


function load_map(route_number, lat, lon) {

    console.log("Loading map for route "+route_number)

    let map = new OpenLayers.Map("map"+route_number);

    let mapnik = new OpenLayers.Layer.OSM();

    let fromProjection = new OpenLayers.Projection("EPSG:4326");   // Transform from WGS 1984
    let toProjection   = new OpenLayers.Projection("EPSG:900913"); // to Spherical Mercator Projection
    let position       = new OpenLayers.LonLat(lon,lat).transform( fromProjection, toProjection);
    let zoom           = 10; 

    map.addLayer(mapnik);

    // Add the Layer with the GPX Track
    let lgpx = new OpenLayers.Layer.Vector("Route", {
        strategies: [new OpenLayers.Strategy.Fixed()],
        protocol: new OpenLayers.Protocol.HTTP({
            url: "/cgi-bin/cwm_backend.py?action=gpx&ride_id="+ride_id+"&route="+route_number,
            format: new OpenLayers.Format.GPX()
        }),
        style: {strokeColor: "red", strokeWidth: 5, strokeOpacity: 0.5},
        projection: new OpenLayers.Projection("EPSG:4326")
    });
    map.addLayer(lgpx);

    map.setCenter(position, zoom );
}