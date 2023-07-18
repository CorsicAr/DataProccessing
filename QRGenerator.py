# Importing library
import qrcode

import wx

import  os

# Window to select file base
class QR_Generator(wx.Panel):

    def __init__(self, parent):

        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        # Browse button

        self.Title = wx.StaticText(self, label="Setup and save your QR codes")

        IndxTtl = wx.StaticText(self, label="Indexs/Catagories")
        self.Indxs = wx.TextCtrl(self, size=(200, -1), value='a,b,c,d,e,f,g')
        self.number_indxs = 4
        self.indx_slideI =  wx.Slider(self, value=self.number_indxs, minValue=0, maxValue=20,
                            style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL, name="Rows")
        self.indx_slideI.Bind(wx.EVT_SLIDER, self.on_slideI)
        sliderITtl = wx.StaticText(self, label="Num Indxs")

        self.NumQRSX = 2
        self.indx_slideX = wx.Slider(self, value=self.NumQRSX, minValue=0, maxValue=20,
                                     style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL, name="Rows")
        self.indx_slideX.Bind(wx.EVT_SLIDER, self.on_slideX)
        sliderXTtl = wx.StaticText(self, label="Num QRS on x axis")

        self.NumQRSY = 2
        self.indx_slideY = wx.Slider(self, value=self.NumQRSY, minValue=0, maxValue=20,
                                     style=wx.SL_HORIZONTAL | wx.SL_VALUE_LABEL, name="Rows")
        self.indx_slideY.Bind(wx.EVT_SLIDER, self.on_slideY)
        sliderYTtl = wx.StaticText(self, label="Rows")

        self.Root_Path = wx.TextCtrl(self, size=(200, -1))

        browse_btn = wx.Button(self, label='Save')
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)


######## Main Layout
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hsizerBrowse = wx.BoxSizer(wx.HORIZONTAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
## Title and sliders
        main_sizer.Add(self.Title, 0, wx.ALL, 5)

        ####  set indxs
        hsizer.Add(self.Indxs, 0, wx.ALL, 5)
        hsizer.Add(IndxTtl, 0, wx.ALL, 5)

        main_sizer.Add(hsizer, 0, wx.ALL, 5)

        main_sizer.Add(self.indx_slideI, 0, wx.ALL, 5)
        main_sizer.Add(self.indx_slideX, 0, wx.ALL, 5)
        main_sizer.Add(self.indx_slideY, 0, wx.ALL, 5)
####  Browse and save
        hsizerBrowse.Add(browse_btn, 0, wx.ALL, 5)
        hsizerBrowse.Add(self.Root_Path, 0, wx.ALL, 5)

        main_sizer.Add(hsizerBrowse, 0, wx.ALL, 5)



        self.SetSizer(main_sizer)
        main_sizer.Fit(parent)

        self.Layout()

        ## on indx slider
    def on_slideI(self, event):
        obj = event.GetEventObject()
        self.NumberIndxs = obj.GetValue()

        ## on X slider
    def on_slideX(self, event):
        obj = event.GetEventObject()
        self.NumQRSX = obj.GetValue()
        ## on Y slider
    def on_slideY(self, event):
        obj = event.GetEventObject()
        self.NumQRSY = obj.GetValue()

        main_sizer = wx.BoxSizer(wx.VERTICAL)

    def on_browse(self, event):
        wildcard = "folders (*)|*"
        with wx.DirDialog(None, "Choose a file",
                           style=wx.ID_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.Root_Path.SetValue(dialog.GetPath())
                self.Itterate_QRS(dialog.GetPath())
    def Itterate_QRS(self, path):

        for x in range(0,self.NumQRSX):
            for y in range(0, self.NumQRSY):
                pos = str(x) + ',' + str(y)
                data = [pos,    self.Indxs.GetValue(), str(self.number_indxs)]
                data = ("; ").join(data)
                self.save_QR(os.path.join(path,pos),data)

    def save_QR(self, path = 'QR', data = 'data'):

        qr = qrcode.QRCode(version=1,
                           box_size=10,
                           border=0)

        # Adding data to the instance 'qr'
        qr.add_data(data)

        qr.make(fit=True)
        img = qr.make_image(fill_color='black',
                            back_color='white')


        # Saving as an image file
        img.save(path+'.png')



