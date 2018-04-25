from fractions import Fraction
from math import log2

flat = Fraction(-1,2)
natural = 0
sharp = Fraction(1,2)

class IdentityTransposer:
  def transpose(self,pitch):
    return pitch

class NoteContext:
  def __init__(self,sharps=0,unit_length=Fraction(1/8)):
    self.sharps = sharps
    self.unit_length = unit_length
    self.transposer = IdentityTransposer()

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
    'composer': 'C',
    'meter': 'P',
    'tagline': 'N',
    'piece': 'N'
}
