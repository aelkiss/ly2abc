class NoneOutputter:
  def output(self,text):
    pass

  def flush_buffer(self):
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

  def set_time_signature(self,numerator,denominator):
    self.numerator = numerator
    self.denominator = denominator
    self.elapsed_time = 0
    self.outputter.output_info_field("M: %s" % self.time_signature())

  def pass_time(self,duration):
    if duration == 0: return
    self.at_beginning = False
    self.output_breaks()
    self.outputter.flush_buffer()
    if self.bar_type == None: self.bar_type = '|'
    self.elapsed_time += duration
    self.broke = False

  def output_breaks(self):
    if self.at_beginning and self.bar_type == None:
      return

    self.output_inline_breaks()

    if self.line_break(): self.outputter.output_line_break()

  def output_inline_breaks(self):
    if self.broke:
      return

    if self.bar_line():
      self.outputter.output_barline(" %s " % (self.bar_type))
      self.bar_type = "|"
      self.broke = True
    elif self.beam_break():
      self.outputter.output_beam_break()
      self.broke = True

  def manual_bar(self,break_str):
    self.broke = True
    self.outputter.output_barline(break_str)

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
