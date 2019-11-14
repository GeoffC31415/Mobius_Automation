from __future__ import print_function
import os, time
import glob
from datetime import timedelta as td
from datetime import datetime as dt

sourcePath = '/var/www/html/Mobius_Website/images/'

def get_mp4s():
	return glob.glob(sourcePath + '*.mp4')
	
def filterT(filelist, minhr, maxhr):
	"""Returns entries from filterlist which were taken between
	minhr and maxhr (e.g. 6, 22 will return files between 06:00 
	and 21:59:59)
	"""
	# format: xx-YYYYMMDDHHMMSS.mp4
	intime = []
	for f in filelist:
		f_hr = int(f[-10:-8])
		if f_hr >= minhr and f_hr < maxhr:
			intime.append(f)
	return intime
	
def filterS(filelist, maxsize):
	""" Returns entries which are smaller than maxsize in bytes.
	"""
	insize = []
	for f in filelist:
		size = os.path.getsize(f)
		if size < maxsize:
			insize.append(f)
	return insize
	
def filterA(filelist, agelimit):
	"""Returns entries which are older than the agelimit from now.
	"""
	oldfiles = []
	runtime = dt.now()
	for f in filelist:
		filedate = dt.fromtimestamp(os.path.getmtime(f))
		if filedate < (dt.now() - agelimit):
			oldfiles.append(f)
	return oldfiles
	
def removeFiles(filelist):
	n = 0
	for f in filelist:
		try:
			os.remove(f)
			n += 1
		except:
			print('Could not remove file ' + f)
	print(str(time.ctime()) + '    Removed {} files'.format(n))

def cleanVideos(minhr, maxhr, maxsize):
	f = get_mp4s()
	f2 = filterT(f, minhr, maxhr)
	f3 = filterS(f, maxsize)
	f4 = filterA(f, td(days=14))
	
	log = ''
	filecount = 0
	if len(f2) > 0:
		log += ', removing {} during day'.format(len(f2))
		filecount += len(f2)
	if len(f3) > 0:
		log += ', removing {} below size limit'.format(len(f3))
		filecount += len(f3)
	if len(f4) > 0:
		log += ', removing {} older than two weeks'.format(len(f4))
		filecount += len(f4)
	if filecount > 0:
		log += ', {} total'.format(filecount)
		print(str(time.ctime()) + '    Checked {} videos'.format(len(f)) + log)
		removeFiles(f4+f3+f2)
