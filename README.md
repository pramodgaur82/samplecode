### VPS Setup Instructions

1. Set up nameservers for domain, principally the A record https://www.digitalocean.com/community/tutorials/how-to-set-up-a-host-name-with-digitalocean

2. Spool up VPS

3. Secure VPS https://www.digitalocean.com/community/tutorials/initial-server-setup-with-ubuntu-16-04
	- Add SSH keys
	- Add new user
	- Disable password login
	- Disable root login
	- Enable UFW firewall

4. Generate SSH key and add to GitHub

5. Install prerequisites

		sudo apt-get install pkg-config build-essential python-dev apache2 python-virtualenv python-pip libffi6 libffi-dev libapache2-mod-wsgi

6. Clone site repo

2. Make a virtualenv and activate it

		virtualenv demo
		source demo/bin/activate

3. Install requirements

		pip --no-cache-dir install -r requirements.txt 

	`--no-cache-dir` helps avoid out of memory errors on low RAM servers. 

4. Run `python db_create.py`
5. Run the server 

		python run.py

6. Go to website [http://localhost:8000](http://localhost:8000)

### Set up apache

Write the site conf file:

		<VirtualHost *:80>
		    ServerName meguk2017.com

		    WSGIDaemonProcess meguk2017.com user=www-data group=www-data threads=5
		    WSGIScriptAlias / /meguk2017.com/main/app.wsgi
		    WSGIProcessGroup meguk2017.com
		    Alias /static /meguk2017.com/main/app/static

		    <Directory /meguk2017.com/main/app/static>
		        Require all granted
		    </Directory>

		    <Directory /meguk2017.com/main>
		        <Files app.wsgi>
		                #Require all granted
		                Require ip 82.6.151.105
		        </Files>
		    </Directory>
		</VirtualHost>

### Database scripts

See [http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database](http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database)

### Helpful links

- Login system, good overview: http://exploreflask.com/en/latest/users.html
- More login: https://blog.openshift.com/use-flask-login-to-add-user-authentication-to-your-python-application/
- More login: https://realpython.com/blog/python/introduction-to-flask-part-2-creating-a-login-page/
- Also see User class: http://stackoverflow.com/questions/12075535/flask-login-cant-understand-how-it-works
- Great tutorial: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

### Sending mail

On Mac OS, see 

- http://www.developerfiles.com/how-to-send-emails-from-localhost-mac-os-x-el-capitan/
- http://stackoverflow.com/questions/26447316/mac-os-x-10-10-yosemite-postfix-sasl-authentication-failed

On Linux/VPS, see

- https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-postfix-as-a-send-only-smtp-server-on-ubuntu-16-04

Also follow directions on setting up SPF records and DKIM

### Renewing certificate

The HTTPS certificate needs to be renewed every 90 days. Should be easy to do

	sudo letsencrypt renew

### Limiting numbers

`config.LIMIT_DINNER` and `config.LIMIT_WAITLIST` impose automatic limits on dinner and conference registration. 

After the number of people who have selected 'intends dinner' exceeds `LIMIT_DINNER`

- The dinner checkbox will be hidden from the registration form (also disabling the dietary requirements dropdown)
- The dinner checkbox will be hidden from the user's account page _unless they are already attending the dinner_ which means that users can always opt out of the dinner. Similarly, if an administrator opts someone into the dinner, the checkbox will then appear for the user. Once conference editing is turned off, all users will see a readonly checkbox showing their dinner status

After the number of people in the system exceeds 250

- The registration page will display a warning about the conference oversubscribed
- Users who log in will see a message saying that they are on the waitlist and not attending the conference

For simplicity and to integrate with the existing system, waitlisting starts after the number of people in the system exceeds 250
