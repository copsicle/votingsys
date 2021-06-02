#!/bin/bash
uwsgi --master --emperor /etc/uwsgi/sites --die-on-term --uid USER --gid www-data
