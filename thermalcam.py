import busio
import adafruit_amg88xx
import time
import board
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from skimage.transform import resize

threshold = 26.0

size = (128,128)
file_name = '60cm.avi'
file_name_txt = "60cm.txt"
fps = 20.0
# y = ax + b, for visualization
a = 1.6
b = 1

i2c_bus = busio.I2C(board.SCL, board.SDA)
amg = adafruit_amg88xx.AMG88XX(i2c_bus)

# saving video object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(file_name, fourcc, fps, size)
time.sleep(1)

while True:
    array_raw = np.array(amg.pixels)
    min_val = np.min(array_raw)
    max_val = np.max(array_raw)
    
    print(f"min : {np.min(array_raw)}")
    print(f"max : {np.max(array_raw)}")
    array = ((array_raw.copy()) * a - b)
    th    = int(threshold * a - b)
    array = array.astype(np.uint8)
    array = cv2.resize(array, size)
    ret, thresh = cv2.threshold(array, th, 255, 0)
    contour = cv2.findContours(thresh, 1,2)[1]
    array = cv2.applyColorMap(array, cv2.COLORMAP_JET)
    if len(contour):
        cnt = max(contour, key=cv2.contourArea)
        area = cv2.contourArea(cnt)
        if area > 1:
            with open(file_name_txt, "w+") as f:
                f.write(f"min_temp\tmax_temp\tfps\tpixel\tLuas\n")
                f.write(f"{min_val}\t\t{max_val}\t\t{fps}\t{size[0]*size[1]}\t{area}\n")
            print(f"max-area : {area}")
            print("========")
            x,y,w,h = cv2.boundingRect(cnt)
            cv2.rectangle(array, (x,y), (x+w,y+h), (255,255,255), 1)
            
    
    
    # write the flipped frame
    out.write(array)
    cv2.imshow("Frame", array)
    cv2.imshow("Thresh", thresh)
    key = cv2.waitKey(1) & 0xFF
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
out.release()
cv2.destroyAllWindows()


fig, (ax) = plt.subplots(nrows=1)

levels = MaxNLocator(nbins=15).tick_values(array_raw.min(), array_raw.max())
cmap = plt.get_cmap('jet')
norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)


array_raw = resize(array_raw, size)
array_raw = np.flip(array_raw, 0)
cf = ax.pcolormesh( array_raw, norm=norm,
                  cmap=cmap)
fig.colorbar(cf, ax=ax)
ax.set_title('contourf with levels')
ax.grid: True
fig.tight_layout()
plt.show()

