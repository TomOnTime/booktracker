all:

install: push

push:
	cp write_awz.py creds.py ~/bin/.

diff:
	diff write_awz.py ~/bin/.
	diff creds.py ~/bin/.
