function Video(data)
{
    var me = this;

    this.id = null;
    this.start = null;
    this.end = null;
    this.width = null;
    this.height = null;
    this.name = null;
    this.label = null;
    this.num_frames = null;

    this.frameurl = function(i)
    {
        return "frames/" + me.name +  "/" + parseInt(i) + ".jpg" + "?videoid="+me.id;
   }
}

function video_import(data, is_training)
{
    var video = new Video();
    video.id = parseInt(data["video_id"]);
    video.start = parseInt(data["start"]);
    video.end = parseInt(data["end"]);
    video.width = parseInt(data["width"]);
    video.height = parseInt(data["height"]);
    video.name = data["name"];
    video.is_training = is_training;
    // video.label = parseFloat(data["perobject"]);
    // video.num_frames = parseInt(data["num_frames"]);

    console.log("The next video has been configured!");

    return video;
}
