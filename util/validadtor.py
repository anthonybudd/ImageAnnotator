from __future__ import division
from Tkinter import *
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

SKIP = 1

# Classes
CLASSES = ['trafficlight', 'ordersign', 'directionsign', 'other']
# colors for the bboxes
COLORS = ['red', 'blue', 'yellow', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 480, 640

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text) ]

class LabelTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.bind("<space>", self.nextImage)
        self.parent.title("LabelTool")
        self.frame = Frame(self.parent)
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
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


        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='root',
            db='routeshoot',
            cursorclass=pymysql.cursors.DictCursor)

        # ----------------- GUI stuff ---------------------
        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.grid(row = 1, column = 1, rowspan = 4, sticky = W+N)

        # showing bbox info & delete bbox
        self.lb1 = Label(self.frame, text = 'Bounding boxes:')
        self.lb1.grid(row = 1, column = 2,  sticky = W+N)
        self.listbox = Listbox(self.frame, width = 28, height = 12)
        self.listbox.grid(row = 2, column = 2, sticky = N)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 5, column = 1, columnspan = 2, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)

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
        self.load()

    def load(self, dbg = False):
        SQL = "SELECT * FROM `items` WHERE id > %s ORDER BY id DESC LIMIT 500 "
        imageList = []
        with self.connection.cursor() as cursor:
            cursor.execute(SQL, (SKIP))
            for row in cursor.fetchall():
                imageList.append(row)

        self.imageList = imageList

        if len(self.imageList) == 0:
            print 'No .jpg images found in the specified dir!'
            return

        self.cur = 1
        self.total = len(self.imageList)
        self.loadImage()


    def loadImage(self):
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath['image_path'])
        imgWidth = int(self.img.size[0])
        imgHeight = int(self.img.size[1])

        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.delete("all")
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image=self.tkimg, anchor=NW)
        self.lb1.config(text = "ID: " + str(imagepath['id']) +' - '+ str(imagepath['class']))
        self.mainPanel.create_rectangle(imagepath['bbox_x1'], imagepath['bbox_y1'], (int(imagepath['bbox_x1']) + int(imagepath['bbox_width'])), (int(imagepath['bbox_y1']) + int(imagepath['bbox_height'])), width=2, outline='#F00')  

    def prevImage(self, event = None):
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        if (len(self.bboxList) > 0):
            self.saveImage()

        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

if __name__ == '__main__':
    root = Tk()
    tool = LabelTool(root)
    root.mainloop()
    tool.load()
