# -*- coding:utf-8 -*-
import wx
import os
import sys
import re
import subprocess

BC_EXE = r"C:\Users\YangYongli\Downloads\BeyondComparePortable\BeyondComparePortable\App\BeyondCompare\BCompare.exe"
NEON_SRC = r"D:\workspace\neon\src"
NEON_BRANCH_SRC = r"D:\workspace\neon_branch\src"


def create(parent):
    return CompareListFrame(parent)

[wxID_FRAME1, wxID_FRAME1CANCELBTN, wxID_FRAME1COMPAREBTN,
wxID_FRAME1FILESPATHTEXTCTRL, wxID_FRAME1PANEL, wxID_FRAME1STATICTEXT1,
] = [wx.NewId() for _init_ctrls in range(6)]

class CompareListFrame(wx.Frame):
    def _init_sizers(self):
        # generated method, don't edit

        self.scrolledWindow1.SetSizer(self.gridSizer2)


    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FRAME1, name='', parent=prnt,
              pos=wx.Point(468, 85), size=wx.Size(786, 579),
              style=wx.DEFAULT_FRAME_STYLE, title='Compare Files')
        self.SetClientSize(wx.Size(770, 541))

        self.panel = wx.Panel(id=wxID_FRAME1PANEL, name='panel', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(770, 541),
              style=wx.TAB_TRAVERSAL)

        self.staticText1 = wx.StaticText(id=wxID_FRAME1STATICTEXT1,
              label='File path list(relate to src/):', name='staticText1',
              parent=self.panel, pos=wx.Point(24, 16), size=wx.Size(320, 24),
              style=0)
        self.staticText1.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL,
              wx.NORMAL, False, ''))

        self.filesPathTextCtrl = wx.TextCtrl(id=wxID_FRAME1FILESPATHTEXTCTRL,
              name='filesPathTextCtrl', parent=self.panel, pos=wx.Point(25, 56),
              size=wx.Size(720, 400), style=wx.TE_MULTILINE|wx.TE_RICH2, value='')
        self.filesPathTextCtrl.Center(wx.HORIZONTAL)
        self.filesPathTextCtrl.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL,
              wx.NORMAL, False, ''))
        self.filesPathTextCtrl.SetToolTipString('File Path List')

        self.compareBtn = wx.Button(id=wxID_FRAME1COMPAREBTN, label='Compare',
              name='compareBtn', parent=self.panel, pos=wx.Point(424, 496),
              size=wx.Size(75, 24), style=0)

        self.Bind(wx.EVT_BUTTON, self.OnCompareFiles, self.compareBtn)

        self.clearBtn = wx.Button(id=wxID_FRAME1CANCELBTN, label='Clear',
              name='clearBtn', parent=self.panel, pos=wx.Point(592, 496),
              size=wx.Size(75, 24), style=0)

        self.Bind(wx.EVT_BUTTON, self.OnClearFiles, self.clearBtn)

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnCompareFiles(self, evt):
        filelistContent = self.filesPathTextCtrl.GetValue()
        if filelistContent is None:
            return
        filelist = filelistContent.split()
        self.filesPathTextCtrl.SetValue("\n".join(filelist))
        
        for fn in filelist:
            fn = fn.replace("\n", "").replace("\r", "").strip()
            if "" == fn: 
                continue
            mainpath = os.path.join(NEON_SRC, fn)
            branchpath = os.path.join(NEON_BRANCH_SRC, fn)
            os.system(BC_EXE + " \"" + mainpath + "\" \"" + branchpath + "\"")

    def OnClearFiles(self, evt):
        self.filesPathTextCtrl.SetValue("")



class CompareApp(wx.App):
    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect, filename)
       
    def OnInit(self):
        self.frame = CompareListFrame(None)
        self.frame.Show()
        return True

    def OnExit(self):
        pass

if __name__ == "__main__":
    app = CompareApp()
    app.MainLoop()
