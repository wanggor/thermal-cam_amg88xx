import busio
import adafruit_amg88xx
import time
import board
import cv2
import numpy as np


size = (64,64)
file_name = 'output.avi'
fps = 20.0
# y = ax + b, for visualization
a = 12.5
b = 287

i2c_bus = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c_bus)

# saving video object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(file_name, fourcc, fps, size)
time.sleep(1)

while True:
    array = np.array(amg.pixels)
    array = ((array) * a - b)
    array = array.astype(np.uint8)
    array = cv2.resize(array, size) 
    array = cv2.applyColorMap(array, cv2.COLORMAP_JET)
    
    # write the flipped frame
    out.write(array)
    cv2.imshow("Frame", array)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
out.release()
cv2.destroyAllWindows()
