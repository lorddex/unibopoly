#
#   wilbur.py
#
#   Author: Ora Lassila mailto:ora.lassila@nokia.com
#   Copyright (c) 2001-2008 Nokia. All Rights Reserved.
#

import piglet
import iso8601
import re
import os

class DB(object):
    def __init__(self, dbfile, seed=False):
        self.dbfile = dbfile
        self.nodeCache = {}
        self.memberProps = []
        self.home = os.getenv("PIGLET_HOME")
        self.qe = self.makeQueryEngine()
        self.db = piglet.open(dbfile)
        self.type = self['rdf:type']
        self.subprop = self['rdfs:subPropertyOf']
        self.subclass = self['rdfs:subClassOf']
        self.resource = self['rdfs:Resource']
        self.sa = self['owl:sameAs']
        self.reasoner = 0 # self['piglet:Reasoner']
        self.literalParser = LiteralParser(self)
        self.bootstrap()
        (sources, namespaces, triples) = self.seedData()
        if seed:
            for source in set(sources):
                self.load(source, True, True)
        for (prefix, uri) in set(namespaces):
            self.addNamespace(prefix, uri)
        for (s, p, o, temp) in set(triples):
            self.add(s, p, o, 0, temp)
        self.postProcess(0)

    def bootstrap(self): pass

    def postProcess(self, source): pass

    def makeQueryEngine(self):
        return WQL(self)

    def seedData(self):
        if self.home:
            return (["file://%s/website/piglet.rdf" % self.home,
                     "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
                     "http://www.w3.org/2000/01/rdf-schema#",
                     "http://www.w3.org/2002/07/owl#"],
                    [],
                    [])
        else:
            raise Error("No PIGLET_HOME environment variable defined")

    def newMemberProp(self, i):
        prop = self.node("http://www.w3.org/1999/02/22-rdf-syntax-ns#_%d" % (i))
        self.memberProps.append(prop)
        return prop

    def getMemberProp(self, i):
        n = len(self.memberProps) + 1
        if i < n:
            return self.memberProps[i-1]
        elif i == n:
            return self.newMemberProp(i)
        else:
            raise Error("Out-of-sequence member index %d" % (i))
            
    def __getitem__(self, qname):
        n = self.nodeCache.get(qname)
        if not n:
            n = self.node(self.db.expand(qname))
            self.nodeCache[qname] = n
        return n

    def values(self, node, path, reasoner=False):
        if isinstance(path, int):
            return [o for (s, p, o) in self.query(node, path, 0)]
        elif isinstance(path, SpecialPathNode):
            return path.values(self, node, reasoner)
        elif isinstance(path, list):
            return self.values(node, self.qe.fsa(path), reasoner)
        elif isinstance(path, PathFSA):
            collector = Collector(self, path)
            collector.walk(node)
            return list(collector.results)
        elif isinstance(path, str):
            return self.values(node, self.qe.canonicalize(path), reasoner)
        else:
            raise UnsupportedPath(path)

    def related(self, source, path, sink, reasoner=False):
        if isinstance(path, int):
            return self.db.count(source, path, sink, 0)
        elif isinstance(path, SpecialPathNode):
            return path.related(self, source, sink, reasoner)
        elif isinstance(path, list):
            return self.related(source, self.qe.fsa(path), sink, reasoner)
        elif isinstance(path, PathFSA):
            return Reacher(self, path, sink).walk(source)
        elif isinstance(path, str):
            return self.related(source, self.qe.canonicalize(path), sink, reasoner)
        else:
            raise UnsupportedPath(path)

    def query(self, s, p, o, source=0):
        return self.db.query(s, p, o, source)

    def sources(self, s, p, o):
        return self.db.sources(s, p, o)

    def count(self, s, p, o, source=0):
        return self.db.count(s, p, o, source)

    def add(self, s, p, o, source=0, temporary=False):
        return self.db.add(s, p, o, source, 1 if temporary else 0)

    def delete(self, s, p, o, source=0, temporary=False):
        return self.db.delete(s, p, o, source, 1 if temporary else 0)

    def load(self, source, verbose=True, seed=False):
        if isinstance(source, str):
            source = self.node(source)
        return self.db.load(source, 0, 1 if verbose else 0)

    def info(self, node):
        return self.db.info(node)

    def node(self, uri):
        return self.db.node(uri)

    def literal(self, contents, dt=0, language=""):
        return self.db.literal(contents, dt, language)

    def augmentLiteral(self, node, datatype):
        return self.db.augmentLiteral(node, datatype)

    def expand_m3(self, qname):
        tmp = self.db.expand_m3(qname)
        if tmp:
            return tmp
        else:
            return qname

    def expand(self, qname):
        return self.db.expand(qname)

    def abbreviate(self, uri):
        return self.db.abbreviate(uri)

    def addNamespace(self, prefix, uri):
        return self.db.addNamespace(prefix, uri)

    def delNamespace(self, prefix):
        return self.db.delNamespace(prefix)

    def match(self, pattern):
        return self.db.match(pattern)

    def literalValue(self, node, datatype=None):
        if node < 0:
            return self.literalParser.parseLiteral(node, datatype)
        else:
            raise Error("Node %s is not a literal" % self.info(node))

    def translate(self, node, db):
        if node > 0:
            return db.node(self.info(node))
        elif node < 0:
            (string, dt, lang) = self.info(node)
            return db.literal(string, dt, lang)
        else:
            return 0

