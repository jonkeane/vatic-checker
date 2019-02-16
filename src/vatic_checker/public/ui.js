var ui_disabled = 0;
// maximum number of tries when validating
max_tries = 4;
video_skip = 0;

function ui_build(video)
{
    var screen = ui_setup(video);
    var videoframe = $("#videoframe");
    var player = new VideoPlayer(videoframe, video);

    ui_setupbuttons(video, player);
    ui_setupslider(player);
    ui_setupsubmit(video);

    // disable submit button until an annotation is made (by checking when the
    // annotation input has a change)
    $("#submitbutton").button("option", "disabled", true);
    $(document).ready(function(){
        // TODO: This causes the submit button to re-enable when the incorrect
        // annotation dialog comes up — find some way around that.
        $('input[type=text]').keyup(annoCheck).focusout(annoCheck);
    });
    $('#annotation_label').keypress(function(event) {
        var keycode = event.keyCode || event.which;
        if(keycode == '13') {
            if (ui_disabled) return;
            if ($("#submitbutton")[0].classList.contains("ui-button-disabled")) return;
            ui_submit(video);
        }
    });

    ui_setupclickskip(video, player);
    ui_setupkeyboardshortcuts_inputsafe(video, player);

    $("#playbutton").focus()

}

function ui_setup(video)
{
    var screen = $("<div id='annotatescreen'></div>").appendTo(container);
    $("<table>" +
        "<tr>" +
            "<td><div id='instructions'>Type the word that was fingerspelled into the box below the video.</td>" +
            // These are reversed from where we want them because css
            "<td><div id='logoutbutton' class='button'>Logout</div><div id='status_container'></div></td>" +
        "</tr>" +
        "<tr>" +
              "<td><div id='videoframe'></div></td>" +
              "<td rowspan='2'><div id='sidebar'></div></td>" +
          "</tr><tr style='height: 15px;' ></tr>" +
          "<tr>" +
              "<td/>" +
              "<td><div id='frameinfobar'></div></td>" +
          "</tr>" +
          "<tr>" +
          "<td><div id='bottombar'><div id='play_controls'></div><div id='annobar'></div><div id='speedcontrol'></div></div></td>" +
              "<td><div id='submitbar'></div></td>" +
          "</tr>" +
          "<tr>" +
              "<td><div id='startendbar'></div></td>" +
          "</tr>" +
      "</table>").appendTo(screen).css("width", "100%");

//    video.width = video.width + 200;
//    video.height = video.height + 200;
    var playerwidth = Math.max(720, video.width);

    $("#videoframe").css({"width": video.width + "px",
                          "height": video.height + "px",
                          "margin": "0 auto"})
                    .parent().css("width", playerwidth + "px");
    // place slider just below video (to line up with marks)
    $("#videoframe").append("<div id='playerslider'></div>");


    $("#sidebar").css({"height": video.height + "px",
                       "width": "300px"});

    $("#annotatescreen").css("width", (playerwidth + 300) + "px");

    $("#frameinfobar").css({"padding-left": "20px", "width": "150px"});
    $("#frameinfobar").append("<div style='float: left;'><strong>Frame: </strong></div><div id='frameinfo'></div>");
    $("#frameinfo").css({"width": "30px", "padding-left": "10px", "float": "left"});

    $("#play_controls").append("<button class='button' id='rewindbutton'>Rewind</button> ");
    $("#play_controls").append("<button class='button' style='width:85px' id='playbutton'>Play</button></div>");

    $("#annobar").append("<form onsubmit='return false;' id='annotation_form'></form>");
    $("#annotation_form").append("<input id='annotation_label' type='text' autocomplete='off' placeholder='Type your annotation here'></input>");

    $("<div id='objectcontainer'></div>").appendTo("#sidebar");
    $("#objectcontainer").append("<p><b>Instructions</b></p>");
    $("#objectcontainer").append("<p>Watch the fingerspelling sequence and write the word you see.</p>");
    $("#objectcontainer").append("<p>Use the following diacritics:</p>");

    $("#objectcontainer").append("<p><b>[letters spelled]*[letters intended]</b><br/>If the letters spelled differ from the word intended, please record both in the annotation with an asterisk separating them.</p>");

    $("#objectcontainer").append("<p><b>[best guess at letters]?</b><br/>If you are unsure of which letters were spelled, you may indicate this with a question mark at the end.</p>");

    $("#objectcontainer").append("<p><b>2:[word]</b><br/>If both hands fingerspell the same word.</p>");

    $("#objectcontainer").append("<p><b>[word] [word]</b><br/>If a fingerspelling sequence includes multiple consecutive words with no intervening signs or the hand going down, label it as a single sequence with one start frame and one end frame.  Separate the words with a space if there is no visible break between them.</p>");

    $("#objectcontainer").append("<p><b>[word]![word]</b><br/>If there is a visible break between the words, use an exclamation mark to separate them (e.g. a slight pause, shift of the hand, etc).</p>")



    $("#speedcontrol").append(
    "<input type='radio' name='speedcontrol' " +
        "value='5,1' id='speedcontrolslower'>" +
    "<label for='speedcontrolslower'>Slower</label>" +
    "<input type='radio' name='speedcontrol' " +
        "value='15,1' id='speedcontrolslow'>" +
    "<label for='speedcontrolslow'>Slow</label>" +
    "<input type='radio' name='speedcontrol' " +
        "value='30,1' id='speedcontrolnorm' checked='checked'>" +
    "<label for='speedcontrolnorm'>Normal</label>" +
    "<input type='radio' name='speedcontrol' " +
        "value='90,1' id='speedcontrolfast'>" +
    "<label for='speedcontrolfast'>Fast</label>"
    );

    $("#submitbar").append("<form onsubmit='return false;' id='myForm'><button id='submitbutton' class='button'>Submit</button></form>");

    $("#submitbutton").html("Save Work");

    return screen;
}

