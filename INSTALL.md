Installation Instructions
=========================

These were made when installing on an AWS lightsail Amazon Linux 2 instance

Load packages
-------------

```
sudo yum -y install git
cd /srv
sudo git clone https://github.com/s-andrews/cyclewithme.git
```

We need mongodb which we need to install an additional repository

This is ```/etc/yum.repos.d/mongodb-org-4.4.repo```

```
[mongodb-org-4.4]
name=MongoDB Repository
baseurl=https://repo.mongodb.org/yum/amazon/2/mongodb-org/4.4/x86_64/
gpgcheck=1
enabled=1
gpgkey=https://www.mongodb.org/static/pgp/server-4.4.asc
```

Once that's installed you can do:

```
sudo yum install -y mongodb-org
sudo systemctl start mongod
sudo systemctl enable mongod
```

Configure apache
----------------

```
sudo yum -y install httpd mod_ssl
sudo systemctl enable httpd
sudo systemctl start httpd
```

Next we need to copy the ```conf/cyclewithme.conf``` file into ```/etc/http.d/conf.d/```


Configure python
----------------

We need pymongo to be available

```
sudo python3 -m pip install pymongo
```

Now we can restart apache and the basic site should work

```
sudo systemctl restart httpd
```


Getting an SSL certificate
==========================

There were multiple steps to this

Adding to the firewall
----------------------

Lightsail instances only allow http intially, so in the networking section of the instance you need to add https to the firewall


Installing snap
---------------

We want to use certbot, but that's installed via snap

We need to add the snap repository to yum.

```
cd /etc/yum.repos.d/
sudo wget https://people.canonical.com/~mvo/snapd/amazon-linux2/snapd-amzn2.repo
```

Now we can enable snap and use it to install certbot

```
sudo yum install snapd
sudo systemctl start snapd
sudo systemctl enable snapd
sudo snap install core; sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Then we can get the cert

```
sudo certbot --apache
```

..and restart apache

```
sudo systemctl restart httpd
```

Other configuration
===================

We want to enable all updates

```
sudo yum -y install yum-cron
sudo systemctl enable yum-cron
sudo systemctl start yum-cron
```

We want to renew certificates automatically, so save this into ```/etc/cron.daily/certbot.cron```

```
#!/bin/bash
certbot renew
```

Make it executable:

```
sudo chmod 755 /etc/cron.daily/certbot.cron
```

..and we should be done.


















