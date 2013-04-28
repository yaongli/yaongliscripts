# -*- coding:utf-8 -*-
import wx
import os
import sys
import re
import subprocess

class DownloadTemplateFrame(wx.Frame):
    def __init__(self, parent):
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
        self.GetValue()

     

class DownloadTemplateApp(wx.App):
    def __init__(self, redirect=True, filename=None):
        wx.App.__init__(self, redirect, filename)
       
    def OnInit(self):
        self.frame = DownloadTemplateFrame(None)
        self.frame.Center()
        self.frame.Show()
        return True

    def OnExit(self):
        pass

if __name__ == "__main__":
    app = DownloadTemplateApp(redirect=False)
    app.MainLoop()
