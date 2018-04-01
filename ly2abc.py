import ly.document
import ly.music
import ly.music.items
import sys
import re
import pdb
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

class FilehandleOutputter:
  def __init__(self,fh):
    self.fh = fh

  def output(self,text):
    self.fh.write(text)

class NoneOutputter:
  def output(self,text):
    pass

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
      
  def __init__(self,numerator,denominator,outputter=NoneOutputter()):
    self.elapsed_time = 0
    self.at_beginning = True
    self.denominator = denominator
    self.numerator = numerator
    self.outputter = outputter
    # don't output a barline at the start of the piece
    self.bar_type = None
    self.broke = False
    self.after_bar_items = []

  def set_time_signature(self,numerator,denominator):
    self.numerator = numerator
    self.denominator = denominator
    self.elapsed_time = 0
    self.output_after_bar("\n", "M: %s\n" % self.time_signature())


  def output_after_bar(self,*items):
    # if right after a break, print it, otherwise wait for right after 
    # the next bar
    if self.broke:
      for item in items:
        self.outputter.output(item)
    else:
      self.after_bar_items += items


  def pass_time(self,duration):
    if duration == 0: return
    self.at_beginning = False
    self.output_breaks()
    if self.bar_type == None: self.bar_type = '|'
    self.elapsed_time += duration
    self.broke = False

  def output_breaks(self,continuation=False):
    if self.at_beginning and self.bar_type == None:
      return

    self.output_inline_breaks()

    # output a continuation marker if we need to have a line break e.g. for a
    # directive but wouldn't otherwise have a line break

    if self.line_break() or continuation:
      self.outputter.output("\n")

  def output_inline_breaks(self):
    if self.broke:
      return

    if self.bar_line():
      self.outputter.output(" %s " % (self.bar_type))
      self.bar_type = "|"
      for item in self.after_bar_items:
        self.outputter.output(item)
      self.after_bar_items = []
      self.broke = True
    elif self.beam_break():
      self.outputter.output(" ")
      self.broke = True

  def manual_bar(self,break_str):
    self.broke = True
    self.outputter.output(break_str)

  def line_break(self):
    return self.beats() != 0 and self.measures() % 6 == 0

  def beam_break(self):
    return self.beats() != 0 and self.beats() % BarManager.beamers[self.numerator] == 0

  def bar_line(self):
    rval=(self.bar_type and self.beats() % self.numerator == 0)
    return rval

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
    'composer': 'C',
    'meter': 'P',
    'tagline': 'N',
    'piece': 'N'
}

# def tempo:
#   print("Handling tempo")

class LilypondMusic:

  def __init__(self,music,outputter=FilehandleOutputter(sys.stdout)):
    self.outputter = outputter
    self.note_context = NoteContext()
    self.unit_length = None
    self.music = music
    self.section = None
    self.note_buffer = []
    self.current_duration = 0

  def traverse(self,node,handlers):
    method = handlers.get(type(node))
    if method: 
      method(node,handlers)
    else:
      for child in node:
        self.traverse(child,handlers)

  def output(self,text):
    self.outputter.output(text)

  def output_abc(self):
    handlers = { 
      ly.music.items.TimeSignature: self.time_signature,
      ly.music.items.KeySignature: self.key_signature,
      ly.music.items.Relative: self.relative,
    }
    self.traverse(self.music,handlers)
    # finalize bars at the end
    if self.bar_manager: self.bar_manager.output_breaks()

  def time_signature(self,t,_=None):
    numerator = t.numerator()
    denominator = t.fraction().denominator

    if self.unit_length == None:
      self.bar_manager = BarManager(numerator,denominator,self.outputter)
      self.unit_length = self.default_unit_length(numerator,denominator)
      self.output("M: %s\n" % self.bar_manager.time_signature())
      self.output("L: %s\n" % self.unit_length)
      self.note_context.unit_length = self.unit_length
    else:
      # meter change
      self.flush_buffer()
      self.bar_manager.set_time_signature(numerator,denominator)

  def key_signature(self,k,_=None):
    key = Key(k.pitch(),k.mode())
    self.note_context.sharps = key.sharps()
    self.output("K: %s\n" % (key.to_abc()))

  def relative(self,r,_=None):
    def note(n,_=None):
      self.last_pitch = n.pitch

    handlers = {
      ly.music.items.Note: note,
      ly.music.items.MusicList: self.music_list,
    }

    self.traverse(r,handlers)

  def note(self,n,_=None):
    duration = n.length()
    pitch = n.pitch.copy()
    pitch.makeAbsolute(self.last_pitch)
    self.print_note(pitch,duration)
    self.last_pitch = pitch

  def partial(self,p,_=None):
    duration = p.partial_length()
    self.bar_manager.pass_time(-duration)

  def rest(self,r,_=None):
    duration = r.length()
    self.print_note(None,duration)

  def repeat(self,r,handlers=None):
    if(r.specifier() == 'volta'):
      if self.bar_manager.bar_type == ":|": self.bar_manager.bar_type = "::"
      else: self.bar_manager.bar_type = "|:"

      self.repeat_count = r.repeat_count()
      for n in r: self.traverse(n,handlers)
      self.flush_buffer()
      self.bar_manager.bar_type = ":|"
    elif(r.specifier() == 'unfold'):
      for i in range(0,r.repeat_count()):
        for n in r: self.traverse(n,handlers)
    else:
      sys.stsderr.write("WARNING: Ignoring unhandled repeat specifier %s\n" % r.specifier())
      
  def alternative(self,a,handlers={}):
    def output_alternative(alt_range,music_list):
      self.outputter.output(" [%s " % alt_range)
      self.traverse(music_list,handlers)
      self.bar_manager.manual_bar(" :|] ")

    # override the ending repeat from the volta, if needed
    self.bar_manager.bar_type = '|'
    self.bar_manager.output_breaks()
    for music_list in a:

      alt_range = "1"
      if self.repeat_count > len(music_list):
        alt_range = "1-%d" % (self.repeat_count - len(music_list) + 1)
      output_alternative(alt_range,music_list[0])

      alternative = self.repeat_count - len(music_list) + 2

