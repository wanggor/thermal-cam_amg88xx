from PyQt5.QtWidgets import QApplication,QMainWindow,QStyleFactory
from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import QTimer,Qt
from PyQt5.QtGui import QImage, QPixmap
import cv2
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
from skimage.transform import resize
import sys
import os
import random
import busio
import adafruit_amg88xx
import time
import board

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        self.ui = uic.loadUi('gui.ui',self)
        self.isstart = False
        self.output_path = ""
        self.array = None
        self.data = []
        self.setup()

    def setup(self):
        self.ui.pushButton_start.clicked.connect(self.start)
        self.ui.pushButton_stop.clicked.connect(self.stop)
        
        self.i2c_bus = busio.I2C(board.SCL, board.SDA)
        self.amg = adafruit_amg88xx.AMG88XX(self.i2c_bus)
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        

    def start(self):
        if not self.isstart:
            self.size = (128,128)
            base_dir = "output"
            self.a = float(self.ui.lineEdit_a.text())
            self.b = float(self.ui.lineEdit_b.text())
            self.threshold = float(self.ui.lineEdit_threshold.text())
            self.output_name = self.ui.lineEdit_output.text()

            self.output_path = os.path.join(base_dir, self.output_name)
            if not os.path.isdir(base_dir):
                os.mkdir(base_dir)
            if not os.path.isdir(self.output_path):
                os.mkdir(self.output_path)
                
            # saving video object
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(os.path.join(self.output_path, "output.avi"), fourcc, 20.0, self.size)

            self.timer.start()
            self.isstart = True

    def stop(self):
        if self.isstart:
            self.timer.stop()
            self.out.release()
            self.isstart = False
            self.ui.label_frame.clear()
            if self.output_path != "":
                with open(os.path.join(self.output_path,'output.txt'), "w") as f:
                    for row in self.data:
                        for col in row:
                            f.write(str(col) + "\t")
                        f.write("\n")
            
            if self.array is not None:
                fig, (ax) = plt.subplots(nrows=1)
                levels = MaxNLocator(nbins=15).tick_values(self.array.min(), self.array.max())
                cmap = plt.get_cmap('jet')
                norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
                self.array = resize(self.array, self.size)
                self.array = np.flip(self.array, 0)
                cf = ax.pcolormesh( self.array, norm=norm,
                                cmap=cmap)
                fig.colorbar(cf, ax=ax)
                ax.set_title('contourf with levels')
                ax.grid: True
                fig.tight_layout()
                fig.savefig(os.path.join(self.output_path,'image.png'))
                plt.close(fig)
                self.array = None
            self.output_path = ""
            self.data = []
            self.array = None

    def update(self):
        data = []
        
        array_raw = np.array(self.amg.pixels)
        min_val = np.min(array_raw)
        max_val = np.max(array_raw)
        self.array = array_raw
        array = ((array_raw.copy()) * self.a - self.b)
        th    = int(self.threshold * self.a - self.b)
        
        array = array.astype(np.uint8)
        array = cv2.resize(array, self.size)
        ret, thresh = cv2.threshold(array, th, 255, 0)
        contour = cv2.findContours(thresh, 1,2)[1]
        array = cv2.applyColorMap(array, cv2.COLORMAP_JET)
        if len(contour):
            for cnt in contour:
                area = cv2.contourArea(cnt)
                if area > 1:
                    x,y,w,h = cv2.boundingRect(cnt)
                    cv2.rectangle(array, (x,y), (x+w,y+h), (255,255,255), 1)
                    data.append([x + w//2, y + h//2, w, h, area])

        self.out.write(array)
        h, w, ch = array.shape
        bytesPerLine = ch * w
        convertToQtFormat = QImage(array.data, w, h, bytesPerLine, QImage.Format_RGB888)
        p = convertToQtFormat.scaled(self.ui.label_frame.width(), self.ui.label_frame.height(), Qt.KeepAspectRatio)
        self.ui.label_frame.setPixmap(QPixmap.fromImage(p))
        self.update_data_table(data)
        self.data = data

    def update_data_table(self, data):
        n_row = len(data)
        self.ui.tableWidget.setRowCount(n_row)
        for n,row in enumerate(data):
            for j,key in enumerate(data[n]):
                self.ui.tableWidget.setItem(n,j, QtWidgets.QTableWidgetItem(str(key)))

    def closeEvent(self, event):
        self.out.release()
                

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Dialog = Main()
    Dialog.setWindowTitle("")
    Dialog.showMaximized()
    sys.exit(app.exec_())