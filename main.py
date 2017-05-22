from __future__ import division
from Tkinter import *
import tkMessageBox
import tkFileDialog
import tkMessageBox
from PIL import Image, ImageTk
from random import randint
import pymysql.cursors
import re
import os
import glob
import time
import shutil
import random
import math as m
import cmath as cm
import numpy as np


COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
SIZE = 480, 640

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]


class LabelTool():
    def __init__(self, master):
        self.parent = master
        self.parent.title("Label Tool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList = []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.selectedClass = 0

        # initialize mouse state
        self.STATE = {}
        self.STATE['click'] = 0
        self.STATE['x'], self.STATE['y'] = 0, 0
        self.STATE['gR'] = []
        self.STATE['gR_deg'] = 0

        # reference to bbox
        self.bboxIdList = []
        self.bboxId = None
        self.bboxList = []
        self.hl = None
        self.vl = None

        self.connectionHost = 'localhost';
        self.connectionUser = 'root';
        self.connectionPassword = 'root';
        self.connectionDB = 'image_annotator';
        self.connection = False;


        # ----------------- GUI stuff ---------------------
        # dir entry & load
        self.ldBtn = Button(self.frame, text="Load Dir", command=self.selectDir)
        self.ldBtn.grid(row = 0, column = 2, sticky = W+E)

        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove) 
        self.parent.bind("<Escape>", self.cancelBBox)
        self.parent.bind("<Delete>", self.delBBox)
        self.parent.bind("<Prior>", self.prevImage)
        self.parent.bind("<Next>", self.nextImage)
        self.parent.bind("<space>", self.nextImage)
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 28, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)
        self.btnClear = Button(self.frame, text = 'ClearAll', command = self.clearBBox)
        self.btnClear.grid(row = 3, column = 2, sticky = W+E+N)

        self.imageClass = Entry(self.frame)
        self.imageClass.grid(row = 4, column = 2, sticky = W+E+N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)

        # example pannel for illustration
        self.egPanel = Frame(self.frame, border = 10)
        self.egPanel.grid(row = 1, column = 0, rowspan = 5, sticky = N)
        self.tmpLabel2 = Label(self.egPanel, text = "")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.egLabels = []
        for i in range(3):
            self.egLabels.append(Label(self.egPanel))
            self.egLabels[-1].pack(side = TOP)

        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)

        self.frame.columnconfigure(1, weight = 1)
        self.frame.rowconfigure(4, weight = 1)

        self.selectDir()

    def setClassDropdown(self, value):
        self.selectedClass = CLASSES.index(value)

    def selectDir(self):
        self.imageDir = tkFileDialog.askdirectory()
        self.loadDir()

    def loadDir(self):
        self.imageList = glob.glob(os.path.join(self.imageDir, '*.jpg'))
        self.imageList.sort(key=natural_keys);
        
        if len(self.imageList) == 0:
            print 'No .jpg images found in the specified dir!'
            return

        self.cur = 1
        self.total = len(self.imageList)
        print '%d images loaded from %s' %(self.total, self.imageDir)

        self.loadImage()

    def loadImage(self):
        self.clearBBox()
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

    def saveImage(self):
        if len(self.imageClass.get()) == 0:
            tkMessageBox.showinfo("Error", "You must specifty the image class")
            return False

        curImg = self.imageList[self.cur - 1]
        filename, fileExtension = os.path.splitext(curImg)

        if not os.path.isdir("/Users/anthonybudd/.bbox"):
            os.makedirs("/Users/anthonybudd/.bbox")

        if self.connection == False:
            self.connection = pymysql.connect(
                host        = self.connectionHost,
                user        = self.connectionUser,
                password    = self.connectionPassword,
                db          = self.connectionDB,
                cursorclass = pymysql.cursors.DictCursor)

        with self.connection.cursor() as cursor:
            for bbox in self.bboxList:
                destination = ('/Users/anthonybudd/.bbox/'+ str(int(time.time())) +'-'+ str(randint(0,1000)) + fileExtension)
                shutil.copyfile(curImg, destination)

                img = Image.open(destination)
                imgWidth = int(img.size[0])
                imgHeight = int(img.size[1])

                bbox_x1_ratio = ((bbox[2] - bbox[0]) /2) + bbox[0]
                bbox_y1_ratio = ((bbox[3] - bbox[1]) /2) + bbox[1]
                bbox_width = (bbox[2] - bbox[0]) 
                bbox_height = (bbox[3] - bbox[1])

                bbox_x1_center_ratio = self.asRatioOf(bbox_x1_ratio, imgWidth)
                bbox_y1_center_ratio = self.asRatioOf(bbox_y1_ratio, imgHeight)
                bbox_width_ratio = self.asRatioOf(bbox_width, imgWidth)
                bbox_height_ratio = self.asRatioOf(bbox_height, imgHeight)

                sql = "INSERT INTO `items` (`class`, `image_path`, `image_height`, `image_width`, `bbox_x1`, `bbox_y1`, `bbox_width`, `bbox_height`, `bbox_x1_center_ratio`, `bbox_y1_center_ratio`, `bbox_width_ratio`, `bbox_height_ratio`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                cursor.execute(sql, (self.imageClass.get(), destination, imgHeight, imgWidth, bbox[0], bbox[1], bbox_width, bbox_height, bbox_x1_center_ratio, bbox_y1_center_ratio, bbox_width_ratio, bbox_height_ratio)) 
                self.connection.commit()
        return True
            
    def mouseClick(self, event):
        if self.STATE['click'] == 0:    
            self.STATE['x'], self.STATE['y'] = event.x, event.y
            self.STATE['click'] = 1
        else:
            x1, x2 = min(self.STATE['x'], event.x), max(self.STATE['x'], event.x)
            y1, y2 = min(self.STATE['y'], event.y), max(self.STATE['y'], event.y)
            self.bboxList.append((x1, y1, x2, y2))
            self.bboxIdList.append(self.bboxId)
            self.bboxId = None
            self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(x1, y1, x2, y2))
            self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])
            self.STATE['click'] = 0

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg: #mouse tracking
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        
        if self.STATE['click'] == 1:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)

            self.bboxId = self.mainPanel.create_rectangle(self.STATE['x'], self.STATE['y'], \
                                                            event.x, event.y, \
                                                            width = 2, \
                                                            outline = COLORS[len(self.bboxList) % len(COLORS)])  

    def cancelBBox(self, event):
        if 1 == self.STATE['click']:
            if self.bboxId:
                self.mainPanel.delete(self.bboxId)
                self.bboxId = None
                self.STATE['click'] = -1

    def delBBox(self):
        sel = self.listbox.curselection()
        if len(sel) != 1 :
            return
        idx = int(sel[0])
        self.mainPanel.delete(self.bboxIdList[idx])
        self.bboxIdList.pop(idx)
        self.bboxList.pop(idx)
        self.listbox.delete(idx)
        self.STATE['click'] = 0

    def clearBBox(self):
        for idx in range(len(self.bboxIdList)):
            self.mainPanel.delete(self.bboxIdList[idx])
        self.listbox.delete(0, len(self.bboxList))
        self.bboxIdList = []
        self.bboxList = []
        self.STATE['click'] = 0

    def prevImage(self, event = None):
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        if len(self.bboxList) > 0:
            if self.saveImage() == True:
                if self.cur < self.total:
                    self.cur += 1
                    self.loadImage()

    def asRatioOf(self, a, b):
        if(a == 0) or (b == 0):
            return 0
        return ((a/1)/b)
    
    def gRCorner(self,xc,yc,x0,y0): 
        w=abs(x0-xc)*2
        h=abs(y0-yc)*2
        x2=2*xc-x0
        y2=2*yc-y0
        x0,x2=max(x0,x2),min(x0,x2)
        y0,y2=max(y0,y2),min(y0,y2)
        corner_x=x0,x0,x2,x2
        corner_y=y0,y2,y2,y0
        return zip(corner_x, corner_y), w, h

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