function ui_setupbuttons(video, player)
{

    add_status_button("#status_container");

    $("#logoutbutton").click(function() {
        clear_session_params(reload = true);
    }).button({
        icons: {
            primary: "ui-icon-circle-close"
        }
    });

    $("#playbutton").click(function() {
        if (!$(this).button("option", "disabled"))
        {
            player.toggle();

            if (player.paused)
            {
                eventlog("playpause", "Paused video");
            }
            else
            {
                eventlog("playpause", "Play video");
            }
        }
    }).button({
        disabled: false,
        icons: {
            primary: "ui-icon-play"
        }
    });

    $("#rewindbutton").click(function() {
        if (ui_disabled) return;
        player.pause();
        player.seek(player.video.start);
        eventlog("rewind", "Rewind to start");
    }).button({
        disabled: true,
        icons: {
            primary: "ui-icon-seek-first"
        }
    });

    player.onplay.push(function() {
        $("#playbutton").button("option", {
            label: "Pause",
            icons: {
                primary: "ui-icon-pause"
            }
        });
    });

    player.onpause.push(function() {
        $("#playbutton").button("option", {
            label: "Play",
            icons: {
                primary: "ui-icon-play"
            }
        });
    });

    player.onupdate.push(function() {
        if (player.frame == player.video.end)
        {
            $("#playbutton").button("option", "disabled", true);
        }
        else if ($("#playbutton").button("option", "disabled"))
        {
            $("#playbutton").button("option", "disabled", false);
        }

        if (player.frame == player.video.start)
        {
            $("#rewindbutton").button("option", "disabled", true);
        }
        else if ($("#rewindbutton").button("option", "disabled"))
        {
            $("#rewindbutton").button("option", "disabled", false);
        }
    });

    $("#speedcontrol").buttonset();

    $("input[name='speedcontrol']").click(function() {
        player.fps = parseInt($(this).val().split(",")[0]);
        player.playdelta = parseInt($(this).val().split(",")[1]);
        console.log("Change FPS to " + player.fps);
        console.log("Change play delta to " + player.playdelta);
        if (!player.paused)
        {
            player.pause();
            player.play();
        }
        eventlog("speedcontrol", "FPS = " + player.fps + " and delta = " + player.playdelta);
        // save to session params
        insert_param("speed", this.id);
    });

    // Check the speed control based on session parameters (default to normal)
    var params = get_session_params();
    if (params.speed == "speedcontrolslower") {
        $("#speedcontrolslower").prop("checked", true).trigger("click");
    } else if (params.speed == "speedcontrolslow") {
        $("#speedcontrolslow").prop("checked", true).trigger("click");
    } else if (params.speed == "speedcontrolnorm") {
        $("#speedcontrolnorm").prop("checked", true).trigger("click");
    } else if (params.speed == "speedcontrolfast") {
        $("#speedcontrolfast").prop("checked", true).trigger("click");
    }
    // refresh all buttons now
    $("#speedcontrolslower").button("enable").button("refresh");
    $("#speedcontrolslow").button("enable").button("refresh");
    $("#speedcontrolnorm").button("enable").button("refresh");
    $("#speedcontrolfast").button("enable").button("refresh");
}

