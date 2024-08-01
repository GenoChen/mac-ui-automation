import re
from typing import Any, NamedTuple

from ApplicationServices import (
    AXUIElementGetTypeID,
    AXValueGetType,
    NSPointFromString,
    NSRangeFromString,
    NSRectFromString,
    NSSizeFromString,
    kAXValueCFRangeType,
    kAXValueCGPointType,
    kAXValueCGRectType,
    kAXValueCGSizeType,
)
from CoreFoundation import CFArrayGetTypeID, CFGetTypeID, CFStringGetTypeID


class CGRect(NamedTuple):
    x: float
    y: float
    width: float
    height: float


class CFRange(NamedTuple):
    location: float
    length: int


class CGPoint(NamedTuple):
    x: float
    y: float


class CGSize(NamedTuple):
    width: float
    height: float


class Converter:
    def __init__(self, axuielementclass=None):
        self.app_ref_class = axuielementclass

    def convert_value(self, value):
        if CFGetTypeID(value) == CFStringGetTypeID():
            try:
                return str(value)
            except UnicodeEncodeError:
                return str(value.encode("utf-8"))
        if CFGetTypeID(value) == AXUIElementGetTypeID():
            return self.convert_app_ref(value)
        if CFGetTypeID(value) == CFArrayGetTypeID():
            return self.convert_list(value)
        if AXValueGetType(value) == kAXValueCGSizeType:
            return self.convert_size(value)
        if AXValueGetType(value) == kAXValueCGPointType:
            return self.convert_point(value)
        if AXValueGetType(value) == kAXValueCFRangeType:
            return self.convert_range(value)
        if AXValueGetType(value) == kAXValueCGRectType:
            return self.convert_rect(value)
        else:
            return value

    def convert_list(self, value):
        return [self.convert_value(item) for item in value]

    def convert_app_ref(self, value):
        return self.app_ref_class(ref=value)

    @staticmethod
    def convert_size(value) -> CGSize:
        repr_searched = re.search("{.*}", str(value)).group()
        # CGSize = namedtuple("CGSize", ["width", "height"])
        size = NSSizeFromString(repr_searched)

        return CGSize(size.width, size.height)

    @staticmethod
    def convert_point(value) -> CGPoint:
        repr_searched = re.search("{.*}", str(value)).group()
        # CGPoint = namedtuple("CGPoint", ["x", "y"])
        point = NSPointFromString(repr_searched)

        return CGPoint(point.x, point.y)

    @staticmethod
    def convert_range(value) -> CFRange:
        repr_searched = re.search("{.*}", str(value)).group()
        # CFRange = namedtuple("CFRange", ["location", "length"])
        range = NSRangeFromString(repr_searched)

        return CFRange(range.location, range.length)

    @staticmethod
    def convert_rect(value: Any) -> CGRect:
        repr_searched = re.search("{.*}", str(value)).group()
        # CGRect = namedtuple("CGRect", ["x", "y", "width", "height"])
        rect = NSRectFromString(repr_searched)

        return CGRect(rect.origin.x, rect.origin.y, rect.size.width, rect.size.height)
