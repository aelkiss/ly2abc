import ly.document
import ly.music
from sys import argv

assignments = { 
    'title': 'T',
    'subtitle': 'T',
    'poet': 'C',
    'meter': 'P',
    'tagline': 'N'
}

# def tempo:
#   print("Handling tempo")

def pitch_map(p):
  return p.output().capitalize()


def ly_globals(g):
  for k in g.find(ly.music.items.KeySignature):
    print(f"K: {pitch_map(k.pitch())}{k.mode()}")
  for t in g.find(ly.music.items.TimeSignature):
    print(f"T: {t.numerator()}/{t.fraction().denominator}")

# def chords:
#   print("Handling chords")

def music(a):
  print("Handling music")

dispatch = {
#    'ppTempo': tempo,
    'global' : ly_globals,
#    'ppChordLine': chords,
    'ppMusicOne': music
}


def process_assignment(a):
  abc_field = assignments[a.name()]
  print(f"{abc_field}: {a.value().plaintext()}")


f=open(argv[1],"r")
d=ly.document.Document(f.read())
m=ly.music.document(d)

for h in m.find(ly.music.items.Header):
  for a in h.find(ly.music.items.Assignment):
    process_assignment(a)

for a in m.find(ly.music.items.Assignment):
  dispatch.get(a.name(), lambda x: None)(a)

# key signature --> find in global
# time signature --> find in global
# find shortest note --> L
# in ppMusicOne
#    track repeats - open repeat / close repeat
#    MarkupWord Drone -> note
#    UserCommand ppMark -> P: [track ppMarks so far]
#        (or rehearsal mark for release version)
    