function annoCheck(){
    var filled = false;
    if($('#annotation_label').val() != ''){
        filled = true;
    }
    $("#submitbutton").button("option", "disabled", !filled);
}

function ui_setupkeyboardshortcuts_inputsafe(video, player)
{
    $(window).keypress(function(e) {
        console.log("Key press: " + e.keyCode);

        if (ui_disabled)
        {
            console.log("Key press ignored because UI is disabled.");
            return;
        }

        var keycode = e.keyCode ? e.keyCode : e.which;
        eventlog("keyboard", "Key press: " + keycode);

        var skip = 0;
        if (keycode == 44) // , old: + d
        {
            skip = video_skip > 0 ? -video_skip : -10;
        }
        else if (keycode == 46) // . old: + f
        {
            skip = video_skip > 0 ? video_skip : 10;
        }
        else if (keycode == 62) // > old: + v
        {
            skip = video_skip > 0 ? video_skip : 1;
        }
        else if (keycode == 60) // < old: + c
        {
            skip = video_skip > 0 ? -video_skip : -1;
        }

        if (skip != 0)
        {
            player.pause();
            player.displace(skip);

            ui_snaptokeyframe(video, player);
        }
    });

}






function ui_setupslider(player)
{
    var slider = $("#playerslider");
    slider.slider({
        range: "min",
        value: player.video.start,
        min: player.video.start,
        max: player.video.end,
        slide: function(event, ui) {
            player.pause();
            player.seek(ui.value);
            // probably too much bandwidth
            //eventlog("slider", "Seek to " + ui.value);
        }
    });

    /*slider.children(".ui-slider-handle").hide();*/
    slider.children(".ui-slider-range").css({
        "background-color": "#868686",
        "background-image": "none"});

    slider.css({
        marginTop: parseInt(slider.parent().css("height")) +20 + "px", // for under video position only
        width: parseInt(slider.parent().css("width")) + "px", // for under video position only
        float: "bottom",
        position: "absolute" // for under video position only
    });

    player.onupdate.push(function() {
        slider.slider({value: player.frame});
    });
}

function ui_iskeyframe(frame, video)
{
    return frame == video.end || (frame - video.start) % video_skip == 0;
}

function ui_snaptokeyframe(video, player)
{
    if (video_skip > 0 && !ui_iskeyframe(player.frame, video))
    {
        console.log("Fixing slider to key frame");
        var remainder = (player.frame - video.start) % video_skip;
        if (remainder > video_skip / 2)
        {
            player.seek(player.frame + (video_skip - remainder));
        }
        else
        {
            player.seek(player.frame - remainder);
        }
    }
}