#      if len(music_list) > 3:
#        for ending in music_list[1:-1]:
#          output_alternative(str(alternative),ending())
#          alternative += 1

      if len(music_list) >= 2:
        # last ending - would be rather odd not to have this
        self.outputter.output((" [%d ") % alternative)
        self.traverse(music_list[-1],handlers)

    self.repeat_count = None

  def music_list(self,m,_=None):
    def key_signature(k,handlers=None):
      self.flush_buffer()
      self.bar_manager.output_breaks(continuation=True)
      return self.key_signature(k,handlers)

    handlers = {
      ly.music.items.Note: self.note, 
      ly.music.items.Rest: self.rest,
      ly.music.items.TimeSignature: self.time_signature,
      ly.music.items.KeySignature: key_signature,
      ly.music.items.Repeat: self.repeat,
      ly.music.items.Command: self.command,
      ly.music.items.UserCommand: self.usercommand,
      ly.music.items.Partial: self.partial
    }

    self.traverse(m,handlers)
    self.flush_buffer()

  def usercommand(self,usercommand,handlers):
    if(usercommand.name() == 'ppMark'):
      if not self.section: self.section = 'A'
      self.flush_buffer()
      self.bar_manager.output_breaks(continuation=True)
      self.outputter.output("P: %s\n" % self.section)
      self.section = chr(ord(self.section) + 1)
    else:
      r = re.match(r'ppMark(\w)',usercommand.name())
      if r: 
        self.bar_manager.output_breaks(continuation=True)
        self.outputter.output("P: %s\n" % r.group(1))
        self.flush_buffer()
    for n in usercommand:
      self.traverse(usercommand,handlers)

  def command(self,m,_=None):
    if(m.token == "\\bar"):
      bars = {
          "|": " | ",
          "||": " || ",
          ".|": " [| ",
          "|.": " |] ",
          ".|:": " |: ",
          ":..:": " :: ",
          ":|.|:": " :: ",
          ":|.:": " :: ",
          ":.|.:": " :: ",
          "[|:":   " |: ",
          ":|][|:": " :: ",
          ":|]": " :| ",
          ":|.": " :| ",
          }
      self.flush_buffer()
      self.bar_manager.manual_bar((bars.get(m.next_sibling().plaintext(),' | ')))
        
  # private

  def print_note(self,pitch,duration):
    self.flush_buffer()
    self.note_buffer = [Note(pitch,duration,self.note_context).to_abc()]
    self.current_duration += duration
#    self.output(self.note_buffer[0])
  #        print(f"time so far: {time_so_far}")

  def default_unit_length(self,numerator,denominator):
    if Fraction(numerator,denominator) < Fraction(3,4):
      return Fraction(1,16)
    elif denominator <= 2:
      return Fraction(1,4)
    else:
      return Fraction(1,8)

  def flush_buffer(self):
    self.bar_manager.pass_time(self.current_duration)
    for item in self.note_buffer:
      self.output(item)
    self.note_buffer = []
    self.current_duration = 0


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

    LilypondMusic(m).output_abc()

    print()
    print()
