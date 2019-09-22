#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Simple python command line tool to pack / unpack the Amazfit Bip font firmware files

# (C) José Rebelo
# https://gist.github.com/joserebelo/b9be41b7b88774f712e2f864fdd39878

# (E) Yener Durak & Eddie - Make this working with Amazfit Bip
# https://gist.github.com/joserebelo/b9be41b7b88774f712e2f864fdd39878

# Thanks to https://github.com/prof-membrane for initial analisys
# https://github.com/Freeyourgadget/Gadgetbridge/issues/734#issuecomment-320108514

from PIL import Image
from pathlib import Path
import math
import binascii
import sys
import os
import glob

# Unpack the Amazfit Bip font file
# Creates 1bpp bmp images
def unpackFont(font_path):
	print('Unpacking', font_path)
	
	font_file = open(font_path, 'rb')
	font_path.join(font_path.split(os.sep)[:-1])
	if not os.path.exists('bmp-mib4'):
		os.makedirs('bmp-mib4')
	# header = 16 bytes
	header = font_file.read(0x20)

	byte04 = header[0x04]
	print ("byte04 chaohu=8 mib4=1 falcon=a :%x" %byte04)

	byte0A = header[0x0A]
	print ("byte0B version?!:%x" %byte0A)

	offset = (header[0x1F] << 24) + (header[0x1E] << 16) + (header[0x1D] << 8) + header[0x1C]
	#offset = int.from_bytes(header[0x1f:0x1b:-1] , byteorder='big') # same like before... more pythonic way
	print ("offset to fixed size fonts: 0x%x" %offset)

	num_ranges_b = font_file.read(0x2)
	num_ranges = (num_ranges_b[0x1] << 8) + num_ranges_b[0x0]
	
	ranges = font_file.read(num_ranges*6)
	#print ("ranges:" ,ranges)
	startrange = (ranges[len(ranges)-5] << 8) + ranges[len(ranges)-6]
	endrange = (ranges[len(ranges)-3] << 8) + ranges[len(ranges)-4]
	num_characters = (ranges[len(ranges)-1] << 8) + ranges[len(ranges)-2] +  endrange - startrange + 1
	print ("num_characters: %d" % (num_characters))
	
	startrange = (ranges[1] << 8) + ranges[0]
	endrange = (ranges[3] << 8) + ranges[2]
	#sys.exit(1)
	range_nr = 0;
	for i in range (0, num_characters):
	#for i in range (0, 32):
		sys.stdout.write("%d/%d\r" % (i,num_characters))
		#print ("startrange:%x %d" % (startrange,startrange))
		#print ("endrange:%x %d" % (endrange,endrange))
	
		img = Image.new('1', (24, 24), 0)
		pixels = img.load()
		char_bytes = font_file.read(72) 
		x = 0
		y = 0
		# big endian
		int_bytes = []
		#print (len(char_bytes),["%02x" % c  for c in char_bytes])
		for b in range(0,24):
			int_bytes.append((char_bytes[b*3+0]<<16) + (char_bytes[b*3+1]<<8) + char_bytes[b*3+2])
		#print (["%06x" % c  for c in int_bytes])
		for byte in int_bytes:
			#print (byte)
			bits = [(byte >> bit) & 1 for bit in range(24 - 1, -1, -1)]
			#print ("->"," ".join([ chr(b+32) for b in bits]).replace("!","X"),"<-")
			for b in bits:
				pixels[x, y] = b
				x += 1
				if x == 24:
					x = 0
					y += 1
		margin_top = font_file.read(1)
		img.save("bmp-mib4" + os.sep + '{:04x}'.format(startrange) + '{:02x}'.format(margin_top[0] ) + '.bmp') 
		#print ("margin_top:%x" % margin_top[0])
		startrange += 1
		if startrange > endrange and range_nr+1 < num_ranges:
			range_nr += 1
			startrange = (ranges[range_nr * 6 + 1] << 8) + ranges[range_nr * 6]
			endrange = (ranges[range_nr * 6 + 3] << 8) + ranges[range_nr * 6 + 2]
		
	if offset !=  0xffffffff:
		if not os.path.exists('bmp-mib4-fixed'):
			os.makedirs('bmp-mib4-fixed')

		num_ranges_b = font_file.read(0x2)
		num_ranges = (num_ranges_b[0x1] << 8) + num_ranges_b[0x0]

		ranges = font_file.read(num_ranges*6)
		#print ("ranges:" ,ranges)
		startrange = (ranges[len(ranges)-5] << 8) + ranges[len(ranges)-6]
		endrange = (ranges[len(ranges)-3] << 8) + ranges[len(ranges)-4]
		num_characters = (ranges[len(ranges)-1] << 8) + ranges[len(ranges)-2] +  endrange - startrange + 1
		print ("num_characters: %d" % (num_characters))

		startrange = (ranges[1] << 8) + ranges[0]
		endrange = (ranges[3] << 8) + ranges[2]
		#sys.exit(1)
		range_nr = 0;
		for i in range (0, num_characters):
			sys.stdout.write("%d/%d\r" % (i,num_characters))
			#print ("startrange:%x %d" % (startrange,startrange))
			#print ("endrange:%x %d" % (endrange,endrange))

			img = Image.new('1', (16, 20), 0)
			pixels = img.load()
			#char_bytes = font_file.read(8)
			char_bytes = font_file.read(40)
			x = 0
			y = 0
			# big endian
			int_bytes = []
			#print (["%02x" % c for c in list(char_bytes)])
			for b in range(0,20):
				int_bytes.append((char_bytes[b*2+0]<<8) + char_bytes[b*2+1])
			#print (["%04x" % c  for c in int_bytes])
			for byte in int_bytes:
				#print (byte)
				bits = [(byte >> bit) & 1 for bit in range(16 - 1, -1, -1)]
				#print ("->"," ".join([ chr(b+32) for b in bits]).replace("!","X"),"<-")
				for b in bits:
					pixels[x, y] = b
					x += 1
					if x == 16:
						x = 0
						y += 1
			#margin_top = font_file.read(1)
			margin_top = [0]
			img.save("bmp-mib4-fixed" + os.sep + '{:04x}'.format(startrange) + str(margin_top[0] % 16) + '.bmp') 
			#print ("margin_top:%x" % (margin_top[0] % 16))
			startrange += 1
			if startrange > endrange and range_nr+1 < num_ranges:
				range_nr += 1
				startrange = (ranges[range_nr * 6 + 1] << 8) + ranges[range_nr * 6]
				endrange = (ranges[range_nr * 6 + 3] << 8) + ranges[range_nr * 6 + 2]