function ui_setupclickskip(video, player)
{
    if (video_skip <= 0)
    {
        return;
    }

    player.onupdate.push(function() {
        if (ui_iskeyframe(player.frame, video))
        {
            console.log("Key frame hit");
            player.pause();
            $("#playbutton").button("option", "disabled", false);
        }
        else
        {
            $("#playbutton").button("option", "disabled", true);
        }
    });

    $("#playerslider").bind("slidestop", function() {
        ui_snaptokeyframe(video, player);
    });
}

function ui_setupsubmit(video)
{
    $("#submitbutton").button({
        icons: {
            primary: 'ui-icon-check'
        }
    }).click(function() {
        if (ui_disabled) return;
        if ($("#submitbutton")[0].classList.contains("ui-button-disabled")) return;
        ui_submit(video);
    });
}

function ui_submit(video)
{
    // TODO: replace null here with something describing what's being submitted
    console.log("Start submit - status: " + null);

    var overlay = $('<div id="overlay"></div>').appendTo("#container");
    ui_disable();

    var note = $("<div id='submitdialog'></div>").appendTo("#container");

    function handle_response(valid, callback) {
        var error_types = ["borked"]
        // TODO: if wanted, use the mturk-style hints.
        // // error types as defined in qa.py, these will trigger slightly different
        // // warnings on the correction screen.
        // var error_types = ["missing gap", "missing two hands",
        // "missing star signer spelling error", "annotator spelling error",
        // "spelling error", "missing annotation/misalignment"]

        console.log(valid);
        if (valid == "all good")
        {
            console.log("Training was successful, good job!");
            callback();
        }
        else if (max_tries < 1) {
            note.remove();
            overlay.remove();
            console.log("Training failed and tries are up!");
            total_failedvalidation();
        }
        else if (error_types.includes(valid))
        {
            console.log(valid);
            note.remove();
            overlay.remove();
            console.log(max_tries);
            max_tries = max_tries-1;
            ui_annotator_error(valid);
        }
        else
        {
            note.remove();
            overlay.remove();
            console.log("Validation failed!");
            console.log(max_tries);
            max_tries = max_tries-1;
            ui_annotator_error("unknown");
        }
    }

    function saveVideo(is_training, callback)
    {
        var params = get_session_params();
        var data = {
            video_id : video.id,
            anno_value : $('#annotation_label').val(),
            user_guid : params.user_guid,
        };
        data = JSON.stringify(data);
        var endpoint = is_training ? "save_training" : "save_annotation"
        server_post(endpoint, [video.id], data, function(data) {
            if (is_training)
            {
                handle_response(data, callback);
            }
            else
            {
                callback();
            }
            });
    }

    if (video.is_training)
    {
        console.log("Submit redirect to train validate");

        note.html("Checking...");
        saveVideo(video.is_training, function(data) {
            note.html("Good work!");
            window.setTimeout(function() {
                            location.reload();
                        }, 1000);

        });
    }
    else
    {
        note.html("Saving... Please wait...");
        saveVideo(video.is_training, function(data) {
            note.html("Saved!");
            window.setTimeout(function() {
                            location.reload();
                        }, 1000);
        });
    }
}




function ui_getvideo_error(msg)
{
    $('<div id="overlay"></div>').appendTo("#container");
    var h = $('<div id="failedverificationdialog"></div>')
    h.appendTo("#container");

    h.append("<h1>Oops!</h1>");
    h.append(msg);
}


function total_failedvalidation()
{
    $('<div id="overlay"></div>').appendTo("#container");
    var h = $('<div id="failedverificationdialog"></div>')
    h.appendTo("#container");

    h.append("<h1>Incorrect annotation</h1>");
    h.append("<p>Sorry, but you have not completed the training in the number of attempts allowed.</p>");
    h.append("<p>You can try again by refreshing your page.</p>");
    h.append("<p>If you still cannot complete the training, please contact the researcher.</p>");
}

