function annoer_has_trained(iftrue, iffalse)
{
    server_next_video(function(data) {
        if (data["trained"])
        {
            iftrue(data);
        }
        else
        {
            iffalse(data);
        }
    });
}

function server_next_video(callback)
{
    console.log("Querying for server for next video to annotate");
    var params = get_session_params();
    if (params.user_guid)
    {
        server_request("get_next",
            [params.user_guid],
            function (data) {
                server_jobstats_data = data;
                callback(data);
            });
    }
    else
    {
        // here we show a login screen
        loginscreen()
    }
}

function server_geturl(action, parameters)
{
    var url = "server/" + action;
    for (var x in parameters)
    {
        url += "/" + parameters[x];
    }
    return url;
}

function server_post(action, parameters, data, callback)
{
    var url = server_geturl(action, parameters);
    console.log("Server post: " + url);
    $.ajax({
        url: url,
        dataType: "json",
        type: "POST",
        data: data,
        success: function(data) {
            callback(data);
        },
        error: function(xhr, textstatus) {
            console.log(xhr.responseText);
            death("Server Error", xhr.responseText);
        }
    });
}

function server_request(action, parameters, callback)
{
    var url = server_geturl(action, parameters);
    console.log("Server request: " + url);
    $.ajax({
        url: url,
        dataType: "json",
        success: function(data) {
            callback(data);
        },
        error: function(xhr, textstatus) {
            console.log(xhr.responseText);
            death("Server Error", xhr.responseText);
        }
    });
}

var event_log = [];
function eventlog(domain, message)
{
    var timestamp = (new Date()).getTime();
    event_log.push([timestamp, domain, message]);
    //console.log(timestamp + " " + domain + ": " + message);
}

function death(message, server_message = "")
{
    console.log(message);
    document.write("<style>body{background-color:#333;color:#fff;text-align:center;padding-top:100px;font-weight:bold;font-size:30px;font-family:Arial;</style>" + message + "<br/><br/><br/>" + server_message);
}
