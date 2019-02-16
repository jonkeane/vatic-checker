function status_screen(stats, h)
{
    var spacer_div = "<div style='clear:both;margin:50px'></div>";
    var no_spacer_div = "<div style='clear:both;margin:5px'></div>";

    h.append("<div style='font-size: 20px;'><b>User statistics</b></div>");
    var annotator_stats = h.append("<div id='annotator_stats'></div>");
    user_data = stats["annotation_results"];
    total_videos = stats["total_videos"];


    $('#annotator_stats').append("<table id='annotator_stats_table'></table>")
    $('#annotator_stats_table').append("<th id='username_header' style='min-width:100px'>username</th>")
    $('#annotator_stats_table').append("<th id='videos_header'>videos completed</th>")
    $('#annotator_stats_table').append("<th/>")
    $('#annotator_stats_table').append("<th>trained?</th>")

    // by default, sort by number of videos annotated
    user_data.sort(sort_by('annotations_completed', true, parseInt));
    render_user_table_body(user_data);
    $('#videos_header').append(" <span class='glyphicon glyphicon-chevron-down'/>")

    // resort by # of videos annotatated
    $('#videos_header').click(function() {
        if ($(this).children('span.glyphicon.glyphicon-chevron-down').length > 0) {
            go_to_up = true;
        } else {
            go_to_up = false;
        }

        // remove the table and any sort indcators
        $(this).parent().children('tbody').remove()
        $(this).parent().children('th').children('span.glyphicon').remove();

        if (go_to_up) {
            // sorted down already, sort up and rerender
            user_data.sort(sort_by('annotations_completed', false, parseInt));
            $(this).append(" <span class='glyphicon glyphicon-chevron-up'/>")
            render_user_table_body(user_data);
        } else {
            // sorted up already or no sort
            user_data.sort(sort_by('annotations_completed', true, parseInt));
            $(this).append(" <span class='glyphicon glyphicon-chevron-down'/>")
            render_user_table_body(user_data);
        }
    })

    // resort by username
    $('#username_header').click(function() {
        if ($(this).children('span.glyphicon.glyphicon-chevron-down').length > 0) {
            go_to_up = true;
        } else {
            go_to_up = false;
        }

        // remove the table and any sort indcators
        $(this).parent().children('tbody').remove()
        $(this).parent().children('th').children('span.glyphicon').remove();

        if (go_to_up) {
            // sorted down already, sort up and rerender
            user_data.sort(sort_by('username', false, function(a){return a.toLowerCase()}));
            $(this).append(" <span class='glyphicon glyphicon-chevron-up'/>")
            render_user_table_body(user_data);
        } else {
            // sorted up already or no sort
            user_data.sort(sort_by('username', true, function(a){return a.toLowerCase()}));
            $(this).append(" <span class='glyphicon glyphicon-chevron-down'/>")
            render_user_table_body(user_data);
        }
    })

     h.append("<br/>");
     h.append("<br/>");

     h.append("<div><b id='video_stat_heading'>Video statistics</b> <form style='margin-block-end: 0px' onsubmit='return false;'><input id='filter_vdieos' type='text' autocomplete='off' placeholder='video name'></input> <button id='filterbutton' class='button'>filter</button></form></div>");

     video_stats = h.append("<div id='video_stats'></div>");
     video_data = stats["video_results"];
     total_users = stats["total_users"];

     $("#filterbutton").button().click(function() {
         video_data = stats["video_results"].filter(function(vid) {
          return vid.video_name.match($('#filter_vdieos').val()) ? true : false;
        });
        $('#video_stats_table').children('tbody').remove();

        // restore the default
        video_data.sort(sort_by('annotations_completed', true, parseInt));
        $('#video_stats_table').children('th').children('span.glyphicon').remove();
        $('#annos_header').append(" <span class='glyphicon glyphicon-chevron-down'/>")

        redner_video_table_body(video_data);
     });

     $('#video_stats').append("<table id='video_stats_table'></table>")
     $('#video_stats_table').append("<th id='video_id_header'>id</th>")
     $('#video_stats_table').append("<th id='video_name_header'>video name</th>")
     $('#video_stats_table').append("<th id='annos_header'>annotations completed</th>")
     $('#video_stats_table').append("<th/>")

     // by default, sort by number of annotations
     video_data.sort(sort_by('annotations_completed', true, parseInt));
     redner_video_table_body(video_data);
     $('#annos_header').append(" <span class='glyphicon glyphicon-chevron-down'/>")

     // resort by id
     $('#video_id_header').click(function() {
         if ($(this).children('span.glyphicon.glyphicon-chevron-down').length > 0) {
             go_to_up = true;
         } else {
             go_to_up = false;
         }

         // remove the table and any sort indcators
         $(this).parent().children('tbody').remove()
         $(this).parent().children('th').children('span.glyphicon').remove();

         if (go_to_up) {
             // sorted down already, sort up and rerender
             video_data.sort(sort_by('video_id', false, parseInt));
             $(this).append(" <span class='glyphicon glyphicon-chevron-up'/>")
             redner_video_table_body(video_data);
         } else {
             // sorted up already or no sort
             video_data.sort(sort_by('video_id', true, parseInt));
             $(this).append(" <span class='glyphicon glyphicon-chevron-down'/>")
             redner_video_table_body(video_data);
         }
     })

     // resort by # of videos annotatated
     $('#annos_header').click(function() {
         if ($(this).children('span.glyphicon.glyphicon-chevron-down').length > 0) {
             go_to_up = true;
         } else {
             go_to_up = false;
         }

         // remove the table and any sort indcators
         $(this).parent().children('tbody').remove()
         $(this).parent().children('th').children('span.glyphicon').remove();

         if (go_to_up) {
             // sorted down already, sort up and rerender
             video_data.sort(sort_by('annotations_completed', false, parseInt));
             $(this).append(" <span class='glyphicon glyphicon-chevron-up'/>")
             redner_video_table_body(video_data);
         } else {
             // sorted up already or no sort
             video_data.sort(sort_by('annotations_completed', true, parseInt));
             $(this).append(" <span class='glyphicon glyphicon-chevron-down'/>")
             redner_video_table_body(video_data);
         }
     })

     // resort by username
     $('#video_name_header').click(function() {
         if ($(this).children('span.glyphicon.glyphicon-chevron-down').length > 0) {
             go_to_up = true;
         } else {
             go_to_up = false;
         }

         // remove the table and any sort indcators
         $(this).parent().children('tbody').remove()
         $(this).parent().children('th').children('span.glyphicon').remove();

         if (go_to_up) {
             // sorted down already, sort up and rerender
             video_data.sort(sort_by('video_name', false, function(a){return a.toLowerCase()}));
             $(this).append(" <span class='glyphicon glyphicon-chevron-up'/>")
             redner_video_table_body(video_data);
         } else {
             // sorted up already or no sort
             video_data.sort(sort_by('video_name', true, function(a){return a.toLowerCase()}));
             $(this).append(" <span class='glyphicon glyphicon-chevron-down'/>")
             redner_video_table_body(video_data);
         }
     })

}

