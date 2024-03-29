# image_viewer_working.py
import glob
import random

import wx
# pages imported from other scripts
import ImageCroping
import RootSelector
import QRGenerator

# function to open main window and transfer between pages
########################################################################
class MyForm(wx.Frame):

    #----------------------------------------------------------------------
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY,
                          "Directory Selection")
        self.panel_one = RootSelector.RootPathSelection(self)
        self.panel_two = ImageCroping.ImageCropPanel(self)
        self.panel_three = QRGenerator.QR_Generator(self)
        self.panel_three.Hide()
        self.panel_two.Hide()

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.panel_one, 1, wx.EXPAND)
        self.sizer.Add(self.panel_two, 1, wx.EXPAND)
        self.sizer.Add(self.panel_three, 1, wx.EXPAND)
        self.SetSizer(self.sizer)

        menubar = wx.MenuBar()
        fileMenu = wx.Menu()

        self.panel_one.NextStep.Bind(wx.EVT_BUTTON, self.onSwitchPanels)

        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

    #----------------------------------------------------------------------
    def onSwitchPanels(self, event):
        paths = self.panel_one.img_Folders.GetValue().split('\n')

        self.panel_two.set_root(paths)
        self.panel_one.Hide()
        self.panel_two.Show()

        self.Layout()

# Run the program
if __name__ == "__main__":
    app = wx.App(False)
    frame = MyForm()
    frame.Show()
    app.MainLoop()