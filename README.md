Syrup
=====

Open source Configuration Management Database (CMDB) system.

License
-------

This software is licensed under terms of the [Simplified (2-cluase) BSD License](http://opensource.org/licenses/BSD-2-Clause) as approved by the Open Source Initiative.


Install
-------

```shell
# as root
apt-get install python-pip
pip install -r requirements.txt

# as normal user
git clone https://github.com/beli-sk/syrup.git
cd syrup
mkdir sqlite
./manage.py syncdb
./manage.py runserver
```

or using virtualenv - all python requirements will be installed only inside virtual environment for this project

```shell
# as root
apt-get install python-pip python-virtualenv

# as normal user
virtualenv syrup_env
cd syrup_env
source bin/activate
git clone https://github.com/beli-sk/syrup.git
cd syrup
pip install -r requirements.txt
mkdir sqlite
./manage.py syncdb
./manage.py runserver

# to exit the virtual python environment
deactivate
```
