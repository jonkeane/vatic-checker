var development = false;

var container;

$(document).ready(function() { boot() });

function boot()
{
    console.log("Booting...");

    container = $("#container");

    var ua = window.navigator.userAgent;
    var msie = ua.indexOf("MSIE ");
    if (msie > 0)
    {
        container.html("<p style='width:500px;'><strong>Sorry!</strong> This application does not currently support Internet Explorer. Please upgrade to a more modern browser to complete this HIT. We recommend <a href='http://www.google.com/chrome' target='_blank'>Google Chrome</a> or <a href='http://www.getfirefox.com' target='_blank'>Mozilla Firefox</a>.</p>");
        return;
    }

    var storage_parameters = get_session_params();

    function dispatch(this_is_training, data)
    {
        if (data.error_msg) {
            // this condition might not happen
            console.log('There was an error.');
            ui_enable(1);
            ui_getjob_error(data.error_msg);
        } else {
            loadingscreen(video_import(data, this_is_training));
        }
    }

    annoer_next_video(function(data) {
        console.log("The annotator has completed training");
        dispatch(false, data);
    }, function(data) {
        console.log("The annotator needs to complete the training");
        dispatch(true, data);
    },function(data) {
        console.log("The annotator has no more videos to annotate");
        no_more_videos();
    });
}

function loadingscreen(video)
{
    var ls = $("<div id='loadingscreen'></div>");
    ls.append("<div id='loadingscreentext'>Downloading the video...</div>");
    ls.append("<div id='loadingscreenslider'></div>");

    container.html(ls);

    eventlog("preload", "Start preloading");
    console.log(video)
    preloadvideo(video.start, video.end, video.frameurl,
        preloadslider($("#loadingscreenslider"), function(progress) {
            if (progress == 1)
            {

                ls.remove()

                ui_build(video);

                eventlog("preload", "Done preloading");
            }
        })
    );
}

function no_more_videos()
{
    var ls = $("<div id='finishedscreen'></div>");
    ls.append("<div id='finishedscreentext'></div>");
    container.html(ls);

    $("#finishedscreentext").append("<h1>You've annotated all the videos!</h1>");
    $("#finishedscreentext").append("<img src='party-popper.png'/>");
    $("#finishedscreentext").append("<p>Each user is only able to annotate each video once. There are no more videos on the server for you to annotate. If you think this is in error, please contact the researcher.</p>");
    $("#finishedscreentext").append("<div id='logoutbuttonfinished' class='button'>Logout</div>");
    $("#logoutbuttonfinished").click(function() {
        clear_session_params(reload = true);
    }).button();
    add_status_button("#finishedscreentext");

    eventlog("preload", "There are no more videos to annotate");
}

function add_status_button(where)
{
    if (get_session_params()["can_see_status"]) {
        $(where).append("<div id='status_button' class='button'>Status</div>");
        $("#status_button").click(function() {
            ui_showstatus();
        }).button();
    }
}

function loginscreen()
{
    var ls = $("<div id='loginscreen'></div>");
    ls.append("<div id='loginscreentext'></div>");
    container.html(ls);

    $("#loginscreentext").append("<h1>Please login</h1>");
    $("#loginscreentext").append("<p>If you don't have a username, please contact the researcher.</p>");

    $("#loginscreentext").append("<form onsubmit='return false;' id='login'></form>");
    $("#login").append("<div id='usernamelabel'><h3 style='margin-bottom:0px; display:inline-block;'>Username</h3></div>");
    $("#login").append("<div><input id='username' type='text' autocomplete='off'></input></div>");
    $("#login").append("<div class='g-recaptcha' data-sitekey='6LfFxoUUAAAAAOjnjaXknybhFoNIUBDCvH5IsC-U' data-callback='remove_captchafail'></div>") // ttic key
    // $("#login").append("<div class='g-recaptcha' data-sitekey='6LePuIUUAAAAAIl_cGo2946oqqrLycEbmWAP3AJ-' data-callback='remove_captchafail'></div>") // testing key
    $("#login").append("<div><button id='loginsubmitbutton' class='button'>Submit</button></div>");
    $("#loginsubmitbutton").button().click(function() {
        if (ui_disabled) return;
        if ($("#loginsubmitbutton")[0].classList.contains("ui-button-disabled")) return;
        if (grecaptcha.getResponse() == "") {
            if($("#captchafailure").length) return;

            $("#login").append('<h3 id=\'captchafailure\'>You must fill in the <i>I\'m not a robot</i> form before submitting.</h3>')
            return;
        }
        trylogin(insert_param);
    });


    eventlog("preload", "Waiting for login");
}

function trylogin(callback)
{
    data = {
        "username": $('#username').val(),
        "recaptcha": grecaptcha.getResponse()
    }
    data = JSON.stringify(data);
    server_post("login", ["not_needed"], data, function(data) {
        if (data["success"]) {
            // insert can_see_status, default false
            status = data["can_see_status"] ? data["can_see_status"] : false
            insert_param("can_see_status", status)
            // callback is also insert_param, but will also reload
            callback("user_guid", data["user_guid"], reload = true)
        } else {
            if (data["reason"] == "Incorrect username") {
                $('#usernamelabel').append("<h3 id='usernamefailure'>"+data["reason"]+"</h3>")
            } grecaptcha.reset();
            //  captcha total failure?
            death("Could not log in. You can try refreshing the page again.")
        }
    });
}

function get_session_params()
{
    var out = {};
    out.user_guid = window.sessionStorage.getItem("user_guid")

    // default can_see_status to false, need to check the string for True/true
    can_see_status = window.sessionStorage.getItem("can_see_status")
    out.can_see_status = can_see_status ? can_see_status.toLowerCase() == "true" : false

    // get speed, but if it doesn't exist, then just use "speedcontrolnorm"
    possible_speeds = ["speedcontrolslower", "speedcontrolslow", "speedcontrolnorm", "speedcontrolfast"]
    speed = window.sessionStorage.getItem("speed")
    if (speed != null)
    {
        out.speed = $.inArray(speed, possible_speeds) > -1 ? speed : "speedcontrolnorm";
    }
    else
    {
        out.speed = "speedcontrolnorm"
    }

    return out;
}

function insert_param(key, value, reload = false)
{
    // store in session store that persists across reloads
    window.sessionStorage.setItem(key, value)
    if (reload) {
        location.reload();
    }
}

function clear_session_params(reload = false)
{
    window.sessionStorage.removeItem("user_guid");
    window.sessionStorage.removeItem("can_see_status");
    window.sessionStorage.removeItem("speed");
    if (reload) {
        location.reload();
    }
}

function remove_captchafail()
{
    $('#captchafailure').remove()
}
