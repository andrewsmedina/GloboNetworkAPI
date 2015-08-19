Installing Globo NetworkAPI
###########################


Using pre-configured VM
***********************

In order to use the pre-configured VM you need to have `vagrant <https://www.vagrantup.com/downloads.html>` and `VirtualBox <https://www.virtualbox.org/wiki/Downloads>` installed in your machine.

After that, go to the directory you want to install and do::

  git clone https://github.com/globocom/GloboNetworkAPI
  cd GloboNetworkAPI-WebUI
  vagrant plugin install vagrant-omnibus
  vagrant up

After this you'll have the GloboNetworkAPI running on http://10.0.0.2:8000/

Installing from scratch
***********************

Following examples were based on CentOS 7.0.1406 installation.

All root passwords were configured to "default".

All

Create a specific User/Group
****************************

::

	useradd -m -U networkapi
	passwd networkapi
	visudo
		networkapi      ALL=(ALL)       ALL

	sudo mkdir /opt/app/
	sudo chmod 777 /opt/app/


Download Code
*************

Download Globo NetworkAPI code from `Globocom GitHub <https://github.com/globocom/GloboNetworkAPI>`_.

In this example we are downloading code to ``/opt/app``::

	sudo yum install git
	cd /opt/app/
	git clone https://github.com/globocom/GloboNetworkAPI

We are exporting this variable below to better document the install process::

	export NETWORKAPI_FOLDER=/opt/app/GloboNetworkAPI/
	echo "export NETWORKAPI_FOLDER=/opt/app/GloboNetworkAPI/" >> ~/.bashrc


Create a VirtualEnv
*******************

::

	sudo yum install python-virtualenv
	sudo easy_install pip
	virtualenv ~/virtualenvs/networkapi_env
	source ~/virtualenvs/networkapi_env/bin/activate
	echo "source ~/virtualenvs/networkapi_env/bin/activate" >> ~/.bashrc


Install Dependencies
********************

You will need the following packages in order to install the next python packages via ``pip``::

	sudo yum install mysql
	sudo yum install mysql-devel
	sudo yum install gcc

Install the packages listed on ``$NETWORKAPI_FOLDER/requirements.txt`` file:

::

	pip install -r $NETWORKAPI_FOLDER/requirements.txt

Create a ``sitecustomize.py`` inside your ``/path/to/lib/python2.X`` folder with the following content::

	import sys
	sys.setdefaultencoding('utf-8')

::

	echo -e "import sys\nsys.setdefaultencoding('utf-8')\n" > ~/virtualenvs/networkapi_env/lib/python2.7/sitecustomize.py


Install Memcached
*****************

You can run memcached locally or you can set file variable ``CACHE_BACKEND`` to use a remote memcached farm in file ``$NETWORKAPI_FOLDER/networkapi/environment_settings.py``.

In case you need to run locally::

	sudo yum install memcached
	sudo systemctl start memcached
	sudo systemctl enable memcached

MySQL Server Configuration
**************************

For details on MySQL installation, check `MySQL Documentation <http://dev.mysql.com/doc/refman/5.1/en/installing.html>`_.

::

	sudo yum install mariadb-server mariadb
	sudo systemctl start mariadb.service
	sudo systemctl enable mariadb.service
	sudo /usr/bin/mysql_secure_installation

Test installation and create a telecom database::

	mysql -u root -p<password>
	CREATE user 'telecom' IDENTIFIED BY '<password>';
	GRANT ALL ON *.* TO 'telecom'@'%';
	FLUSH PRIVILEGES;

Create the necessary tables::

	mysql -u <user> -p <password> -h <host> <dbname> < $NETWORKAPI_FOLDER/dev/database_configuration.sql

If you want to load into your database the environment used for documentation examples::

	mysql -u <user> -p <password> -h <host> <dbname> < $NETWORKAPI_FOLDER/dev/load_example_environment.sql

Configure the Globo NetworkAPI code to use your MySQL instance:

