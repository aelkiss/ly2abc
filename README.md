LilyPond to ABC converter using [python-ly](https://pypi.python.org/pypi/python-ly)

Usage: 

* `pipenv install`
* `pipenv run python ly2abc.py myfile.ly`

This is heavily a work in progress. It does not yet handle conversion from
LilyPond for the following features of the ABC specification:

* Chords
* Tuplets
* Annotations other than markup above the node
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
* Unfolded repeats inside \chordmode (volta repeats should be OK so long as they match what's in the primary melody line)
* Transposed \chordmode

To make overrideable:

* Unit length
* Beaming strategy


TODO

%%ambitus

BUGS

internal \partial not handled well (Won't fix)
accidentals get printed multiple times in a given measure (see e.g. bassa toscana)
** ending barlines / repeats not on a measure offset
G\_8 clefs for melody not handled

Notes for chord mode
- if we advanced an output buffer and the elapsed time exceeds the duration of the chord... then we need to split output buffers. Can ABC handle chord changes that happen in the middle of a note?

TODO:
- better handle case if chord changes happen in the middle of a note
