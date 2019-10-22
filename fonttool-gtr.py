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
import json

import argparse

#site with unicode ranges
#https://www.compart.com/en/unicode/block/U+A720

# ! @x20 widht 2x22 (32)  0x20-0x4c
# " @x4c width 5x9  (76)
# # @x78 width 10x22 (121)
# $ @x155 width 8x26
# 4 @x938 with 9
# 5 @xa05 width 8

#@x478E5 forse c'è la tabella
#@4db30 fine file

#http://www.brescianet.com/appunti/vari/unicode.htm#Latino_base
#w+ is the w+ the space between the next char
#vo is the vertical offset of the image...
#ofs         Ul  Uh w  h  vo    w+
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

dirname = "bmp-gtr"


# Unpack the Amazfit Bip font file
# Creates 1bpp bmp images
def unpackFont(font_path, raw = None, verbose = 0):
	print('Unpacking', font_path)
	
	font_file = open(font_path, 'rb')
	font_path.join(font_path.split(os.sep)[:-1])
	if not os.path.exists(dirname):
		os.makedirs(dirname)
	# header = 16 bytes
	file_content = font_file.read()
	header = file_content[0x0:0x20]
	#header = font_file.read(0x22)
	fontVersion = ord(header[4:5])
	print ("fontVersion",fontVersion)
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
	#print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%04x" %(pointer, last_block.hex(), img_addr, unicode, ))
	print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%04x" %(pointer, " ".join(["%02x" % el for el in list(last_block)]), img_addr, unicode, ))
	
	addresses = 0
	
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
		addresses += 1
		#next_block = file_content[pointer+0xe:pointer+0xe+0xe]
		
		#next_img_addr = (ord(next_block[3:4])<<24) + (ord(next_block[2:3])<<16) + (ord(next_block[1:2])<<8)+ (ord(next_block[0:1])<<0)
		#try:
		img_addr = (ord(last_block[3:4])<<24) + (ord(last_block[2:3])<<16) + (ord(last_block[1:2])<<8)+ (ord(last_block[0:1])<<0)
		unicode = (ord(last_block[5:6])<<8) + (ord(last_block[4:5])<<0)
		width=ord(last_block[6:7])
		height=ord(last_block[7:8])
		
		# FF0061 = carattere combinato
		
		#print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%04x" %(pointer, last_block.hex(), img_addr, unicode, ))
		if verbose > 0:
			print ("           ptr_to_img |U+xxy|w |h |      w+|footer  |")
			print ("----------------------|-----|--|--|--|--|--|--------|")
			print ("ptr=%06x %s img_data_addr=%08x+0x20 unicode=%04x" %(pointer, " ".join(["%02x" % el for el in list(last_block)]), img_addr, unicode, ))
		if False: #unicode != 0x00c7 and unicode != 0x00c8 :
			#print (unicode)
			continue
		#el
		elif True:
			imgsize = int((width+1) //2) *height

			if verbose > 0:
				print ("imgsize:0x%04x h:%d w:%d h:%x w:%x" % (imgsize,height,width,height,width))
			
			if raw:
				#write_raw_image_data
				bmp = open(dirname + os.path.sep + "%04x-%s-%s.data" %  (unicode,"".join(["%02x" % el for el in list(last_block[6::])]),"" ),"wb")
				bmp.write(file_content[0x20+img_addr:0x20+img_addr+imgsize])
				bmp.close()
						
			if width >0 and height >0:
				#if unicode == 0x000021:
				#	print(file_content[0x20+img_addr:0x20+img_addr+imgsize])
				#print ("XX w: %d h:%d %d %d" %(width, height,((width+1)//2),(width)//2))

				png_out_image=[]
				decode_len=1
				depth = 4
				decode_len=1
				bit_mask=(pow(2,depth) -1)
				pos=0x20 + img_addr
				for row in range(0,height):
					row_out=[]
					shift_mask=0
					value = file_content[pos]
					for col in range(0,width * decode_len):
						#decode len is 1 .. or 4 if 32 bits
						row_out.append( ((value  >> shift_mask) & bit_mask) *0x11 )
						if (shift_mask==8-depth):
							#byte is full
							shift_mask=0
							pos+=1
							try:
								value=file_content[pos]
							except:
								print ("FIXME", pos, len(self.fileContent))
							#print 'addr %d val %x'%(pos-16-12-start,value)
						else:
							#we need to fill other bits
							shift_mask+=depth
					if ( shift_mask != 0):
						#other bits are useless
						pos+=1
					
					#print(row_out)
					png_out_image.append(row_out)
				png_attr={}
				png_attr["greyscale"] = True
				png_attr['bitdepth']=8
				png_attr['compression'] = 0
				#png_out_file =open("bmp-gtr" + os.path.sep + "%08x.png" % unicode,"wb")
				png_out_file = open(dirname + os.path.sep + "%04x-%s.png" %  (unicode,"".join(["%02x" % el for el in list(last_block[6::])])),"wb")
				pngwriter=png.Writer(width, height, **png_attr)
				pngwriter.write(png_out_file,png_out_image)
				png_out_file.close()
				if verbose > 0:
					print ("file %s saved" % (dirname + os.path.sep + "%04x.png" % unicode))
			else:
				dummypng = open(dirname + os.path.sep + "%04x-%s.png" %  (unicode,"".join(["%02x" % el for el in list(last_block[6::])]) ),"wb")
				#dummypng.write(char(0x0)
				dummypng.close()

		pointer -=0xe
		last_block = file_content[pointer:pointer+0xe]

		if verbose >0:
			print ()

	config = {}
	config["fontFlags"] = fontFlag
	config["fontVersion"] = fontVersion
	config["offset"] = len(file_content) + pointer + 0xe
	config["addresses"] = addresses
	
	
	fjson =  open(dirname + os.path.sep + "_font_info.json", "w")
	json.dump(config, fjson, indent=4, sort_keys=True)
	fjson.close()


# Create a Amazfit Bip file from bmps
def packFont(font_path, raw = None, verbose = 0):
	print('Packing', font_path)
	
	fjson = open(dirname + os.path.sep + "_font_info.json", "r")
	config = json.load(fjson)
	fjson.close()
	
	#header = bytearray(binascii.unhexlify('4E455A4B08FFFFFFFFFF01000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'))
	header = bytearray(binascii.unhexlify('4E455A4B99FFFFFFFFFF99000000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'))
	bmps = bytearray()
	mappings = bytearray()
	
	header[0x0A] = config["fontFlags"]
	header[0x04] = config["fontVersion"]
	
	range_nr = 0
	seq_nr = 0
	startrange = -1
	
	bmp_files = sorted(glob.glob(dirname +  os.sep + '*.png'))

	for i in range (0, len(bmp_files)):
		#margin_top = int(bmp_files[i].split(os.sep)[1][4:6],16)
		
		if(i == 0):
			unicode = int(bmp_files[i].split(os.sep)[1][0:4],16)
			blob = binascii.unhexlify(bmp_files[i].split(os.sep)[1][9:21])
		else:
			unicode = next_unicode
			blob = next_blob
		
		if(i+1 < len(bmp_files)):
			next_unicode = int(bmp_files[i+1].split(os.sep)[1][0:4],16)
			next_blob = binascii.unhexlify(bmp_files[i+1].split(os.sep)[1][9:21])
		else:
			next_unicode = -1
			
		if verbose > 0:
			print (unicode,next_unicode)
		
		if (unicode != next_unicode):		
			if (startrange == -1):
				range_nr += 1			 
				startrange = unicode
			
			if verbose > 0:
				print (bmp_files[i])
			mappings.extend(len(bmps).to_bytes(4,'little')) #address
			mappings.extend(unicode.to_bytes(2,'little')) #address

			if os.stat(bmp_files[i]).st_size == 0:
				width = 0
				height = 0
				mappings.extend(width.to_bytes(1,'big')) 
				mappings.extend(height.to_bytes(1,'big')) 
				#mappings.extend(width.to_bytes(1,'big')) 
				#mappings.extend(height.to_bytes(1,'big')) 
				#mappings.extend(height.to_bytes(1,'big')) 
				#mappings.extend(binascii.unhexlify('FF0001')) 
				mappings.extend(blob)
				continue
			pngreader = png.Reader(bmp_files[i])
			(width, height, png_in_image, attr) = pngreader.read()
			unk = 0
			mappings.extend(width.to_bytes(1,'big')) 
			mappings.extend(height.to_bytes(1,'big')) 
			#mappings.extend(unk.to_bytes(1,'big')) 
			#mappings.extend(unk.to_bytes(1,'big')) 
			#mappings.extend(unk.to_bytes(1,'big')) 
			#mappings.extend(binascii.unhexlify('FF0001'))
			mappings.extend(blob)
			
			depth=attr['bitdepth']
			grey=attr['greyscale']
			alpha=attr['alpha']
			
			if depth != 8 or not grey or alpha:
				print ("Image %s not compatible, should be grayscale, bitdepth 8, without alpha channel" % (bmp_files[i]))
			
			bmpsraw = bytearray() #DEBUG CODE
			raw_out_image=''
			if verbose > 0:
				print ("w:%d h:%d" %(width,height))
			cnt=0
			depth=4
			for row in png_in_image:
				shift_mask=0
				value=0
				for ii in range(0,len(row)):
					value|=((row[ii]//0x10) <<shift_mask)
					if (shift_mask ==8-depth):
						bmps.extend(value.to_bytes(1, 'big'))
						bmpsraw.extend(value.to_bytes(1, 'big'))  #DEBUG CODE
						value=0
						shift_mask=0
					else:
						shift_mask+=depth
				if ( shift_mask != 0):
					bmps.extend(value.to_bytes(1, 'big'))
					bmpsraw.extend(value.to_bytes(1, 'big'))  #DEBUG CODE

			if raw:
				f = open(bmp_files[i]+".raw","wb")  #DEBUG CODE
				f.write(bmpsraw)  #DEBUG CODE
				f.close()  #DEBUG CODE
		else:
			print('multiple files of {:04x}'.format(unicode))

	rnr = range_nr.to_bytes(2, byteorder='big')

	font_file = open(font_path, 'wb')
	font_file.write(header)	
	font_file.write(bmps)
	if verbose > 0:
		print (len(bmps))
	if len(bmps) > config["offset"] - 0x20:
		print ("file too big, remove some fonts %d > %d" % (len(bmps) , config["offset"]) )
		sys.exit(1)
	font_file.write(bytes([0]* (config["offset"] - len(bmps) - 0x20)  ))##fixme) #7 should be computated to align
	font_file.write(mappings)

parser = argparse.ArgumentParser(description="Font tool for amazfit")
parser.add_argument('-d', '--directory', dest='dirname', default=dirname)
parser.add_argument('-r', '--raw', dest='raw', action='store_true')
parser.add_argument('-v', dest='verbose', action='count', default=0, help='verbose')
parser.add_argument("mode", help="<pack|unpack>")
parser.add_argument("filename", 
                    help="<filename>")
args = parser.parse_args()

if args.dirname:
	dirname = args.dirname

if args.mode and args.mode == 'unpack':
	unpackFont(args.filename, raw = args.raw, verbose = args.verbose)
elif args.mode and args.mode == 'pack':
	packFont(args.filename, raw = args.raw, verbose = args.verbose)
else:
	print('Usage:')
	print('   python', sys.argv[0], 'unpack Mili_falcon.ft')
	print('   python', sys.argv[0], 'pack new_Mili_falcon.ft')
