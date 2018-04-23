import ly.document
import ly.music
import ly.music.items
import sys
import re
import pdb
from ly2abc.lilypond_music import LilypondMusic

# key signature --> find in global
# time signature --> find in global
# find shortest note --> L
# in ppMusicOne
#    track repeats - open repeat / close repeat
#    MarkupWord Drone -> note
#    UserCommand ppMark -> P: [track ppMarks so far]
#        (or rehearsal mark for release version)


header_fields = { 
    'title': 'T',
    'subtitle': 'T',
    'poet': 'C',
    'composer': 'C',
    'meter': 'P',
    'tagline': 'N',
    'piece': 'N'
}

# def tempo:
#   print("Handling tempo")


if __name__ == "__main__":
  index = 1
  for filename in sys.argv[1:]:
    f=open(filename,"r")
    d=ly.document.Document(f.read())
    m=ly.music.document(d)

    print("X: %d" % (index))
    # automatically break lines for display except where there's a $ character
    print("I: linebreak $")
    index += 1

    for h in m.find(ly.music.items.Header):
      for a in h.find(ly.music.items.Assignment):
        abc_field = header_fields[a.name()]
        print(f"{abc_field}: {a.value().plaintext()}")

    l = LilypondMusic(m)
    l.output_abc()
    # XXX fixme
    l.outputter.reify()

    print()
    print()
