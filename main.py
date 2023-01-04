# image_viewer_working.py
import random

import wx
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg as NavigationToolbar2Wx
import matplotlib.image as mpimg
import matplotlib.lines as lines
import matplotlib.patches as mpatches
import math
import random

class ImagePanel(wx.Panel):

    def __init__(self, parent, image_size):
        super().__init__(parent)
        self.img_cntrl = None
        self.buf_size = 0
        self.patches = None
        self.img = None
        self.toolbar = None
        self.canvas = None
        self.figure = None
        self.dc = None
        self.axes = None
        self.max_size = 512
        self.num_row = 0
        self.num_colum = 0

        # click point lists
        self.positionsX = []
        self.positionsY = []

        # matplotlib panel
        self.frame_panel = wx.Panel(self, name="DataEntry")
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, self.figure)
        self.canvas.mpl_connect('button_press_event', self.on_click)

        # Browse button
        browse_btn = wx.Button(self, label='Browse')
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        self.photo_txt = wx.TextCtrl(self, size=(200, -1))

        #Rows slider
        sliderR =  wx.Slider(self,  value=0, minValue=0, maxValue=20,style=wx.SL_HORIZONTAL|wx.SL_VALUE_LABEL, name ="Rows")
        sliderR.Bind(wx.EVT_SLIDER, self.on_slideR)
        sliderRTtl = wx.StaticText(self, label="Rows")

        #Columns slider
        sliderC = wx.Slider(self, value=0, minValue=0, maxValue=20, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL,name="Rows")
        sliderC.Bind(wx.EVT_SLIDER, self.on_slideC)
        sliderCTtl = wx.StaticText(self, label="Collumns")

        # boarder slider
        sliderB = wx.Slider(self, value=0, minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL,
                            name="Rows")
        sliderB.Bind(wx.EVT_SLIDER, self.on_slideB)
        sliderBTtl = wx.StaticText(self, label="Buffer Space (px)")

        #Test Crops btn
        croptst_btn = wx.Button(self, label='TestCrops')
        croptst_btn.Bind(wx.EVT_BUTTON, self.preview_crops)

        #Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hsizerBrowse = wx.BoxSizer(wx.HORIZONTAL)
        hsizerRC = wx.BoxSizer(wx.HORIZONTAL)

        # stacking layout
        main_sizer.Add(self.canvas, 0, wx.ALL, 5)
        hsizerBrowse.Add(browse_btn, 0, wx.ALL, 5)
        hsizerBrowse.Add(self.photo_txt, 0, wx.ALL, 5)
        main_sizer.Add(hsizerBrowse, 0, wx.ALL, 5)
        hsizerRC.Add(sliderR, 0, wx.ALL, 5)
        hsizerRC.Add(sliderRTtl, 0, wx.ALL, 5)
        hsizerRC.Add(sliderC, 0, wx.ALL, 5)
        hsizerRC.Add(sliderCTtl, 0, wx.ALL, 5)
        hsizerRC.Add(sliderB, 0, wx.ALL, 5)
        hsizerRC.Add(sliderBTtl, 0, wx.ALL, 5)
        hsizerRC.Add(croptst_btn)
        main_sizer.Add(hsizerRC)

        self.SetSizer(main_sizer)
        main_sizer.Fit(parent)

        self.Layout()

    #on row slider
    def on_slideR(self, event):
        obj = event.GetEventObject()
        self.num_row = obj.GetValue()

    # on column slider
    def on_slideC(self, event):
        obj = event.GetEventObject()
        self.num_colum = obj.GetValue()

    # on column slider
    def on_slideB(self, event):
        obj = event.GetEventObject()
        self.buf_size = obj.GetValue()

    # on browse button
    def on_browse(self, event):
        wildcard = "PNG files (*.png)|*.png"
        with wx.FileDialog(None, "Choose a file",
                           wildcard=wildcard,
                           style=wx.ID_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.photo_txt.SetValue(dialog.GetPaths()[0])
                self.load_image()

    # function to click on matplotlib
    def on_click(self, event):
        numPos = len(self.positionsX)

        if numPos == 4:

            minDist = 1000000000
            indx = -1
            for i, (x,y) in enumerate(zip(self.positionsX,self.positionsY)):

                thisDist = math.dist((x,y),(event.xdata, event.ydata) )

                if thisDist<minDist:
                    minDist=thisDist
                    indx = i

            self.positionsX[indx] = event.xdata
            self.positionsY[indx] = event.ydata


        else:
            self.positionsX.append(event.xdata)
            self.positionsY.append( event.ydata)

            numPos = len(self.positionsX)

        if numPos == 4 :
            try:
                self.lines.remove()
            except:
                self.patches.remove()

            self.order_indxs()

            coords = []
            for (x,y) in zip(self.positionsX, self.positionsY):
                coords.append((x,y))
            self.patches = self.axes.add_patch(mpatches.Polygon(coords, alpha = 0.5))
            self.canvas.draw()
        elif numPos >= 2:
            if numPos>2:
                self.lines.remove()

            line = lines.Line2D(self.positionsX, self.positionsY)

            self.lines = self.axes.add_line(line)
            self.canvas.draw()

    # on browse load image
    def load_image(self):

        self.toolbar = NavigationToolbar2Wx(self.canvas)

        self.toolbar.Realize()

        filepath = self.photo_txt.GetValue()
        self.img = mpimg.imread(filepath)
        print(self.img.shape)
        self.img_cntrl = self.axes.imshow(self.img)
        self.canvas.draw()
        self.Refresh()

    def order_indxs(self):

        #order the points
        self.indx_tl = -1
        self.indx_tr = -1
        self.indx_bl = -1
        self.indx_br = -1

        tl_dist = 1000000000000
        tr_dist = 1000000000000
        bl_dist = 1000000000000
        br_dist = 1000000000000

        for i,(x,y) in enumerate(zip(self.positionsX,self.positionsY)):

            if math.dist((0,0), (x,y))<tl_dist:
                tl_dist=math.dist((0,0), (x,y))
                self.indx_tl = i
            if math.dist((self.img.shape[0],0), (x,y))<tr_dist:
                tr_dist=math.dist((self.img.shape[0],0), (x,y))
                self.indx_tr = i
            if math.dist((0,self.img.shape[1]), (x,y))<bl_dist:
                bl_dist=math.dist((0,self.img.shape[1]), (x,y))
                self.indx_bl = i
            if math.dist((self.img.shape[0],self.img.shape[1]), (x,y))<br_dist:
                br_dist=math.dist((self.img.shape[0],self.img.shape[1]), (x,y))
                self.indx_br = i

    def preview_crops(self, event):

        x = random.randint(0, self.num_row-1)
        y = random.randint(0, self.num_colum-1)

        width = (self.positionsX[self.indx_tr] - self.positionsX[self.indx_tl])/self.num_row
        height = (self.positionsY[self.indx_br] - self.positionsY[self.indx_tr])/self.num_colum
        self.img_crop = self.img[int(self.positionsY[self.indx_tl]+height*y)+self.buf_size:int(self.positionsY[self.indx_tl]+height*y+height)-self.buf_size,int(self.positionsX[self.indx_tl]+width*x)+self.buf_size:int(self.positionsX[self.indx_tl]+width*x+width)-self.buf_size]
        #self.figure.clear(True)
        try:
            self.img_cntrl.remove()
        finally:
            self.img_cntrl = self.axes.imshow(self.img_crop)
            self.canvas.draw()

class MainFrame(wx.Frame):

    def __init__(self):
        super().__init__(None, title='Image Viewer')
        panel = ImagePanel(self, image_size=(240,240))
        self.Show()

if __name__ == '__main__':
    app = wx.App(redirect=False)
    frame = MainFrame()
    app.MainLoop()