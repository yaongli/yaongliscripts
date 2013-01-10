# -*- coding:utf-8 -*- 

import os
import shutil
import sys
import time
import fnmatch
import tempfile
import tarfile
import optparse
from optparse import OptionParser
import logging
import re

import subprocess

DEFAULT_HOST="xxxxxxxxxxxxxxxx"
DEFAULT_PORT="xxxx"
DEFAULT_USERID = "xxxxxxx"
DEFAULT_PASSWORD = "xxxxxxxx"

#FOR SAFE, NOW ONLY CAN IMPORT TO LOCALHOST
DEFAULT_IMPORT_HOST = 'xxx'
DEFAULT_IMPORT_PORT = 'xxx'
DEFAULT_IMPORT_USERID = "xx"
DEFAULT_IMPORT_PASSWORD = "xxxx"

def _cmd(args):
    pass
    os.system(args)
    
def _parse_args():
    """
    Parse the command line for options
    """
    usage = "usage: %prog [options] database1 <database2> ..."
    parser = OptionParser(usage)
    parser.add_option('--export-server', dest='export_server', metavar="export_server", default=DEFAULT_HOST,
        help='The host of database server.')
        
    parser.add_option('--export-port', dest='export_port', metavar="export_port", default=DEFAULT_PORT,
        help='The port of database server')
        
    parser.add_option('--export-userid', dest='export_userid', metavar="export_userid", default=DEFAULT_USERID,
        help='The userid of database server')
    
    parser.add_option('--export-password', dest='export_password', metavar="export_password", default=DEFAULT_PASSWORD,
        help='The password of database server')
    
    parser.add_option('--import-server', dest='import_server', metavar="import_server", default=DEFAULT_IMPORT_HOST,
        help='The host of import database server.')
        
    parser.add_option('--import-port', dest='import_port', metavar="import_port", default=DEFAULT_IMPORT_PORT,
        help='The port of import database server.')
        
    parser.add_option('--import-userid', dest='import_userid', metavar="import_userid", default=DEFAULT_IMPORT_USERID,
        help='The userid of import database server')
    
    parser.add_option('--import-password', dest='import_password', metavar="import_password", default=DEFAULT_IMPORT_PASSWORD,
        help='The password of import database server')
    
    parser.add_option('-c', '--change-to-innodb', dest='change_to_innodb', action="store_true", help='')
    
    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error("Need database name.")
    
    return (options, args)

def change_myisam_to_innodb(database):
    print "---Begin to change MyISAM to InnoDB---"
    myisam_file = open(("%s_ddl.sql" % database), "rb")
    ddl_content = myisam_file.read()
    myisam_file.close()
    
    ddl_content = ddl_content.replace("ENGINE=MyISAM", "ENGINE=InnoDB").replace(",\r\n  FULLTEXT KEY", "#,\r\n  #FULLTEXT KEY").replace(",\n  FULLTEXT KEY", "#,\n  #FULLTEXT KEY")
    
    innodb_file = open(("%s_innodb_ddl.sql" % database), "wb")
    innodb_file.write(ddl_content)
    innodb_file.flush()
    innodb_file.close()
    print "---End to change MyISAM to InnoDB---"

def export_database(parameters):
    print "---Begin to export database %s---" % parameters['database']
    cmd = "mysqldump -h %(export_server)s -P %(export_port)s -d -u%(export_userid)s -p%(export_password)s %(database)s > %(database)s_ddl.sql" % parameters
    print "......Export DDL: ", cmd
    _cmd(cmd)
    print "......Export DDL: OK"
    print ""
    
    cmd = "mysqldump -h %(export_server)s -P %(export_port)s -t -u%(export_userid)s -p%(export_password)s %(database)s > %(database)s_data.sql" % parameters
    print "......Export DATA: ", cmd
    _cmd(cmd)
    print "......Export DATA OK"
    
    print "---End to export database %s---" % parameters['database']
    
def import_database(parameters):
    print "---Begin to import database %s---" % parameters['database']
    temp_file = open("temp_create_database.sql", "wb")
    temp_file.write("DROP DATABASE IF EXISTS %(database)s;\n" % parameters)
    temp_file.write("CREATE DATABASE %(database)s;\n" % parameters)
    temp_file.flush()
    temp_file.close()
    
    cmd = "mysql -u%(import_userid)s -p%(import_password)s < temp_create_database.sql" % parameters
    print "......Create database DDL: ", cmd
    _cmd(cmd)
    print "......Create database DDL: OK"
    
    cmd = "mysql -u%(import_userid)s -p%(import_password)s %(database)s < %(database)s" % parameters
    if parameters.get('change_to_innodb'):
        print "..........Use innodb ddl sql to create tables."
        cmd = cmd + "_innodb_ddl.sql"
    else:
        cmd = cmd + "_ddl.sql"
    
    print "......Import DDL: ", cmd
    _cmd(cmd)
    print "......Import DDL: OK"
    print ""
    
    cmd = "mysql -u%(import_userid)s -p%(import_password)s %(database)s < %(database)s_data.sql" % parameters
    print "......Import DATA: ", cmd
    _cmd(cmd)
    print "......Import DATA OK"
    
    print "---End to import database %s---" % parameters['database']

def main():
    options, args = _parse_args()

    for database in args:
        print "++++    Begin to deal with database %s    ++++" % database
        parameters = dict(options.__dict__)
        parameters["database"] = database
        export_database(parameters)
        
        if(parameters.get('change_to_innodb')):
            change_myisam_to_innodb(database)
        
        import_database(parameters)
        
        print "++++    ENd   to deal with database %s    ++++" % database
    
if __name__ == "__main__":
    main()


































