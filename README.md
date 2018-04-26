LilyPond to ABC converter using [python-ly](https://pypi.python.org/pypi/python-ly)

Usage: 

* `pipenv install`
* `pipenv run python ly2abc.py myfile.ly`

This is heavily a work in progress. It does not yet handle conversion from
LilyPond for the following features of the ABC specification:

* Chords
* Tuplets
* Annotations
* Modes besides major, minor, dorian, mixolydian
* Double accidentals
* Decorations
* Grace notes
* Clefs other than treble clef
* Multi-measure rests
* Modified or explicit key signatures
* Suggested drone (from ppile markup) --> include via %%text in the same place as midi directives?

No support is planned for:

* Lyrics
* Multiple voices

On the LilyPond side, it does not support:

* Volta repeats that are not on a barline boundary
* Explicit beaming
* Explicit line breaks
* Any feature of LilyPond that isn't supported by ABC

To make overrideable:

* Unit length
* Beaming strategy

BUGS

internal \partial not handled well
missing closing repeat on tamrett, ly bens

IMMEDIATE TODO

handle drone specified as markup
handle (3) specified as markup
