import subprocess
import sys
import re
import math
import os
import cv2
import argparse
import shutil

len_exp = 'Duration: (\d{2}):(\d{2}):(\d{2})\.\d+,'
re_len = re.compile(len_exp)

"""
Extract frames from a video clip using ffmpeg
@Parameters
    in_file_path:input video clip path
    frames_out_path: Path where extracted frames needs to be stored
"""
def extract_frames_from_video_ffmpeg(in_file_path, frames_out_path):

    #parse input file path to create output path
    dir_name, file_name = os.path.split(in_file_path)
    sub_folder_name = ".".join(file_name.split('.')[:-1])
    folder_name, num = sub_folder_name.split('-')

    #create a folder to store frames
    mid_path = os.path.join(frames_out_path, folder_name)
    if not os.path.exists(mid_path):
	os.makedirs(mid_path)

    #create a complete output path
    f_out_path = os.path.join(mid_path, sub_folder_name)
    if not os.path.exists(f_out_path):
	os.makedirs(f_out_path)

    #ffmpeg command to extract frames
    out_path = os.path.join(f_out_path, "frame-")
    s_cmd = "ffmpeg -i %s -t 1 -f image2 %s" %(in_file_path, out_path)
    ss_cmd = s_cmd+'%d.jpg'
    subprocess.Popen(ss_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

"""
Extract frames from each of the samll (1 sec) video clips using opencv
@Parameters
    in_file_path:input path of a Small video clip
    frames_out_path:output path where individual frames needs to be stored
"""
def extract_frames_from_video_CV(in_file_path, frames_out_path):

    cap = cv2.VideoCapture(in_file_path)

    #parse input file path to create output path
    dir_name, file_name = os.path.split(in_file_path)
    sub_folder_name = ".".join(file_name.split('.')[:-1])
    folder_name, num = sub_folder_name.split('-')

    #create a folder to store frames
    mid_path = os.path.join(frames_out_path, folder_name)
    if not os.path.exists(mid_path):
	os.makedirs(mid_path)

    #create a complete output path
    f_out_path = mid_path + "/"+ sub_folder_name
    if not os.path.exists(f_out_path):
	os.makedirs(f_out_path)
	
    #read all the frames and write into output path
    count = 0
    while cap.isOpened():
	fPath = "frame-"+str(count)+".jpg"
	comp_out_path = f_out_path + '/' + fPath

	ret, frame = cap.read()
	if ret == True:
	    cv2.imwrite(comp_out_path, frame)
	    count += 1
	else:
	    break

    #release resources
    cap.release()
    cv2.destroyAllWindows()

"""
Split a video file into equal parts based on sLength
@Parameters
    in_file_path:input video clip path
    sLength:desired small video clip length
    out_path: output video clip path where smaller length video clips needs to be saved
"""
def split_video_into_equal_parts(in_file_path, sLength, out_path):
    print("video_splitter::split_video_into_equal_parts in_file_path:, sLength:, out_path:", in_file_path, sLength, out_path)

    #make sure sLength should be greater than 0
    if sLength <= 0:
        raise SystemExit

    """
    print("ffmpeg version")
    ffmpeg_p = subprocess.Popen('ffmpeg', stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
    output, _ = ffmpeg_p.communicate()
    print(_)

    print("####################################################")
    s_cmd = "ffmpeg -filter:v idet -frames:v 100 -an -f rawvideo -y /dev/null -i %s"%(in_file_path)
    out_val = subprocess.Popen(s_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()
    #out_val = subprocess.Popen("ffmpeg -i '"+in_file_path+"' 2>&1 | grep "Co, shell=True, stdout=subprocess.PIPE).stdout.read()
    print(out_val)
    print("####################################################")
    """
    #use subprocess to load ffmpeg and retrieve duration of the clip
    out_val = subprocess.Popen("ffmpeg -i '"+in_file_path+"' 2>&1 | grep 'Duration'", shell = True, stdout = subprocess.PIPE).stdout.read()
    #out_val = subprocess.Popen("ffmpeg -i '"+in_file_path+"' 2>&1 | grep 'Stream'", shell = True, stdout = subprocess.PIPE).stdout.read()
    print("out val:",out_val)
    matches = re_len.search(out_val.decode('utf-8'))
    if matches:
        video_len = int(matches.group(1)) * 3600 + int(matches.group(2)) * 60 + int(matches.group(3))
        print ("video len", video_len)
    else:
        print("wrong video file")
        raise SystemExit

    #compute no.of small video clips of a bigger video clip
    s_count = int(math.ceil(video_len/float(sLength)))
    if s_count == 1:
        print("video clip is ver small")
        raise SystemExit

    """
    #set the audio and video codec
    vcodec = "h264"
    vcodec = "libx264"
    acodec = "copy"
    extra = "-threads 8"
    filt = "-filter:v setpts=0.5*PTS"
    s_cmd = " -i '%s' -c:v %s -preset ultrafast -acodec %s"%(in_file_path, vcodec, acodec)
    """
    s_cmd = " -i '%s'"%(in_file_path) #use default CODEC
	
    try:
        dir_name, file_name = os.path.split(in_file_path)
        fileext = file_name.split(".")[-1]
    except IndexError as e:
        raise IndexError("No . in filename. Error: " + str(e))

    #create output path to store small video clips
    new_folder_name = ".".join(file_name.split('.')[:-1])
    out_file_path = out_path+"/"+new_folder_name
    if not os.path.exists(out_file_path):
        os.makedirs(out_file_path)

    #split as small video clips based on sLength and write into output path
    out_file_path = out_file_path + '/'+ new_folder_name
    for n in range(0, s_count):
        s_str = ""
        if n == 0:
            s_start = 0
        else:
            s_start = sLength*n
            #s_str += "ffmpeg"+" -ss "+str(s_start)+" -t "+str(sLength) + s_cmd + " '"+out_file_path + "-" + str(n) + "." + fileext + "'"
            s_str += "ffmpeg"+" -ss "+str(s_start)+ s_cmd + " -t "+str(sLength) + " '"+out_file_path + "-" + str(n) + "." + fileext + "'"
            print("About to run: "+s_str)
            out_val = subprocess.Popen(s_str, shell=True, stdout=subprocess.PIPE).stdout.read()

"""
Extract fps information from each video clip
@Parameters
    file_path:video clip path
"""
def extract_fps(file_path):
    vCap = cv2.VideoCapture(file_path)

    #find opencv version
    (maj_ver, min_ver, submin_ver) = (cv2.__version__).split('.')

    if int(maj_ver) < 3 :
	fps = vCap.get(cv2.cv.CV_CAP_PROP_FPS)
    else:
	fps = vCap.get(cv2.CAP_PROP_FPS)

    vCap.release()

"""
Split video clip based on starting position and small clip length given
@Parameters
	file_path: Path of the video movie clip
	start_pos: position at which it should start splitting rather than begining
	split_length: Length of the small clip from the start_pos
	out_path: path where small video clip needs to be stored
"""
def split_video_random(file_path, start_pos, split_length, out_path):

    """
    #Provide video codec
    vcodec = "h264"
    acodec = "copy"
    extra = ""
    split_cmd = "ffmpeg -i '%s' -vcodec %s -acodec %s -y %s" % (file_path, vcodec, acodec, extra)
    s_cmd = " -i '%s' -vcodec %s -acodec %s"%(file_path, vcodec, acodec)
    """
    s_cmd = " -i '%s'"%(file_path) #use default CODEC
    try:
	fileext = file_path.split(".")[-1]
    except IndexError as e:
	raise IndexError("No ext. in filename. Error: " + str(e))

    split_start = start_pos
    split_length = split_length
    head, tail = os.path.split(file_path)
    name, ext = tail.split('.')
    filebase=name+'_'+str(start_pos)+'-'+str(split_length)

    dstfilebase = out_path + '/' + filebase # create output file base

    #split_str = ""
    #split_str += " -ss " + str(split_start) + " -t " + str(split_length) + " '"+ dstfilebase + "." + fileext + "'"

    s_str = ""	
    #s_str += "ffmpeg"+" -ss "+str(split_start)+" -t "+str(split_length) + s_cmd + " '"+dstfilebase + "." + fileext + "'"
    s_str += "ffmpeg" + " -ss " + str(split_start) + s_cmd + " -t " + str(split_length) + " '"+ dstfilebase + "." + fileext + "'"
    print("########################################################")
    #print "About to run: "+split_cmd+split_str
    print("About to run: "+s_str)
    print("########################################################")
    #output = subprocess.Popen(split_cmd+split_str, shell = True, stdout = subprocess.PIPE).stdout.read()
    output = subprocess.Popen(s_str, shell=True, stdout=subprocess.PIPE).stdout.read()

"""
It splits the video clip either equally or based on position and length provided
@Parameters
	args: argumentes passed from command prompt
"""
def video_clip_split(args):

    frames_out_path = ""
    if args.split_option == "equal": # split video clip as equal parts from the beging of the clip

        #Parse the original video files directory and split each one of them as 1 sec video clip
	sLength = 5
	in_path = '/mnt/data/raw_video_files'
	out_path = '/mnt/data/small_video_clips'

	#check the movies already indexed
	indexed_movies_lst = []
	for ind_name in os.listdir(out_path):
	    indexed_movies_lst.append(ind_name)

	for fname in os.listdir(in_path):

            basename, ext=fname.split(".")

            """
	    skip the indexed movies
	    This is based on searching the folder name (if folder is matched to movie name, means that splitting is done
	    """
            if basename in indexed_movies_lst: #skip the indexed movies
                continue

            in_file_path = os.path.join(in_path, fname)
            split_video_into_equal_parts(in_file_path, sLength, out_path)

	"""print("############ frames extraction #################")
	frames_out_path = '../video_files/small_video_clip_frames/'

	#Add all the processed small clips to list, so that we do not need to process them
	processed_movies_list = []
	for m_name in os.listdir(frames_out_path):
	    movie_sub_path = os.path.join(frames_out_path, m_name)
	    for small_clip_names in os.listdir(movie_sub_path):
		processed_movies_list.append(small_clip_names)

	for sub_dir in os.listdir(out_path):
	    sub_dir_path = os.path.join(out_path, sub_dir)
	    for fname in os.listdir(sub_dir_path):
		name, ext = fname.split('.')
		if name in processed_movies_list: #check in case if frames extracted already
		    continue
		in_file_path = os.path.join(sub_dir_path, fname)
		extract_frames_from_video_ffmpeg(in_file_path, frames_out_path)"""

    elif args.split_option == "random": #split video clip at random position with given length
		
	#Clean already detected clips data
	out_path = '../video_files/small_video_clips_rand/randomly_generated'
	if os.path.exists(out_path):
	    shutil.rmtree(out_path)
	if not os.path.exists(out_path):
	    os.makedirs(out_path)

	split_video_random(args.video_file_path, args.start_pos, args.split_length, out_path)

	#create path to store frames
	frames_out_path = '../video_files/small_video_clip_frames_rand/random_clips_frames'
	if os.path.exists(frames_out_path):
	    shutil.rmtree(frames_out_path)
	if not os.path.exists(out_path):
	    os.makedirs(frames_out_path)

	#extreact frames
	for fname in os.listdir(out_path):
	    in_file_path = os.path.join(out_path, fname)
	    extract_frames_from_video_ffmpeg(in_file_path, frames_out_path)

    else:
	sys.exit("option is wrong")

    return frames_out_path

def iframes_extraction():
    filename = "../video_files/original_video_clips/breaking_bad_s01e01.mkv"
    iframe_path = "../video_files/iframes_data"
    if not os.path.exists(iframe_path):
        os.mkdir(iframe_path)
    command = 'ffprobe -v error -show_entries frame=pict_type -of default=noprint_wrappers=1'.split()
    out = subprocess.check_output(command + [filename]).decode()
    f_types = out.replace('pict_type=','').split()
    frame_types = zip(range(len(f_types)), f_types)
    i_frames = [x[0] for x in frame_types if x[1]=='I']
    if i_frames:
        cap = cv2.VideoCapture(filename)
    for frame_no in i_frames:
        #cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        cap.set(1, frame_no)
        ret, frame = cap.read()
        outname = iframe_path+'i_frame_'+str(frame_no)+'.jpg'
        cv2.imwrite(outname, frame)
        cap.release()
    print("I-Frame selection Done!!")

"""
Extract all the frames from a large video clip and store in the output path
@Parameters:
        in_path: path where video file presents
        out_path: path where extracted frames needs to be stored
"""
def extract_all_frames(in_path, out_path):

    #skip the movies for which frames extracted
    frames_extracted_movies = []
    for movie_name in os.listdir(out_path):
        frames_extracted_movies.append(movie_name)


    #parse all the videos and extract frames
    for movie_name in os.listdir(in_path):
        name, ext = movie_name.split(".")
        if name in frames_extracted_movies:
            continue
        movie_in_path = in_path+movie_name
        frames_out_path = out_path+name
        if not os.path.exists(frames_out_path):
            os.makedirs(frames_out_path)

        #f_out_path = out_path + '/' + 'frame-'
        #s_cmd = "ffmpeg -i %s -t 1 -f image2 %s" %(in_path, f_out_path)
        #ss_cmd = s_cmd+'%d.jpg'

        ss_cmd = "ffmpeg -i " + movie_in_path + " " + frames_out_path + "/frame-%06d.jpg"
        subprocess.Popen(ss_cmd, shell = True, stdout=subprocess.PIPE).stdout.read()

"""
Extract a few frames from the given position and store in the given path, this can be used in testing
@Parameters:
    in_path: path where video clip presents
    out_path: path where extracted frames needs to be stored
    start_pos: position from where frames needs to be extracted
    no_of_frames: Number of frames needs to be extracted
"""
def extract_few_frames(in_path, out_path, start_pos, no_of_frames):

    pDir, fname = os.path.split(in_path)
    name, ext = fname.split(".")

    if os.path.exists(out_path):
        shutil.rmtree(out_path)
    comp_out_path = out_path+name
    if not os.path.exists(comp_out_path):
        os.makedirs(comp_out_path)

    s_cmd = " -i '%s'"%(in_path)
    ss_cmd = "ffmpeg -ss " + str(start_pos) + s_cmd + " -vframes " + str(no_of_frames) + " " + comp_out_path + "/frame-%06d.jpg"
    subprocess.Popen(ss_cmd, shell=True, stdout=subprocess.PIPE).stdout.read()

def main():
    parser = argparse.ArgumentParser(description="Video splitting")
    parser.add_argument("--video_file_path", dest="video_file_path", type=str, default="", help="input video file path")
    parser.add_argument("--split_option", dest="split_option", type=str, default="equal", help="option to choose random split or equal")
    parser.add_argument("--start_pos", dest="start_pos", type=int, default=0, help="The starting position")
    parser.add_argument("--split_length", dest="split_length", type=int, default=5, help="length of the smaller clip")
    args = parser.parse_args()

    """
    #extract fps information
    for r, d, fnames in os.walk("../video_files/original_video_clips"):
	for fname in fnames:
	    file_path = os.path.join(r, fname)
	    extract_fps(file_path)"""
	
    video_clip_split(args)

if __name__ == "__main__":
    main()
