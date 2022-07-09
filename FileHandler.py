import os
import time
import glob
from datetime import timedelta as td
from datetime import datetime as dt

sourcePath = '/var/www/html/Mobius_Website/images/'
maxage_days = 14


def get_mp4s():
    return set(glob.glob(sourcePath + '*.mp4'))


def filterT(filelist, minhr, maxhr):
    """Returns entries from filterlist which were taken between
    minhr and maxhr (e.g. 6, 22 will return files between 06:00
    and 21:59:59)
    """
    # format: xx-YYYYMMDDHHMMSS.mp4
    intime = []
    totalsize = 0
    for f in filelist:
        f_hr = int(f[-10:-8])
        if f_hr >= minhr and f_hr < maxhr:
            intime.append(f)
            totalsize += os.path.getsize(f)
    return set(intime), totalsize / 1024


def filterS(filelist, maxsize):
    """ Returns entries which are smaller than maxsize in bytes.
    """
    insize = []
    totalsize = 0
    for f in filelist:
        size = os.path.getsize(f)
        if size < maxsize:
            insize.append(f)
            totalsize += os.path.getsize(f)
    return set(insize), totalsize / 1024


def filterA(filelist, agelimit):
    """Returns entries which are older than the agelimit from now.
    """
    oldfiles = []
    totalsize = 0
    for f in filelist:
        filedate = dt.fromtimestamp(os.path.getmtime(f))
        if filedate < (dt.now() - agelimit):
            oldfiles.append(f)
            totalsize += os.path.getsize(f)
    return set(oldfiles), totalsize / 1024


def get_total_size(startdate, enddate):
    """ Takes datetime start and end, returns size of all files between
    those times. Uses file modified date."""
    filelist = get_mp4s()
    totalsize = 0
    for f in filelist:
        filedate = dt.fromtimestamp(os.path.getmtime(f))
        if (filedate > startdate) and (filedate < enddate):
            totalsize += os.path.getsize(f)
    return totalsize


def removeFiles(filelist):
    n = 0
    for f in filelist:
        try:
            os.remove(f)
            n += 1
        except Exception:
            print(str(time.ctime()) + '        Could not remove file ' + f)
    print(str(time.ctime()) + '    Removed {} files'.format(n))


def cleanVideos(minhr, maxhr, maxsize):
    remaining_files = get_mp4s()
    totalfilecount = len(remaining_files)

    filterfuncs = [
        {
            'function': filterT,
            'condition': (minhr, maxhr),
            'desc': '\n' + str(time.ctime()) + '        Removing {} during day, {} KB'
        },
        {
            'function': filterS,
            'condition': (maxsize,),
            'desc': '\n' + str(time.ctime()) + '        Removing {} below size limit, {} KB'
        },
        {
            'function': filterA,
            'condition': (td(days=maxage_days),),
            'desc': '\n' + str(time.ctime()) + '        Removing {} old files, {} KB'
        }
    ]

    log = ''
    filecount = 0
    removals = []
    for func_obj in filterfuncs:
        f, s = func_obj['function'](remaining_files, *func_obj['condition'])
        if len(f) > 0:
            log += func_obj['desc'].format(len(f), s)

        filecount += len(f)
        removals += f
        remaining_files -= f

    print(str(time.ctime()) + '    Checked {} videos'.format(totalfilecount) + log)
    removeFiles(removals)
