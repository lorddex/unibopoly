#
#   iso8601.py
#
#   Author: Ora Lassila mailto:ora.lassila@nokia.com
#   Copyright (c) 2001-2008 Nokia. All Rights Reserved.
#

import datetime
import re

class iso8601:
    patterns = {'iso8601':
                    (("(?P<y>[0-9]{4})-(?P<mo>[0-9]{2})-(?P<d>[0-9]{2})"
                      "(?:T(?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2})"
                      "(?P<z>[-+Z](?:(?P<oh>[0-9]{2}):(?P<om>[0-9]{2}))?)?)?$"),
                     True),
                'exif':
                    (("(?P<y>[0-9]{4}):(?P<mo>[0-9]{2}):(?P<d>[0-9]{2})"
                      "(?:[ ](?P<h>[0-9]{2}):(?P<m>[0-9]{2}):(?P<s>[0-9]{2}))?"),
                     False)}

    def __init__(self):
        self.re = dict()
        self.tz = dict()
        for key in self.patterns:
            (pattern, self.tz[key]) = self.patterns[key]
            self.re[key] = re.compile(pattern)

    def parse(self, string):
        for key in self.re:
            match = self.re[key].match(string)
            if match:
                (y, mo, d, h, m, s) = match.group("y", "mo", "d", "h", "m", "s")
                if not h:
                    return (datetime.date(int(y), int(mo), int(d)),
                            False)
                elif self.tz[key]:
                    (z, oh, om) = match.group("z", "oh", "om")
                    return (datetime.datetime(int(y), int(mo), int(d),
                                              int(h), int(m), int(s), 0,
                                              timezone(0 if z[0] == 'Z' else oh,
                                                       0 if z[0] == 'Z' else om,
                                                       z[0] == '-')),
                            True)
                else:
                    return (datetime.datetime(int(y), int(mo), int(d),
                                              int(h), int(m), int(s), 0, timezone()),
                            True)
        return (None, False)

    def parseToLiteral(self, string, db):
        (date, hasTime) = self.parse(string)
        if date:
            return db.literal(date.isoformat(),
                              db['xsd:datetime' if hasTime else 'xsd:date'], "")
        else:
            return None

class timezone(datetime.tzinfo):
    def __init__(self, oh=0, om=0, negative=False):
        m = (int(oh) if oh else 0) * 60 + (int(om) if om else 0)
        self.offset = datetime.timedelta(minutes=(-m if negative else m))

    def utcoffset(self, dt):
        return self.offset

    def dst(self, dt):
        return None
