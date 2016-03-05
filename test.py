import util
from shapely.geometry import Point


print util.angle(Point(0,-1), Point(0,0), Point(0,1))