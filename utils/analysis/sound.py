import random
import numpy
import matplotlib.pyplot as plt
import os
import wave
import pylab
from scipy.io import wavfile
import librosa
import librosa.display
from pydub import AudioSegment
from scipy.fftpack import fft
import subprocess

from utils.other import rdnname,writefile

def execmd(cmd):
	cnt = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE,stdout=subprocess.PIPE,stdin=subprocess.PIPE).communicate()[0].decode()
	return cnt

def sprectrogram(myAudio):
	result = []
	try:
		samplingFreq, mySound = wavfile.read(myAudio)
		mySoundDataType = mySound.dtype
		mySound = mySound / (2.**15)
		mySoundShape = mySound.shape
		samplePoints = float(mySound.shape[0])
		signalDuration =  mySound.shape[0] / samplingFreq
		mySoundOneChannel = mySound[:,0]
		timeArray = numpy.arange(0, samplePoints, 1)
		timeArray = timeArray / samplingFreq
		timeArray = timeArray * 1000
		plt.plot(timeArray, mySoundOneChannel, color='green')
		plt.xlabel('Time (ms)')
		plt.ylabel('Amplitude')
		plt.savefig('/tmp/spectro_audio1.png')
		result.append([f'**Spectrogram 1**',f'/tmp/spectro_audio1.png'])
		mySoundLength = len(mySound)
		fftArray = fft(mySoundOneChannel)
		numUniquePoints = int(numpy.ceil((mySoundLength + 1) / 2.0))
		fftArray = fftArray[0:numUniquePoints]
		fftArray = abs(fftArray)
		fftArray = fftArray / float(mySoundLength)
		fftArray = fftArray **2
		if mySoundLength % 2 > 0:
			fftArray[1:len(fftArray)] = fftArray[1:len(fftArray)] * 2
		else:
			fftArray[1:len(fftArray) -1] = fftArray[1:len(fftArray) -1] * 2  
		freqArray = numpy.arange(0, numUniquePoints, 1.0) * (samplingFreq / mySoundLength);
		plt.plot(freqArray/1000, 10 * numpy.log10 (fftArray), color='blue')
		plt.xlabel('Frequency (Khz)')
		plt.ylabel('Power (dB)')
		plt.savefig('/tmp/spectro_audio2.png')
		result.append([f'**Spectrogram 2**',f'/tmp/spectro_audio2.png'])
		freqArrayLength = len(freqArray)
		result.append([f'**Frequency**',f'/tmp/freqData.txt'])
		result.append([f'**Fourier transformation**',f'/tmp/fftData.txt'])
		numpy.savetxt("/tmp/freqData.txt", freqArray, fmt='%6.2f')
		numpy.savetxt("/tmp/fftData.txt", fftArray)
	except Exception as ex:
		print(ex)
		pass
	
	try:
		x, sr = librosa.load(myAudio, sr=44100)
		X = librosa.stft(x)
		Xdb = librosa.amplitude_to_db(abs(X))
		plt.figure(figsize=(14, 5))
		librosa.display.specshow(Xdb, sr = sr, x_axis = 'time', y_axis = 'log')
		plt.savefig('/tmp/spectro_audio3.png')
		result.append([f'**Spectrogram 3**',f'/tmp/spectro_audio3.png'])
	except Exception as ex:
		print(ex)
		pass

	try:
		x, sr = librosa.load(myAudio, sr=44100)
		X = librosa.stft(x)	
		Xdb = librosa.amplitude_to_db(abs(X))
		plt.figure(figsize=(14, 5))
		librosa.display.specshow(Xdb, sr = sr, x_axis = 'time', y_axis = 'hz')
		plt.savefig('/tmp/spectro_audio4.png')
		result.append([f'**Spectrogram 4**',f'/tmp/spectro_audio4.png'])
	except Exception as ex:
		print(ex)
		pass

	try:
		wav = wave.open(myAudio, 'r')
		frames = wav.readframes(-1)
		sound_info = pylab.fromstring(frames, 'int16')
		frame_rate = wav.getframerate()
		wav.close()
		pylab.figure(num=None, figsize=(19, 12))
		pylab.subplot(111)
		pylab.title('spectrogram of %r' % myAudio)
		pylab.specgram(sound_info, Fs=frame_rate)
		pylab.savefig('/tmp/spectro_audio5.png')
		result.append([f'**Spectrogram 5**',f'/tmp/spectro_audio5.png'])
	except Exception as ex:
		print(ex)
		pass

	return result

