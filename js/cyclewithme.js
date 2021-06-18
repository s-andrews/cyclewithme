$( document ).ready(function() {

    is_admin = false

    get_ride()

    // Check the guid
    guid = Cookies.get("cwmguid")
    if (! guid) {
        guid = generate_guid()
    }
    // Update or set the guid cookie
    Cookies.set("cwmguid",guid,{ 'samesite': 'strict', 'expires': 365 })

    // Add a handler for the signup submission
    $("#modalsignupbutton").click(complete_signup)
});


function generate_guid() {
    // We make this long enough that it's statistically
    // unlikely that they're going to clash by random
    let result           = [];
    let characters       = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
    var charactersLength = characters.length;
    for ( var i = 0; i < 30; i++ ) {
      result.push(characters.charAt(Math.floor(Math.random() * charactersLength)));
   }
   return result.join('');
}


function complete_signup() {
    // Get the route number from the data attribute 
    // on the submit button

    let route_number = $("#modalsignupbutton").data("routenumber")

    // Get their name from the input form
    let name = $("#signupnamefield").val()

    // Get their guid to submit alongside the name
    let guid = Cookies.get("cwmguid")

    // Update the cookie with the name they've provided
    Cookies.set("cwmname",name,{ 'samesite': 'strict', 'expires': 365 })

    console.log("Set name to "+name)

    // Submit this to the back end.

    $.ajax(
        {
            url: "/cgi-bin/cwm_backend.py",
            data: {
                action: "signup",
                ride: ride_id,
                route: route_number,
                name: name,
                guid: guid
            },
            success: function() {
                get_ride()
            }
        }
    )


    // Close the modal
    $("#signupmodal").modal("hide")

}


function get_ride() {
    // Check the URL for ride=XXXXXX to get the ride event ID

    // The URL will be of the form XXXX?ride=XXXXX&ADMIN=XXXXX
    // where the admin is optional
    
    let href = window.location.href

    // Remove everything before the ?
    let args = href.split("\?")[1]

    // Get the key/value pairs
    let keyval = args.split("&")

    ride_id=""
    admin_id=""

    for (i in keyval) {
        let splitval = keyval[i].split("=")
        if (splitval[0]=="ride") {
            ride_id = splitval[1]
        }
        else if (splitval[0]=="admin") {
            admin_id = splitval[1]
        }
    }

    if (admin_id) {
        validate_admin(ride_id,admin_id)
    }

    // TODO: bail out if no ride id?
    update_ride(null);
}


function validate_admin(ride,admin) {
    $.ajax(
        {
            url: "/cgi-bin/cwm_backend.py",
            data: {
                action: "validate_admin",
                ride: ride,
                admin: admin
            },
            success: function(x) {
                console.log("Response='"+x+"'")
                if (x.trim() == "True"){
                    is_admin = true
                 $(".adminonly").show()
                }
            }
        }
    )
}


function update_ride(json) {

    // Either request the json for this ride, or parse it to update the view
    if (json == null) {
        // Send an ajax request for the json file

        $.ajax(
            {
                url: "/cgi-bin/cwm_backend.py",
                data: {
                    action: "json",
                    ride: ride_id
                },
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

    // Check our guid against signups
    let guid = Cookies.get("cwmguid")

    for (i in json.routes) {
        let route = json.routes[i];

        let signed_up = false

        let joined_names = []
        for (j in route.joined) {
            joined_names.push(route.joined[j].name)
            if (route.joined[j].guid == guid) {
                signed_up = true
            }
        }

        let button_text = "Sign Up"
        let button_class = "btn-primary signup"

        if (signed_up) {
            button_text = "Signed Up - Press to Widthdraw"
            button_class = "btn-success withdraw"
        }

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
                                <li><strong>Spaces:</strong> ${route.spaces} total, ${route.joined.length} taken <button type="button" class="btn btn-sm btn-secondary" data-html="true" data-container="body" data-toggle="popover" data-placement="right" data-content="${joined_names.join("<br>")}">Who?</button></li>
                            </ul>
                            <div class="text-center">
                                <a href="#" data-routenumber="${route.number}" class="btn ${button_class}">${button_text}</a>
                                <a href="#" data-routenumber="${route.number}" class="btn btn-danger adminonly">Delete Route</a>
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

    // Enable the withdraw buttons
    $(".withdraw").click(function(e) {

        console.log("withdrawing")
        e.preventDefault();

        route_number = $(this).data("routenumber")

        $.ajax(
            {
                url: "/cgi-bin/cwm_backend.py",
                data: {
                    action: "withdraw",
                    ride: ride_id,
                    route: route_number,
                    guid: guid
                },
                success: function() {
                    get_ride()
                }
            }
        )
    
    })

    // Make admin options visible if we are one
    if (is_admin) {
        $(".adminonly").show()
    }
    
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