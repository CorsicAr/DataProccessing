# image_viewer_working.py
import glob
import random

import wx


class RootPathSelection(wx.Panel):

    def __init__(self, parent):

        """Constructor"""
        wx.Panel.__init__(self, parent=parent)
        # Browse button

        self.Folders = []
        Title = wx.StaticText(self, label="Browse for the root folder of scanned docs")
        browse_btn = wx.Button(self, label='Browse')
        browse_btn.Bind(wx.EVT_BUTTON, self.on_browse)
        path_title = wx.StaticText(self, label="Path")
        self.Root_Path = wx.TextCtrl(self, size=(200, -1))
        num_folders_title = wx.StaticText(self, label="NumFolders")
        self.Num_Folders = wx.TextCtrl(self,  size=(200, -1))
        self.img_Folders = wx.TextCtrl(self, size=(400, 300), style=wx.TE_MULTILINE)
        self.NextStep = wx.Button(self, label='Next Step')
        self.NextStep.Disable()

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        hsizerBrowse = wx.BoxSizer(wx.HORIZONTAL)
        hsizerRC = wx.BoxSizer(wx.HORIZONTAL)


        # stacking layout
        main_sizer.Add(Title, 0, wx.ALL, 5)
        hsizerBrowse.Add(browse_btn, 0, wx.ALL, 5)
        hsizerBrowse.Add(self.Root_Path, 0, wx.ALL, 5)
        hsizerBrowse.Add(path_title, 0, wx.ALL, 5)
        main_sizer.Add(hsizerBrowse, 0, wx.ALL, 5)
        hsizerRC.Add(self.Num_Folders, 0,wx.ALL, 5)
        hsizerRC.Add(num_folders_title, 0,wx.ALL, 5)
        main_sizer.Add(hsizerRC, 0, wx.ALL, 5)
        main_sizer.Add(self.img_Folders)
        main_sizer.Add(self.NextStep)
        self.SetSizer(main_sizer)
        main_sizer.Fit(parent)

        self.Layout()
    def on_browse(self, event):
        wildcard = "folders (*)|*"
        with wx.DirDialog(None, "Choose a file",
                           style=wx.ID_OPEN) as dialog:
            if dialog.ShowModal() == wx.ID_OK:
                self.Root_Path.SetValue(dialog.GetPath())
                self.Folders = glob.glob(dialog.GetPath()+"/*/")


                if len(self.Folders) > 0:
                    self.Num_Folders.SetValue(str(len(self.Folders)))
                    self.NextStep.Enable()
                    for path in self.Folders:
                        self.img_Folders.WriteText(path + ' \n')


