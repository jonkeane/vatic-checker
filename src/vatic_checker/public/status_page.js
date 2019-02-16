function status_screen(stats, h)
{
    var spacer_div = "<div style='clear:both;margin:50px'></div>";
    var no_spacer_div = "<div style='clear:both;margin:5px'></div>";

    h.append("<h1>User statistics</h1>");
    var annotator_stats = h.append("<div id='annotator_stats'></div>");
    data = stats["annotation_results"];
    total_videos = stats["total_videos"];

    annotator_stats.append("<table id='annotator_stats_table'></table>")
    $('#annotator_stats_table').append("<th>username</th>")
    $('#annotator_stats_table').append("<th>videos completed</th>")
    $('#annotator_stats_table').append("<th/>")
    $('#annotator_stats_table').append("<th>trained?</th>")

     $.each(data, function(i, item) {
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

     h.append("<br/>");
     h.append("<br/>");

     h.append("<h1>Video statistics</h1>");
     var video_stats = h.append("<div id='video_stats'></div>");
     data = stats["video_results"];
     total_users = stats["total_users"];

     video_stats.append("<table id='video_stats_table'></table>")
     $('#video_stats_table').append("<th>video name</th>")
     $('#video_stats_table').append("<th>annotations completed</th>")
     $('#video_stats_table').append("<th/>")

      $.each(data, function(i, item) {
          var $tr = $('<tr>').append(
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
