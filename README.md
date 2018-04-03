LilyPond to ABC converter using [python-ly](https://pypi.python.org/pypi/python-ly)

Usage: 

* `pipenv install`
* `pipenv run python ly2abc.py myfile.ly`

This is heavily a work in progress. It does not yet handle conversion from
LilyPond for the following features of the ABC specification:

* Ties or slurs
* Section markers
* Chords
* Tuplets
* Annotations
** (for fakebook, should handle the idiosyncratic multiple-repeat markup)
* Modes besides major, minor, dorian, mixolydian
* Double accidentals
* Decorations
* Grace notes
* Clefs other than treble clef
* Multi-measure rests
* Modified or explicit key signatures

No support is planned for:

* Lyrics
* Multiple voices

On the LilyPond side, it does not support:

* Volta repeats that are not on a barline boundary
* Explicit beaming
* Explicit line breaks
* Music outside a `ppMusicOne` assign
* Key signatures or time signatures outside a `global` assign
* Transposed music sections
* Any feature of LilyPond that isn't supported by ABC

To make overrideable:

* Unit length
* Beaming strategy

BUGS

some repeat signs are in the wrong place (see e.g. Egle before D)
some part signs appear to be offset
transpose still isn't handled

