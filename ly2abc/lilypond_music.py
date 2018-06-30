import ly.music.items
import re
import sys
from ly2abc.note import *
from ly.pitch import transpose
from ly2abc.output_buffer import OutputBuffer
from ly2abc.bar_manager import BarManager
from fractions import Fraction

class FilehandleOutputter:
  def __init__(self,fh):
    self.fh = fh
    self.buffers = []

  def output(self,text):
    self.fh.write(text)

  def reify(self):
    for buffer in self.buffers:
      buffer.print_buffer()

  def save_buffer(self,buffer):
    self.buffers.append(buffer)

class LilypondMusic:

  def __init__(self,music,outputter=OutputBuffer(FilehandleOutputter(sys.stdout)),output_assigns=None):
    self.outputter = outputter
    self.note_context = NoteContext()
    self.unit_length = None
    self.music = music
    self.section = None
    self.note_buffer = []
    self.chords = []
    self.old_duration = 0
    self.output_assigns = output_assigns

  def traverse(self,node,handlers,i=0):
    method = handlers.get(type(node))
    if method:
      method(node,handlers)
    else:
      for child in node:
        self.traverse(child,handlers)

  def output_abc(self):
    handlers = {
      ly.music.items.TimeSignature: self.time_signature,
      ly.music.items.KeySignature: self.key_signature,
      ly.music.items.Relative: self.relative,
      ly.music.items.ChordMode: self.chord_mode,
      ly.music.items.Assignment: self.assign,
      ly.music.items.Transpose: self.transpose,
    }
    self.traverse(self.music,handlers)

    self.pass_time()
    self.interpolate_chords()

  def interpolate_chords(self):
    buffers = self.outputter.outputter.buffers
    buffer_index = 0
    while buffers[buffer_index].duration == 0:
      buffer_index += 1

    for (chord,duration) in self.chords:
      if chord: buffers[buffer_index].output_chord(chord)
      passed_time = 0
      while(passed_time < duration):
        passed_time += buffers[buffer_index].duration
        buffer_index += 1
      if passed_time != duration:
        print("WARNING: passed time %s doesn't match duration %s - chord change in middle of note?" % (passed_time,duration))

  def time_signature(self,t,_=None):
    numerator = t.numerator()
    denominator = t.fraction().denominator

    if self.unit_length == None:
      self.bar_manager = BarManager(numerator,denominator,self.outputter)
      self.unit_length = self.default_unit_length(numerator,denominator)
      self.outputter.output_info_field("M: %s" % self.bar_manager.time_signature())
      self.outputter.output_info_field("L: %s" % self.unit_length)
      self.note_context.unit_length = self.unit_length
    else:
      # meter change
      self.bar_manager.set_time_signature(numerator,denominator)

  def key_signature(self,k,_=None):
    key = Key(self.note_context.transposer.transpose(k.pitch()),k.mode())
    self.note_context.sharps = key.sharps()
    self.outputter.output_info_field("K: %s" % (key.to_abc()))


  def transpose(self,node,handlers):
    old_transposer = self.note_context.transposer
    self.note_context.transposer = ly.pitch.transpose.Transposer(node[0].pitch,node[1].pitch)
    for child in node[2:]:
      self.traverse(child,handlers)
    self.note_context.transposer = old_transposer

  def chord_mode(self,node,_=None):
    handlers = {
      ly.music.items.Note: self.chord_note,
      ly.music.items.Skip: self.chord_skip,
      ly.music.items.ChordSpecifier: self.chord_specifier
    }

    self.traverse(node,handlers)

  def chord_note(self,n,_=None):
    pitch = n.pitch.copy()
    self.note_context.transposer.transpose(pitch)
    pitch_map = {
      '': '',
      'is': '#',
      'es': 'b',
      's': '#',
      'f': 'b'
    }
    # need to map pitch to abc chord name - use both nl and english names
    pitchname = pitch.output()
    notename = pitchname[0].upper()
    modifier = pitch_map[pitchname[1:]]
    self.chords.append((notename+modifier,n.length()))

  def chord_specifier(self,n,_=None):
    handlers = {
      ly.music.items.ChordItem: self.chord_item
    }

    self.traverse(n,handlers)

  def chord_item(self,item,_=None):
    if(item.token != ':'):
      (chord,length) = self.chords[-1]
      self.chords[-1] = (chord + item.token, length)

  def chord_skip(self,s,_=None):
    self.chords.append([None,s.length()])

  def assign(self,node,handlers):
    if self.output_assigns == None or node.name() in self.output_assigns:
      for child in node:
        self.traverse(child,handlers)

  def relative(self,r,_=None):
    def note(n,_=None):
      self.last_pitch = n.pitch

    handlers = {
      ly.music.items.Note: note,
      ly.music.items.MusicList: self.music_list,
      ly.music.items.Transpose: self.transpose,
    }

    self.traverse(r,handlers)

  def note(self,n,_=None):
    duration = n.length()
    pitch = n.pitch.copy()
    pitch.makeAbsolute(self.last_pitch)
    self.last_pitch = pitch.copy()
    self.note_context.transposer.transpose(pitch)
    self.print_note(pitch,duration)

  def tie(self,n,_=None):
    self.outputter.output_tie()

  def partial(self,p,_=None):
    duration = p.partial_length()
    self.outputter = self.bar_manager.pass_time(-duration)

  def rest(self,r,_=None):
    duration = r.length()
    self.print_note(None,duration)

  def repeat(self,r,handlers=None):
    if(r.specifier() == 'volta'):
      self.outputter.markup_to_bar()
      if self.outputter.barline == ":|":
        self.bar_manager.manual_bar("::")
      else:
        self.bar_manager.manual_bar("|:")

      self.repeat_count = r.repeat_count()
      for n in r: self.traverse(n,handlers)
      self.outputter.markup_to_bar()
      self.bar_manager.manual_bar(":|")
    elif(r.specifier() == 'unfold'):
      for i in range(0,r.repeat_count()):
        for n in r: self.traverse(n,handlers)
    else:
      sys.stsderr.write("WARNING: Ignoring unhandled repeat specifier %s\n" % r.specifier())

  def alternative(self,a,handlers={}):
    def output_alternative(alt_range,music_list):
      self.outputter.output_volta(" [%s " % alt_range)
      self.traverse(music_list,handlers)
      self.bar_manager.manual_bar(":|]")

    for music_list in a:
      alt_range = "1"
      if self.repeat_count > len(music_list):
        alt_range = "1-%d" % (self.repeat_count - len(music_list) + 1)
      output_alternative(alt_range,music_list[0])

      alternative = self.repeat_count - len(music_list) + 2

      if len(music_list) >= 3:
        for ending in music_list[1:-1]:
          output_alternative(str(alternative),ending)
          alternative += 1

      if len(music_list) >= 2:
        # last ending - would be rather odd not to have this
        self.outputter.output_volta((" [%d ") % alternative)
        self.traverse(music_list[-1],handlers)

    self.repeat_count = None

  def markup(self,node,_=None):
    self.outputter.previous.output_markup("^" + node.plaintext())

  def music_list(self,m,_=None):
    handlers = {
      ly.music.items.Note: self.note,
      ly.music.items.Tie: self.tie,
      ly.music.items.Rest: self.rest,
      ly.music.items.TimeSignature: self.time_signature,
      ly.music.items.KeySignature: self.key_signature,
      ly.music.items.Repeat: self.repeat,
      ly.music.items.Alternative: self.alternative,
      ly.music.items.Command: self.command,
      ly.music.items.UserCommand: self.usercommand,
      ly.music.items.Partial: self.partial,
      ly.music.items.Transpose: self.transpose,
      ly.music.items.Markup: self.markup,
    }

    self.traverse(m,handlers)

  def next_mark(self):
    if not self.section:
      self.section = 'A'
    else:
      self.section = chr(ord(self.section) + 1)
    return self.section

  def usercommand(self,usercommand,handlers):
    if(usercommand.name() == 'ppMark'):
      self.outputter.output_markup("^%s" % self.next_mark())
    else:
      r = re.match(r'ppMark(\w)',usercommand.name())
      if r:
        self.outputter.previous.output_markup("^%s" % r.group(1))
    for n in usercommand:
      self.traverse(usercommand,handlers)

  def command(self,m,_=None):
    def bar():
      bars = {
          "|": "|",
          "||": "||",
          ".|": "[|",
          "|.": "|]",
          ".|:": "|:",
          ":..:": "::",
          ":|.|:": "::",
          ":|.:": "::",
          ":.|.:": "::",
          "[|:":   "|:",
          ":|][|:": "::",
          ":|]": ":|",
          ":|.": ":|",
          }
      self.bar_manager.manual_bar((bars.get(m.next_sibling().plaintext(),'|')))

    def mark():
      if(isinstance(m.next_sibling(),ly.music.items.String)):
        thismark = m.next_sibling().plaintext()
      else:
        thismark = self.next_mark()
      self.outputter.output_markup("^%s" % thismark)

    if(m.token == "\\bar"): bar()
    if(m.token == "\\mark"): mark()

  # private

  def print_note(self,pitch,duration):
    self.pass_time()
    self.outputter.output_note(Note(pitch,duration,self.note_context).to_abc(),duration)
    self.old_duration += duration

  def default_unit_length(self,numerator,denominator):
    if Fraction(numerator,denominator) < Fraction(3,4):
      return Fraction(1,16)
    elif denominator <= 2:
      return Fraction(1,4)
    else:
      return Fraction(1,8)

  def pass_time(self):
    self.outputter = self.bar_manager.pass_time(self.old_duration)
    self.old_duration = 0
