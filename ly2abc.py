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

class BarManager:
  """ provides support for telling when to break beaming, bars, and lines """
  # break beams after this number of beats in the numerator
  beamers = { 
      2:  1,
      3:  3,
      4:  2,
      5:  1,
      6:  3,
      7:  1,
      8:  2,
      9:  3
  }
      
  def __init__(self,numerator,denominator):
    self.elapsed_time = 0
    self.denominator = denominator
    self.numerator = numerator

  def pass_time(self,duration):
    self.elapsed_time += duration

  def line_break(self):
    return self.measures() % 6 == 0

  def beam_break(self):
    return self.beats() % BarManager.beamers[self.numerator] == 0

  def bar_line(self):
    return self.beats() % self.numerator == 0

  def beats(self):
    return self.elapsed_time * self.denominator

  def measures(self):
    return self.elapsed_time * self.denominator / self.numerator

  def time_signature(self):
    return "%s/%s" % (self.numerator,self.denominator)

class Key:
  alters = { flat: "b",
      natural: "",
      sharp: "#" }

  modes = { 'major': 0,
            'mixolydian': -1,
            'dorian': -2,
            'minor': -3 }

  def __init__(self,pitch,mode):
    self.pitch = pitch
    self.mode = mode

  def sharps(self):
    """ Maps the note to the number of sharps in the key.
     0 (C) -> 0; 1 (D) -> 2; 2 (E) -> 4; 3 (F) -> -1; 4 (G) -> 1; 5 (A) -> 3; 6 (B) -> 5
     The +1 / -1 in the calculation is to avoid a special case for F needing to
     be -1 rather than 6 (which is F#) Every half step alteration adds 7 sharps
     (e.g. C# has 7 sharps; Bb has -2 sharps = 2 flats)
    """
    return (self.pitch.note * 2 + 1) % 7 - 1 + 14 * self.pitch.alter + Key.modes[self.mode]

  def to_abc(self):
    return "%s%s %s" % (Note.notes[self.pitch.note],Key.alters[self.pitch.alter],self.mode)

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
    return self.abc_pitch() + self.duration()

  # private

  def abc_pitch(self):
    if self.pitch: return self.octave()(self.note()) 
    else: return 'z'

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
    units = self.length / self.context.unit_length
    prefix = ""
    if units.numerator > 1:
      prefix = str(units.numerator)

    return prefix + ("/" * int(log2(units.denominator)))

header_fields = { 
    'title': 'T',
    'subtitle': 'T',
    'poet': 'C',
    'meter': 'P',
    'tagline': 'N'
}

# def tempo:
#   print("Handling tempo")

def ly_globals(g):
  unit_length = Fraction(1/8)

  for t in g.find(ly.music.items.TimeSignature):
    global bar_manager
    numerator = t.numerator()
    denominator = t.fraction().denominator
    bar_manager = BarManager(numerator,denominator)
    print("M: %s" % bar_manager.time_signature())
    if Fraction(numerator,denominator) < Fraction(3/4):
      unit_length = Fraction(1/16)
    elif denominator <= 2:
      unit_length = Fraction(1/4)

    print("L: %s" % unit_length)

  for k in g.find(ly.music.items.KeySignature):
    global note_context
    key = Key(k.pitch(),k.mode())
    note_context = NoteContext(key.sharps(),unit_length)
    print("K: %s" % (key.to_abc()))

# def chords:
#   print("Handling chords")

def print_note(pitch,duration):
  global note_context, bar_manager

  print(Note(pitch,duration,note_context).to_abc(), end='')
#        print(f"time so far: {time_so_far}")
  if bar_manager.bar_line():
    print(" | ",end='')
    if bar_manager.line_break():
      print()
  elif bar_manager.beam_break():
    print(" ",end='')


def music(music_assign):
  for m in music_assign.find(ly.music.items.MusicList,depth=2):
    last_pitch = None
    for n in music_assign.find((ly.music.items.Note,ly.music.items.Rest)):
      bar_manager.pass_time(n.length())

      pitch = None
      duration = n.length()

      # make the pitch absolute
      if hasattr(n,'pitch'):
        pitch = n.pitch
        if last_pitch: pitch.makeAbsolute(last_pitch)

      if(duration > 0):
        print_note(pitch,duration)

      if hasattr(n,'pitch'): last_pitch = pitch

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
