class OutputBuffer:
  def __init__(self, outputter):
    self.outputter = outputter
    self.at_beginning = True
    self.__reset()

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
    return self.outputter.all_output()

  def output_line_break(self):
    self.line_break = True

  def output_beam_break(self):
    self.beam_break = True

  def output_note(self,item):
    if self.note_output:
      raise RuntimeError("called OutputBuffer#output_note a second time before flushing (passed '%s', was '%s')" % (item, self.note_output))
    else:
      self.note_output = item

  def flush_buffer(self):

    if self.at_beginning:
      for item in self.info_fields:
        self.__output(item)
        self.__output("\n")
      if self.barline: self.__output(self.barline)
    else:
      if self.beam_break: self.__output(" ")
      if self.barline: self.__output(self.barline)
      if self.line_break: self.__output("\n")
      for item in self.info_fields:
        self.__output(item)
        self.__output("\n")

    if self.note_output: self.__output(self.note_output)
    if self.volta_bracket: self.__output(self.volta_bracket)

    self.at_beginning = False
    self.__reset()

  def __reset(self):
    self.note_output = None
    self.line_break = False
    self.beam_break = False
    self.info_fields = []
    self.barline = None
    self.volta_bracket = None

  def __output(self, stuff):
    self.outputter.output(stuff)
