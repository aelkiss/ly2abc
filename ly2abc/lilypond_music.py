import ly.music.items
import re
import sys
from ly2abc.note import *
from ly2abc.output_buffer import OutputBuffer
from ly2abc.bar_manager import BarManager
from fractions import Fraction

class FilehandleOutputter:
  def __init__(self,fh):
    self.fh = fh
    self.last_output = None

  def output(self,text):
    self.fh.write(text)
    self.last_output = text

class LilypondMusic:

  def __init__(self,music,outputter=OutputBuffer(FilehandleOutputter(sys.stdout))):
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

  def output_abc(self):
    handlers = { 
      ly.music.items.TimeSignature: self.time_signature,
      ly.music.items.KeySignature: self.key_signature,
      ly.music.items.Relative: self.relative,
    }
    self.traverse(self.music,handlers)
    # finalize bars at the end
    if self.bar_manager: self.bar_manager.output_breaks()
    self.outputter.flush_buffer()

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
      self.flush_buffer()
      self.bar_manager.set_time_signature(numerator,denominator)

  def key_signature(self,k,_=None):
    key = Key(k.pitch(),k.mode())
    self.note_context.sharps = key.sharps()
    self.outputter.output_info_field("K: %s" % (key.to_abc()))

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
      self.outputter.output_volta(" [%s " % alt_range)
      self.traverse(music_list,handlers)
      self.outputter.flush_buffer()
      self.bar_manager.manual_bar(" :|] ")

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
        self.outputter.output_volta((" [%d ") % alternative)
        self.traverse(music_list[-1],handlers)
        self.outputter.flush_buffer()

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
      ly.music.items.Alternative: self.alternative,
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
      self.outputter.output_info_field("P: %s" % self.section)
      self.section = chr(ord(self.section) + 1)
    else:
      r = re.match(r'ppMark(\w)',usercommand.name())
      if r: 
        self.bar_manager.output_breaks(continuation=True)
        self.outputter.output_info_field("P: %s" % r.group(1))
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
    self.outputter.output_note(Note(pitch,duration,self.note_context).to_abc())
    self.current_duration += duration

  def default_unit_length(self,numerator,denominator):
    if Fraction(numerator,denominator) < Fraction(3,4):
      return Fraction(1,16)
    elif denominator <= 2:
      return Fraction(1,4)
    else:
      return Fraction(1,8)

  def flush_buffer(self):
    self.bar_manager.pass_time(self.current_duration)
    self.current_duration = 0
