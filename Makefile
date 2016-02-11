all:

install: push

FILES=awzconfig.py  creds.py  dump_asin_timeseries.py  gmonitor.py  write_awz.py

push:
	cp $(FILES) ~/bin/.

diff:
	for i in $(FILES) ; do diff $$i ~/bin/. ; done
