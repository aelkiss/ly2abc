import ly.document
import ly.music
from sys import argv

header_fields = { 
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

def duration_map(d):
  eighths = d*8
  if eighths > 1:
    return eighths
  else:
    return ""

def ly_globals(g):
  for k in g.find(ly.music.items.KeySignature):
    print(f"K: {pitch_map(k.pitch())}{k.mode()}")
  for t in g.find(ly.music.items.TimeSignature):
    print(f"T: {t.numerator()}/{t.fraction().denominator}")

# def chords:
#   print("Handling chords")

def music(music_assign):
  time_so_far = 0
  for m in music_assign.find(ly.music.items.MusicList,depth=2):
    for n in music_assign.find(ly.music.items.Note):
      # assume we're in 6/8

      if(n.length() > 0):
        print(f"{pitch_map(n.pitch)}{duration_map(n.length())}", end='')
        time_so_far += n.length()
#        print(f"time so far: {time_so_far}")
        if time_so_far*8 % 6 == 0: # barline every 6 beats
          print(" | ",end='')
          if time_so_far*8 % 36 == 0: # newline every 6 measures / 36 beats
            print()
        elif time_so_far*8 % 3 == 0: # split beaming in the middle
          print(" ",end='')

  print("")
  print("")
        


dispatch = {
#    'ppTempo': tempo,
    'global' : ly_globals,
#    'ppChordLine': chords,
    'ppMusicOne': music
}

f=open(argv[1],"r")
d=ly.document.Document(f.read())
m=ly.music.document(d)

for h in m.find(ly.music.items.Header):
  for a in h.find(ly.music.items.Assignment):
    abc_field = header_fields[a.name()]
    print(f"{abc_field}: {a.value().plaintext()}")

for a in m.find(ly.music.items.Assignment,depth=1):
  dispatch.get(a.name(), lambda x: None)(a)

# key signature --> find in global
# time signature --> find in global
# find shortest note --> L
# in ppMusicOne
#    track repeats - open repeat / close repeat
#    MarkupWord Drone -> note
#    UserCommand ppMark -> P: [track ppMarks so far]
#        (or rehearsal mark for release version)
    

