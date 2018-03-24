LilyPond to ABC converter using [python-ly](https://pypi.python.org/pypi/python-ly)

Usage: 

* `pipenv install`
* `pipenv run python ly2abc.py myfile.ly`

This is heavily a work in progress. It does not yet handle conversion from
LilyPond for the following features of the ABC specification:

* Rests
* Meters other than 6/8
* Repeats of any kind
* Key or meter changes
* Section markers
* Chords
* Tuplets
* Clefs other than treble clef
* Modes besides major, minor, dorian, mixolydian
* Explicit beaming
* Explicit line breaks
* Double accidentals
* Grace notes
* Decorations
* Annotations
* Modified or explicit key signatures

No support is planned for:

* Lyrics
* Multiple voices

On the LilyPond side, it does not support:

* Music outside a `ppMusicOne` assign
* Key signatures or time signatures outside a `global` assign
* Transposed music sections
