# General Voting System for Party Based Public Elections

This is my final project for college, it is targeted to computerize our current election system over the internet.

I have implemented basic authentication utilizing ID no. and birth date and then a more advanced face recognition based authentication.

This system is not perfect, and it's not supposed to be, as it is my grad project.

The project is built around a cluster of 3 main servers, in a production deployment there would be many clusters to increase decentralization.

The cluster consists of 2 web servers (one for authentication and one for voting) and one cache server (Memcached), the seperation is important to seperate a voter from his vote.

The two web servers run on Django (with uwsgi and nginx as the underlying server infrastructure), the folders in this repository represent the different servers accordingly to their name.

There is little to no configuration needed for the cache server as it is not exposed to the internet, so it is omitted from this repo.

The servers should all be connected with a private network to enable communication with the cache, there is no communication between the servers themselves that is not through the internet.

A domain name is needed for a HTTPS certificate which is required for this system, you can acquire a free one at Freenom. The authentication server is given the index for the domain (@, www) while the voting server gets the vote subdomain.

# Setup

1. Set up a Memcached server and note the private IP address
2. Set up the two web servers (install dependencies, clone git repo and open ports 80 and 443)
3. Insert the configuration files for each server accordingly and get the certificates for your domain
4. Update the nginx configuration with the path to your certificates
5. Update the settings.py file with your domain name, the cache private IP address and a new SECRET_KEY which can be generated using the python secrets library.
6. Migrate the data models into the databases and collect the static documents.
7. Run uWSGI with the script provided either in a virtual terminal (screen) or as a system service.

You should be able to access the site and utilize the admin panel (which should be disabled in production) to insert data.

Note: Make sure to go through the configuration files and replace USER with the username of your system and example.com with your domain. With this configuration it is required that the folder of the server is in the home folder of the user of you system.

# Contact

I understand that the information I put here about this project is not exactly in depth, if you wish you can contact me on Telegram for more details: @G_Afifa

I will be able to supply my project book and explain the deployment details if needed.
