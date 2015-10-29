# The Avatar System: API Layer
## Installation Guide for Ubuntu Server 14.04.3
### Install Required Packages
```
sudo apt-get install lamp-server^
sudo apt-get install php5-curl
sudo apt-get install postgresql-9.4 postgresql-contrib
```
### Configure PHP 5
```
sudo nano /etc/php5/apache2/php.ini
```
Modify the value of `upload_max_filesize` from `8M` to `1024M`, and the value of `post_max_size` from `8M` to `1024M`.
```
sudo service apache2 restart
```
### Configure PostgreSQL 9.4
```
sudo nano /etc/postgresql/9.4/main/pg_hba.conf
```
Modify the authentication of all connections to `trust`.
```
sudo /etc/init.d/postgresql restart
psql -h localhost -U postgres postgres -c "CREATE DATABASE avatar;"
```
### Install Python Libraries
```
sudo apt-get install python-pip
sudo apt-get install python-numpy python-scipy python-pandas
sudo apt-get install python-psycopg2
sudo pip install markdown xlsxwriter networkx
sudo pip install statsmodels
```
### Install Django
```
sudo pip install Django
sudo pip install djangorestframework
sudo pip install django-filter django-cors-headers django-queryset-csv
sudo pip install Celery
sudo pip install django-celery
```
### Migrate Database
```
python manage.py migrate
```
### Start Server
```
python manage.py runserver 0.0.0.0:9001
```