var sort_by = function(field, reverse, primer){
   var key = primer ?
       function(x) {return primer(x[field])} :
       function(x) {return x[field]};

   reverse = !reverse ? 1 : -1;

   return function (a, b) {
       return a = key(a), b = key(b), reverse * ((a > b) - (b > a));
     }
}

function render_user_table_body(user_data)
{
    $.each(user_data, function(i, item) {
        if (item.completed_training) {
            train_status = $('<div style="text-align: center;"><span title="training completed" class="glyphicon glyphicon-ok"/></div>');
        } else {
            train_status = $('<div style="text-align: center;"><span title="training not completed" class="glyphicon glyphicon-remove"/></div>');
        }
        var $tr = $('<tr>').append(
            $('<td>').text(item.username),
            $('<td>').append(
                $('<div style="clear:both;width:350px">').append($('<div>').progressbar({
                    value: item.annotations_completed/total_videos*100
                }))
            ),
            $('<td>').text(item.annotations_completed+"/"+total_videos),
            $('<td>').append(train_status)
        ).appendTo('#annotator_stats_table');
    });
}

function redner_video_table_body(video_data)
{
    $.each(video_data, function(i, item) {
        var $tr = $('<tr>').append(
            $('<td>').text(item.video_id),
            $('<td>').text(item.video_name),
            $('<td style="clear:both;width:300px">').append(
                $('<div>').progressbar({
                    value: item.annotations_completed/total_users*100
                })
            ),
            $('<td>').text(item.annotations_completed+"/"+total_users),
        ).appendTo('#video_stats_table');
    });
}
