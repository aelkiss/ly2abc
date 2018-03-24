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
flat = Fraction(-1,2)
natural = 0
sharp = Fraction(1,2)

class Key:
  def __init__(self,pitch,mode):
    pass

class NoteContext:
  def __init__(self,sharps=0,unit_length=Fraction(1/8)):
    self.sharps = sharps
    self.unit_length = unit_length

class Note:
  octaves = [ lambda x: x.upper() + ",",
              lambda x: x.upper(),
              lambda x: x.lower(),
              lambda x: x.lower() + "'",
              lambda x: x.lower() + "''",
              lambda x: x.lower() + "'''" ]

  notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

  natural_alters = { flat: "_",
                     natural: "",
                     sharp: "^"}

  sharp_alters = { flat: "_",
                 natural: "=",
                 sharp: ""}

  flat_alters = { flat: "",
                 natural: "=",
                 sharp: "^"}

  circle = [3, 0, 4, 1, 5, 2, 6]

  def __init__(self,pitch,length,context=None):
    self.pitch = pitch
    self.length = length
    self.context = context

  def to_abc(self): 
    return self.octave()(self.note()) + self.duration()

  # private

  def octave(self):
    return Note.octaves[self.pitch.octave]

  def note(self):
    return self.accidental() + Note.notes[self.pitch.note]

  def accidental(self):
    # determine normal disposition of note in the mode
    normal = self.key_alter()
    alter = self.pitch.alter

    # is this one altered?
    if normal == natural: return self.natural_alters[alter]
    elif normal == flat: return self.flat_alters[alter]
    elif normal == sharp: return self.sharp_alters[alter]

  def key_alter(self):
    sharp_order = self.circle.index(self.pitch.note) + 1
    key_sharps = self.context.sharps
    flat_order = sharp_order - 8

    if(key_sharps > 0 and sharp_order <= key_sharps):
      return Fraction(1/2)
    elif(key_sharps < 0 and flat_order >= key_sharps):
      return Fraction(-1/2)
    else:
      return 0


  def duration(self):
    eighths = self.length*8
    prefix = ""
    if eighths.numerator > 1:
      prefix = str(eighths.numerator)

    return prefix + ("/" * int(log2(eighths.denominator)))

header_fields = { 
    'title': 'T',
    'subtitle': 'T',
    'poet': 'C',
    'meter': 'P',
    'tagline': 'N'
}

# def tempo:
#   print("Handling tempo")

key_sharps = None

circle = ['Cb', 'Gb', 'Db', 'Ab', 'Eb', 'Bb', 'F', 'C', 'G', 'D', 'A', 'E', 'B', 'F#', 'C#']
modes = { 'major': 0,
          'mixolydian': -1,
          'dorian': -2,
          'minor': -3 }

def sharps(note,mode):
  return circle.index(note) - 7 + modes[mode]

abc_key_alters = { flat: lambda x: x + "b",
    natural: lambda x: x,
    sharp: lambda x: x + "#" }

abc_pitches = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

def ly_globals(g):
  unit_length = Fraction(1/8)

  for t in g.find(ly.music.items.TimeSignature):
    print(f"M: {t.numerator()}/{t.fraction().denominator}")
    if t.fraction() < 0.75:
      unit_length = Fraction(1/16)

  for k in g.find(ly.music.items.KeySignature):
    global note_context
    note = abc_key_alters[k.pitch().alter](abc_pitches[k.pitch().note]).upper()
    mode = k.mode()
    note_context = NoteContext(sharps(note,mode),unit_length)
    print(f"K: {note}{mode}")

# def chords:
#   print("Handling chords")

def music(music_assign):
  global note_context
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
        print(Note(pitch,n.length(),note_context).to_abc(), end='')
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
