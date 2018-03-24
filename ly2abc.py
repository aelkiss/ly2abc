import ly.document
import ly.music
from sys import argv
from fractions import Fraction
from math import log2

# key signature --> find in global
# time signature --> find in global
# find shortest note --> L
# in ppMusicOne
#    track repeats - open repeat / close repeat
#    MarkupWord Drone -> note
#    UserCommand ppMark -> P: [track ppMarks so far]
#        (or rehearsal mark for release version)
    

class NoteConverter:
  octaves = [ lambda x: x.upper() + ",",
              lambda x: x.upper(),
              lambda x: x.lower(),
              lambda x: x.lower() + "'",
              lambda x: x.lower() + "''",
              lambda x: x.lower() + "'''" ]

  notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

  natural_alters = { Fraction(-1,2): "_",
                 Fraction(0): "",
                 Fraction(1,2): "^"}


  def __init__(self,pitch,length):
    self.pitch = pitch
    self.length = length

  def to_abc(self): 
    return self.octave()(self.note()) + self.duration()

  def octave(self):
    return NoteConverter.octaves[self.pitch.octave]

  def note(self):
    return self.accidental() + NoteConverter.notes[self.pitch.note]

  def accidental(self):
    return NoteConverter.natural_alters[self.pitch.alter]

  def duration(self):
    eighths = self.length*8
    if eighths > 1:
      return str(eighths)
    elif eighths == 1:
      return ""
    elif eighths.numerator == 1:
      return "/" * int(log2(eighths.denominator))

header_fields = { 
    'title': 'T',
    'subtitle': 'T',
    'poet': 'C',
    'meter': 'P',
    'tagline': 'N'
}

# def tempo:
#   print("Handling tempo")

flat = Fraction(-1,2)
natural = Fraction(0)
sharp = Fraction(1,2)

key_sharps = None

circle = ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#']
modes = { 'major': 0,
          'mixolydian': -1,
          'dorian': -2,
          'minor': -3 }

def sharps(note,mode):
  return circle.index(note) - 7 + modes[mode]

def accidental(note,key_sharps):
  sharp_order = circle.index(note) - 5
  flat_order = sharp_order - 8
  if(key_sharps > 0 and sharp_order <= key_sharps):
    return Fraction(1/2)
  elif(key_sharps < 0 and flat_order >= key_sharps):
    return Fraction(-1/2)
  else:
    return 0


abc_key_alters = { flat: lambda x: x + "b",
    natural: lambda x: x,
    sharp: lambda x: x + "#" }

abc_pitches = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

abc_sharp_alters = { Fraction(-1,2): "_",
               Fraction(0): "=",
               Fraction(1,2): ""}

abc_natural_alters = { Fraction(-1,2): "_",
                 Fraction(0): "",
                 Fraction(1,2): "^"}

abc_flat_alters = { Fraction(-1,2): "",
               Fraction(0): "=",
               Fraction(1,2): "^"}

abc_octaves = [ lambda x: x.upper() + ",",
                lambda x: x.upper(),
                lambda x: x.lower(),
                lambda x: x.lower() + "'",
                lambda x: x.lower() + "''",
                lambda x: x.lower() + "'''" ]

def abc_pitch(p):
  return abc_accidental(p) + abc_pitches[p.note]

def abc_accidental(p):
  # determine normal disposition of note in the mode
  normal = accidental(abc_pitches[p.note],key_sharps)
  # is this one altered?
  if normal == 0:
    return abc_natural_alters[p.alter]
  elif normal == Fraction(-1,2):
    return abc_flat_alters[p.alter]
  elif normal == Fraction(1,2):
    return abc_sharp_alters[p.alter]

def pitch_map(p):
  return abc_octaves[p.octave](abc_pitch(p))

def duration_map(d):
  eighths = d*8
  if eighths > 1:
    return eighths
  else:
    return ""

def ly_globals(g):
  for t in g.find(ly.music.items.TimeSignature):
    print(f"M: {t.numerator()}/{t.fraction().denominator}")
  for k in g.find(ly.music.items.KeySignature):
    global key_sharps
    note = abc_key_alters[k.pitch().alter](abc_pitches[k.pitch().note]).upper()
    mode = k.mode()
    key_sharps = sharps(note,mode)
    print(f"K: {note}{mode}")

# def chords:
#   print("Handling chords")

def music(music_assign):
  time_so_far = 0
  for m in music_assign.find(ly.music.items.MusicList,depth=2):
    last_pitch = None
    for n in music_assign.find(ly.music.items.Note):
      # assume we're in 6/8

      # make the pitch absolute
      pitch = n.pitch
      if last_pitch:
        pitch.makeAbsolute(last_pitch)

      if(n.length() > 0):
        print(f"{pitch_map(pitch)}{duration_map(n.length())}", end='')
        time_so_far += n.length()
#        print(f"time so far: {time_so_far}")
        if time_so_far*8 % 6 == 0: # barline every 6 beats
          print(" | ",end='')
          if time_so_far*8 % 36 == 0: # newline every 6 measures / 36 beats
            print()
        elif time_so_far*8 % 3 == 0: # split beaming in the middle
          print(" ",end='')
      last_pitch = pitch

        

  print("")
  print("")
        


dispatch = {
#    'ppTempo': tempo,
    'global' : ly_globals,
#    'ppChordLine': chords,
    'ppMusicOne': music
}


if __name__ == "__main__":
  f=open(argv[1],"r")
  d=ly.document.Document(f.read())
  m=ly.music.document(d)

  for h in m.find(ly.music.items.Header):
    for a in h.find(ly.music.items.Assignment):
      abc_field = header_fields[a.name()]
      print(f"{abc_field}: {a.value().plaintext()}")

  for a in m.find(ly.music.items.Assignment,depth=1):
    dispatch.get(a.name(), lambda x: None)(a)
