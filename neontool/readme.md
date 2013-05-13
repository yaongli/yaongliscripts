(1) Create database
create database neontool;

GRANT ALL PRIVILEGES ON neontool.* TO 'yaongli'@'localhost' IDENTIFIED BY 'yaongli' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON neontool.* TO 'yaongli'@'%' IDENTIFIED BY 'yaongli' WITH GRANT OPTION;


If getting: _mysql_exceptions.OperationalError: (2003, "Can't connect to MySQL server on 'localhost' (10061)")
Add this to my.ini

[mysqld]
enable-named-pipe=1
socket=MySQL

if in "C:\Windows\System32\drivers\etc\hosts"
127.0.0.1       localhost
::1             localhost

Change it to :
127.0.0.1       localhost

Don't use ipv6 localhost


(2) Commands

>python manage.py syncdb