class WQL:
    specialTokens = ['any', 'members', 'self', 'p-of-o', 'p-of-s']

    def __init__(self, db):
        self.db = db
        self.fsaCache = {}

    def fsa(self, path):
        p = self.canonicalize(path)
        r = repr(p)
        f = self.fsaCache.get(r)
        if f == None:
            f = PathFSA(p)
            self.fsaCache[r] = f
        return f

    def canonicalize(self, path):
        if isinstance(path, list):
            (op, arg, args) = (path[0], path[1], path[2:])
            if op == 'rep*':
                return [op, self.canonicalize(arg)]
            elif op == 'rep+':
                return self.canonicalize(['seq', arg, ['rep*', arg]])
            elif op == 'inv':
                return self.canonicalize(self.invert(arg))
            elif op == 'value':
                return DefaultValue(arg)
            elif op == 'norewrite':
                return self.canonicalize(arg)
            elif op == 'filter':
                return StringFilter(arg)
            elif op in ['seq', 'seq+', 'or']:
                if args:
                    # incomplete!
                    if len(args) > 1:
                        return self.canonicalize([op, arg, [op] + args])
                    else:
                        return [op, self.canonicalize(arg), self.canonicalize(args[0])]
                else:
                    return self.canonicalize(arg)
        elif path in self.specialTokens:
            return SpecialToken(path)
        elif path == 'all':
            return 0
        elif not isinstance(path, str):
            return path
        else:
            raise UnsupportedPath(path)

    def isDefaultValue(self, path):
        return (isinstance(path, DefaultValue)
                or (isinstance(path, list) and path[0] == 'value'))

    def invert(self, path):
        if isinstance(path, list):
            return ([path[0]] +
                    [self.invert(i) for i in path[:0:-1] if not self.isDefaultValue(i)])
        elif isinstance(path, InverseNode):
            return path.node
        elif path == 'self':
            return 'self'
        else:
            return InverseNode(self.canonicalize(path))

class Error(Exception, object): pass

class UnsupportedPath(Error):
    def __init__(self, path):
        super(UnsupportedPath, self).__init__("Unsupported path '%s'" % (path))

class UnknownToken(Error):
    def __init__(self, token):
        super(UnknownToken, self).__init__("Unknown token '%s'" % (token))

class SpecialPathNode:
    def __init__(self, node): self.node = node
    def __repr__(self): return "%s(%s)" % (self.__class__, self.node)

    def values(self, db, node, reasoner=False):
        raise Error("No 'values' method defined for %s" % (self))

    def related(self, db, source, sink, reasoner=False):
        raise Error("No 'related' method defined for %s" % (self))

