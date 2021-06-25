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
    $("#modalsignupbutton").click(function(e){
        e.preventDefault();
        complete_signup()
    })

    // Add a handler for the new route submission button
    $("#newroutesubmit").click(function(e){
        console.log("Clicked Submit")
        e.preventDefault()
        add_new_route()
        $("#newroutemodal").modal("hide")
    })

    // Add newroute button handler
    $("#newroutebutton").click(function(){
        $("#newroutemodal").modal("show")
    })

    // Add the new event handler
    $("#neweventsubmit").click(function(e) {
        e.preventDefault()
        create_new_event()
    })

    // Make the file upload actually show the 
    // file name
    $('input[type="file"]').change(function(e){
        var fileName = e.target.files[0].name;
        $('.custom-file-label').html(fileName);
    });
});


function create_new_event() {
    // Make a new event and redirect to the event page

    let eventtitle = $("#neweventtitle").val()
    let eventdate = $("#neweventdate").val()

    $.ajax(
        {
            url: "/cgi-bin/cwm_backend.py",
            data: {
                action: "newevent",
                title: eventtitle,
                date: eventdate
            },
            success: function(ids) {
                let sections = ids.split(" ")
                ride_id = sections[0]
                admin_id = sections[1]
                window.location.replace("/?ride="+ride_id+"&admin="+admin_id)
            }
        }
    )


}


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

    // TODO: Check there's space

    let route_number = $("#modalsignupbutton").data("routenumber")

    // Get their name from the input form
    let name = $("#signupnamefield").val()

    // Get their guid to submit alongside the name
    let guid = Cookies.get("cwmguid")

    // Update the cookie with the name they've provided
    Cookies.set("cwmname",name,{ 'samesite': 'strict', 'expires': 365 })

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
            success: function(route_number) {
                // We need to modify the code for
                // the ride to show that we're 
                // signed up
                console.log("Signed up for "+route_number)

                // List the signup buttons
                let signup_buttons = $(".signup")

                // Go through them to find the one which 
                // matches the route number
                for (let i=0;i<signup_buttons.length;i++) {
                    let button = signup_buttons.eq(i)
                    if (button.data("routenumber") != route_number) {
                        continue
                    }

                    // Change the button text and class
                    button.text("Withdraw")
                    button.removeClass("btn-primary")
                    button.removeClass("signup")
                    button.addClass("btn-warning")
                    button.addClass("withdraw")

                    // Make the alert banner visible
                    button.parent().parent().find(".alert").removeClass("hidden")

                    // Increase the value in the taken field
                    let takennumber = button.parent().parent().find(".takennumber")
                    takennumber.text(parseInt(takennumber.text())+1)

                    // Add your name to the list of attendees
                    // TODO: Work out how to do this...

                    // Rebind the click event
                    rebind_signup_buttons()
                }

            }
        }
    )


    // Close the modal
    $("#signupmodal").modal("hide")

}

function add_new_route() {

    let title = $("#newtitle").val()
    let description = $("#newdescription").val()
    let start = $("#newstart").val()
    let departs = $("#newdeparts").val()
    let pace = $("#newpace").val()
    let stop = $("#newstop").val()
    let leader = $("#newleader").val()
    let spaces = $("#newspaces").val()
    let gpx = $("#newgpx")[0].files[0]

    // Submit this to the back end.

    let data = new FormData();

    data.append("action","new_route");
    data.append("ride_id",ride_id),
    data.append("admin_id",admin_id),
    data.append("title",title);
    data.append("description",description);
    data.append("start",start);
    data.append("departs",departs);
    data.append("pace",pace);
    data.append("stop",stop);
    data.append("leader",leader);
    data.append("spaces",spaces);
    data.append("gpx",gpx);

    $.ajax(
        {
        type: "POST",
        url: "/cgi-bin/cwm_backend.py",
        data: data,
        processData: false,
        contentType: false,
        success: function() {
            get_ride()
        },
        error: function(query,status,error){
            console.log("Add new route failed: "+status+" Error:"+error);
        }
    });

}


function get_ride() {
    // Check the URL for ride=XXXXXX to get the ride event ID

    // The URL will be of the form XXXX?ride=XXXXX&ADMIN=XXXXX
    // where the admin is optional
    
    let href = window.location.href

    // Remove everything before the ?
    let args = href.split("\?")[1]

    // Get the key/value pairs
    ride_id=""
    admin_id=""

    if (args) {
        let keyval = args.split("&")


        for (i in keyval) {
            let splitval = keyval[i].split("=")
            if (splitval[0]=="ride") {
                ride_id = splitval[1]
            }
            else if (splitval[0]=="admin") {
                admin_id = splitval[1]
            }
        }
    }

    if (admin_id) {
        validate_admin(ride_id,admin_id)
    }

    if (ride_id) {
        $("#newrideinstructions").hide();
        update_ride(null);
    }
    else {
        $("#showevent").hide();
        populate_new_ride()
    }
}


function populate_new_ride() {
    // This adds some basic information to the page to allow
    // people to set up a new ride
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
                    // Set the links on the invites
                    $("#invitelink").attr("href","/?ride="+ride_id)
                    $("#admininvitelink").attr("href","/?ride="+ride_id+"&admin="+admin_id)
                    $(".adminonly").show()
                }
            }
        }
    )
}