function ui_annotator_error(error_code)
{
    $('<div id="overlay"></div>').appendTo("#container");
    var h = $('<div id="failedverificationdialog"></div>')
    h.appendTo("#container");

    h.append("<h1>Incorrect annotation</h1>");
    h.append("<p>We need to ensure that all annotators are using the same annotation system and are matching each other. The annotation you entered does not match our standard. Please take a look and try again.</p>");

    h.append("<p>Please review the instructions again, double check your annotations, and submit again. Remember annotate only the letters that are fingerspelled.</p>");

    h.append("<p>When you are ready to continue, press the button below.</p>");

    $('<div class="button" id="failedverificationbutton">Try Again</div>').appendTo(h).button({
        icons: {
            primary: "ui-icon-refresh"
        }
    }).click(function() {
        ui_enable();
        $("#overlay").remove();
        h.remove();
    }).wrap("<div style='text-align:center;padding:5x 0;' />");
}

function isChildOf(child, parent) {
  if (child.parentNode === parent) {
    return true;
  } else if (child.parentNode === null) {
    return false;
  } else {
    return isChildOf(child.parentNode, parent);
  }
}

function ui_disable()
{
    if (ui_disabled++ == 0)
    {
        $("#playbutton").button("option", "disabled", true);
        $("#rewindbutton").button("option", "disabled", true);
        $("#submitbutton").button("option", "disabled", true);
        $("#playerslider").slider("option", "disabled", true);

        console.log("Disengaged UI");
    }

    console.log("UI disabled with count = " + ui_disabled);
}

function ui_enable(flag)
{
    if (--ui_disabled == 0)
    {
	$("#playbutton").button("option", "disabled", false);
	$("#rewindbutton").button("option", "disabled", false);
        $("#submitbutton").button("option", "disabled", false);
        $("#playerslider").slider("option", "disabled", false);

        console.log("Engaged UI");
    }

    ui_disabled = Math.max(0, ui_disabled);

    console.log("UI disabled with count = " + ui_disabled);
}



function ui_showstatus(job)
{
    console.log("Popup status");

    if ($("#statusdialog").size() > 0)
    {
        return;
    }

    eventlog("status", "Popup status");

    $('<div id="overlay"></div>').appendTo("#container");
    var h = $('<div id="statusdialog"></div>').appendTo("#container");
    var inst_controls = $('<div id="statuscontrols"></div>').appendTo(h);

    $('<div class="button" id="statusclosetop" style="float: right;">Dismiss Status</div>').appendTo(inst_controls).button({
        icons: {
            primary: "ui-icon-circle-close"
        }
    }).click(ui_closestatus);

    server_request("status",
        [get_session_params().user_guid],
        function(data) {
            status_screen(data, h);
        });

    ui_disable();

    document.body.addEventListener("click", function(e) {
      var target = e.target || e.srcElement;
      var status_area = document.getElementById("statusdialog");
      var status_button = document.getElementById("status_button");

      // if the clicked object is in the status area or the status
      // button itself ignore the click. Additionally if the status are not up
      // ignore the click. If the status are up, and the click is outside of the
      // status, then close the status.
      if ( ( status_area != null && target !== status_area && !isChildOf(target, status_area) ) &&
           ( status_button != null && target !== status_button && !isChildOf(target, status_button) ) &&
           // ignore span elements for sorting
           target.tagName != "SPAN") {
             ui_closestatus();
      }
    }, false);
}

function isChildOf(child, parent) {
  if (child.parentNode === parent) {
    return true;
  } else if (child.parentNode === null) {
    return false;
  } else {
    return isChildOf(child.parentNode, parent);
  }
}

function ui_closestatus()
{
    console.log("Popdown status");
    $("#overlay").remove();
    $("#statusdialog").remove();
    eventlog("status", "Popdown status");

    ui_enable();
}