class InverseNode(SpecialPathNode):
    def values(self, db, node, reasoner=False):
        path = self.node
        if isinstance(path, SpecialToken):
            path = path.node
            if path == 'any':
                return [s for (s, p, o) in db.query(0, 0, node)]
            elif path == 'members':
                results = set()
                for p in self.memberProps(db):
                    v = db.values(node, InverseNode(p), False)
                    if v:
                        results.add(v)
                    else:
                        break
                return list(results)
            elif path == 'p-of-s':
                return [s for (s, p, o) in db.query(0, node, 0)]
            elif path == 'p-of-o':
                return [o for (s, p, o) in db.query(0, node, 0)]
            else:
                raise UnknownToken(path)
        else:
            return [s for (s, p, o) in db.query(0, path, node)]

    def related(self, db, source, sink, reasoner=False):
        return db.related(sink, self.node, source, reasoner)

class DefaultValue(SpecialPathNode):
    def values(self, db, node, reasoner=False):
        return [self.node]

    def related(self, db, source, sink, reasoner=False):
        return (self.node == sink)

class SpecialToken(SpecialPathNode):
    def memberProps(self, db, start=1):
        while True:
            yield db.getMemberProp(start)
            start += 1

    def values(self, db, node, reasoner=False):
        path = self.node
        if path == 'any':
            return [o for (s, p, o) in db.query(node, 0, 0)]
        elif path == 'members':
            results = []
            for p in self.memberProps(db):
                v = db.values(node, p, False)
                if v:
                    results += v
                else:
                    break
            return results
        elif path == 'self':
            return [node]
        elif path == 'p-of-s':
            return [p for (s, p, o) in db.query(node, 0, 0)]
        elif path == 'p-of-o':
            return [p for (s, p, o) in db.query(0, 0, node)]
        else:
            raise UnknownToken(path)

    def related(self, db, source, sink, reasoner=False):
        path = self.node
        if path == 'any':
            return db.db.count(source, path, sink, 0)
        elif path == 'members':
            for p in self.memberProps(db):
                if db.related(source, p, sink, False):
                    return True
            return False
        elif path == 'self':
            return (source == sink)
        elif path == 'p-of-s':
            return db.db.count(source, sink, 0, 0)
        elif path == 'p-of-o':
            return db.db.count(0, sink, source, 0)
        else:
            raise UnknownToken(path)

class PathFilter(SpecialPathNode):
    def match(self, db, node): raise Error("No 'match' method defined for %s" % (self))

    def values(self, db, node, reasoner=False):
        return (node if self.match(db, node) else [])

class StringFilter(PathFilter):
    def __init__(self, node):
        super(StringFilter, self).__init__(node)
        self.re = re.compile(node)

    def match(self, db, node):
        str = db.info(node)
        return self.re.search(str if node > 0 else str[0])

class Walker(object):
    def __init__(self, db, fsa):
        self.db = db
        self.fsa = fsa
        self.states = {}

    def visited(self, node, i):
        if not node in self.states:
            self.states[node] = []
            return False
        else:
            return i in self.states[node]

    def walk(self, node, i=0):
        if not self.visited(node, i):
            self.states[node].append(i)
            state = self.fsa.fsa[i]
            if state.terminal and self.collect(node):
                return True
            if isinstance(node, int):
                for tr in state.transitions:
                    for val in self.db.values(node, tr.input, False):
                        if self.walk(val, tr.index):
                            return True
        return False

class Collector(Walker):
    def __init__(self, db, fsa):
        super(Collector, self).__init__(db, fsa)
        self.results = set()

    def collect(self, node):
        self.results.add(node)
        return False

class Reacher(Walker):
    def __init__(self, db, fsa, sink):
        super(Reacher, self).__init__(db, fsa)
        self.sink = sink
        
    def collect(self, node):
        return (node == self.sink)

