import cv2
import numpy as np
import datetime
import os
import time

def check_standar_deviation(data_list, tol):
    data_list = np.array(data_list)
    std = np.std(data_list, axis=0)
    return np.mean(std) > tol

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name


file_name       = 'output/30cm.avi' #namefile of video
threshold_value = -1 # -1 otsu, > 0 threshold biasa 
invers          = True  # True = dibawah nilai threshold diambil, False = diatas nilai threshold diambil
buffer_frame    = 5 # jumlah data yang di pertahankan dari untuk mendapatkan nilai standar deviasi dari cx, cy, w, h
tolerance       = 0.4 # nilai batas standar deviasi, dibawah nilai ini tidak dianggap api
base_dir        = "output"
output_name     = "data1"

cap = cv2.VideoCapture(file_name)
data = []
data_save = []
data_std = []
data_frame_rate = []

if output_name == "":
    output_path = os.path.join(base_dir, datetime.datetime.now().strftime('%Y,%m,%d_%H,%M,%S') )
else:
    output_path = os.path.join(base_dir, output_name )
if not os.path.isdir(base_dir):
    os.mkdir(base_dir)
if not os.path.isdir(output_path):
    os.mkdir(output_path)

# Define the codec and create VideoWriter object
ret, frame = cap.read()
H,W,_ = frame.shape
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out1 = cv2.VideoWriter(os.path.join(output_path,'output-jet.avi'),cv2.VideoWriter_fourcc(*'XVID'), 20.0, (W,H))
out2 = cv2.VideoWriter(os.path.join(output_path,'output-bin.avi'),cv2.VideoWriter_fourcc(*'XVID'), 20.0, (W,H))

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

n = 0

t = time.time()

# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, image = cap.read()
  if ret == True:
    if n != 0:
        data_frame_rate.append(time.time() - t)
    t = time.time()

    n += 1
    frame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    if threshold_value == -1:
        if invers:
            ret3,thresh = cv2.threshold(frame,0,255,cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        else:
            ret3,thresh = cv2.threshold(frame,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    else:
        if invers:
            ret, thresh = cv2.threshold(frame, threshold_value, 255, 1)
        else:
             ret, thresh = cv2.threshold(frame, threshold_value, 255, 0)

    contour = cv2.findContours(thresh, 0,2)[0]
    if len(contour):
        for cnt in contour:
            area = cv2.contourArea(cnt)
            if area > 1:
                x,y,w,h = cv2.boundingRect(cnt)
                if len(data) < buffer_frame:
                    cx = x + w//2
                    cy = y + h//2
                    data.append([cx,cy, w,h])
                else:
                    cx = x + w//2
                    cy = y + h//2
                    data.append([cx,cy, w,h])
                    data.pop(0)
                
                if check_standar_deviation(data, tolerance):
                    cv2.rectangle(image, (x,y), (x+w,y+h), (255,255,255), 1)
                    data_save.append([n, cx, cy, w, h, area])
                    data_std.append([n, data])

    out1.write(image)
    rgb_img = cv2.cvtColor(thresh, cv2.COLOR_GRAY2RGB)
    out2.write(rgb_img)

    cv2.imshow('Frame',image)
    cv2.imshow('Frame - Binary',thresh)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

  # Break the loop
  else: 
    break

out1.release()
out2.release()
# When everything done, release the video capture object
cap.release()

with open(os.path.join(output_path,'data-obj.txt'), "w") as f:
    for row in data_save:
        for col in row:
            f.write(str(col) + "\t")
        f.write("\n")

with open(os.path.join(output_path,'data-std.txt'), "w") as f:
    for row in data_std:
        for col in row:
            f.write(str(col) + "\t")
        f.write("\n")

mean = 1/ np.mean(np.array(data_frame_rate))
with open(os.path.join(output_path,'framerate.txt'), "w") as f:
    f.write(str(mean))
# Closes all the frames
cv2.destroyAllWindows()
