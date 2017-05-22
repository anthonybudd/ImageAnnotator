import os
import cv2
import sys
import math
import time
	
def getFPS(video):
	major_ver = int((cv2.__version__).split('.')[0])
	if int(major_ver)  < 3 :
		fps = video.get(cv2.cv.CV_CAP_PROP_FPS)
	else :
		fps = video.get(cv2.CAP_PROP_FPS)
	return fps

def printProgress(iteration, total, prefix = 'Progress', suffix = 'Complete', decimals = 1, barLength = 50, fill = '|'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(barLength * iteration // total)
    bar = fill * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s [%s] %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

path = sys.argv[1]
now = time.time()
video = cv2.VideoCapture(path)
file = os.path.basename(path)
directory, fileExtension = os.path.splitext(file)
frameRate = getFPS(video)
frameID = 0
iterations = int(video.get(cv2.cv.CV_CAP_PROP_FRAME_COUNT))
printProgress(0, iterations)


if not os.path.exists(directory):
	os.makedirs(directory)

while(video.isOpened()):
	try:
		frameID = frameID +1
		ret, frame = video.read()
		if(ret != True):
			break

		if(frameID % math.floor(frameRate / 4) == 0):
			sec = int(frameID / frameRate)
			filename = directory +"/"+ os.path.splitext(os.path.basename(sys.argv[1]))[0] +"-"+ str(frameID) +"-"+ str(int(time.time())) +".jpg"
			cv2.imwrite(filename, frame)
			printProgress(frameID, iterations)
	except KeyboardInterrupt:
		print "Done! (" + str(int(time.time() - now)) + "s)"
		video.release()

video.release()

print "\nDone! (" + str(int(time.time() - now)) + "s)"

print "Zipping..."

os.system((' ').join(['zip', '-r', (directory+'.zip'), directory, '>> /dev/null 2>&1']))

print "Zipped: " + directory +".zip"

os.system((' ').join(['mv', path, path.replace('Videos', 'done-videos')]))
os.system((' ').join(['rm -rf', directory]))