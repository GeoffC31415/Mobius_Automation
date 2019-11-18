from __future__ import print_function
import os, time
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
	return set(intime), totalsize/1024
	
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
	return set(insize), totalsize/1024
	
def filterA(filelist, agelimit):
	"""Returns entries which are older than the agelimit from now.
	"""
	oldfiles = []
	totalsize = 0
	runtime = dt.now()
	for f in filelist:
		filedate = dt.fromtimestamp(os.path.getmtime(f))
		if filedate < (dt.now() - agelimit):
			oldfiles.append(f)
			totalsize += os.path.getsize(f)
	return set(oldfiles), totalsize/1024
	
def removeFiles(filelist):
	n = 0
	for f in filelist:
		try:
			os.remove(f)
			n += 1
		except:
			print(str(time.ctime()) + '        Could not remove file ' + f)
	print(str(time.ctime()) + '    Removed {} files'.format(n))

def cleanVideos(minhr, maxhr, maxsize):
	f = get_mp4s()
	f2, s2 = filterT(f, minhr, maxhr)
	f3, s3 = filterS(f-f2, maxsize)
	f4, s4 = filterA(f-f2-f3, td(days=maxage_days))
	
	log = ''
	filecount = 0
	if len(f2) > 0:
		log += '\n' + str(time.ctime()) + '        Removing {} during day, {} KB'.format(len(f2), s2)
		filecount += len(f2)
	if len(f3) > 0:
		log += '\n' + str(time.ctime()) + '        Removing {} below size limit, {} KB'.format(len(f3), s3)
		filecount += len(f3)
	if len(f4) > 0:
		log += '\n' + str(time.ctime()) + '        Removing {} older than {} days, {} KB'.format(len(f4), maxage_days, s4)
		filecount += len(f4)
	if filecount > 0:
		print(str(time.ctime()) + '    Checked {} videos'.format(len(f)) + log)
		removeFiles(f4|f3|f2)
