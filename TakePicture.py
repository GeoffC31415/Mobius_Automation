#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  WriteRecords.py
#  
#  Copyright 2017  <pi@raspberrypi>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#  

from picamera import PiCamera

def main():
	camera = PiCamera()
	curfile = '/home/pi/Desktop/image.jpg'
		
	camera.rotation = 180
	camera.capture(curfile)	
	#camera.start_preview()	
	return 0


if __name__ == '__main__':
	main()
