/*
 * var videoplayer = VideoPlayer($("#frame"), 1000,
 *                   function (x) { return "/images/" + x + ".jpg"; });
 * videoplayer.play();
 */
function VideoPlayer(handle, video)
{
    var me = this;

    this.handle = handle;
    this.video = video;
    this.frame = video.start;
    this.paused = true;
    this.fps = 30;
    this.playdelta = 1;

    this.onplay = []; 
    this.onpause = []; 
    this.onupdate = [];

    /*
     * Toggles playing the video. If playing, pauses. If paused, plays.
     */
    this.toggle = function()
    {
        if (this.paused)
        {
            this.play();
        }
        else
        {
            this.pause();
        }
    }

    /*
     * Starts playing the video if paused.
     */
    this.play = function()
    {
        if (this.paused)
        {
            console.log("Playing...");
            this.paused = false;
            this.interval = window.setInterval(function() {
                if (me.frame >= me.video.end)
                {
                    me.pause();
                }
                else
                {
                    me.displace(me.playdelta);
                }
            }, 1. / this.fps * 1000);

            this._callback(this.onplay);
        }
    }

    /*
     * Pauses the video if playing.
     */
    this.pause = function()
    {
        if (!this.paused)
        {
            console.log("Paused.");
            this.paused = true;
            window.clearInterval(this.interval);
            this.interval = null;

            this._callback(this.onpause);
        }
    }

    /*
     * Seeks to a specific video frame.
     */
    this.seek = function(target)
    {
        this.frame = target;
        this.updateframe();
    }

    /*
     * Displaces video frame by a delta.
     */
    this.displace = function(delta)
    {
        this.frame += delta;
        this.updateframe();
    }

    /*
     * Updates the current frame. Call whenever the frame changes.
     */
    this.updateframe = function()
    {
        this.frame = Math.min(this.frame, this.video.end);
        this.frame = Math.max(this.frame, this.video.start);

        var url = this.video.frameurl(this.frame);
        this.handle.css("background-image", "url('" + url + "')");
        this.handle.css("background-repeat", "no-repeat");

        this._callback(this.onupdate);

	$("#frameinfo").html(this.frame);
    }

    /*
     * Calls callbacks
     */
    this._callback = function(list)
    {
        for (var i = 0; i < list.length; i++)
        {
            list[i]();
        }
    }

    this.updateframe();
}
