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

DEFAULT_HOST="xxxxxxxxxxx"
DEFAULT_PORT="xx"
DEFAULT_USERID = "xxx"
DEFAULT_PASSWORD = "xx"

DEFAULT_IMPORT_HOST = 'xx'
DEFAULT_IMPORT_PORT = 'xx'
DEFAULT_IMPORT_USERID = "xxx"
DEFAULT_IMPORT_PASSWORD = "xxx"

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
    
    parser.add_option('--export-only', dest='export_only', action="store_true", help='Export only')
    
    parser.add_option('--import-only', dest='import_only', action="store_true", help='Import only')
    
    parser.add_option('--change-only', dest='change_only', action="store_true", help='Change from myisam to innodb only')
    
    options, args = parser.parse_args()
    if len(args) == 0:
        parser.error("Need database name.")
    
    trueNum = 0
    if options.change_to_innodb: trueNum += 1
    if options.export_only: trueNum += 1
    if options.import_only: trueNum += 1
    
    if trueNum > 1:
        parser.error("Options --export-only/--import-only/--change-only/--change-to-innodb just need one.")
    
    return (options, args)

def change_myisam_to_innodb(database):
    print "---Begin to change MyISAM to InnoDB---"
    if not os.path.exists(("%s_ddl.sql" % database)):
        print "[ERROR] DDL sql file %s_ddl.sql does not exists."  % database
        print "-----------------------------------------"
        print "| [ERROR] Failed to change ddl file for %s |" % database
        print "-----------------------------------------"
        return 1
            
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
    has_import_file = True
    if parameters.get('change_to_innodb'):
        if not os.path.exists("%(database)s_innodb_ddl.sql" % parameters):
            print "[ERROR] DDL sql file %(database)s_innodb_ddl.sql does not exists."  % parameters
            has_import_file = False
    else:
        if not os.path.exists("%(database)s_ddl.sql" % parameters):
            print "[ERROR] DDL sql file %(database)s_ddl.sql does not exists."  % parameters
            has_import_file = False
        
    if not os.path.exists("%(database)s_data.sql" % parameters):
        print "[ERROR] Data sql file %(database)s_data.sql does not exists."  % parameters
        has_import_file = False
        
    if not has_import_file:
        print "--------------------------------------"
        print "|  [ERROR] Failed to import %(database)s |"  % parameters
        print "--------------------------------------"
        return 1
        
    temp_file = open("temp_create_database.sql", "wb")
    temp_file.write("DROP DATABASE IF EXISTS %(database)s;\n" % parameters)
    temp_file.write("CREATE DATABASE %(database)s;\n" % parameters)
    temp_file.flush()
    temp_file.close()
    
    cmd = "mysql -h %(import_server)s -P %(import_port)s -u%(import_userid)s -p%(import_password)s < temp_create_database.sql" % parameters
    print "......Create database DDL: ", cmd
    _cmd(cmd)
    print "......Create database DDL: OK"
    
    cmd = "mysql -h %(import_server)s -P %(import_port)s -u%(import_userid)s -p%(import_password)s %(database)s < %(database)s" % parameters
    if parameters.get('change_to_innodb'):
        print "..........Use innodb ddl sql to create tables."
        cmd = cmd + "_innodb_ddl.sql"
    else:
        cmd = cmd + "_ddl.sql"
    
    print "......Import DDL: ", cmd
    _cmd(cmd)
    print "......Import DDL: OK"
    print ""
    
    cmd = "mysql -h %(import_server)s -P %(import_port)s -u%(import_userid)s -p%(import_password)s %(database)s < %(database)s_data.sql" % parameters
    print "......Import DATA: ", cmd
    _cmd(cmd)
    print "......Import DATA OK"
    
    print "---End to import database %s---" % parameters['database']

    
def check_subworkdir(subworkdir):
    if os.path.exists(subworkdir):
        is_handle = True
        while True:
            user_input = raw_input("Work directory %s for database (%s) exists.Enter 'Y' to delete the existed directory and continue? or Enter 'N' to skip this database. [Y/N]" % (subworkdir, database)) 
            if 'N' == user_input.upper():
                print '[WARNING] Skipping database %s' % database
                return False
            elif 'Y' == user_input.upper():
                print "Delete %s " % subworkdir
                shutil.rmtree(subworkdir)
                return True
            else:
                pass
    else:
        return True

def main():
    options, args = _parse_args()

    workdir = os.path.abspath(os.curdir)
    for database in args:
        print "++++    Begin to deal with database %s    ++++" % database
        subworkdir = os.path.join(workdir, database)
        #if not check_subworkdir(subworkdir):
        #    continue
        
        if not os.path.exists(subworkdir):
            os.makedirs(subworkdir)
        os.chdir(subworkdir)
        print "Change to %s " % subworkdir
        
        parameters = dict(options.__dict__)
        parameters["database"] = database
        
        if not (options.change_only or options.import_only):
            export_database(parameters)
        
        if (parameters.get('change_to_innodb') or options.change_only):
            change_myisam_to_innodb(database)
            
        if not (options.change_only or options.export_only):
            import_database(parameters)
        
        print "++++    ENd   to deal with database %s    ++++" % database
        os.chdir(workdir)
    
if __name__ == "__main__":
    main()

