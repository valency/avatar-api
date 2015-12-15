# The Avatar System: API Layer
## Installation Guide for Ubuntu Server 14.04.3
### Install Required Packages
```
sudo apt-get install lamp-server^
sudo apt-get install php5-curl
sudo apt-get install postgresql-9.4 postgresql-contrib
sudo apt-get install nginx
```
### Configure Apache 2
```
sudo vim /etc/apache2/ports.conf
sudo vim /etc/apache2/sites-available/000-default.conf
```
Modify ports from `80` to `8080`, and `443` to `8443`.
```
sudo service apache2 restart
```
### Configure PHP 5
```
sudo vim /etc/php5/apache2/php.ini
```
Modify the value of `upload_max_filesize` and `post_max_size` from `8M` to `1024M`.
```
sudo service apache2 restart
```
### Configure PostgreSQL 9.4
```
sudo vim /etc/postgresql/9.4/main/pg_hba.conf
```
Modify the authentication of all connections to `trust`.
```
sudo /etc/init.d/postgresql restart
psql -h localhost -U postgres postgres -c "CREATE DATABASE avatar;"
```
### Configure NGINX
```
sudo vim /etc/nginx/nginx.conf
```
Add `client_max_body_size 1024m;` to `http` section.
```
sudo vim /etc/nginx/sites-available/default
```
Under `server` section, disable the settings of `root` and `location /`, and then add the following settings: 
```
location / {
  proxy_pass http://127.0.0.1:8080/;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 43200000;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Host $http_host;
  proxy_set_header X-NginX-Proxy true;
  proxy_buffering off;
}
location /api/avatar/ {
  proxy_pass http://127.0.0.1:9001/;
  proxy_http_version 1.1;
  proxy_set_header Upgrade $http_upgrade;
  proxy_set_header Connection "upgrade";
  proxy_read_timeout 43200000;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header Host $http_host;
  proxy_set_header X-NginX-Proxy true;
  proxy_buffering off;
}
```
```
sudo service nginx restart
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
sudo pip install Django djangorestframework django-filter django-cors-headers django-queryset-csv
sudo pip install Celery django-celery
```
### Install Avatar API
```
mkdir /var/www/api/
git clone git@github.com:valency/avatar-api.git /var/www/api/avatar
cd /var/www/api/avatar
python manage.py makemigrations avatar_core
python manage.py makemigrations avatar_user
python manage.py makemigrations avatar_map_matching
python manage.py makemigrations avatar_simulator
python manage.py migrate
python manage.py collectstatic
```
### Start Server
```
screen
python manage.py runserver 0.0.0.0:9001
```
