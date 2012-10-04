Syrup
=====

Open source Configuration Management Database (CMDB) system.

License
-------

This software is licensed under terms of the [Simplified (2-cluase) BSD License](http://opensource.org/licenses/BSD-2-Clause) as approved by the Open Source Initiative.


Install
-------

```shell
sudo apt-get install python-pip
git clone https://github.com/beli-sk/syrup.git
cd syrup
sudo pip install -r requirements.txt
mkdir sqlite
./manage.py syncdb --noinput
./manage.py runserver
```

Or using virtualenv - all python requirements will be installed only inside virtual environment for this project:

```shell
sudo apt-get install python-pip python-virtualenv
virtualenv syrup_env
cd syrup_env
source bin/activate
git clone https://github.com/beli-sk/syrup.git
cd syrup
pip install -r requirements.txt
mkdir sqlite
./manage.py syncdb --noinput
./manage.py runserver

# to exit the virtual python environment
deactivate
```

This will initialize an empty database with single user `admin`, password `syrup`.
