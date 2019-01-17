# YiDashCamConcatenate (YDCC)
Combine individual video segments from Yi Dash Cam recordings into a single 
continuous recording per trip and adds optional metadata to output file.

## License
Copyright (C) 2019  David John Neiferd

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

Main repository is located at: https://github.com/JohnDN90/YiDashCamConcatenate

## Legalities
This code uses FFmpeg to combine the multiple segments of video (typically 1 
minute in length) that the Yi Dash Cam creates into a single video file per 
trip. As such, this creates a new video file using your PC to be used in place
of the individual Yi Dash Cam video segments. 

To keep the information accurate to the original files, the "Accessed" time and
"Modified" time on the combined video file are set equal to the original 
"Modified" time of the first video segment that was used in the combined video
file. This time should correspond with the timestamp overlay in the video itself
unless you have modified the video file before using this program. This time is
also encoded in the video metadata as well.

Although the original  video and audio remain completely unaltered when using 
the "copy" codec. This  may have  implications as to whether your new combined 
video can be submitted as
evidence in a trial. Consult your attorney for details.  In the event that your 
Yi Dash Cam captures video of a crash or other interesting events, I suggest 
keeping the original Yi Dash Cam video files as they are and not using this 
program. This program is best used for archiving uneventful dash cam footage or
combining clips to upload to a video hosting website.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

## Requirements
FFmpeg (https://www.ffmpeg.org/)

jpegoptim (https://github.com/tjko/jpegoptim) if you want to optimize photos
to reduce file size while maintaining same quality. For a binary file for 
Windows see (https://github.com/XhmikosR/jpegoptim-windows/releases) .

Python 2.7 for running from Python (not required for executable). If running 
from Python the following modules are required as well: time, os, subprocess, 
pytz, and datetime.

## Instructions
1) Obtain the compiled executable, YDCC, from the releases page 
(https://github.com/JohnDN90/YiDashCamConcatenate/releases).

2) Edit the settings.cfg file to your desired settings. See Settings sections for
more details.

3) In Linux, open a terminal and type /path/to/DashCamArchive, press enter, and 
follow on-screen instruction. (Be sure to replace /path/to with the actual path 
on your PC).  If you get a "Permission denied" error, you'll have to set "YDCC"
as executable by right clicking on YDCC, click Properties, click Permission, 
click the  box beside "Allow executing file as program" so that a checkmark 
appears in it, then click Close.

4) In Windows, double click "YDCC", it should open in the Command Prompt, follow
the on-screen instructions.


## Settings
The settings.cfg needs to follow Python syntax.

### Program Parameters
Change ffmpegPath to the path to the ffmpeg executable on your system.

Change jpegoptimPath to the path to the jpegoptim executable on your system. Not 
required if optimizePhotos is set to False.

### File I/O Parameters
Change sdCardRoot to the path that contains the "/Movie", "/Photo", and "/EMR" 
directories created by the Yi Dash Cam.

Change outputDir to the path that you want your combined videos to be saved.

### Metadata Parameters
You can optionally leave all of these details as a blank string, "", if you do
not want to add the metadata, however I recommend adding it as it will help in
the future to identify which camera the video was recorded on as well as who
owns the rights to the video. 

Change camName to the name of your dash camera.

Change camModel to the model number of your camera.

Change camSerialNumber to the serial number of your camera.

Change comment to anything you want.

Change copyright to the name of the person who owns the rights to the video.

### Video Parameters

#### maxDiff
This is the number of seconds that is allowed to pass between consecutive video
segments for the video segments to be considered part of the same trip. For 
example, consider maxDiff=10. If video 1 has a modifcation time of 09:10:05 and 
video 2 has a modifcation time of 09:10:14, then only 9 seconds have elapses 
between the two video segments, which is less than maxDiff=10, and they will be 
considered part of the same trip and combined together.  However, if video 2 has
a modification time of 09:10:16, then 11 seconds have elapsed the two video 
segments and they will be considered two different trips.

#### videoCodec
This is the video codec which should be used for processing the dash cam video 
segments. Available options are "libx264", "libx265", or "copy". 

"copy" combines
the video segments of a trip into a single video file without re-encoding the 
audio or video which results in no quality loss between the original and 
combined videos. This is the fastest method.

"libx264" combines the video segments of a trip into a single video file and 
re-encodes the video using H.264 codec, audio is copied directly without 
re-encoding. This should only be used if you are trying to reduce filesize to 
save hard drive space. This is much slower than "copy" as it requires 
re-encoding the video.

"libx265" combines the video segments of a trip into a single video file and 
re-encodes the video using H.265 codec, audio is copied directly without 
re-encoding. This should only be used if you are trying to reduce filesize to 
save hard drive space. H.265 is more efficient than H.264 and can result in a 
smaller file size for the same quality level, but also takes longer to encode.

#### CRF
This sets the constant rate factor (CRF) used when re-encoding with libx264 or
libx265. 

For libx264, valid values are between 0-51 where 0 is lossless encoding with 
largest file size and 51 is the worst quality with smallest file size.  A value
of 17 or 18 is considered visually lossless. Reasonable values are between 
17-28. See https://trac.ffmpeg.org/wiki/Encode/H.264 for more details.

For libx265, valid values are between 0-51, although 0 is not lossless in this 
case it is still the highest quality with largest file size and 51 is worst 
quality with smallest file size. The CRF scale for libx265 and libx264 is NOT 
the same. Roughly speaking, a CRF=28 in libx265 should look the same as CRF=23
in libx264, but with about half the file size. See 
https://trac.ffmpeg.org/wiki/Encode/H.265 for more details. 

This has no effect when using videoCodec="copy".

#### speed
This sets the preset used in libx264 or libx265 with vaid options being 
"ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", 
"slower", "veryslow", and "placebo".  Generally, the slower the preset you 
choose the better the compression and smaller the file size. However, 
the slower presets also take much longer to re-encode the video. A reasonable
value, depending on your PC, is probably "medium" or "slow". See
https://trac.ffmpeg.org/wiki/Encode/H.264 for more details. 

This has no effect when using videoCodec="copy".

#### resolution
This sets the desired output resolution of your video.  You can either upscale
or downscale the video. However, this is very little reason to upscale the
video and a more practical use case of this is to downscale the video to 
decrease file size at the expense of quality (for instance when archiving 
uneventful video). You should try to keep the same aspect ratio when resizing
to avoid distorting the video. Set this to None to disable resizing. 

This has 
no effect when using videoCodec="copy".

#### downscaler
This are extra flags that are passed to FFmpeg to configure the resizer used
when changing the resolution of the video. You shouldn't have to change these
unless you have a specific reason to do so. See 
https://trac.ffmpeg.org/wiki/Scaling and https://ffmpeg.org/ffmpeg-scaler.html 
for more details. 

This has no effect when using videoCodec="copy" or 
when resolution=None.


#### combineMovieAndEMR
Whether the videos stored in the EMR folder should be combined with the videos
in the Movie folder. EMR is for emergency recordings, but an automatic EMR 
recordings can be sensitive and set up by a speed bump for example.  If you 
know for a fact that all the videos in the EMR folder are a result false 
positives (i.e. speed bumps) set this to True.  If you have any true emergency
recordings (i.e. crash, accident, etc.), set this to False.

#### optimizePhotos
Whether the photos should be optimized to reduce storage requirements without
reducing photo quality.  This is essentially lossless compression which utilizes
the jpegoptim program. If set to True, you must specify the path to jpegoptim on
your system in the jpegoptimPath variable.


