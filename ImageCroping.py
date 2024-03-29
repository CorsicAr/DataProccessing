## import libs

import glob

import cv2
import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.image as mpimg
import matplotlib.lines as lines
import matplotlib.patches as mpatches
import math
import random
import os
from PIL import Image
import  numpy as np

from rdflib import URIRef, BNode, Literal, Namespace
from rdflib.namespace import FOAF, DCTERMS, XSD, RDF, SDO
from rdflib import Graph

import QRRead

# Window to crop imgs, create class with wx panel
class ImageCropPanel(wx.Panel):

    def __init__(self, parent):
        ## init it to parent window
        super().__init__(parent)
        ## init variables (I can't rember what they all do, but feel free to comment)
        self.data = None
        self.scan_data = []
        self.folder_indx = 0
        self.image_indx = 0
        self.img_cntrl = None
        self.buf_size = 0
        self.patches = None
        self.img = None
        self.toolbar = None
        self.canvas = None
        self.figure = None
        self.dc = None
        self.axes = None
        self.num_row = 4
        self.num_colum = 10
        self.zoomed = False

        # click point lists
        self.positionsX = []
        self.positionsY = []

        # matplotlib panel
        self.frame_panel = wx.Panel(self, name="DataEntry")
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.figure.subplots_adjust(0, 0, 1, 1)
        self.axes.set_axis_off()
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_click)


        # GUI with wx
        ## Folder button
        last_btn = wx.Button(self, label='Last')
        last_btn.Bind(wx.EVT_BUTTON, self.on_last_btn)
        nxt_btn = wx.Button(self, label='Next')
        nxt_btn.Bind(wx.EVT_BUTTON, self.on_nxt_btn)
        self.file_txt = wx.TextCtrl(self, size=(200, -1))
        folderInfoTtl = wx.StaticText(self,label = "Folder Info")
        self.folder_info = wx.TextCtrl(self, size=(300, -1))

        ## input datat
        nameTitle = wx.StaticText(self, label="Name")
        self.name = wx.TextCtrl(self, size=(300, -1))
        homeTitle = wx.StaticText(self, label="Home")
        self.home = wx.TextCtrl(self, size=(200, -1))
        intTitle = wx.StaticText(self, label="Intention")
        self.intention = wx.TextCtrl(self, size=(500, -1))
        zoomDataButton = wx.Button(self, label="Zoom to Data")
        zoomDataButton.Bind(wx.EVT_BUTTON, self.zoom_to_data)
        saveDataButton = wx.Button(self, label="Save Data")
        saveDataButton.Bind(wx.EVT_BUTTON, self.save_data)

        ## Img browse button
        last_img_btn = wx.Button(self, label='Last')
        last_img_btn.Bind(wx.EVT_BUTTON, self.on_last_img_btn)
        nxt_img_btn = wx.Button(self, label='Next')
        nxt_img_btn.Bind(wx.EVT_BUTTON, self.on_next_img_btn)
        self.photo_txt = wx.TextCtrl(self, size=(200, -1))
        imgInfoTtl = wx.StaticText(self, label="Image Info")
        self.img_info = wx.TextCtrl(self, size=(300, -1))

        # Rows slider
        self.sliderR = wx.Slider(self, value=self.num_row, minValue=0, maxValue=20,
                            style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL, name="Rows")
        self.sliderR.Bind(wx.EVT_SLIDER, self.on_slideR)
        sliderRTtl = wx.StaticText(self, label="Rows")

        # Columns slider
        self.sliderC = wx.Slider(self, value=self.num_colum, minValue=0, maxValue=20,
                            style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL, name="Rows")
        self.sliderC.Bind(wx.EVT_SLIDER, self.on_slideC)
        sliderCTtl = wx.StaticText(self, label="Collumns")

        # boarder slider
        self.sliderB = wx.Slider(self, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL,
                            name="Rows")
        self.sliderB.Bind(wx.EVT_SLIDER, self.on_slideB)
        sliderBTtl = wx.StaticText(self, label="Buffer Space (px)")

        # Test Crops btn
        croptst_btn = wx.Button(self, label='TestCrops')
        croptst_btn.Bind(wx.EVT_BUTTON, self.preview_crops)

        ## Letter selection
        self.af_btn = wx.CheckBox(self, label='A - F')
        self.af_btn.Bind(wx.EVT_CHECKBOX, self.on_letters)
        self.gp_btn = wx.CheckBox(self, label='G - P')
        self.gp_btn.Bind(wx.EVT_CHECKBOX, self.on_letters)
        self.qz_btn = wx.CheckBox(self, label='Q - Z')
        self.qz_btn.Bind(wx.EVT_CHECKBOX, self.on_letters)
        self.symbol_btn = wx.CheckBox(self, label='Symbol')
        self.symbol_btn.Bind(wx.EVT_CHECKBOX, self.on_letters)
        self.symbol_input = wx.TextCtrl(self, size=(500, -1))
        self.symbol_input.Disable()

        # Save Set btn
        set_imgs_btn = wx.Button(self, label='Set Image Crop')
        set_imgs_btn.Bind(wx.EVT_BUTTON, self.set_image_data)

        # Save Images btn
        save_imgs_btn = wx.Button(self, label='Save Image Crop')
        save_imgs_btn.Bind(wx.EVT_BUTTON, self.on_browse_save)

        # Scan QR btn
        scan_qr_btn = wx.Button(self, label='Automatic QR Scan')
        scan_qr_btn.Bind(wx.EVT_BUTTON, self.on_qr_scan)

        # Layout
        image_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hsizerBrowse = wx.BoxSizer(wx.HORIZONTAL)
        hsizerImg = wx.BoxSizer(wx.HORIZONTAL)
        hsizerRC = wx.BoxSizer(wx.HORIZONTAL)

        # stacking layout, basically orderning the components into a gui layout by parenting them.
        image_sizer.Add(self.canvas, 0, wx.ALL, 5)


        hsizerBrowse.Add(last_btn, 0, wx.ALL, 5)
        hsizerBrowse.Add(self.file_txt, 0, wx.ALL, 5)
        hsizerBrowse.Add(nxt_btn, 0, wx.ALL, 5)
        hsizerBrowse.Add(folderInfoTtl)
        hsizerBrowse.Add(self.folder_info)
        main_sizer.Add(hsizerBrowse, 0, wx.ALL, 5)


        hsizername = wx.BoxSizer(wx.HORIZONTAL)
        hsizerhome = wx.BoxSizer(wx.HORIZONTAL)
        hsizerint = wx.BoxSizer(wx.HORIZONTAL)

        hsizername.Add(nameTitle, 0, wx.ALL, 5)
        hsizername.Add(self.name, 0, wx.ALL, 5)
        hsizerhome.Add(homeTitle, 0, wx.ALL, 5)
        hsizerhome.Add(self.home, 0, wx.ALL, 5)
        hsizerint.Add(intTitle, 0, wx.ALL, 5)
        hsizerint.Add(self.intention, 0, wx.ALL, 5)

        main_sizer.Add(hsizername, 0, wx.ALL, 5)
        main_sizer.Add(hsizerhome, 0, wx.ALL, 5)
        main_sizer.Add(hsizerint, 0, wx.ALL, 5)
        main_sizer.Add(zoomDataButton, 0, wx.ALL, 5)
        main_sizer.Add(saveDataButton, 0, wx.ALL, 5)


        hsizerImg.Add(last_img_btn, 0, wx.ALL, 5)
        hsizerImg.Add(self.photo_txt, 0, wx.ALL, 5)
        hsizerImg.Add(nxt_img_btn, 0, wx.ALL, 5)
        hsizerImg.Add(imgInfoTtl)
        hsizerImg.Add(self.img_info)
        main_sizer.Add(hsizerImg, 0, wx.ALL, 5)

        hsizerRC.Add(self.sliderR, 0, wx.ALL, 5)
        hsizerRC.Add(sliderRTtl, 0, wx.ALL, 5)
        hsizerRC.Add(self.sliderC, 0, wx.ALL, 5)
        hsizerRC.Add(sliderCTtl, 0, wx.ALL, 5)
        hsizerRC.Add(self.sliderB, 0, wx.ALL, 5)
        hsizerRC.Add(sliderBTtl, 0, wx.ALL, 5)
        hsizerRC.Add(croptst_btn)

        hsizerletters = wx.BoxSizer(wx.HORIZONTAL)
        hsizerletters.Add(self.af_btn)
        hsizerletters.Add(self.gp_btn)
        hsizerletters.Add(self.qz_btn)
        hsizerletters.Add(self.symbol_btn)

        main_sizer.Add(hsizerRC)
        main_sizer.Add(hsizerletters)
        main_sizer.Add(self.symbol_input)
        main_sizer.Add(set_imgs_btn)
        main_sizer.Add(save_imgs_btn)
        main_sizer.Add(scan_qr_btn)

        image_sizer.Add(main_sizer, 0, wx.ALL, 5)

        self.SetSizer(image_sizer)
        image_sizer.Fit(parent)

        self.Layout()


    # Function for letter selection toggles
    def on_letters(self, event):

        cb = event.GetEventObject()
        self.letters = cb.GetLabel()

        if cb.GetLabel() == 'A - F':
            self.gp_btn.SetValue(0)
            self.qz_btn.SetValue(0)
            self.symbol_btn.SetValue(0)
            self.symbol_input.Disable()

        elif cb.GetLabel() == 'G - P':
            self.af_btn.SetValue(0)
            self.qz_btn.SetValue(0)
            self.symbol_btn.SetValue(0)
            self.symbol_input.Disable()

        elif cb.GetLabel() == 'Q - Z':
            self.af_btn.SetValue(0)
            self.gp_btn.SetValue(0)
            self.symbol_btn.SetValue(0)
            self.symbol_input.Disable()

        elif cb.GetLabel() == 'Symbol':
            self.af_btn.SetValue(0)
            self.gp_btn.SetValue(0)
            self.qz_btn.SetValue(0)
            self.symbol_input.Enable()


        self.Refresh()

    # Function to set root of images and load them
    def set_root(self, paths):
        self.root_paths = paths
        self.root_indx = 0
        self.file_txt.SetValue(paths[self.root_indx])

        self.scan_data = []

        for path in paths:
            scan = ScanInfo(path)
            if len(scan.images) == 0:
                continue
            self.scan_data.append(scan)
        self.set_info()
        self.load_image()

    ## function to zoom into where the hand written datais
    def zoom_to_data(self, event):

        if self.zoomed:
            self.zoomed = False
            try:
                self.img_cntrl.remove()
            finally:
                self.img_cntrl = self.axes.imshow(self.img)
                self.canvas.draw()
        else:
            self.zoomed = True
            self.img_crop = self.img[0:int(self.img.shape[0] * 0.3), ::]
            try:
                self.img_cntrl.remove()
            finally:
                self.img_cntrl = self.axes.imshow(self.img_crop)
                self.canvas.draw()

    ## saves the data? still working it out
    def save_data(self, event):
        self.scan_data[self.folder_indx].setData(self.name.GetValue(), self.home.GetValue(), self.intention.GetValue())
        self.set_info()

    ## on row slider
    def on_slideR(self, event):
        obj = event.GetEventObject()
        self.num_row = obj.GetValue()

    ## on column slider
    def on_slideC(self, event):
        obj = event.GetEventObject()
        self.num_colum = obj.GetValue()

    ## on column slider
    def on_slideB(self, event):
        obj = event.GetEventObject()
        self.buf_size = obj.GetValue()

    ## changes img to last
    def on_last_img_btn(self, event):
        self.image_indx -= 1
        if self.image_indx < 0:
            self.image_indx = len(self.scan_data[self.folder_indx].images) - 1
        self.load_image()

    ## changes img to next
    def on_next_img_btn(self, event):
        self.image_indx += 1
        if self.image_indx > len(self.scan_data[self.folder_indx].images) - 1:
            self.image_indx = 0
        self.load_image()

    ## changes page indx to last
    def on_last_btn(self, event):
        self.folder_indx -= 1
        if self.folder_indx < 0:
            self.folder_indx = len(self.scan_data) - 1
        self.set_info()
        self.file_txt.SetValue(self.scan_data[self.folder_indx].root_path)
        self.load_image()
    ## changes page indx to next
    def on_nxt_btn(self, event):
        self.folder_indx += 1

        if self.folder_indx > len(self.scan_data) - 1:
            self.folder_indx = 0
        self.set_info()
        self.file_txt.SetValue(self.scan_data[self.folder_indx].root_path)
        self.load_image()

    ## sets the info of the folder?
    def set_info(self):
        text = ""
        if self.scan_data[self.folder_indx].full == True:
            text+= "Info Set + "
        else:
            text+= "Info Not Set + "

        numImgs= len(self.scan_data[self.folder_indx].images)
        numSet = 0
        for imgs in self.scan_data[self.folder_indx].images:
            if imgs.full == True:
                numSet+=1

        text += str(numSet) + " / " + str(numImgs) + " Images Set"

        self.folder_info.SetValue(text)


    # function to click on matplotlib
    def on_click(self, event):
        numPos = len(self.positionsX)

        if numPos == 4:

            minDist = 1000000000
            indx = -1
            for i, (x, y) in enumerate(zip(self.positionsX, self.positionsY)):

                thisDist = math.dist((x, y), (event.xdata, event.ydata))

                if thisDist < minDist:
                    minDist = thisDist
                    indx = i

            self.positionsX[indx] = event.xdata
            self.positionsY[indx] = event.ydata


        else:
            self.positionsX.append(event.xdata)
            self.positionsY.append(event.ydata)

            numPos = len(self.positionsX)

        if numPos == 4:
            try:
                self.lines.remove()
            except:
                self.patches.remove()

            self.order_indxs()

            coords = []
            for (x, y) in zip(self.positionsX, self.positionsY):
                coords.append((x, y))
            self.patches = self.axes.add_patch(mpatches.Polygon(coords, alpha=0.5))
            self.canvas.draw()
        elif numPos >= 2:
            if numPos > 2:
                self.lines.remove()

            line = lines.Line2D(self.positionsX, self.positionsY)

            self.lines = self.axes.add_line(line)
            self.canvas.draw()

    # on browse load image
    def load_image(self):

        if self.scan_data[self.folder_indx].images[self.image_indx].full == True:
            self.img_info.SetValue("Set")
        else:
            self.img_info.SetValue("Un-Set")

        self.photo_txt.SetValue(self.scan_data[self.folder_indx].images[self.image_indx].path)
        filepath = self.photo_txt.GetValue()
        self.img = cv2.imread(filepath)
        self.img_cntrl = self.axes.imshow(self.img)
        self.canvas.draw()
        self.Refresh()

    # when cropping this works out which corners which
    def order_indxs(self):

        # order the points
        self.indx_tl = -1
        self.indx_tr = -1
        self.indx_bl = -1
        self.indx_br = -1

        tl_dist = 1000000000000
        tr_dist = 1000000000000
        bl_dist = 1000000000000
        br_dist = 1000000000000

        for i, (x, y) in enumerate(zip(self.positionsX, self.positionsY)):

            if math.dist((0, 0), (x, y)) < tl_dist:
                tl_dist = math.dist((0, 0), (x, y))
                self.indx_tl = i
            if math.dist((self.img.shape[0], 0), (x, y)) < tr_dist:
                tr_dist = math.dist((self.img.shape[0], 0), (x, y))
                self.indx_tr = i
            if math.dist((0, self.img.shape[1]), (x, y)) < bl_dist:
                bl_dist = math.dist((0, self.img.shape[1]), (x, y))
                self.indx_bl = i
            if math.dist((self.img.shape[0], self.img.shape[1]), (x, y)) < br_dist:
                br_dist = math.dist((self.img.shape[0], self.img.shape[1]), (x, y))
                self.indx_br = i

    ## shows a random preview of a cropped index
    def preview_crops(self, event):

        x = random.randint(0, self.num_row - 1)
        y = random.randint(0, self.num_colum - 1)

        self.set_crop_size()


        self.crop_image(x, y)
        # self.figure.clear(True)

        try:
            self.img_cntrl.remove()
        finally:
            self.img_cntrl = self.axes.imshow(self.img_crop)
            self.canvas.draw()

    ## gets the size between the points
    def set_crop_size(self):

        # self.set_crop_size()
        points = np.hstack((self.positionsX, self.positionsY))

        self.sqaure_img = QRRead.four_point_transform(self.img, points)
        self.height, self.width, _ = self.sqaure_img.shape

        self.width /= self.num_row
        self.height /= self.num_colum

    ## crops the scan to x,y of width and height
    def crop_image(self, x, y):


        self.img_crop = self.sqaure_img[int(self.height * y) + self.buf_size:int(
                        self.height * y + self.height) - self.buf_size,
                        int( self.width * x) + self.buf_size:int(
                        self.width * x + self.width) - self.buf_size]
    ## called on save button after browsed folder
    def on_qr_scan(self, event):

        self.data = QRRead.read_qr_code(self.img)

        # set positions
        self.positionsX = self.data.points_x
        self.positionsY = self.data.points_y
        # set rows and columns
        self.sliderR.SetValue(self.data.num_indxs)
        self.sliderC.SetValue(self.data.num_symbols)
        self.num_colum = self.data.num_indxs
        self.num_row = self.data.num_symbols
        # set using symbols
        self.letters = 'Symbol'
        self.af_btn.SetValue(0)
        self.gp_btn.SetValue(0)
        self.qz_btn.SetValue(0)
        self.symbol_btn.SetValue(1)
        self.symbol_input.Enable()
        self.symbol_input.SetValue(self.data.indxs_str)

        try:
            self.lines.remove()
        except:
            print("no lines")
        try:
            self.patches.remove()
        except:
            print("no polys")

        coords = np.hstack((self.positionsX, self.positionsY))

        self.patches = self.axes.add_patch(mpatches.Polygon(coords, alpha=0.5))
        self.canvas.draw()

    def on_browse_save(self, event):
        wildcard = "folders (*)|*"
        with wx.DirDialog(None, "Choose a save folder",
                          style=wx.ID_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.save_images(dialog.GetPath())
    ## prepares the crop images variables
    def set_image_data(self, event):

        #tl = [self.positionsX[self.indx_tl], self.positionsY[self.indx_tl]]
        #tr = [self.positionsX[self.indx_tr], self.positionsY[self.indx_tr]]
        #bl = [self.positionsX[self.indx_bl], self.positionsY[self.indx_bl]]
        #br = [self.positionsX[self.indx_br], self.positionsY[self.indx_br]]

        self.scan_data[self.folder_indx].images[self.image_indx].set_points(self.positionsX,self.positionsY)# .set_bbox(tl, tr, bl, br)
        self.scan_data[self.folder_indx].images[self.image_indx].set_grid_param(self.num_row, self.num_colum,
                                                                                self.buf_size)
        if self.letters == 'Symbol':
            self.scan_data[self.folder_indx].images[self.image_indx].set_letter_range(self.symbol_input.GetValue())
            print(self.scan_data[self.folder_indx].images[self.image_indx].letter_range)
        else:
            self.scan_data[self.folder_indx].images[self.image_indx].set_letter_range(self.letters)

        self.set_info()

        if self.scan_data[self.folder_indx].images[self.image_indx].full == True:
            self.img_info.SetValue("Set")
        else:
            self.img_info.SetValue("Un-Set")

    ## saves the data as a LOD format and saves imgs
    def save_images(self, base_path):

        EX = Namespace('http://fmnist.org/')

        # then we can create nades to specify the namespace
        # and put the name of the entity

        g = Graph()

        # Bind prefix to namespace to make it more readable
        g.bind('ex', EX)
        g.bind('foaf', FOAF)
        g.bind('schema', SDO)
        g.bind('dcterms', DCTERMS)



        for i, scan in enumerate( self.scan_data):
            self.folder_indx = i
            person = None
            if scan.name == None:
                scanName = os.path.join(base_path, str(i) + '\\')
                person = EX[str(i)]
            else:
                scanName = os.path.join(base_path, scan.name + '\\')
                person = EX[scan.name]

            g.add((person, RDF.type, FOAF.Person))
            home = Literal(scan.home, lang='en')
            intention = Literal(scan.intention, lang='en')
            g.add((person, SDO.homeLocation, home))
            g.add((person, SDO.intensity, intention))

            try:
                os.mkdir(scanName)
            except:
                print("Overwriting Person: ", scan.name)

            for j, img in enumerate(scan.images):

                print(img.rows, img.columns)
                self.image_indx = j

                letter_range = []
                if img.letter_range == 'A - F':
                    letter_range = ['a','b','c','d','e','f']
                elif img.letter_range == 'G - P':
                    letter_range = ['g','h','i','j','k','l', 'm', 'n', 'o','p']
                elif img.letter_range == 'Q - Z':
                    letter_range = ['q','r','s','t','u','v', 'w', 'x', 'y', 'z']
                else:
                    letter_range = img.letter_range.split(',')
                    print(len(letter_range))
                    print(img.letter_range)

                self.load_image()
                self.sqaure_img = img.set_crop_size(self.img)
                imgIndx = 0
                print(self.sqaure_img.shape)
                for y in range(0, img.columns):

                    ltr = ""
                    folderName = ""
                    if len(letter_range) <= y:
                        ltr = str(imgIndx)
                        folderName = os.path.join(scanName, ltr + '\\')
                        imgIndx+=1
                    else:
                        ltr =letter_range[y]
                        folderName = os.path.join(scanName, ltr + '\\')

                    if i==0:
                        letter = Literal(ltr, lang='en')
                        g.add((letter, RDF.type, FOAF.topic))
                        g.add((person, DCTERMS.creator, letter))

                    try:
                        os.mkdir(folderName)
                    except:
                        print("Overwriting Letter: ", ltr)

                    for x in range(0, img.rows):

                        cropped_img = img.crop_image(self.sqaure_img, y, x)
                        print(np.sum(cropped_img.shape), cropped_img.shape)
                        if np.sum(cropped_img.shape)==0:
                            continue
                        try:
                            self.img_cntrl.remove()
                        finally:
                            self.img_cntrl = self.axes.imshow(cropped_img)

                        self.canvas.draw()
                        path = os.path.join(os.path.abspath(os.getcwd()), folderName)
                        path = os.path.join(path, str(x) + '.png')
                        cropped_img *= 255

                        path = Literal(path, lang='en')
                        
                        g.add((letter, FOAF.Image, path))
                        g.add((person, DCTERMS.created, path))

                        pil_img = Image.fromarray((cropped_img).astype(np.uint8))
                        pil_img.save(path)


        g.serialize(destination= base_path+'//f_mnist_Dataset.ttl')
        g.serialize(destination=base_path + '//f_mnist_Dataset.xml')

# class to hold scan data
class ScanInfo:

    def __init__(self, root):
        self.full = False
        self.intention = None
        self.home = None
        self.name = None
        self.root_path = root
        self.image_paths = glob.glob(root[:-1] + '*.png')
        self.images = []
        for path in self.image_paths:
            img_info = ImageCropInfo()
            img_info.set_img(path)
            self.addImage(img_info)

    def addImage(self, image_info):
        self.images.append(image_info)

    def setData(self, name, home, intention):
        self.name = name
        self.home = home
        self.intention = intention
        self.full = True


# class to hold crop info data
class ImageCropInfo:
    def __init__(self):
        self.height = None
        self.width = None
        self.path = ""
        self.tl = -1
        self.tr = -1
        self.bl = -1
        self.br = -1
        self.buffer = 0
        self.rows = 0
        self.columns = 0
        self.full = False
        self.letter_range = None

    def set_img(self, imgpath):
        self.path = imgpath
    def set_letter_range(self, letterRange):
        self.letter_range = letterRange
    def set_bbox(self, topleft, topright, bottomleft, bottomright):
        self.tl = topleft
        self.tr = topright
        self.bl = bottomleft
        self.br = bottomright
        self.full = True

    def set_points(self, points_x, points_y):
        self.points = np.hstack((points_x,points_y))

    def set_grid_param(self, numrows, numcollumns, buffersize):
        self.rows = numrows
        self.columns = numcollumns
        self.buffer = buffersize

    def set_crop_size(self, img):


        sqaure_img = QRRead.four_point_transform(img, self.points)
        self.height, self.width, _ = sqaure_img.shape
        print('h:', self.height, 'c:', self.rows)

        self.width /= self.columns
        self.height /=  self.rows

        print('h:', self.height, 'w:', self.width)

        return  sqaure_img

    def crop_image(self, img, x, y):
        img_crop = img[int( self.height * y) + self.buffer:int( self.height * y + self.height)
                            - self.buffer, int( self.width * x) + self.buffer:int(
                            self.width * x + self.width) - self.buffer]
        return img_crop