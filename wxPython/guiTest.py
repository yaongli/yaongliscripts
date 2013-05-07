# coding:utf-8
"""
http://blog.donews.com/limodou/archive/2005/08/15/509966.aspx
@author: limodou
"""
import wx
import time
import threading
import Queue
import traceback
import sys
from wxPython.wx import *
from wxPython.lib import newevent

DispatchEvent, EVT_DISPATCH = newevent.NewEvent()

class GenericDispatchMixin:
    def __init__(self):
        EVT_DISPATCH(self, self.OnDispatchEvent)

    def OnDispatchEvent(self, event):
        event.method(*event.arguments)

    def ThreadSafeDispatch(self, method, *arguments):
        wxPostEvent(self, DispatchEvent(method = method, arguments = arguments))

class MainApp(wx.App):
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

class MainFrame(wx.Frame, GenericDispatchMixin):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "Long term")
        GenericDispatchMixin.__init__(self)

        box = wx.BoxSizer(wx.HORIZONTAL)

        self.ID_BTN = wx.NewId()
        self.btn = wx.Button(self, self.ID_BTN, u"Start", size=(60, 22))
        box.Add(self.btn, 0, wx.ALIGN_CENTRE|wx.ALL, 0)
        
        wx.EVT_BUTTON(self.btn, self.ID_BTN, self.OnStart)
        
        self.SetSizerAndFit(box)
        
        
    def OnStart(self, event):
        self.progress = wx.ProgressDialog(u"Start...", u"Waiting ....", 100, style=wx.PD_AUTO_HIDE|wx.PD_CAN_ABORT)
        self.t = TRun(self)
        self.t.setDaemon(True)
        self.t.start()
        
class TRun(threading.Thread):
    def __init__(self, caller):
        threading.Thread.__init__(self)
        self.caller = caller
        self.flag = True

    def run(self):
        for i in range(100):
            print "run %d" % (i+1)
            self.caller.ThreadSafeDispatch(self.update, i)
            if not self.flag:
                self.destroy()
                print "flag", self.flag
                return
            time.sleep(0.1)
        self.destroy()

    def setFlag(self, flag):
        self.flag = flag

    def update(self, i):
        self.flag = self.caller.progress.Update(i+1)
        print self.flag

    def destroy(self):
        self.caller.ThreadSafeDispatch(self.caller.progress.Destroy)
    
app = MainApp(0)

app.MainLoop()