function update_ride(json) {

    // Check our guid against signups
    let guid = Cookies.get("cwmguid")


    // Either request the json for this ride, or parse it to update the view
    if (json == null) {
        // Send an ajax request for the json file.  We send the guid so 
        // it can be annotated with whether we're going or not and we don't have
        // to see other people's guids.

        $.ajax(
            {
                url: "/cgi-bin/cwm_backend.py",
                data: {
                    action: "json",
                    ride: ride_id,
                    guid: guid
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
        let alert_class = " hidden"

        if (signed_up) {
            button_text = "Widthdraw"
            button_class = "btn-warning withdraw"
            alert_class = ""
        }

        $("#routes").append(`
        <div class="row">
        <div class="col-lg-12">
            <div class="card">
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-5">
                            <h3 class="card-title">${route.name}</h3>
                            <div class="alert alert-success ${alert_class}" role="alert">You're going!</div>
                            <p class="card-text">${route.description}</p>
                            <ul>
                                <li><strong>Start Time:</strong> ${route.start_time}</li>
                                <li><strong>Departs:</strong> ${route.departs}</li>
                                <li><strong>Distance:</strong> ${route.distance} miles</li>
                                <li><strong>Pace:</strong> ${route.pace}</li>
                                <li><strong>Stop(s): </strong> ${route.stop}</li>
                                <li><strong>Leader(s):</strong> ${route.leader}</li>
                                <li><strong>Spaces:</strong> ${route.spaces} total, <span class="takennumber">${route.joined.length}</span> taken <button type="button" class="btn btn-sm btn-secondary" data-html="true" data-container="body" data-toggle="popover" data-placement="right" data-content="${joined_names.join("<br>")}">Who?</button></li>
                            </ul>
                            <div class="text-center">
                                <a href="#" data-routenumber="${route.number}" class="btn ${button_class}">${button_text}</a>
                                <a href="#" data-routenumber="${route.number}" class="btn btn-danger deleteroute adminonly">Delete Route</a>
                            </div>

                        </div>
                        <div class="col-md-7">
                            <div id="map${route.number}" class="map">
                            <a class="btn btn-dark btn-sm gpxdownload" href="/cgi-bin/cwm_backend.py?action=gpx&ride_id=${ride_id}&route=${route.number}" role="button">Download GPX</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
        `)
        load_map(route.number, route.lat, route.lon)
    }

    // Enable the popovers for the list of riders unless
    // we're running as an admin in which case we provide
    // additional information
    if (is_admin) {

    }
    else {
        $('[data-toggle="popover"]').popover()
    }   

    // Make the signup/widtdraw buttons work
    rebind_signup_buttons()

    // Enable the delete route buttons
    $(".deleteroute").click(function(e) {
        e.preventDefault();

        route_number = $(this).data("routenumber")

        $.ajax(
            {
                url: "/cgi-bin/cwm_backend.py",
                data: {
                    action: "delete_route",
                    ride: ride_id,
                    admin: admin_id,
                    route: route_number
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

function rebind_signup_buttons() {
    // Enable the signup buttons
    $(".signup").unbind()
    $(".signup").click(function(e) {
        e.preventDefault();
        $("#modalsignupbutton").data("routenumber",$(this).data("routenumber"))
        let name = Cookies.get("cwmname")
        $("#signupnamefield").val(name)
        $("#signupmodal").modal("show")
    })

    // Enable the withdraw buttons
    $(".withdraw").unbind()
    $(".withdraw").click(function(e) {

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
                success: function(route_number) {
                    // We need to modify the code for
                    // the ride to show that we're 
                    // signed up
                    console.log("Withdrawn from "+route_number)

                    // List the withdraw buttons
                    let withdraw_buttons = $(".withdraw")

                    // Go through them to find the one which 
                    // matches the route number
                    for (let i=0;i<withdraw_buttons.length;i++) {
                        let button = withdraw_buttons.eq(i)
                        if (button.data("routenumber") != route_number) {
                            continue
                        }

                        // Change the button text and class
                        button.text("Sign Up")
                        button.removeClass("btn-warning")
                        button.removeClass("withdraw")
                        button.addClass("btn-primary")
                        button.addClass("signup")

                        // Make the alert banner invisible
                        button.parent().parent().find(".alert").addClass("hidden")

                        // Decrease the value in the taken field
                        let takennumber = button.parent().parent().find(".takennumber")
                        takennumber.text(parseInt(takennumber.text())-1)

                        // Add your name to the list of attendees
                        // TODO: Work out how to do this...

                        // Rebind the click event
                        rebind_signup_buttons()

                    } // End for
                } // End success
            }) // End ajax
    }) // End click
} // End function


function load_map(route_number, lat, lon) {

    let style = {
        'MultiLineString': new ol.style.Style({
          stroke: new ol.style.Stroke({
            color: '#a00',
            width: 4
          })
        })
      };

    let vector = new ol.layer.Vector({
        source: new ol.source.Vector({
          url: "/cgi-bin/cwm_backend.py?action=gpx&ride_id="+ride_id+"&route="+route_number,
          format: new ol.format.GPX()
        }),
        style: function(feature) {
          return style[feature.getGeometry().getType()];
        }
      });

    new ol.Map({
        target: "map"+route_number,
        layers: [
          new ol.layer.Tile({
            source: new ol.source.OSM()
          }),
          vector
        ],
        view: new ol.View({
          center: ol.proj.fromLonLat([lon, lat]),
          zoom: 10
        })
    })
}