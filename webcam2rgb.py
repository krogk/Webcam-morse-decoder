import cv2
import numpy as np

import threading



class Webcam2rgb():

    def start(self, callback, cameraNumber=0, width = None, height = None, fps = None, directShow = False):
        self.callback = callback
        try:
            self.cam = cv2.VideoCapture(cameraNumber + cv2.CAP_DSHOW if directShow else cv2.CAP_ANY) 
            if not self.cam.isOpened():
                print('opening camera')
                self.cam.open(0)
                
            if width:
                self.cam.set(cv2.CAP_PROP_FRAME_WIDTH,width)
            if height:
                self.cam.set(cv2.CAP_PROP_FRAME_HEIGHT,height)
            if fps:
                self.cam.set(cv2.CAP_PROP_FPS, fps)
            self.running = True
            self.thread = threading.Thread(target = self.calc_BRG)
            self.thread.start()
            self.ret_val = True
        except:
            self.running = False
            self.ret_val = False

    def stop(self):
        self.running = False
        self.thread.join()

    def calc_BRG(self):
        while self.running:
            try:
                self.ret_val = False
                self.ret_val, img = self.cam.read()
                h, w, c = img.shape
                brg = img[int(h/2),int(w/2)]
                self.callback(self.ret_val,brg)
            except:
                self.running = False

    def cameraFs(self):
        return self.cam.get(cv2.CAP_PROP_FPS)
