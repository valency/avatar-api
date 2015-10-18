# The Avatar System: API Layer
## Installation Guide for Ubuntu Server 14.04
### Install Required Packages
```
sudo apt-get install lamp-server^
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install php5-curl
```
### Configure PHP 5
```
sudo nano /etc/php5/apache2/php.ini
```

>   upload_max_filesize = 8M `>>` 1024M

>   post_max_size = 8M `>>` 1024M

```
sudo service apache2 restart
```
### Configure PostgreSQL 9.4
```
sudo /etc/init.d/postgresql stop
sudo nano /etc/postgresql/9.4/main/pg_hba.conf
```

>   all all peer / ident `>>` all all trust

```
export PATH=/usr/lib/postgresql/9.4/bin/:$PATH
mkdir ./run
initdb -D ./pgdata
echo "unix_socket_directories = '`pwd`/run'" >>./pgdata/postgresql.conf
pg_ctl start -D ./pgdata -l ./run/postgres.log
psql -h localhost -U <username> postgres -c "CREATE DATABASE avatar;"
```
### Install Python Libraries
```
sudo apt-get install python-setuptools
sudo apt-get install python-dev python-pip
sudo apt-get install python-numpy
sudo apt-get install python-scipy
sudo apt-get install python-psycopg2
sudo apt-get install python-pandas
sudo pip install markdown
sudo pip install xlsxwriter
sudo pip install statsmodels
sudo pip install networkx
```
### Install Django
```
sudo pip install Django
sudo pip install djangorestframework
sudo pip install django-filter
sudo pip install django-cors-headers
sudo pip install django-queryset-csv
```