class PathFSA:
    def __init__(self, path):
        self.expr = path
        self.inputs = []
        self.states = []
        self.fsa = self.construct()
    def __repr__(self): return "<fsa %s>" % self.expr

    def decorate(self, x):
        if not isinstance(x, list):
            node = set([self.PathNode(x)])
            if not x in self.inputs:
                self.inputs = [x] + self.inputs
            return (node, node, False)
        else:
            op = x[0]
            (first, last, null) = self.decorate(x[1])
            if op == 'seq':
                (first2, last2, null2) = self.decorate(x[2])
                self.addFollowers(last, first2)
                return ((first | first2) if null else first,
                        (last | last2) if null2 else last2,
                        null and null2)
            elif op == 'seq+':
                (first2, last2, null2) = self.decorate(x[2])
                self.addFollowers(last, first2)
                return ((first | first2) if null else first, last | last2, null)
            elif op == 'or':
                (first2, last2, null2) = self.decorate(x[2])
                return (first | first2, last | last2, null or null2)
            elif op == 'rep*':
                self.addFollowers(last, first)
                return (first, last, True)

    def addFollowers(self, f, t):
        for i in f:
            i.follows |= t

    def addState(self, positions):
        for item in self.states:
            if item.positions == positions:
                return self.states.index(item)
        self.states.append(self.TempState(positions))
        return len(self.states)-1

    def construct(self):
        self.addState(self.decorate(['seq', self.expr, None])[0])
        i = 0
        while (i < len(self.states)):
            state = self.states[i]
            for input in self.inputs:
                positions = set()
                for p in state.positions:
                    if p.link is input:
                        positions |= p.follows
                if positions:
                    j = self.addState(positions)
                    state.transitions = [self.Transition(input, j)] + state.transitions
            i += 1
            result = []
            for s in self.states:
                terminal = False
                for n in s.positions:
                    if n.link == None:
                        terminal = True
                        break
                result.append(self.State(terminal, s.transitions[::-1]))
        return result

    class PathNode:
        def __init__(self, link): (self.link, self.follows) = (link, set())
        def __repr__(self): return "<node %s>" % (self.link)
            
    class TempState:
        def __init__(self, positions):
            self.positions = positions
            self.transitions = []

    class Transition:
        def __init__(self, input, index): (self.input, self.index) = (input, index)
        def __repr__(self): return "<trans %s-->%s>" % (self.input, self.index)

    class State:
        def __init__(self, terminal, transitions):
            self.terminal = terminal
            self.transitions = transitions
        def __repr__(self): return "<state %s, %s>" % (self.transitions, self.terminal)

class LiteralParser:
    def __init__(self, db):
        self.db = db
        dts = {'xsd:string':           lambda self, c: c,
               'xsd:boolean':          lambda self, c: self.parseBoolean(c),
               'xsd:float':            lambda self, c: float(c),
               'xsd:double':           lambda self, c: float(c),
               'xsd:dateTime':         lambda self, c: self.parseDateTime(c),
               'xsd:date':             lambda self, c: self.parseDateTime(c, False),
               'xsd:normalizedString': lambda self, c: self.parseNormalizedString(c),
               'xsd:integer':          lambda self, c: int(c),
               'xsd:int':              lambda self, c: int(c) }
        self.datatypes = {}
        for dt in dts:
            self.datatypes[self.db[dt]] = dts[dt]
        self.iso8601 = iso8601.iso8601()

    def parseLiteral(self, literal, datatype):
        (contents, dt, lang) = self.db.info(literal)
        return (self.datatypes.get(datatype or dt, lambda s, c: c))(self, contents)

    def parseBoolean(self, contents):
        if contents == "1" or contents == "true":
            return True
        elif contents == "0" or contents == "false":
            return False
        else:
            raise Error("Illegal xsd:boolean value '%'" % (contents))

    def parseNormalizedString(self, contents):
        # must write this, someday...
        return contents

    def parseDateTime(self, contents, includeTime=True):
        (date, hasTime) = self.iso8601.parse(contents)
        if not date:
            raise Error("Unable parse '%s' as a date" % contents)
        elif includeTime != hasTime:
            raise Error("Parsed time '%s' does not match datatype" % contents)
        else:
            return date