File ``$NETWORKAPI_FOLDER/networkapi/environment_settings.py``::

	DATABASE_ENGINE = 'mysql'
	DATABASE_NAME = 'your_db_name'
	DATABASE_USER = 'your_db_user'
	DATABASE_PASSWORD = 'your_db_password'
	DATABASE_HOST = 'your_db_user_host'
	DATABASE_PORT = '3306'
	DATABASE_OPTIONS = {"init_command": "SET storage_engine=INNODB"}

HTTP Server Configuration
*************************

For a better performance, install Green Unicorn to run Globo NetworkAPI.

::

	pip install gunicorn

There is no need to install a nginx or apache to proxy pass the requests, once there is no static files in the API.

Edit ``$NETWORKAPI_FOLDER/gunicorn.conf.py`` to use your log files location and `user preferentes <http://gunicorn-docs.readthedocs.org/en/latest/settings.html#config-file>`_ and run gunicorn::

	cd $NETWORKAPI_FOLDER
	gunicorn networkapi_wsgi:application

Test installation
*****************

Try to access the root location of the API::

	http://your_location:8000/

This should take you a to 404 page listing available url's.

LDAP Server Configuration
*************************

If you want to use LDAP authentication, configure the following variables in ``FILE``:

!TODO

Integrate with Queue
********************

Install Dependencies::

	Apache ActiveMQ

Apache ActiveMQ ™ is the most popular and powerful open source messaging and Integration Patterns server. `Apache ActiveMQ Getting Started <http://activemq.apache.org/getting-started.html>`_.

Example configuration on ``settings.py``::

	BROKER_DESTINATION = "/topic/queue_name"
	BROKER_URI = "failover:(tcp://localhost:61613,tcp://server2:61613)?randomize=false,maxReconnectDelay=1,maxReconnectAttempts=0,startupMaxReconnectAttempts=0,useExponentialBackOff=false,initialReconnectDelay=1"
	SCHEDULER_INTERVAL = 15 #time in seconds

The interval (in seconds) between the background task that resends messages that weren't sent before can be set in the ``SCHEDULER_INTERVAL`` constant.

About ``Consumers``::

	Consumer must have the following connection headers:
	{'client-id': ' your-client-id '}

	On subscribe, consumers must pass some headers as well:
	{'ack': 'client-individual', 'persistent': 'true', 'activemq.retroactive': 'true', 'activemq.subscriptionName': 'your-client-id'}

By using this, the system guarantees that every queue subscriber will receive any dispatched message by all producers, even when they're offline.
It's important to note that consumers **must be subscribed** to the queue **BEFORE** producers send any messages to it, otherwise they will lose the sent messages before their subscription.


Output::

	{
		"action": "<action>",
		"kind": "<vlan>",
		"data":
		{
			 "id_vlan":<id>,
			 "num_vlan":"<num_vlan>",
			 "id_environment":<environment_id>,
			 "networks_ipv4" : [
				  {
				   "id" : <id>,
				   "ip_formated" : "<oct1>.<oct2>.<oct3>.<oct4>/<block>"
				  }
			 ],
			 "networks_ipv6" : [
				  {
				   "id":<id>,
				   "ip_formated" : "<oct1>.<oct2>.<oct3>.<oct4>.<oct5>.<oct6>.<oct7>.<oct8>/<block>"
				  }
			 ],
			 "description":"<description>"
		}
    }

Features that use the ``QueueManager``::

	Vlan  remove()
	uri: vlan/<id_vlan>/remove/

	Vlan  create_ipv4()
	uri: vlan/v4/create/

	Vlan  create_ipv6()
	uri: vlan/v6/create/

	Vlan  create_acl()
	uri: vlan/create/acl/

	Vlan  create_script_acl()
	uri: vlan/create/script/acl/

	Vlan  create_vlan()
	uri: vlan/create/

	Vlan  criar()
	uri: vlan/<id_vlan>/criar/

Working with Documentation
**************************

If you want to generate documentation, you need the following python modules installed::

	pip install sphinx==1.2.2
	pip install sphinx-rtd-theme==0.1.6
	pip install pytest==2.2.4

Front End
*********

If you want o have a Front End user application to use with Globo NetworkAPI you can install `GloboNetworkAPI WebUI <http://globonetworkapi-webui.readthedocs.org/>`_.



