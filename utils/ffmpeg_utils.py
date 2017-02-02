
import os,subprocess

rf_script = os.environ['RFSCRIPT']
ffmpeg_path = rf_script + '/lib/ffmpeg-20161227-0ff8c6b-win64-static/bin/ffmpeg.exe'

# playblast  -fmt "avi" -startTime 301 -endTime 325 -sequenceTime 1 -forceOverwrite -filename "movies/s0030.avi" -clearCache 1 -showOrnaments 0 -percent 100 -wh 1024 778 -offScreen -viewer 0 -useTraxSounds -compression "none" -quality 70;

# playblast -fmt "avi" -startTime 101 -endTime 325 -sequenceTime 1 -forceOverwrite -filename "movies/Shot.avi" -clearCache 1 -showOrnaments 0 -percent 100 -wh 960 540 -offScreen -viewer 1 -useTraxSounds -compression "none" -quality 70;

def convert_to_mov(src,dst):
	# convert directly from all video formats to mov(H.264) format
	cmd = ffmpeg_path
	cmd += ' -y -i ' + src
	cmd += ' -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags +faststart -vf scale=-2:720,format=yuv420p '
	cmd += dst

	p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
	p.communicate()

	if os.path.exists(src) and os.path.exists(dst):
		os.remove(src)

	return dst


# C:/Users/vanef/Dropbox/script_server/lib/ffmpeg-20161227-0ff8c6b-win64-static/bin/ffmpeg.exe -y -i C:/Users/vanef/Dropbox/media_server/project/scene/ep01/q0010/all/movies/pr_ep01_q0010_s0020_v006.avi -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k -movflags +faststart -vf scale=-2:720,format=yuv420p C:/Users/vanef/Dropbox/media_server/project/scene/ep01/q0010/all/movies/pr_ep01_q0010_s0020_v006.mov
# C:/Users/vanef/Dropbox/script_server/lib/ffmpeg-20161227-0ff8c6b-win64-static/bin/ffmpeg.exe -y -i C:/Users/vanef/Documents/maya/projects/default/movies/s0010.avi -c:v libx264 C:/Users/vanef/Documents/maya/projects/default/movies/s0010.mov
