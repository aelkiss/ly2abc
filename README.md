LilyPond to ABC converter using [python-ly](https://pypi.python.org/pypi/python-ly)

Usage: 

* `pipenv install`
* `pipenv run python ly2abc.py myfile.ly`

This is heavily a work in progress. It does not yet handle conversion from
LilyPond for the following features of the ABC specification:

* Repeats of any kind
* Ties or slurs
* Section markers
* Key or meter changes
* Chords
* Tuplets
* Annotations
** (for fakebook, should handle the idiosyncratic multiple-repeat markup)
* Modes besides major, minor, dorian, mixolydian
* Double accidentals
* Decorations
* Grace notes
* Clefs other than treble clef
* Explicit beaming
* Explicit line breaks
* Multi-measure rests
* Modified or explicit key signatures

No support is planned for:

* Lyrics
* Multiple voices

On the LilyPond side, it does not support:

* Music outside a `ppMusicOne` assign
* Key signatures or time signatures outside a `global` assign
* Transposed music sections

To make overrideable:

* Unit length
* Beaming strategy