# Create a Amazfit Bip file from bmps
def packFont(font_path):
	print('Packing', font_path)
	font_file = open(font_path, 'wb')
	header = bytearray(binascii.unhexlify('4E455A4B01FFFFFFFFFF03000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0000'))
	bmps = bytearray()
	
	range_nr = 0
	seq_nr = 0
	startrange = -1
	
	bmp_files = sorted(glob.glob('bmp-mib4' +  os.sep + '*'))
	if True:

		for i in range (0, len(bmp_files)):
		#for i in range (0, 10):
			sys.stdout.write("%d/%d\r" % (i,len(bmp_files)))
			margin_top = int(bmp_files[i].split(os.sep)[1][4:6],16)
			
			if(i == 0):
				unicode = int(bmp_files[i].split(os.sep)[1][0:4],16)
			else:
				unicode = next_unicode
			
			if(i+1 < len(bmp_files)):
				next_unicode = int(bmp_files[i+1].split(os.sep)[1][0:4],16)
			else:
				next_unicode = -1
			
			if (unicode != next_unicode):
				if (startrange == -1):
					range_nr += 1			 
					startrange = unicode
				
				img = Image.open(bmp_files[i])
				img_rgb = img.convert('RGB')
				pixels = img_rgb.load()
				
				x = 0
				y = 0
				char_width = 0;
				
				cnt=0
				#cnt2=0
				#print ("LEN",len(bmps),cnt,cnt2,char_width)
				#ft = bytearray()
				while y < 24:
					b = 0
					for j in range(0, 8):
						cnt+=1
						#print (x,y)
						if pixels[x, y] != (0, 0, 0):
							b = b | (1 << (7 - j))
							if (x > char_width):
								char_width = x
							#sys.stdout.write("X")
						#else:
							#sys.stdout.write(" ")

						x += 1
						if x == 24:
							x = 0
							y += 1
							#sys.stdout.write("\n")
						#if y == 23:
						#	print ("23")
						#	if pixels[x,y] != (0,0,0):
						#		sys.stdout.write("X")
						#	else:
						#		sys.stdout.write(" ")
						
					#cnt2+=1
					#print ("DEBUG",b.to_bytes(1, 'big'))
					bmps.extend(b.to_bytes(1, 'big'))
					#ft.extend(b.to_bytes(1, 'big'))
				
				#print ("LEN",len(bmps),cnt,cnt2,char_width)
				#char_width = (char_width <<3 )+ margin_top;
				#char_width = (char_width <<3 )+ margin_top;
				if char_width < margin_top:
				#if char_width == 0:
					char_width = margin_top
				#print ("ft %02d CHAR_WIDTH 0x%02x MARGIN TOP 0x%02x" %(i,char_width, margin_top))
				bmps.extend(char_width.to_bytes(1, 'big'))
				#print (["%02x" % c for c in list(ft)]) 
				
				
				if (unicode+1 != next_unicode):
					endrange = unicode
					sb = startrange.to_bytes(2, byteorder='big')
					header.append(sb[1])
					header.append(sb[0])
					eb = endrange.to_bytes(2, byteorder='big')	
					header.append(eb[1])
					header.append(eb[0])
					seq = seq_nr.to_bytes(2, byteorder='big')	
					header.append(seq[1])
					header.append(seq[0])
					seq_nr += endrange - startrange + 1
					startrange = -1
			else:
				print('multiple files of {:04x}'.format(unicode))

		rnr = range_nr.to_bytes(2, byteorder='big')
		header[0x20] = rnr[1]
		header[0x21] = rnr[0]
	else:
		print ("#avoid compute all progressive font for develpment of fixed one")
		f = open("Font.emoticon.MB4.v3a.ft", "rb")
		header = bytearray(f.read(0x20))
		rnrb = f.read(0x2)
		rnr = int.from_bytes(bytearray(rnrb[::-1]), byteorder='big')
		print ("%x" % (rnr ))
		print ("%x" % (rnr * 6))
		#bmps = f.read(0x198417 - rnr * 6)
		bmps = f.read(0x198417)
		f.close()
		header.extend([0,0])
		#header[0x20] = rnrb[0]
		#header[0x21] = rnrb[1]
	
	offset = (len(bmps) + range_nr *6 + 2)
	print ("len_bmps_files:%x "%len(bmp_files))
	print ("len_bmps should be:%x "%(len(bmp_files) * 73))
	print ("len_bmps:%x "%len(bmps))
	print ("len_header:%x "%len(header))
	ofs = offset.to_bytes(4, byteorder='big')
	header[0x1f] = ofs[0]
	header[0x1e] = ofs[1]
	header[0x1d] = ofs[2]
	header[0x1c] = ofs[3]

	font_file.write(header)
	font_file.write(bmps)

	#pack fixed fize fonts

	header = bytearray([0,0])
	bmps = bytearray()
	
	range_nr = 0
	seq_nr = 0
	startrange = -1
	
	bmp_files = sorted(glob.glob('bmp-mib4-fixed' +  os.sep + '*'))

	for i in range (0, len(bmp_files)):
	#for i in range (0, 10):
		sys.stdout.write("%d/%d\r" % (i,len(bmp_files)))
		margin_top = int(bmp_files[i].split(os.sep)[1][4:5],16)
		
		if(i == 0):
			unicode = int(bmp_files[i].split(os.sep)[1][0:4],16)
		else:
			unicode = next_unicode
		
		if(i+1 < len(bmp_files)):
			next_unicode = int(bmp_files[i+1].split(os.sep)[1][0:4],16)
		else:
			next_unicode = -1
		
		if (unicode != next_unicode):
			if (startrange == -1):
				range_nr += 1			 
				startrange = unicode
			
			img = Image.open(bmp_files[i])
			img_rgb = img.convert('RGB')
			pixels = img_rgb.load()
			
			x = 0
			y = 0
			char_width = 0;
			
			cnt=0
			#cnt2=0
			#print ("LEN",len(bmps),cnt,cnt2,char_width)
			ft = bytearray()
			while y < 20:
				b = 0
				for j in range(0, 8):
					cnt+=1
					#print (x,y)
					if pixels[x, y] != (0, 0, 0):
						b = b | (1 << (7 - j))
						if (x > char_width):
							char_width = x
					x += 1
					if x == 16:
						x = 0
						y += 1
					#if y == 23:
					#	print ("23")
					#	if pixels[x,y] != (0,0,0):
					#		sys.stdout.write("X")
					#	else:
					#		sys.stdout.write(" ")
					
				#cnt2+=1
				#print ("DEBUG",b.to_bytes(1, 'big'))
				bmps.extend(b.to_bytes(1, 'big'))
				ft.extend(b.to_bytes(1, 'big'))
				
			
			#print ("LEN",len(bmps),cnt,cnt2,char_width)
			#char_width = (char_width <<3 )+ margin_top;
			#char_width = (char_width <<3 )+ margin_top;
			if char_width < margin_top:
			#if char_width == 0:
				char_width = margin_top
			#print ("ft %02d CHAR_WIDTH 0x%02x MARGIN TOP 0x%02x" %(i,char_width, margin_top))
			#bmps.extend(char_width.to_bytes(1, 'big'))
			#print ("i:%d" % i," ".join(["%02x" % c for c in list(ft)])) 
			
			
			if (unicode+1 != next_unicode):
				endrange = unicode
				sb = startrange.to_bytes(2, byteorder='big')
				header.append(sb[1])
				header.append(sb[0])
				eb = endrange.to_bytes(2, byteorder='big')	
				header.append(eb[1])
				header.append(eb[0])
				seq = seq_nr.to_bytes(2, byteorder='big')	
				header.append(seq[1])
				header.append(seq[0])
				seq_nr += endrange - startrange + 1
				startrange = -1
		else:
			print('multiple files of {:04x}'.format(unicode))

	rnr = range_nr.to_bytes(2, byteorder='big')
	header[0]=rnr[1]
	header[1]=rnr[0]
	
	font_file.write(header)
	font_file.write(bmps)

if len(sys.argv) == 3 and sys.argv[1] == 'unpack':
	unpackFont(sys.argv[2])
elif len(sys.argv) == 3 and sys.argv[1] == 'pack':
	packFont(sys.argv[2])
else:
	print('Usage:')
	print('   python', sys.argv[0], 'unpack Mili_chaohu.ft')
	print('   python', sys.argv[0], 'pack new_Mili_chaohu.ft')
