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
import png

# ! @x20 widht 2x22 (32)  0x20-0x4c
# " @x4c width 5x9  (76)
# # @x78 width 10x22 (121)
# $ @x155 width 8x26
# 4 @x938 with 9
# 5 @xa05 width 8

#@x478E5 forse c'è la tabella
#@4db30 fine file

#http://www.brescianet.com/appunti/vari/unicode.htm#Latino_base
#ofs         ASC       h        w
#00 00 00 00 00  00 00 00 00 00 00 ff 00 01 nul
#00 00 00 00 0d  00 00 00 00 00 08 ff 00 01 cr
#00 00 00 00 20  00 00 00 00 00 08 ff 00 01 sp
#00 00 00 00 21  00 04 16 16 02 08 ff 00 01 !
#2c 00 00 00 22  00 0a 08 16 01 0c ff 00 01 "
#59 00 00 00 23  00 13 16 16 00 13 ff 00 01 #
#35 01 00 00 24  00 0f 1a 17 01 11 ff 00 01 $

#3e 37 00 00 a2  00 0d 16 16 02 11 ff 00 01 c/

#@47958->20
#@47970->2c


#le immagini sono 4bpp


# Unpack the Amazfit Bip font file
# Creates 1bpp bmp images
def unpackFont(font_path):
	print('Unpacking', font_path)
	
	font_file = open(font_path, 'rb')
	font_path.join(font_path.split(os.sep)[:-1])
	if not os.path.exists('bmp-gtr'):
		os.makedirs('bmp-gtr')
	# header = 16 bytes
	file_content = font_file.read()
	header = file_content[0x0:0x20]
	#header = font_file.read(0x22)
	font_format = ord(header[4:5])
	print ("font_format",font_format)
	#num_ranges = (header[0x21] << 8) + header[0x20]
	#print ("num_ranges 0x%x" % num_ranges)
	
	fontFlag = header[0x0A]
	isNonLatin = bool(fontFlag & 1)
	isLatin = bool((fontFlag & 2)>>1)
	print ("non-Latin: %s" % (isNonLatin))
	print ("Latin:     %s" % (isLatin))
	
	
	last_block = file_content[-0xe::]
	print ("last_block", last_block)
	last_img = (ord(last_block[3:4])<<24) + (ord(last_block[2:3])<<16) + (ord(last_block[1:2])<<8)+ (ord(last_block[0:1])<<0)
	unicode = (ord(last_block[5:6])<<8) + (ord(last_block[4:5])<<0)
	pointer=0
	img_addr=0
	#print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%08x" %(pointer, last_block.hex(), img_addr, unicode, ))
	print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%08x" %(pointer, " ".join(["%02x" % el for el in list(last_block)]), img_addr, unicode, ))
	
	
	width=ord(last_block[6:7])
	height=ord(last_block[7:8])
	print ("w: %d h:%d" %(width, height))
	
	dimensione_stimata = int((width+1) //2) *height
	print ("dimensione_stimata 0x%02x"%dimensione_stimata)
	print ("last_img_addr = %x" % last_img)
	print ()	
	#pointer = last_img + 0x20 +dimensione_stimata + 7
	pointer =-0xe	
	print ("pointer; 0x%06x" % pointer )
	while last_block[-4::] != b'\x00\x00\x00\x00':
		#next_block = file_content[pointer+0xe:pointer+0xe+0xe]
		
		#next_img_addr = (ord(next_block[3:4])<<24) + (ord(next_block[2:3])<<16) + (ord(next_block[1:2])<<8)+ (ord(next_block[0:1])<<0)
		#try:
		img_addr = (ord(last_block[3:4])<<24) + (ord(last_block[2:3])<<16) + (ord(last_block[1:2])<<8)+ (ord(last_block[0:1])<<0)
		unicode = (ord(last_block[5:6])<<8) + (ord(last_block[4:5])<<0)
		width=ord(last_block[6:7])
		height=ord(last_block[7:8])
		#print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%08x" %(pointer, last_block.hex(), img_addr, unicode, ))
		print ("           ptr_to_img |U+xxy|w |h |        |footer  |")
		print ("----------------------|-----|--|--|--|--|--|--------|")
		print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%08x" %(pointer, " ".join(["%02x" % el for el in list(last_block)]), img_addr, unicode, ))
		pointer -=0xe
		last_block = file_content[pointer:pointer+0xe]
		if False: #unicode != 0x00c7 and unicode != 0x00c8 :
			#print (unicode)
			continue
		#el
		elif True:
			imgsize = int((width+1) //2) *height

			print ("imgsize:0x%04x h:%d w:%d h:%x w:%x" % (imgsize,height,width,height,width))
			#write_raw_image_data
			#bmp = open("gtr\\%08x.data" % unicode, 'wb')
			#bmp.write(file_content[0x20+img_addr:0x20+img_addr+imgsize])
			#bmp.close()
			
			if width >0 and height >0:
				#if unicode == 0x000021:
				#	print(file_content[0x20+img_addr:0x20+img_addr+imgsize])
				#print ("XX w: %d h:%d %d %d" %(width, height,((width+1)//2),(width)//2))
				png_attr={}
				png_attr["greyscale"] = True
				png_attr['bitdepth']=4
				png_out_file =open("bmp-gtr\\%08x.png" % unicode,"wb")
				pngwriter=png.Writer(width, height, **png_attr)
				png_out_image=[]
				decode_len=1
				for row in range(0,height):
					row_out=[]
					for col in range(0,width):
						#if unicode == 0x000021:
						#
						#	#print ("%0x"% (0x20+img_addr+pos))
						#if unicode == 0x0000c7:
						#	print ("XX",(width+1)//2,(width)//2)
						if (col % 2) == 0:
						        #pari
							ch = ord(file_content[0x20+img_addr+row*((width+1)//2) + col//2:0x20+img_addr+row*((width+1)//2)+ col//2+1]) &0xf
						else:
						        #dispari
							ch = ord(file_content[0x20+img_addr+row*((width+1)//2) + col//2:0x20+img_addr+row*((width+1)//2)+ col//2+1]) >>4
						#if row==11 and unicode==0x0028:
						#	print(col,0x20+img_addr+pos,file_content[0x20+img_addr+pos:0x20+img_addr+pos+1],ch)
						
						row_out.append(ch)
					#print(row_out)
					png_out_image.append(row_out)
				#print (png_out_image)
				pngwriter.write(png_out_file,png_out_image)
				png_out_file.close()

		print ()

		
	sys.exit(1)
	print ("0x%x", last_block)
	last_block = file_content[-0xe-0xe::]
	last_img = (ord(last_block[3:4])<<24) + (ord(last_block[2:3])<<16) + (ord(last_block[1:2])<<8)+ (ord(last_block[0:1])<<0)
	print ("0x%08x"% last_img)

	sys.exit(1)
	
	
	
	ranges = font_file.read(num_ranges*6)
	startrange = (ranges[len(ranges)-5] << 8) + ranges[len(ranges)-6]
	endrange = (ranges[len(ranges)-3] << 8) + ranges[len(ranges)-4]
	num_characters = (ranges[len(ranges)-1] << 8) + ranges[len(ranges)-2] +  endrange - startrange + 1

	startrange = (ranges[1] << 8) + ranges[0]
	endrange = (ranges[3] << 8) + ranges[2]
	range_nr = 0;
	for i in range (0, num_characters):

		img = Image.new('1', (16, 16), 0)
		pixels = img.load()
		char_bytes = font_file.read(32)
		print ("%d/%d" % (i,num_characters))
		x = 0
		y = 0
		# big endian
		for byte in char_bytes:
			#print (byte)
			bits = [(byte >> bit) & 1 for bit in range(8 - 1, -1, -1)]
			for b in bits:
				pixels[x, y] = b
				x += 1
				if x == 16:
					x = 0
					y += 1
		margin_top = font_file.read(1)
		img.save("bmp" + os.sep + '{:04x}'.format(startrange) + str(margin_top[0] % 16) + '.bmp') 
		
		startrange += 1
		if startrange > endrange and range_nr+1 < num_ranges:
			range_nr += 1
			startrange = (ranges[range_nr * 6 + 1] << 8) + ranges[range_nr * 6]
			endrange = (ranges[range_nr * 6 + 3] << 8) + ranges[range_nr * 6 + 2]

# Create a Amazfit Bip file from bmps
def packFont(font_path):
	print('Packing', font_path)
	font_file = open(font_path, 'wb')
	header = bytearray(binascii.unhexlify('4E455A4B08FFFFFFFFFF01000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF0000'))
	bmps = bytearray()
	
	range_nr = 0
	seq_nr = 0
	startrange = -1
	
	bmp_files = sorted(glob.glob('bmp' +  os.sep + '*'))

	for i in range (0, len(bmp_files)):
		margin_top = int(bmp_files[i][8])
		
		if(i == 0):
			unicode = int(bmp_files[i][4:-5],16)
		else:
			unicode = next_unicode
		
		if(i+1 < len(bmp_files)):
			next_unicode = int(bmp_files[i+1][4:-5],16)
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

			while y < 16:
				b = 0
				for j in range(0, 8):
					if pixels[x, y] != (0, 0, 0):
						b = b | (1 << (7 - j))
						if (x > char_width):
							char_width = x
					x += 1
					if x == 16:
						x = 0
						y += 1
				bmps.extend(b.to_bytes(1, 'big'))
			char_width = char_width * 16 + margin_top;
			bmps.extend(char_width.to_bytes(1, 'big'))
			
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
