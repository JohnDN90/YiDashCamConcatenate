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
from subprocess import check_output
from pytz import timezone, utc
from datetime import datetime
from shutil import copyfile
import sys


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
        outFile = os.path.join(outputDir, os.path.basename(file))
        copyfile(file, outFile)
        if optimizePhotos:
            cmd = ['jpegoptim', '-p', outFile]
            check_output(cmd)


def processVideos(vlist):
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
            with open("vidList.txt", 'w') as listFile:
                for vid in vidList:
                    listFile.write("file '%s'\n" % vid)
            fTime = getTitleTime(vidList[0])
            outputPath = "%s/%s_%s_trip.mp4" % (outputDir, mTime, fTime)
            localmtime = getLocalmtime(vidList[0])
            if codec == "copy":
                cmd = '"%s" -hide_banner -f concat -safe 0 -i vidList.txt -metadata creation_time="%s" -metadata artist="%s" -metadata author="%s" -metadata album_author="%s" -metadata comment="%s" -metadata copyright="%s" ' \
                      '-c:v %s -c:a copy -movflags +faststart "%s"' \
                      % (
                      ffmpegPath, localmtime, author, author, author, comment,
                      copyright, codec, outputPath)
            elif (codec == "libx264") or (codec == "libx265"):
                if res is None:
                    cmd = '"%s" -hide_banner -f concat -safe 0 -i vidList.txt -metadata creation_time="%s" -metadata artist="%s" -metadata author="%s" -metadata album_author="%s" -metadata comment="%s" -metadata copyright="%s" ' \
                          '-c:v %s -preset %s ' \
                          '-crf %s -c:a copy -movflags +faststart "%s"' \
                          % (ffmpegPath, localmtime, author, author, author,
                             comment, copyright,
                             codec, preset, crf, outputPath)
                else:
                    cmd = '"%s" -hide_banner -f concat -safe 0 -i vidList.txt -metadata creation_time="%s" -metadata artist="%s" -metadata author="%s" -metadata album_author="%s" -metadata comment="%s" -metadata copyright="%s" ' \
                          '-vf scale=%s -sws_flags %s -c:v %s -preset %s ' \
                          '-crf %s -c:a copy -movflags +faststart "%s"' \
                          % (ffmpegPath, localmtime, author, author, author,
                             comment, copyright, res, downscaler, codec, preset,
                             crf,
                             outputPath)
            else:
                raise ValueError(
                    "User-specified codec, %s, is not valid." % codec)
            atime = os.path.getatime(vidList[0])
            mtime = os.path.getmtime(vidList[0])
            # 1+1
            print("Video List:\n%s\n" % vidList)
            print("cmd = \n%s\n" % cmd)
            os.system(cmd)
            os.utime(outputPath, (atime, mtime))

        istart = ind_newVids[-1]
        vidList = vidDateList[istart:]
        with open("vidList.txt", 'w') as listFile:
            for vid in vidList:
                listFile.write("file '%s'\n" % vid)
        fTime = getTitleTime(vidList[0])
        outputPath = "%s/%s_%s_trip.mp4" % (outputDir, mTime, fTime)
        localmtime = getLocalmtime(vidList[0])
        if codec == "copy":
            cmd = '"%s" -hide_banner -f concat -safe 0 -i vidList.txt -metadata creation_time="%s" -metadata artist="%s" -metadata author="%s" -metadata album_author="%s" -metadata comment="%s" -metadata copyright="%s" ' \
                  '-c:v %s -c:a copy -movflags +faststart "%s"' \
                  % (ffmpegPath, localmtime, author, author, author, comment,
                     copyright,
                     codec, outputPath)
        elif (codec == "libx264") or (codec == "libx265"):
            if res is None:
                cmd = '"%s" -hide_banner -f concat -safe 0 -i vidList.txt -metadata creation_time="%s" -metadata artist="%s" -metadata author="%s" -metadata album_author="%s" -metadata comment="%s" -metadata copyright="%s" ' \
                      '-c:v %s -preset %s ' \
                      '-crf %s -c:a copy -movflags +faststart "%s"' \
                      % (
                      ffmpegPath, localmtime, author, author, author, comment,
                      copyright, codec, preset, crf, outputPath)
            else:
                cmd = '"%s" -hide_banner -f concat -safe 0 -i vidList.txt -metadata creation_time="%s" -metadata artist="%s" -metadata author="%s" -metadata album_author="%s" -metadata comment="%s" -metadata copyright="%s" ' \
                      '-vf scale=%s -sws_flags %s -c:v %s -preset %s ' \
                      '-crf %s -c:a copy -movflags +faststart "%s"' \
                      % (
                      ffmpegPath, localmtime, author, author, author, comment,
                      copyright, res, downscaler, codec, preset, crf,
                      outputPath)
        else:
            raise ValueError("User-specified codec, %s, is not valid." % codec)
        # 1+1
        atime = os.path.getatime(vidList[0])
        mtime = os.path.getmtime(vidList[0])

        print("Video List:\n%s\n" % vidList)
        os.system(cmd)
        os.utime(outputPath, (atime, mtime))

    try:
        os.remove("vidList.txt")
    except:
        pass



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
    processVideos(fullList)
else:
    processVideos(fullVidList)
    processVideos(fullEmrList)


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