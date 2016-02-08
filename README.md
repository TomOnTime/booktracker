# booktracker

Track Amazon product codes in Google Cloud Monitoring.


# How to install

Copy write_awz.py to bin.

Create a file called "creds.py" with your creds:

```
AMAZON_ACCESS_KEY =  'yourkey'
AMAZON_SECRET_KEY = 'thesecretkeythatisgenerated'
AMAZON_ASSOC_TAG = 'tagname'
```

NOTE: A gpg-encrypted version of creds.py is in this repo. You can decrypt it if you use "blackbox" (https://github.com/TomOnTime/blackbox) and are an administrator. 

The source code of write_awz.py includes the list of ASINs to collect information about.
