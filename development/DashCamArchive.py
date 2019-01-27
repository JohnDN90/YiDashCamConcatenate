"""
YiDashCamConcatenate (YDCC)

Combine individual video segments from Yi Dash Cam recordings into a single
continuous recording per trip and adds optional metadata to output file.

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
"""

from time import sleep

print("\n\nYiDashCamConcatenate Copyright (C) 2019 David John Neiferd\n")
print("This program is distributed in the hope that it will be useful,")
print("but WITHOUT ANY WARRANTY; without even the implied warranty of")
print("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
print("GNU General Public License for more details.")
print("This is free software, and you are welcome to redistribute it")
print("under certain conditions.")
print("See the README.md and LICENSE files for details.\n\n")

sleep(5)

import os
from subprocess import check_output, call
from pytz import timezone, utc
from datetime import datetime
from shutil import copyfile
import sys
import shlex

if os.name == "nt":
    import pywintypes, win32file, win32con
    def changeFileCreationTime(fname, newtime):
        wintime = pywintypes.Time(newtime)
        winfile = win32file.CreateFile(
            fname, win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE | win32con.FILE_SHARE_DELETE,
            None, win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL, None)
        win32file.SetFileTime(winfile, wintime, None, None)
        winfile.close()
else:
    def changeFileCreationTime(fname, newtime):
        pass

def getUTCmtime(filePath):
    mt = os.path.getmtime(filePath)
    local = timezone("America/New_York")
    naive = datetime.fromtimestamp(mt)
    local_dt = local.localize(naive, is_dst=None)
    utc_dt = local_dt.astimezone(utc)
    return utc_dt.strftime("%Y-%m-%d %H:%M:%S")

def getLocalmtime(filePath):
    mt = os.path.getmtime(filePath)
    naive = datetime.fromtimestamp(mt)
    return naive.strftime("%Y-%m-%d %H:%M:%S")

def pyempty(n):
    return [1.0]*n

def pydiff(v):
    return [j-i for i, j in zip(v[:-1], v[1:])]

def pywhere(v):
    return ([i for i, x in enumerate(v) if x],)

def pyconcatenate(vlist):
    list = []
    for v in vlist:
        list = list + v
    return list

def pyargsort(vlist):
    return sorted(range(len(vlist)), key=vlist.__getitem__)

empty = pyempty
diff = pydiff
where = pywhere
concatenate = pyconcatenate

def getIndNewVids(stimes, maxDiff):
    # logic = (diff(stimes) - 60) > maxDiff
    logic = [(i-60.0)>maxDiff for i in diff(stimes)]
    # ind_newVids = where(logic)[0] + 1
    ind_newVids = [i+1 for i in where(logic)[0]]
    ind_newVids = concatenate(([0], ind_newVids))
    return ind_newVids

# Some defaults if not defined in settings.cfg
maxDiff = 5
codec = "copy"
preset = "medium"
crf = "23"
res = None
downscaler = "bicubic"
sdCardRoot = None
outputDir = None
ffmpegPath = "ffmpeg"
camName = ""
camModel = ""
camSerialNum = ""
comment = ""
copyright = ""
combineMovieAndEMR = False
optimizePhotos = False
resolution = None
CRF = 23
speed = "medium"
videoCodec = "copy"
denoise=None
audioCodec = "aac"
audioBitrate = "192k"

# Load configuration file
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
elif __file__:
    application_path = os.path.dirname(__file__)
for line in open(application_path+"/settings.cfg", 'r'):
    exec(line)
codec = videoCodec
preset = speed
crf = CRF
res = resolution
author = camName + " " + camModel + " " + camSerialNum


if sdCardRoot is None:
    raise ValueError("sdCardRoot was not specified in settings.cfg!")

if outputDir is None:
    raise ValueError("outputDir was not specified in settings.cfg!")

try:
    check_output([ffmpegPath, '-h'])
except:
    raise ValueError("Could not successfully execute '%s -h'. Did you set the correct path to ffmpeg?"%ffmpegPath)

if codec == "copy":
    print("\nvideoCodec has been set to 'copy'.\n'CRF', 'speed', 'resolution', and 'downscaler' options will be ignored.\n")
    preset = None
    crf = None
    res = None
    downscaler = None


print("Loaded Settings\n---------------------------------------------------")

print("ffmpegPath = %s\n"%ffmpegPath)

print("camName = %s"%camName)
print("camSerialNum = %s"%camSerialNum)
print("comment = %s"%comment)
print("copyright = %s\n"%copyright)

print("sdCardRoot = %s"%sdCardRoot)
print("outputDir = %s\n"%outputDir)

print("maxDiff = %s"%maxDiff)
print("videoCodec = %s"%codec)
print("CRF = %s"%crf)
print("speed = %s"%preset)
print("resolution = %s"%res)
print("downscaler = %s"%downscaler)
print("combineMovieAndEMR = %s"%combineMovieAndEMR)
print("optimizePhotos = %s\n"%optimizePhotos)

print("---------------------------------------------------")


ans = raw_input("If the above settings look correct and you agree to the terms of use type yes to begin or no to cancel...   ")
if ans.lower() != "yes":
    raise ValueError("User did not type yes, canceling operation.")

dashCamVidRelativePath = "/Movie"
dashCamEmrRelativePath = "/EMR"
dashCamPhotoRelativePath = "/Photo"

def getTitleDate(filename):
   name = os.path.basename(filename)
   return "_".join(name.split("_")[:3])

def getTitleTime(filename):
    name = os.path.basename(filename)
    return (name.split("_")[-1])[:-4]

def abslistdir(d):
    return [os.path.join(d,f) for f in os.listdir(d)]


def processPhotos(plist):
    for file in plist:
        if file.lower().endswith(".jpg"):
            outFile = os.path.join(outputDir, os.path.basename(file))
            copyfile(file, outFile)
            if optimizePhotos:
                cmd = ['jpegoptim', '-p', outFile]
                check_output(cmd)
            atime = os.path.getatime(file)
            mtime = os.path.getmtime(file)
            ctime = os.path.getctime(file)
            os.utime(outFile, (atime, mtime))
            changeFileCreationTime(outFile, ctime)






def processVideosComplex(vlist):
    mTimes = [getTitleDate(vid) for vid in vlist]
    mTimes = list(set(mTimes))

    for mTime in mTimes:
        vidDateList = [vid for vid in vlist if getTitleDate(vid) == mTime]

        stimes = empty(len(vidDateList))
        for i in range(len(vidDateList)):
            vid = vidDateList[i]
            t = vid.split("_")[-1][:-4]
            stimes[i] = float(t[:2]) * 3600 + float(t[2:4]) * 60 + float(t[4:])

        ind_newVids = getIndNewVids(stimes, maxDiff)

        for i in range(len(ind_newVids) - 1):
            istart = int(ind_newVids[i])
            iend = int(ind_newVids[i + 1])
            vidList = vidDateList[istart:iend]
            concat_cmd1 = ""
            concat_cmd2 = ""
            concat_cmd3 = ""
            n = 0
            for vid in vidList:
                concat_cmd1 = concat_cmd1 + '-i "%s" '%vid
                if res is None and denoise is None:
                    concat_cmd2 = ""
                elif denoise is None:
                    concat_cmd2 = concat_cmd2 + "[%i:v]scale=%s:flags=%s[v%i]; "%(n, res, downscaler, n)
                elif res is None:
                    concat_cmd2 = concat_cmd2 + "[%i:v]%s[v%i]; "%(n, denoise, n)
                else:
                    concat_cmd2 = concat_cmd2 + "[%i:v]%s,scale=%s:flags=%s[v%i]; "%(n, denoise, res, downscaler, n)
                concat_cmd3 = concat_cmd3 + "[v%i][%i:a]"%(n, n)
                n+=1
            concat_cmd = concat_cmd1 + '-filter_complex "'  + concat_cmd2 + concat_cmd3 + 'concat=n=%i:v=1:a=1[v][a]" -map [v] -map [a] '%n
            fTime = getTitleTime(vidList[0])
            outputPath = "%s/%s_%s_trip.mp4" % (outputDir, mTime, fTime)
            localmtime = getLocalmtime(vidList[0])
            if codec == "copy":
                raise RuntimeError("'Stream copy is not possible when concatenating different resolution videos.")

            elif (codec == "libx264") or (codec == "libx265"):
                cmd = [ffmpegPath, '-hide_banner'] + shlex.split(concat_cmd) + \
                      ['-metadata', 'creation_time=%s' % str(localmtime),
                       '-metadata', 'artist="%s"' % author,
                       '-metadata', 'author="%s"' % author,
                       '-metadata', 'album_author="%s"' % author,
                       '-metadata', 'comment="%s"' % comment,
                       '-metadata', 'copyright="%s"' % copyright,
                       '-c:v', codec, '-preset', preset, '-crf', str(crf),
                       '-c:a', audioCodec, '-b:a', audioBitrate, '-movflags', '+faststart',
                       outputPath]
            else:
                raise ValueError(
                    "User-specified codec, %s, is not valid." % codec)
            atime = os.path.getatime(vidList[0])
            mtime = os.path.getmtime(vidList[0])
            call(cmd)
            os.utime(outputPath, (atime, mtime))
            changeFileCreationTime(outputPath, os.path.getctime(vidList[0]))

        istart = ind_newVids[-1]
        vidList = vidDateList[istart:]
        concat_cmd1 = ""
        concat_cmd2 = ""
        concat_cmd3 = ""
        n = 0
        for vid in vidList:
            concat_cmd1 = concat_cmd1 + '-i "%s" ' % vid
            if res is None and denoise is None:
                concat_cmd2 = ""
            elif denoise is None:
                concat_cmd2 = concat_cmd2 + "[%i:v]scale=%s:flags=%s[v%i]; " % (n, res, downscaler, n)
            elif res is None:
                concat_cmd2 = concat_cmd2 + "[%i:v]%s[v%i]; " % (n, denoise, n)
            else:
                concat_cmd2 = concat_cmd2 + "[%i:v]%s,scale=%s:flags=%s[v%i]; " % (n, denoise, res, downscaler, n)
            concat_cmd3 = concat_cmd3 + "[v%i][%i:a]" % (n, n)
            n += 1
        concat_cmd = concat_cmd1 + '-filter_complex "' + concat_cmd2 + concat_cmd3 + 'concat=n=%i:v=1:a=1[v][a]" -map [v] -map [a] ' % n
        fTime = getTitleTime(vidList[0])
        outputPath = "%s/%s_%s_trip.mp4" % (outputDir, mTime, fTime)
        localmtime = getLocalmtime(vidList[0])
        if codec == "copy":
            raise RuntimeError("'Stream copy is not possible when concatenating different resolution videos.")

        elif (codec == "libx264") or (codec == "libx265"):
            cmd = [ffmpegPath, '-hide_banner'] + shlex.split(concat_cmd) + \
                  ['-metadata', 'creation_time=%s' % str(localmtime),
                   '-metadata', 'artist="%s"' % author,
                   '-metadata', 'author="%s"' % author,
                   '-metadata', 'album_author="%s"' % author,
                   '-metadata', 'comment="%s"' % comment,
                   '-metadata', 'copyright="%s"' % copyright,
                   '-c:v', codec, '-preset', preset, '-crf', str(crf),
                   '-c:a', audioCodec, '-b:a', audioBitrate, '-movflags', '+faststart',
                   outputPath]

        else:
            raise ValueError("User-specified codec, %s, is not valid." % codec)
        atime = os.path.getatime(vidList[0])
        mtime = os.path.getmtime(vidList[0])
        call(cmd)
        os.utime(outputPath, (atime, mtime))
        changeFileCreationTime(outputPath, os.path.getctime(vidList[0]))

    try:
        os.remove("vidList.txt")
    except:
        pass


def getResolution(filePath):
    cmd = "ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 '%s'"%filePath
    res = check_output(shlex.split(cmd))
    return res.strip()


def all_same(items):
    return all(x == items[0] for x in items)

vidList = abslistdir(sdCardRoot+dashCamVidRelativePath)
fullVidList = [vid for vid in vidList if (vid.endswith(".MP4") or vid.endswith(".mp4")) and "_s" not in vid]
fullVidList.sort()

emrList = abslistdir(sdCardRoot+dashCamEmrRelativePath)
fullEmrList = [vid for vid in emrList if (vid.endswith(".MP4") or vid.endswith(".mp4")) and "_s" not in vid]
fullEmrList.sort()

picList = abslistdir(sdCardRoot + dashCamPhotoRelativePath)

if combineMovieAndEMR:
    baselist = [os.path.basename(vid) for vid in (fullVidList+fullEmrList)]
    ind = pyargsort(baselist)
    fullBase = (fullVidList+fullEmrList)
    fullList = [fullBase[i] for i in ind]
    resolutions = [getResolution(vid) for vid in fullList]
    if all_same(resolutions) and denoise is None:
        processVideos(fullList)
    else:
        processVideosComplex(fullList)
else:
    resolutions = [getResolution(vid) for vid in fullVidList]
    if all_same(resolutions) and denoise is None:
        processVideos(fullVidList)
    else:
        processVideosComplex(fullVidList)
    resolutions = [getResolution(vid) for vid in fullEmrList]
    if all_same(resolutions) and denoise is None:
        processVideos(fullEmrList)
    else:
        processVideosComplex(fullEmrList)


processPhotos(picList)


print("\nAll done!\n")

print("\n\nYiDashCamConcatenate Copyright (C) 2019 David John Neiferd\n")
print("This program is distributed in the hope that it will be useful,")
print("but WITHOUT ANY WARRANTY; without even the implied warranty of")
print("MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the")
print("GNU General Public License for more details.")
print("This is free software, and you are welcome to redistribute it")
print("under certain conditions.")
print("See the README.md and LICENSE files for details.\n\n")

sleep(6)