def append(result,command,cnt):
    if len(cnt) < 2000  and 'strings' != command.lower():
        result.append('**%s**```\n%s```'%(command,cnt))
    else:
        rdn_name = rdnname()
        writefile('/tmp/%s.txt'%str(rdn_name),cnt)
        result.append(['**%s**'%command,'/tmp/%s.txt'%str(rdn_name)])
    return result

def analyse_sound(path_audio,ext):
	result = []
	if(ext == '.wav'):

		# Sox convertion > For frequency graph		
		new_path = "/tmp/%s.wav"%rdnname()
		os.system('sox %s  %s;rm %s'%(path_audio,new_path,path_audio))
		path_audio = new_path


		# stegolsb Analyse
		for i in range(1,3):
			try:
				cmd = 'stegolsb wavsteg -r -i %s -b 1000 -o /tmp/wavlsb%s.txt -n %s'%(path_audio,str(i),str(i))				
				cnt = execmd(cmd)

				if(os.path.isfile('/tmp/wavlsb%s.txt'%str(i))):
					result.append('**Wavsteg LSBs=%s**```\n%s```'%(str(i),cnt))
					result.append(['**Content=%s**'%str(i),'/tmp/wavlsb%s.txt'%str(i)])

			except Exception as ex:
				result.append('**Wavsteg LSBs=%s**```\n%s```'%(str(i),str(ex)))

		

	# Classical Analysis			
	cmd = {
		"Strings_head":"timeout 10 strings -t x %s | head -n 20"%path_audio,
		"Strings_bottom":"timeout 10 strings -t x %s} | tail -n 20"%path_audio,
		"Exiftool":"timeout 10 exiftool %s"%path_audio,
		"Binwalk":"timeout 10 binwalk %s"%path_audio,
		"Dtmf (Phone)":"timeout 10 dtmf -v %s"%path_audio
	}

	for command in cmd.keys():
		try:
			cnt = execmd(cmd[command])
			result = append(result,command,cnt)			
		except Exception as ex:
			result.append('**%s**```\n%s```'%(command,str(ex)))



	# sstv_cmd = f'timeout 15 sstv -d {path_audio} -o /tmp/sstv.png'
	# print(sstv_cmd)
	# try:
	# 	cnt = os.popen(sstv_cmd).read()
	# 	print(cnt)
	# 	result.append(f'**Sstv**```\n{cnt}```')
	# 	if(os.path.isfile('/tmp/sstv.png')):
	# 		result.append([f'File',f'/tmp/sstv.png'])
	# except Exception as ex:
	# 	result.append(f'**Sstv**```\n'+str(ex)+'```')



	# hideme
	cwd = os.getcwd()
	hidee_cmd = "./hideme ../../../%s -f"%path_audio
	try:
		os.chdir(cwd+'/utils/analysis/tools/AudioStego/build/')
		cnt = execmd(hidee_cmd)
		result = append(result,"Hideme",cnt)
	except Exception as ex:
		result.append('**Hideme**```\n%s```'%str(ex))
	os.chdir(cwd)


	# sprectrogram
	result += sprectrogram(path_audio)


	# sox_cmd Spectrogram
	sox_cmd = f"timeout 10 sox {path_audio} -n spectrogram"
	try:
		res = execmd(sox_cmd)
		rdn_name = rdnname()
		os.popen('mv spectrogram.png /tmp/%s.png'%rdn_name).read()
		result.append(['**SoxSpectrogram**','/tmp/%s.png'%rdn_name])
	except Exception as ex:
		result.append('**SoxSpectrogram**```\n%s```'%str(ex))



	return result