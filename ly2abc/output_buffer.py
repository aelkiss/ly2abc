# NEXT:

# split into BeginningOutputBuffer and OutputBuffer
# remove reset - just construct a new one
# save a reference to the previous output buffer
# use previous buffer for note postfix stuff

class OutputBuffer:
  def __init__(self, outputter, at_beginning = True, previous = None):
    self.outputter = outputter
    self.at_beginning = at_beginning
    self.previous = previous
    self.__reset()

  def next(self):
    self.outputter.save_buffer(self)
    return OutputBuffer(self.outputter,at_beginning = False, previous = self)

  def output_test(self, stuff):
    self.outputter.output(stuff)

  def output_info_field(self, text):
    self.output_line_break()
    self.info_fields.append(text)

  def output_volta(self, text):
    self.volta_bracket = text

  def output_barline(self, text):
    self.barline = text

  def all_output(self):
    return self.reify()

  def reify(self):
    return self.outputter.reify()

  def output_line_break(self):
    self.line_break = True

  def output_beam_break(self):
    self.beam_break = True

  def output_note(self,item):
    if self.note_output:
      raise RuntimeError("called OutputBuffer#output_note a second time before flushing (passed '%s', was '%s')" % (item, self.note_output))
    else:
      self.note_output = item

  def print_buffer(self):
#    import pdb
#    pdb.set_trace()
    if self.at_beginning:
      for item in self.info_fields:
        self.__output(item)
        self.__output("\n")
      if self.barline: self.__output(self.barline)
    else:
      if self.note_output: self.__output(self.note_output)
      if self.beam_break: self.__output(" ")
      if self.barline: self.__output(self.barline)
      if self.line_break: self.__output("\n")
      for item in self.info_fields:
        self.__output(item)
        self.__output("\n")

    if self.volta_bracket: self.__output(self.volta_bracket)

    self.at_beginning = False

  def __reset(self):
    self.note_output = None
    self.line_break = False
    self.beam_break = False
    self.info_fields = []
    self.barline = None
    self.volta_bracket = None

  def __output(self, stuff):
    self.outputter.output(stuff)
