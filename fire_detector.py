import cv2
import numpy as np

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

cap = cv2.VideoCapture(file_name)
data = []

# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")

# Read until video is completed
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
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
                    cv2.rectangle(frame, (x,y), (x+w,y+h), (255,255,255), 1)

    cv2.imshow('Frame',frame)
    cv2.imshow('Frame - Binary',thresh)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break

  # Break the loop
  else: 
    break

# When everything done, release the video capture object
cap.release()

# Closes all the frames
cv2.destroyAllWindows()
