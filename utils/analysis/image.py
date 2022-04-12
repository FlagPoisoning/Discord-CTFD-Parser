import os
import random
import matplotlib.pyplot as plt
from PIL import Image
import numpy
import subprocess

from utils.other import rdnname,writefile

def analyseImage(path):
    im = Image.open(path)
    results = {'size': im.size,'mode': 'full',}
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results

def gifextract(path):
    mode = analyseImage(path)['mode']    
    im = Image.open(path)
    i = 0
    p = im.getpalette()
    last_frame = im.convert('RGBA')    
    try:
        while True:
            if not im.getpalette():
                im.putpalette(p)            
            new_frame = Image.new('RGBA', im.size)
            if mode == 'partial':
                new_frame.paste(last_frame)            
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            new_frame.save("/tmp/gifpng/"+'%s-%d.png' % (''.join(os.path.basename(path).split('.')[:-1]), i), 'PNG')
            i += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        return True
    return False

def lsb_graph(in_file,savepath):
	BS = 100
	img = Image.open(in_file)
	(width, height) = img.size
	conv = img.convert("RGBA").getdata()
	vr = []
	vg = []
	vb = []
	for h in range(height):
		for w in range(width):
			(r, g, b, a) = conv.getpixel((w, h))
			vr.append(r & 1)
			vg.append(g & 1)
			vb.append(b & 1)
	avgR = []
	avgG = []
	avgB = []
	for i in range(0, len(vr), BS):
		avgR.append(numpy.mean(vr[i:i + BS]))
		avgG.append(numpy.mean(vg[i:i + BS]))
		avgB.append(numpy.mean(vb[i:i + BS]))
	numBlocks = len(avgR)
	blocks = [i for i in range(0, numBlocks)]
	plt.axis([0, len(avgR), 0, 1])
	plt.ylabel('Average LSB per block')
	plt.xlabel('Block number')
	plt.plot(blocks, avgB, 'bo')
	plt.savefig(savepath)

def execmd(cmd):
	cnt = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()[0].decode()
	return cnt

def append(result,command,cnt):
    if len(cnt) < 2000  and 'strings' != command.lower():
        result.append('**%s**```\n%s```'%(command,cnt))
    else:
        rdn_name = rdnname()
        writefile('/tmp/%s.txt'%str(rdn_name),cnt)
        result.append(['**%s**'%command,'/tmp/%s.txt'%str(rdn_name)])
    return result

def analyse_picture(img,ext):
	result = []

	## All Cmd 
	cmd = {
		"Strings":"timeout 10 strings -t x %s" %img,
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%img,
		"Strings_bottom":"timeout 10 strings -t x %s | tail -n 20"%img,
		"Exiftool":"timeout 10 exiftool %s"%img,
		"Pngcheck":"timeout 10 pngcheck -vtp7 %s"%img,
		"Identify":"timeout 10 identify -verbose %s"%img,
		"Binwalk":"timeout 10 binwalk %s"%img,
		"Zsteg":"timeout 10 zsteg %s"%img,
		"Stegpy":"timeout 10 stegpy %s"%img,
		"StegoPVD (Line 1-6 = Logo)":"timeout 10 stegopvd bruteforce %s"%img,
		"Jsteg":"timeout 10 jsteg reveal %s"%img
		}

	
	# Execute Cmd for all
	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append(result,command,cnt)
		except Exception as ex:
			result.append('**%s**```\n%s```'%(command,str(ex)))
	

	# Cmd with file as output
	cmd2 = {
		"Stegoveritas":"UUID=`cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w 32 | head -n 1`;TMP_DIR=/data/stegoVeritas/$UUID;mkdir -p $TMP_DIR;stegoveritas %s -out $TMP_DIR -meta -imageTransform -colorMap -trailing;zip -q -r /data/stegoVeritas/$UUID.zip /data/stegoVeritas/$UUID ;rm -r /data/stegoVeritas/$UUID;echo UID=$UUID"%img,
		"LsbDetect": "stegolsb stegdetect -i %s -n 2"%img
	}
	for command in cmd2.keys():
		try:
			cnt = execmd(cmd2[command])
			result_path = ""

			if(command == "Stegoveritas"):
				result_path = '/data/stegoVeritas/%s.zip'%cnt.split('UID=')[1].strip()
			else:
				result_path = '%s/%s_2LSBs.%s'%(os.path.dirname(os.path.abspath(img)),os.path.basename(img).split('.')[0],os.path.basename(img).split('.')[1])

			if(os.path.isfile(result_path)):
				result.append(['**%s**'%command,result_path])
		except Exception as ex:

			print(ex)
			input()

			result.append('**%s**```\n%s```'%(command,str(ex)))



	# If is gif
	## Other Cmd	
	gifpng_cmd = 'zip -q -r /tmp/gifframe.zip /tmp/gifpng;rm -r /tmp/gifpng/%s*'%''.join(os.path.basename(img).split('.')[:-1])

	if('.gif' == ext):
		try:
			if(os.path.isdir('/tmp/gifpng') == False):
				os.mkdir('/tmp/gifpng')
			if(gifextract(img)):				
				execmd(gifpng_cmd)
				if(os.path.isfile('/tmp/gifframe.zip')):
					result.append(['**GifFrames**','/tmp/gifframe.zip'])
		except Exception as ex:
			result.append('**GifFrames**```\n%s```'%str(ex))



	## LsbGraph
	try:
		lsb_graph(img,'/tmp/lsb_graph.png')
		if(os.path.isfile('/tmp/lsb_graph.png')):
			result.append([f'**LsbGraph**',f'/tmp/lsb_graph.png'])
	except Exception as ex:
		result.append('**LsbGraph**```\n%s```'%str(ex))



	return result