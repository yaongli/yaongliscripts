# -*- coding:utf-8 -*-
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
import time
#avoid Encoding Problem
reload(sys)
sys.setdefaultencoding('utf-8')  

DispatchEvent, EVT_DISPATCH = newevent.NewEvent()

class DownloadTemplateFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, id=wx.NewId(), name='DownloadTemplateFrame', parent=parent,
              size=wx.Size(540, 600),
              style=wx.DEFAULT_FRAME_STYLE, title='Download Template')
              
        self.panel = panel = wx.Panel(self, -1)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        siteLabel = wx.StaticText(panel, label="Instance Name:   ")
        hbox.Add(siteLabel,flag=wx.RIGHT, border=8)
        self.instanceText = wx.TextCtrl(panel, size=wx.Size(100, -1))
        self.instanceText.SetToolTipString('Instance name in NEONCRM, (eg. test)')
        hbox.Add(self.instanceText)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        siteLabel = wx.StaticText(panel, label="Site URL:         ")
        hbox.Add(siteLabel,flag=wx.RIGHT, border=18)
        self.siteurlText = wx.TextCtrl(panel, size=wx.Size(300, -1))
        self.siteurlText.SetToolTipString('Clone template from site (eg. www.example.com/about)')
        hbox.Add(self.siteurlText)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.copyToTomcatCheckbox = wx.CheckBox(self.panel, -1, "Copy template to ${TOMCAT_HOME}\\webapps\\np\\clients\\")
        self.copyToTomcatCheckbox.SetValue(True)
        hbox.Add(self.copyToTomcatCheckbox,flag=wx.RIGHT, border=8)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        tomcatHomeLabel = wx.StaticText(panel, label="TOMCAT_HOME: ")
        hbox.Add(tomcatHomeLabel,flag=wx.RIGHT, border=8)
        self.tomcatHomeText = wx.TextCtrl(panel, size=wx.Size(300, -1), value='D:\\Develop\\tomcat')
        hbox.Add(self.tomcatHomeText)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.addJbossMysqlDSCheckbox = wx.CheckBox(self.panel, -1, "Add a mysql datasource config in ${JBOSS_HOME}\\server\\default\\deploy\\mysql-ds.xml")
        self.addJbossMysqlDSCheckbox.SetValue(True)
        hbox.Add(self.addJbossMysqlDSCheckbox,flag=wx.RIGHT, border=8)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        jbossHomeLabel = wx.StaticText(panel, label="JBOSS_HOME:    ")
        hbox.Add(jbossHomeLabel,flag=wx.RIGHT, border=8)
        self.jbossHomeText = wx.TextCtrl(panel, size=wx.Size(300, -1), value='D:\\Develop\\jboss')
        hbox.Add(self.jbossHomeText)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        dbHomeLabel = wx.StaticText(panel, label="Database name:  ")
        hbox.Add(dbHomeLabel, flag=wx.RIGHT, border=8)
        self.dbnameText = wx.TextCtrl(panel, size=wx.Size(100, -1), value='')
        hbox.Add(self.dbnameText)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        dbHostLabel = wx.StaticText(panel, label="Database host:   ")
        hbox.Add(dbHostLabel, flag=wx.RIGHT, border=8)
        dbhostlist = ['localhost', '192.168.1.222', '192.168.1.198']
        self.dbhostComboBox = wx.ComboBox(self.panel, -1, "localhost",
            choices=dbhostlist, style=wx.CB_DROPDOWN | wx.TE_PROCESS_ENTER)
        hbox.Add(self.dbhostComboBox, border=8)
        dbPortLabel = wx.StaticText(panel, label="    Post: ")
        hbox.Add(dbPortLabel, flag=wx.RIGHT, border=8)
        self.dbportText = wx.TextCtrl(panel, size=wx.Size(100, -1), value='3306')
        hbox.Add(self.dbportText)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.executeBtn = wx.Button(panel, label='Start Download', style=0)
        self.Bind(wx.EVT_BUTTON, self.OnDownload, self.executeBtn)
        hbox.Add(self.executeBtn, )
        vbox.Add(hbox, flag=wx.ALIGN_CENTER, border=10)
        vbox.Add((-1, 10))
        
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.logText = wx.TextCtrl(self.panel, -1, "",
                        size=(-1, -1), style=wx.TE_MULTILINE|wx.HSCROLL|wx.TE_RICH2|wx.HSCROLL)
        hbox.Add(self.logText, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, proportion=1, border=10)
        vbox.Add(hbox, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, proportion=1)
        vbox.Add((-1, 10))
        
        panel.SetSizerAndFit(vbox)
        
        
    def __init1__(self, parent):
        wx.Frame.__init__(self, id=wx.NewId(), name='DownloadTemplateFrame', parent=parent,
              size=wx.Size(460, 600),
              style=wx.DEFAULT_FRAME_STYLE, title='Download Template')

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
        message = "".join(args)
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
        print "siteUrl=", self.siteUrl 
        print "instanceName=", self.instanceName 
        print "isCopyToTomcat=", self.isCopyToTomcat 
        print "isAddDataSource=", self.isAddDataSource 
        print "TOMCAT_HOME=", self.TOMCAT_HOME 
        print "JBOSS_HOME=", self.JBOSS_HOME 
        print "dbName=", self.dbName 
        print "dbHost=", self.dbHost 
        print "dbPort=", self.dbPort

    def OnDownload(self, evt):
        if not self.GetValue():
            return
        try:
            self.executeBtn.Disable()
            self.starttime = time.clock()
            self.t = TRun(self)
            self.t.setDaemon(True)
            self.t.start()
        except Exception, e:
            self.executeBtn.Enable()
            print e
            self.MessageBox("Failed! Some errors occur." + e.message)
    
    def OnFinish(self):
        usetime = time.clock() - self.starttime
        print "Used time [%s]s" % usetime
        self.MessageBox("Finish! Used time [%s]s" % usetime)
        self.executeBtn.Enable()
        

class TRun(threading.Thread):
    def __init__(self, caller):
        threading.Thread.__init__(self)
        self.caller = caller
        self.flag = True

    def run(self):
        print "Begin to download web template ..."
        self.dl = UrlDownload(self.caller.siteUrl)
        self.dl.execute()
        print "End to download web template"
        
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
        
        print "======================================"
        print "Finish."
        print "======================================"
        wx.CallAfter(self.caller.OnFinish)
            
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
