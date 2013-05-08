﻿# -*- coding:utf-8 -*-
import wx
import os
import sys
import re
from wsync import UrlDownload
import mysqlds
import shutil
import threading
import Queue
import traceback
from wxPython.wx import *
from wxPython.lib import newevent
#avoid Encoding Problem
reload(sys)
sys.setdefaultencoding('utf-8')  

DispatchEvent, EVT_DISPATCH = newevent.NewEvent()

class GenericDispatchMixin:
    def __init__(self):
        EVT_DISPATCH(self, self.OnDispatchEvent)

    def OnDispatchEvent(self, event):
        event.method(*event.arguments)

    def ThreadSafeDispatch(self, method, *arguments):
        wxPostEvent(self, DispatchEvent(method = method, arguments = arguments))

class DownloadTemplateFrame(wx.Frame, GenericDispatchMixin):
    def __init__(self, parent):
        wx.Frame.__init__(self, id=wx.NewId(), name='DownloadTemplateFrame', parent=parent,
              size=wx.Size(460, 600),
              style=wx.DEFAULT_FRAME_STYLE, title='Download Template')
        GenericDispatchMixin.__init__(self)

        self.panel = wx.Panel(id=wx.NewId(), name='panel', parent=self,
              pos=wx.Point(0, 0), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        LEFT_POS = 20
        LINE_POS = 20
        LINE_HEIGHT = 30 

        self.siteLabel = wx.StaticText(id=wx.NewId(),
              label='Clone template from site (eg. www.example.com/about):', name='siteLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        LINE_POS += LINE_HEIGHT
        self.siteurlText = wx.TextCtrl(id=wx.NewId(),
              name='siteurlText', parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), size=wx.Size(400, -1), value='')
        self.siteurlText.SetToolTipString('Clone template from this url, you should better choose a simple page')

        LINE_POS += LINE_HEIGHT
        self.instanceLabel = wx.StaticText(id=wx.NewId(),
              label='Instance Name (eg. test):', name='instanceLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        LINE_POS += LINE_HEIGHT
        self.instanceText = wx.TextCtrl(id=wx.NewId(),
              name='instanceText', parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), size=wx.Size(200, -1), value='test')
        self.instanceText.SetToolTipString('Instance name in NEONCRM')

        LINE_POS += LINE_HEIGHT
        self.copyToTomcatCheckbox = wx.CheckBox(self.panel, -1, "Copy template to ${TOMCAT_HOME}\\webapps\\np\\clients\\",
             pos=wx.Point(LEFT_POS, LINE_POS))
        self.copyToTomcatCheckbox.SetValue(True)

        LINE_POS += LINE_HEIGHT
        self.tomcatHomeLabel = wx.StaticText(id=wx.NewId(),
              label='TOMCAT_HOME:', name='tomcatHomeLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        self.tomcatHomeText = wx.TextCtrl(id=wx.NewId(),
              name='tomcatHomeText', parent=self.panel, pos=wx.Point(LEFT_POS + 100, LINE_POS), size=wx.Size(300, -1), value='D:\\Develop\\tomcat')
        self.tomcatHomeText.SetToolTipString('Tomcat home')

        LINE_POS += LINE_HEIGHT
        self.addJbossMysqlDSCheckbox = wx.CheckBox(self.panel, -1, "Add a mysql datasource config in ",
             pos=wx.Point(LEFT_POS, LINE_POS))
        self.addJbossMysqlDSCheckbox.SetValue(True)

        LINE_POS += 20
        self.addJbossMysqlDSLabel = wx.StaticText(id=wx.NewId(),
              label='${JBOSS_HOME}\\server\\default\\deploy\\mysql-ds.xml:', name='addJbossMysqlDSLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        LINE_POS += LINE_HEIGHT
        self.jbossHomeLabel = wx.StaticText(id=wx.NewId(),
              label='JBOSS_HOME:', name='jbossHomeLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        self.jbossHomeText = wx.TextCtrl(id=wx.NewId(),
              name='jbossHomeText', parent=self.panel, pos=wx.Point(LEFT_POS + 100, LINE_POS), size=wx.Size(300, -1), value='D:\\Develop\\jboss')
        self.jbossHomeText.SetToolTipString('Jboss home')

        LINE_POS += LINE_HEIGHT
        self.dbnameLabel = wx.StaticText(id=wx.NewId(),
              label='Database Name:', name='dbnameLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        self.dbnameText = wx.TextCtrl(id=wx.NewId(),
              name='dbnameText', parent=self.panel, pos=wx.Point(LEFT_POS + 100, LINE_POS), size=wx.Size(300, -1), value='')
        self.dbnameText.SetToolTipString('Database name used for add datasource to mysql-ds.xml')

        LINE_POS += LINE_HEIGHT
        self.dbhostLabel = wx.StaticText(id=wx.NewId(),
              label='Database Host:', name='dbhostLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)

        dbhostlist = ['localhost', '192.168.1.222', '192.168.1.198']
        self.dbhostComboBox = wx.ComboBox(self.panel, -1, "localhost", pos=wx.Point(LEFT_POS + 100, LINE_POS), 
                        choices=dbhostlist,
                        style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER
                         )

        self.dbportLabel = wx.StaticText(id=wx.NewId(),
              label='Port:', name='dbportLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS + 260, LINE_POS), style=0)
        self.dbportText = wx.TextCtrl(id=wx.NewId(),
              name='dbportText', parent=self.panel, pos=wx.Point(LEFT_POS + 300, LINE_POS), size=wx.Size(100, -1), value='3306')

        LINE_POS += (LINE_HEIGHT)
        self.executeBtn = wx.Button(id=wx.NewId(), label='Start Download',
              name='executeBtn', parent=self.panel, pos=wx.Point(180, LINE_POS),
              style=0)

        self.Bind(wx.EVT_BUTTON, self.OnDownload, self.executeBtn)

        LINE_POS += LINE_HEIGHT
        self.logLabel = wx.StaticText(id=wx.NewId(),
              label='Output', name='logLabel',
              parent=self.panel, pos=wx.Point(LEFT_POS, LINE_POS), style=0)
        LINE_POS += LINE_HEIGHT
        self.logText = wx.TextCtrl(self.panel, -1, "", pos=wx.Point(LEFT_POS, LINE_POS),
                        size=(400, 150), style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_RICH2|wx.HSCROLL)
                        
    def write(self, *args, **kwargs):
        message = "[STDOUT]" + "\n".join(args)
        wx.CallAfter(self.appendLog, message)

    def appendLog(self, message):
        self.logText.AppendText(message)
        
    def MessageBox(self, message):
        dlg = wx.MessageDialog(None, message, "Message", wx.OK | wx.ICON_INFORMATION)
        if dlg.ShowModal() == wx.ID_YES:
            self.Close(True)
        dlg.Destroy()
        
    def GetValue(self):
        self.siteUrl = self.siteurlText.GetValue().strip()
        self.instanceName = self.instanceText.GetValue().strip()
        self.isCopyToTomcat = self.copyToTomcatCheckbox.GetValue()
        self.isAddDataSource = self.addJbossMysqlDSCheckbox.GetValue()
        self.TOMCAT_HOME = self.tomcatHomeText.GetValue().strip()
        self.JBOSS_HOME = self.jbossHomeText.GetValue().strip()
        self.dbName = self.dbnameText.GetValue().strip()
        self.dbHost = self.dbhostComboBox.GetValue().strip()
        self.dbPort = self.dbportText.GetValue().strip()
        self.PrintValue()
        if len(self.siteUrl) == 0:
            self.MessageBox("Please input site url!")
            return False
        if len(self.instanceName) == 0:
            self.MessageBox("Please input instance name!")
            return False
        if self.isCopyToTomcat and len(self.TOMCAT_HOME) == 0:
            self.MessageBox("Please input TOMCAT_HOME!")
            return False
        if self.isAddDataSource:
            if len(self.JBOSS_HOME) == 0:
                self.MessageBox("Please input JBOSS_HOME!")
                return False
            if len(self.dbName) == 0:
                self.MessageBox("Please input database name!")
                return False
            if len(self.dbHost) == 0:
                self.MessageBox("Please select database host!")
                return False
            if len(self.dbPort) == 0:
                self.MessageBox("Please input database port!")
                return False
        return True

    def PrintValue(self):
        print self.siteUrl 
        print self.instanceName 
        print self.isCopyToTomcat 
        print self.isAddDataSource 
        print self.TOMCAT_HOME 
        print self.JBOSS_HOME 
        print self.dbName 
        print self.dbHost 
        print self.dbPort

    def OnDownload(self, evt):
        if not self.GetValue():
            return
        try:
            self.executeBtn.Disable()
            print "Begin to download web template ..."
            self.t = TRun(self)
            self.t.setDaemon(True)
            self.t.start()
        except Exception, e:
            self.executeBtn.Enable()
            print e
            self.MessageBox("Failed! Some errors occur." + e.message)
            
class TRun(threading.Thread):
    def __init__(self, caller):
        threading.Thread.__init__(self)
        self.caller = caller
        self.flag = True

    def run(self):
        self.dl = UrlDownload(self.caller.siteUrl)
        self.dl.execute()
        print "End to download web template"
        
        if True:
            if self.caller.isCopyToTomcat:
                print "Begin to copy template to tomcat ..."
                try:
                    clientdir = os.path.join(self.caller.TOMCAT_HOME, r"webapps\np\clients", self.caller.instanceName)
                    if os.path.exists(clientdir):
                        shutil.rmtree(clientdir)
                    os.makedirs(clientdir)
                    shutil.copytree("temp/result/", clientdir)
                except:
                    print "[ERROR] Copy template to tomcat failed. From %s to %s" % ("temp/result/", clientdir)
                print "End to copy template to tomcat"
            
            if self.caller.isAddDataSource:
                print "Begin to add datasource ..."
                try:
                    mysqlds.mysql_ds_file = os.path.join(self.caller.JBOSS_HOME, r"server\default\deploy\mysql-ds.xml")
                    mysqlds.add_datasource(self.caller.instanceName, self.caller.dbHost, self.caller.dbPort, self.caller.dbName)
                except:
                    print "[ERROR] Add datasource failed."
                print "End to add datasource"
            
            self.caller.MessageBox("Finish!")
            self.caller.executeBtn.Enable()
        


class DownloadTemplateApp(wx.App):
    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect, filename)
       
    def OnInit(self):
        self.frame = DownloadTemplateFrame(None)
        self.frame.Center()
        self.frame.Show()
        self.stdout = sys.stdout
        sys.stdout = self.frame
        try:
            _icon = wx.Icon('import.ico', wx.BITMAP_TYPE_ICO)
            self.frame.SetIcon(_icon)
        except:
            pass
        return True

    def OnExit(self):
        sys.stdout = self.stdout
        pass

if __name__ == "__main__":
    print "Start running ..."
    app = DownloadTemplateApp(redirect=False)
    app.MainLoop()
