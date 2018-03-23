LilyPond to ABC converter using [python-ly](https://pypi.python.org/pypi/python-ly)

Usage: 

* `pipenv install`
* `pipenv run python ly2abc.py myfile.ly`

This is heavily a work in progress. It does not yet handle:

* Meters other than 6/8
* Notes shorter than an eighth note
* Music outside a `ppMusicOne` assign
* Key signatures or time signatures outside a `global` assign
* Repeats
* Section markers
* Chords
