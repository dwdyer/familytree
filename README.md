# Family Tree Django Web App

## Python Virtual Environment

This project requires Python 3.3 or later.

```
mkdir ~/virtualenv
virtualenv -p <path_to>/python3 ~/virtualenv/familytree
. ~/virtualenv/familytree/bin/activate
```

Before installing the requirements, ensure the pre-requisites for Pillow (a
Python imaging library) are satisfied. On OS X run the following command to
ensure X11 headers are available (assumes Xcode is installed):

```
xcode-select --install
```

On Ubuntu, install these libraries first to ensure JPEG support is included:

```
sudo apt-get install libfreetype6-dev libjpeg62 libjpeg62-dev libpng12-dev
```

Then install the project-specific Python libraries:

```
pip install -r ~/familytree/requirements.txt
```


## Database Setup (MySQL)

```
CREATE DATABASE familytree CHARACTER SET utf8 COLLATE utf8_general_ci;
GRANT ALL PRIVILEGES ON familytree.* TO 'familytree'@'localhost' \
    IDENTIFIED BY '<db_password>';
```

## Django Settings

```
cp secret_settings.template secret_settings.py
```

Edit `secret_settings.py` to provide your own OpenCage, MapBox and Dropbox API
keys.
