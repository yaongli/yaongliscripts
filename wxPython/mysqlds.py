# -*- coding:utf-8 -*-
import os
import sys
import re

mysql_ds_file = r"D:\Develop\jboss\server\default\deploy\mysql-ds.xml"

instance_ds_template = r"""
  <local-tx-datasource>
    <jndi-name>DefaultDS-%(instance_name)s</jndi-name>
    <connection-url>jdbc:mysql://%(hostname)s:%(port)s/%(dbname)s?useUnicode=true&amp;characterEncoding=UTF-8</connection-url>
    <driver-class>com.mysql.jdbc.Driver</driver-class>
    <user-name>root</user-name>
    <password>justdoit</password>
    <connection-property name="autoReconnect">true</connection-property>
    <!--pooling parameters-->
    <min-pool-size>1</min-pool-size>
    <max-pool-size>5</max-pool-size>
    <blocking-timeout-millis>5000</blocking-timeout-millis>
    <idle-timeout-minutes>5</idle-timeout-minutes>

  </local-tx-datasource>
"""

end_tag = r"</datasources>"

def replace(old, new):
    content = ""
    with open(mysql_ds_file, 'rb') as dsfile:
        content = dsfile.read()
    
    content = content.replace(old, new)
    
    with open(mysql_ds_file, 'wb') as dsfile:
        dsfile.write(content)

def is_exsits(instance_name):
    jndi_name = "<jndi-name>DefaultDS-%(instance_name)s</jndi-name>" % {'instance_name' : instance_name}
    with open(mysql_ds_file, 'rb') as dsfile:
        content = dsfile.read()
        if content.find(jndi_name) > 0:
            return True
    return False
        
def add_datasource(instance_name, hostname, port, dbname):
    if is_exsits(instance_name):
        print "Datasource %s already exists." % instance_name
    print "----Begin to add datasource for %s to %s-----" % (instance_name, mysql_ds_file)
    old = end_tag
    new = instance_ds_template % {'instance_name' : instance_name,
                                  'hostname':hostname,
                                  'port':port,
                                  'dbname':dbname,                                  
                                 }
    new = new + "\n" + end_tag
    replace(old, new)
    print "----End   to add datasource for %s to %s-----" % (instance_name, mysql_ds_file)

    