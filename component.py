class Component:
  def __init__(self, polygon, name):
    self.polygon = polygon
    self.name = name
    self.children = []
    self.depth = 0

  def add_child(self, child):
    self.children.append(child)

  # @property
  # def area(self):
  #   return self.polygon.area

  # @property
  # def intersects(self):
  #   return self.polygon.intersects

  def __lt__(self, other):
    return self.polygon.area < other.polygon.area

  def __str__(self):
    return "%s(%d)" % (self.name, self.polygon.area)

  def __repr__(self):
    return str(self)

  def __unicode__(self):
    return u"?"

