#!/usr/bin/python

"""
Semantic Information Broker for M3 Smart Spaces.

Copyright Nokia 2008
"""

from SIBConnectivity import TCPListener
from SIBConnectivity import LISTENING_SOCKETS, LISTENING_SOCKETS_LIST
from sys import platform, exit
import resource

import threading
import time
import cStringIO
import Queue
from rdfplus import DB
from optparse import OptionParser
import re
from xml.sax import make_parser, ContentHandler, SAXException
import uuid

# Dictionary of ongoing subscriptions
# Shared with all subscriptions
# Acquire semaphore "reactive_sessions" to access
# Key is session_id, value is Queue.Queue() instance
# used by the session to receive SIB internal messages

# Usage:
#   REACTIVE_SESSIONS_TABLE[SESSION_ID].put((op, arg, addr))
#   Two kinds of tuples
#    ("stop", None, None): stop reactive session
#    ("send", result, None): send result string to Node
REACTIVE_SESSIONS_TABLE = {}
REACTIVE_SESSIONS = threading.Lock()

# Flags for subscriptions that are handling results
# Should be checked before unsetting the msg_queue_event
# Key is (space, tr_id)
# value is boolean
PENDING_SUBSCRIPTION_TABLE = {}
PENDING_SUBSCRIPTION = threading.Lock()

MEMBER_SET_LOCK = {}
MEMBER_SET = {}

# Thread-safe queues for internal messaging
# connection handlers put in operation request tuples
# of form (op, args, return_addr)
# args and return_addr may be None
# op = assert | query | retract
ASSERT_QUEUE = {}
QUERY_QUEUE = {}
msg_queue_event = {}

RDFSTORE = {}
RDFSTORELOCK = {}

SPACES = set([])

WQL_WORDS = ['seq','seq+','or','rep*','rep+','inv','value','norewrite',
             'filter','any','members','p-of-s','p-of-o','self']

# Constants for status codes
M3_SUCCESS = "m3:Success"
M3_SIB_NOTIFICATION_RESET = "m3:SIB.Notification.Reset"
M3_SIB_NOTIFICATION_CLOSING = "m3:SIB.Notification.Closing"
M3_SIB_ERROR = "m3:SIB.Error"
M3_SIB_ERROR_ACCESS_DENIED = "m3:SIB.Error.AccessDenied"
M3_SIB_FAILURE_OUT_OF_RESOURCES = "m3:SIB.Failure.OutOfResources"
M3_SIB_FAILURE_NOT_IMPLEMENTED = "m3:SIB.Failure.NotImplemented"

M3_KP_ERROR = "m3:KP.Error"
M3_KP_ERROR_REQUEST = "m3:KP.Error.Request"
M3_KP_ERROR_MESSAGE_INCOMPLETE = "m3:KP.Error.Message.Incomplete"
M3_KP_ERROR_MESSAGE_SYNTAX = "m3:KP.Error.Message.Syntax"


def expand(space, uri):
    """Helper function to expand qnames.
    Returns the expanded URI, or if expansion was unsuccesful,
    return the original value. NOTE: ASSUMES THAT THE RDFSTORE
    IS PROPERLY LOCKED!"""
    uri_exp = RDFSTORE[space].expand_m3(uri)
    # print "EXPAND: expanded uri", uri
    # print "Got", uri_exp
    if uri_exp:
        return uri_exp
    else:
        return uri

def to_string_triple(space, int_list):
    """Helper function to map piglet triples (in ints) to
    strings. Returns a list of tuples ((s_str, p_str, o_str), lit)
    where lit is True if the string represents a literal.
    NOTE: ASSUMES THAT THE RDFSTORE IS PROPERLY LOCKED!"""
    str_list = []
    for i in int_list:
        triple, ids = i
        s_int, p_int, o_int = triple
        s_str = RDFSTORE[space].info(s_int)
        p_str = RDFSTORE[space].info(p_int)
        
        if o_int < 0:
            o_str = RDFSTORE[space].info(o_int)[0]
            lit = True
        elif o_int > 0:
            o_str = RDFSTORE[space].info(o_int)
            lit = False
        str_list.append((((s_str, p_str, o_str), lit), ids))
    return str_list

def to_string_node(space, int_list):
    """Helper function to map piglet node & lit ints to
    strings. Returns a list of tuples (node, lit)
    where lit is True if the string represents a literal.
    NOTE: ASSUMES THAT THE RDFSTORE IS PROPERLY LOCKED!"""
    str_list = []
    for i in int_list:
        if i < 0:
            str_list.append((RDFSTORE[space].info(i)[0], True))
        elif i > 0:
            str_list.append((RDFSTORE[space].info(i), False))
    return str_list

def to_string_id(space, int_list):
    """Helper function to map piglet node & lit ints to
    strings. Returns a list of strings where the strings
    represent a triple id. 
    NOTE: USE ONLY FOR TRIPLE IDS!
    NOTE: ASSUMES THAT THE RDFSTORE IS PROPERLY LOCKED!"""
    str_list = []
    for i in int_list:
        str_list.append(RDFSTORE[space].info(i))
    return str_list
        
class SIB_main:
    """ The main class of SIB. Starts the scheduler and network listeners"""
    
    def __init__(self, address, tcp_port, discoveryB):
        #signal.signal(signal.SIGINT, SIGINTHandler)
        self.tcp_port = tcp_port
        self.discoveryB = discoveryB
        self.address = address

    def start(self):
        "Start the SIB"
        
        print SPACES, " running at port ", self.tcp_port
        if self.discoveryB:
            import pybonjour
            for ssp in SPACES:
                dnssRef = pybonjour.DNSServiceRegister(name = ssp,
                                                       regtype = "_kspace._tcp",
                                                       port = self.tcp_port)
            print "Registered mDNS info"

        tcplistener = TCPListener(self.address,
                                  self.tcp_port,
                                  "TCP",
                                  SIBRequestHandler)
        tcplistener.setDaemon(True)
        tcplistener.start()

        # Start other listeners here

        while True:
            cmd = raw_input("SIB %s>"%str(SPACES))
            if cmd == "exit" or cmd == "quit":
                global LISTENING_SOCKETS_LIST
                LISTENING_SOCKETS.acquire()
                print "Closing sockets: ", LISTENING_SOCKETS_LIST
                for i in LISTENING_SOCKETS_LIST:
                    i.close()
                    print "Closed ", i
                    #del i
                LISTENING_SOCKETS_LIST = []
                print LISTENING_SOCKETS_LIST
                LISTENING_SOCKETS.release()
                break
            elif cmd == "subs":
                REACTIVE_SESSIONS.acquire()
                for i in REACTIVE_SESSIONS_TABLE:
                    print i
                REACTIVE_SESSIONS.release()
            elif cmd == "clear":
                for space in SPACES:
                    RDFSTORELOCK[space].acquire()
                    triples = RDFSTORE[space].query(0, 0, 0)
                    print "Deleting triples:"
                    for i in triples:
                        s, p, o = i
                        print i
                        RDFSTORE[space].delete(s, p, o)
                    triples = RDFSTORE[space].query(0, 0, 0)
                    print "Triples in SS:", triples
                    RDFSTORELOCK[space].release()
                    

            elif cmd == "help" or cmd == "?":
                print "Available commands:"
                print "quit or exit: closes the SIB (and all smart spaces managed by it)"
                print "subs: lists subscriptions in the spaces managed by SIB"
                print "clear: clear the contents of all spaces managed by SIB"
                print "help or ?: prints this help"
                    
            
class TransactionHandler:
    """Base class for code handling different sessions. Subclassed
    in InsertHandler, RemoveHandler, UpdateHandler, QueryHandler and
    SubscribeHandler. Each transaction should be handled
    by a separate instance of a subclass of TransactionHandler"""

    def __init__(self, conn, array):
        self.int_msg_rep = array
        self.n_id = array["node_id"]
        self.tr_id = array["transaction_id"]
        self.conn = conn


    def _encode(self, results):
        """Internal. Encodes the results as M3-rdf.
        results: a list of tuples (((s, p, o), literal?),[t_id1, t_id2])
        where s, p, o are strings, literal? is True if o is literal
        and t_idN are triple ids pointing to the triple"""
        tmp = ["<triple_list>"]
        for t in results:
            triple, ids = t
            tmp.append('<triple>')
            # tmp.extend(['<triple_id>%s</triple_id>'%str(i) for i in ids])
            spo, litp = triple
            s, p, o = spo
            if not litp:
                objtype = 'URI'
            else:
                objtype = 'literal'
            tmp.append('<subject>%s</subject>'%str(s))
            tmp.append('<predicate>%s</predicate>'%str(p))
            tmp.append('<object type = "%s">'%str(objtype))
            tmp.append('%s</object></triple>'%str(o))
        tmp.append('</triple_list>')
        return "".join(tmp)
        
        
    def handle(self):
        "Virtual method. Provide your own implementation in a subclass"
        pass

class JoinHandler(TransactionHandler):
    "Handle a single JOIN transaction"
    def _create_cnf(self, status):
        "Create a confirmation message for JOIN"
        xml_msg = ""
        tmp = ["<SSAP_message><transaction_type>",
               "JOIN", "</transaction_type>",
               "<message_type>CONFIRM</message_type>"]
        tmp.extend(["<transaction_id>", self.tr_id, "</transaction_id>"])
        tmp.extend(["<node_id>", self.n_id, "</node_id>"])
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(['<parameter name = "status">',
                    status, '</parameter></SSAP_message>'])
        return xml_msg.join(tmp)
        
    def handle(self):
        """Skeleton for proper join process. Accepts if the space
        exists in the SIB."""
        space_id = self.int_msg_rep["space_id"]
        if space_id in SPACES:
            MEMBER_SET_LOCK[space_id].acquire()
            MEMBER_SET[space_id].add(self.int_msg_rep["node_id"])
            MEMBER_SET_LOCK[space_id].release()

            msg = self._create_cnf(M3_SUCCESS)
            print "Node", self.int_msg_rep["node_id"]
            print "joined the smart space", space_id
        else:
            msg = self._create_cnf(M3_SIB_ERROR)
        self.conn.send(msg)
        self.conn.close()

class LeaveHandler(TransactionHandler):
    "Handle a single LEAVE transaction"
    def _create_cnf(self, status):
        xml_msg = ""
        tmp = ["<SSAP_message><transaction_type>",
               "LEAVE", "</transaction_type>",
               "<message_type>CONFIRM</message_type>"]
        tmp.extend(["<transaction_id>", self.tr_id, "</transaction_id>"])
        tmp.extend(["<node_id>", self.n_id, "</node_id>"])
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(['<parameter name = "status">',
                    status, '</parameter></SSAP_message>'])
        return xml_msg.join(tmp)
        
    def handle(self):
        """Skeleton for proper leave process. Accepts if the space
        exists in the SIB."""
        space_id = self.int_msg_rep["space_id"]
        if space_id in SPACES:
            msg = self._create_cnf(M3_SUCCESS)
            self.conn.send(msg)
            self.conn.close()
            MEMBER_SET_LOCK[space_id].acquire()
            MEMBER_SET[space_id].remove(self.int_msg_rep["node_id"])
            MEMBER_SET_LOCK[space_id].release()
        else:
            msg = self._create_cnf(M3_KP_ERROR_MESSAGE_SYNTAX)
            self.conn.send(msg)
            self.conn.close()

class InsertHandler(TransactionHandler):
    "Handle a single INSERT transaction"
    def __init__(self, conn, array):
        TransactionHandler.__init__(self, conn, array)
        self.triples = array["insert_graph"]
    
    def _create_cnf(self, tr_id, status, node_id, bnodes):
        "Internal. Create a INSERT CONFIRM message."
        tmp = ["<SSAP_message><transaction_type>", "INSERT",
               "</transaction_type>", "<message_type>CONFIRM</message_type>"]
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        tmp.extend(["<node_id>", node_id, "</node_id>"])
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(['<parameter name = "status">%s'%status, '</parameter>'])
        tmp.extend(['<parameter name = "bnodes">', '<urilist>'])
        tmp.extend(['<uri tag = "%s">%s</uri>'%i for i in bnodes.items()])
        tmp.extend(['</urilist>', '</parameter>', '</SSAP_message>'])
        return ''.join(tmp)
    
    def handle(self):
        "Process a single Insert transaction"
        debug(3, "INTERNAL. Handle proactive session.", self)
        # Implement multiple triples parameters in single msg
        # later if needed! self.triples is currently a list of
        # 1 element, might be longer later on

        # print "INSERT: ", self.triples
        all_triples = []
        bnodes = {}
        for t in self.triples:
            ttype, pl = t
            if ttype.lower() == "rdf-m3":
                parsed_triples = []
                m3h = M3RDFHandler(parsed_triples, bnodes)
                parser = make_parser()
                parser.setContentHandler(m3h)
                try:
                    parser.parse(cStringIO.StringIO(str(pl)))
                except SAXException:
                    print "Syntax error in triples in transaction %s, discarding." % self.tr_id
                    if not "confirm" in self.int_msg_rep\
                           or self.int_msg_rep["confirm"].lower() == "true":
                        cnf = self._create_cnf(self.tr_id,
                                               M3_KP_ERROR_MESSAGE_SYNTAX,
                                               self.n_id, bnodes)
                        self.conn.send(cnf)
                        self.conn.close()
                        return
                    else:
                        return
                # print "INSERT: parsed triples", parsed_triples
                all_triples.append(("rdf-m3", parsed_triples))
                # print "INSERT: got triples:", parsed_triples
        if not "confirm" in self.int_msg_rep\
               or self.int_msg_rep["confirm"].lower() == "true":
            q = Queue.Queue(1)
            ASSERT_QUEUE[self.int_msg_rep["space_id"]].put(("assert_confirm",
                                                            (self.n_id, 
                                                             self.tr_id,
                                                             all_triples),
                                                            q))
            msg_queue_event[self.int_msg_rep["space_id"]].set()
            op, arg, t_ids = q.get()
            cnf = self._create_cnf(self.tr_id, arg, self.n_id, bnodes)
            self.conn.send(cnf)
            self.conn.close()
            
        else:
            # print "Put insert req to assert queue"
            ASSERT_QUEUE[self.int_msg_rep["space_id"]].put(("assert",
                                                            (self.n_id,
                                                             self.tr_id,
                                                             all_triples),
                                                            None))
            msg_queue_event[self.int_msg_rep["space_id"]].set()
        

class RemoveHandler(TransactionHandler):
    "Class to handle a single REMOVE transaction"
    def __init__(self, conn, array):
        TransactionHandler.__init__(self, conn, array)
        self.rm_list = []
        self.rm_list_tmp = []
        # print "REMOVE:", array["remove_graph"]
        for r in array["remove_graph"]:
            pl_t, pl = r
            parser = make_parser()
            rh = M3RDFHandler(self.rm_list_tmp, {})
            parser.setContentHandler(rh)
            parser.parse(cStringIO.StringIO(str(pl)))
            self.rm_list.extend(self.rm_list_tmp)

    def _create_cnf(self, tr_id, node_id, status = M3_SUCCESS):
        "Create a REMOVE CONFIRM message"
        tmp = ["<SSAP_message><transaction_type>",
               "REMOVE", "</transaction_type>",
               "<message_type>CONFIRM</message_type>"]
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        tmp.extend(["<node_id>", node_id, "</node_id>"])
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(['<parameter name="status">', status,
                    '</parameter>', '</SSAP_message>'])
        return ''.join(tmp)
    
    def handle(self):
        "Handle a REMOVE transaction"
        debug(3, "Handling Remove transaction", self)
        if not "confirm" in self.int_msg_rep\
               or self.int_msg_rep["confirm"].lower() == "true":
            q = Queue.Queue(1) 
            ASSERT_QUEUE[self.int_msg_rep["space_id"]].put(("retract_confirm",
                                                            (self.n_id,
                                                             self.tr_id,
                                                             self.rm_list),
                                                            q))
            msg_queue_event[self.int_msg_rep["space_id"]].set()
            op, result  = q.get()
            cnf = self._create_cnf(self.tr_id, self.n_id, result)
            self.conn.send(cnf)
            self.conn.close()
            
        else:
            ASSERT_QUEUE[self.int_msg_rep["space_id"]].put(("retract",
                                                            (self.n_id,
                                                             self.tr_id,
                                                             self.rm_list),
                                                            None))
            msg_queue_event[self.int_msg_rep["space_id"]].set()

        

class UpdateHandler(TransactionHandler):
    def __init__(self, conn, array):
        TransactionHandler.__init__(self, conn, array)
        self.rem_triples = array["remove_graph"]
        self.ins_triples = array["insert_graph"]
        

    def _create_cnf(self, tr_id, node_id, bnodes, status):
        "Create a UPDATE CONFIRM message"
        tmp = ["<SSAP_message><transaction_type>",
               "UPDATE", "</transaction_type>",
               "<message_type>CONFIRM</message_type>"]
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        tmp.extend(["<node_id>", node_id, "</node_id>"])
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(['<parameter name = "status">%s</parameter>'%status])
        tmp.extend(['<parameter name = "bnodes">', '<urilist>'])
        tmp.extend(['<uri tag = "%s">%s</uri>'%i for i in bnodes.items()])
        tmp.extend(['</urilist>', '</parameter>', '</SSAP_message>'])
        return ''.join(tmp)
    
    def handle(self):
        "Process a single Update transaction"
        debug(3, "INTERNAL. Handle update session.", self)
        all_ins_triples = []
        bnodes = {}
        for t in self.rem_triples:
            # print "UPDATE: unpacking unparsed triples: ", t
            ttype, pl = t
            if ttype.lower() == "rdf-m3":
                rem_triples = []
                m3h = M3RDFHandler(rem_triples, {})
                parser = make_parser()
                parser.setContentHandler(m3h)
                try:
                    parser.parse(cStringIO.StringIO(str(pl)))
                except SAXException:
                    print "Syntax error in triples in transaction %s, discarding." % self.tr_id
                    if not "confirm" in self.int_msg_rep\
                           or self.int_msg_rep["confirm"].lower() == "true":
                        cnf = self._create_cnf(self.tr_id,
                                               M3_KP_ERROR_MESSAGE_SYNTAX,
                                               self.n_id)
                        self.conn.send(cnf)
                        self.conn.close()
                        return
                    else:
                        return
            else:
                print "Content encoding", ttype, "not supported!"

        for t in self.ins_triples:
            # print "UPDATE: unpacking unparsed triples: ", t
            ttype, pl = t
            if ttype.lower() == "rdf-m3":
                bnodes = {}
                ins_triples = []
                m3h = M3RDFHandler(ins_triples, bnodes)
                parser = make_parser()
                parser.setContentHandler(m3h)
                try:
                    parser.parse(cStringIO.StringIO(str(pl)))
                except SAXException:
                    print "Syntax error in triples in transaction %s, discarding." % self.tr_id
                    if not "confirm" in self.int_msg_rep\
                           or self.int_msg_rep["confirm"].lower() == "true":
                        cnf = self._create_cnf(self.tr_id,
                                               M3_KP_ERROR_MESSAGE_SYNTAX,
                                               self.n_id)
                        self.conn.send(cnf)
                        self.conn.close()
                        return
                    else:
                        return
                # print "INSERT: parsed triples", parsed_triples
                all_ins_triples.append(("rdf-m3", ins_triples))
            else:
                print "Content encoding", ttype, "not supported!"

        if not "confirm" in self.int_msg_rep\
               or self.int_msg_rep["confirm"].lower() == "true":
            q = Queue.Queue(1)
            ASSERT_QUEUE[self.int_msg_rep["space_id"]].put(("update_confirm",
                                                            ((self.n_id, 
                                                              self.tr_id,
                                                              rem_triples),
                                                             (self.n_id, 
                                                              self.tr_id,
                                                              all_ins_triples)),
                                                            q))
            msg_queue_event[self.int_msg_rep["space_id"]].set()
            op, arg, rem, ins = q.get()
            cnf = self._create_cnf(self.tr_id, self.n_id, bnodes, arg)
            # print "UPDATE: sending confirmation:"
            # print cnf
            self.conn.send(cnf)
            self.conn.close()
            # print "UPDATE: sent confirmation"
        else:
            ASSERT_QUEUE[self.int_msg_rep["space_id"]].put(("update",
                                                            ((self.n_id, 
                                                              self.tr_id,
                                                              all_rem_triples),
                                                             (self.n_id, 
                                                              self.tr_id,
                                                              all_ins_triples)),
                                                            None))
            msg_queue_event[self.int_msg_rep["space_id"]].set()

class SubscribeHandler(TransactionHandler):
    "Class for handling a single SUBSCRIBE transaction"
    # Should maybe be refactored to several classes
    # based on the different behavior for different options
    # At least for different termination conditions

    def __init__(self, conn, array):
        TransactionHandler.__init__(self, conn, array)
        self.sub_id = ""
        self.query_type = array["type"].lower()
        self.supported_query_types = ["wql-values", "rdf-m3", 
                                      "wql-related", "wql-istype", 
                                      "wql-nodetypes", "wql-issubtype"]

        self.wql_query_types = ["wql-values", "wql-related", "wql-istype", 
                                "wql-nodetypes", "wql-issubtype"]

        if self.query_type in self.wql_query_types:
            self.query = {}
            parser = make_parser()
            wql_mh = WqlHandler(self.query)
            parser.setContentHandler(wql_mh)
            parser.parse(cStringIO.StringIO(str(array["query"])))
        elif self.query_type == "rdf-m3":
            self.query = []
            pq_mh = M3RDFHandler(self.query, {})
            parser = make_parser()
            parser.setContentHandler(pq_mh)
            parser.parse(cStringIO.StringIO(str(array["query"])))
            # print "SUBSCRIBE: parsed query:", self.query
        else:
            print "UNSUPPORTED QUERY TYPE (WQL AND RDF-M3 SUPPORTED)"
            # Raise exception
        if "one_response" in array and array["one_response"].lower() == "true":
            self.one_result = True
        else:
            self.one_result = False

    ####################################
    #
    # Response message generators
    #
    ####################################

    def _create_header(self, n_id, tr_id):
        "Internal. Create the header (invariant part) of return messages"
        tmp = ["<SSAP_message><node_id>", n_id, "</node_id>"]
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        return tmp

    def _create_cnf(self, n_id, tr_id, status, sub_id):
        "Internal. Create a subscribe confirmation message"
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>CONFIRM</message_type>"])
        tmp.extend(['<parameter name = "status">', str(status), '</parameter>'])
        tmp.extend(['<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)
    
    def _create_cnf_rdf(self, n_id, tr_id, status, results, sub_id):
        """Internal. Create a subscribe confirm message for
        triple pattern subscription"""
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>CONFIRM</message_type>"])
        tmp.extend(['<parameter name = "status">', str(status), '</parameter>'])
        tmp.extend(['<parameter name = "results">'])
        tmp.append(self._encode(results))
        tmp.extend(['</parameter><parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    def _create_cnf_uri(self, n_id, tr_id, status, results, sub_id):
        "Internal. Create a subscribe confirm message for wql subscription"
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>CONFIRM</message_type>"])
        tmp.extend(['<parameter name = "status">', str(status), '</parameter>'])
        tmp.extend(['<parameter name = "results"><node_list>'])
                
        for i in results:
            node, litp = i
            if not litp:
                tmp.extend(['<uri>', str(node), '</uri>'])
            else:
                tmp.extend(['<literal>', str(node), '</literal>'])

        tmp.extend(['</node_list></parameter>',
                    '<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    def _create_cnf_bool(self, n_id, tr_id, status, results, sub_id):
        "Internal. Create a subscribe confirm message for wql subscription"
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>CONFIRM</message_type>"])
        tmp.extend(['<parameter name = "status">', str(status), '</parameter>'])
        tmp.extend(['<parameter name = "results">'])
        if results[0]:
            tmp.append("TRUE")
        else:
            tmp.append("FALSE")
        tmp.extend(['</parameter>', '<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)
    
    def _create_ind_rdf(self, n_id, tr_id, added, removed, sub_id):
        """Internal. Create a subscribe indication message for
        triple pattern subscription"""
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>INDICATION</message_type>"])
        tmp.extend(['<parameter name = "new_results">'])
        tmp.append(self._encode(added))
        tmp.extend(['</parameter>', '<parameter name = "obsolete_results">'])
        tmp.append(self._encode(removed))
        tmp.extend(['</parameter>', '<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    def _create_ind_bool(self, n_id, tr_id, added, removed, sub_id):
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>INDICATION</message_type>"])
        tmp.extend(['<parameter name = "new_results">'])
        if added[0]:
            tmp.append("TRUE")
        else:
            tmp.append("FALSE")
        tmp.extend(['</parameter>','<parameter name = "obsolete_results">'])
        if removed[0]:
            tmp.append("TRUE")
        else:
            tmp.append("FALSE")
        tmp.extend(['</parameter>', '<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    def _create_ind_uri(self, n_id, tr_id, added, removed, sub_id):
        """Internal. Create a subscribe indication message for
        wql subscription"""
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>SUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>INDICATION</message_type>"])

        tmp.extend(['<parameter name = "new_results">', '<node_list>'])
        for i in added:
            node, litp = i
            if not litp:
                tmp.extend(['<uri>', str(node), '</uri>'])
            else:
                tmp.extend(['<literal>', str(node), '</literal>'])

        tmp.extend(['</node_list>', '</parameter>'])

        tmp.extend(['<parameter name = "obsolete_results">', '<node_list>'])
        for i in removed:
            node, litp = i
            if not litp:
                tmp.extend(['<uri>', str(node), '</uri>'])
            else:
                tmp.extend(['<literal>', str(node), '</literal>'])

        tmp.extend(['</node_list>', '</parameter>',
                    '<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    def _create_unsub(self, n_id, tr_id, status, sub_id, confirm = True):
        "Internal. Create a unsubscribe confirmation or indication message"
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>UNSUBSCRIBE</transaction_type>"])
        tmp.extend(["<message_type>"])
        if confirm:
            tmp.append("CONFIRM</message_type>")
        else:
            tmp.append("INDICATION</message_type>")
        tmp.extend(['<parameter name = "status">', str(status), '</parameter>'])
        tmp.extend(['<parameter name = "subscription_id">',
                    str(sub_id), '</parameter>'])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    # Message equality check

    def _create_diff(self, new_result):
        """Internal. Calculate the difference between the current query result
        and the previously sent one. Returns a tuple
        (new triples, removed triples)"""
        previous = set(self.previous)
        self.previous = new_result # Save the current baseline
        new_result = set(new_result)
        added = new_result - previous
        removed = previous - new_result

        return (list(added), list(removed))
            
    def _set_initial_result(self, arg):
        """Internal. Calculate initial result for subscription
        query result comparison"""
        # hash_list = map(hash, arg)
        # self.previous_hash = sum(hash_list)
        self.previous = arg
    
    ######################
    #
    # Transaction handler
    #
    ######################
    def handle(self):
        "Process a single subscribe transaction"            

        debug(1, "*** handling subscribe transaction", self)
        self.previous = None
        q = Queue.Queue(1) # Result queue

        space = self.int_msg_rep["space_id"]

        REACTIVE_SESSIONS.acquire()
        if self.tr_id in REACTIVE_SESSIONS_TABLE:
            self.sub_id = str(uuid.uuid4())
        else:
            self.sub_id = self.tr_id
        REACTIVE_SESSIONS_TABLE[self.sub_id] = (q, time.ctime())
        REACTIVE_SESSIONS.release()
        PENDING_SUBSCRIPTION.acquire()
        PENDING_SUBSCRIPTION_TABLE[self.sub_id] = False
        PENDING_SUBSCRIPTION.release()

        # Initial query for setting a baseline

        QUERY_QUEUE[space].put(("query",
                                (self.n_id,
                                 self.sub_id,
                                 self.query_type,
                                 self.query),
                                q))
        msg_queue_event[space].set()

        # Create a response containing initial baseline
        op, arg = q.get()
        if op == "triples":
            msg = self._create_cnf_rdf(self.n_id, self.tr_id,
                                       M3_SUCCESS, arg, self.sub_id)
        elif op == "wql-values" or op == "wql-nodetypes":
            msg = self._create_cnf_uri(self.n_id, self.tr_id,
                                       M3_SUCCESS, arg, self.sub_id)
        elif op == "wql-related" or op == "wql-istype" or op == "wql-issubtype":
            msg = self._create_cnf_bool(self.n_id, self.tr_id,
                                        M3_SUCCESS, arg, self.sub_id)
        self.conn.send(msg)

        print "SUB id: ", self.sub_id, "tr_id: ", self.tr_id
        
        self._set_initial_result(arg)

        QUERY_QUEUE[space].put(("query",
                                (self.n_id,
                                 self.sub_id,
                                 self.query_type,
                                 self.query),
                                q))
        msg_queue_event[space].set()

        # Subscription query loop
        while True:
            op, arg = q.get()
            debug(1, "Got msg:" + str(op) + " : " + str(arg), self)
            if op in self.wql_query_types or op == "triples":
                # if arg == []:
#                     debug(1, "    ... arg was []", self)
#                     #print "SUBSCRIBE", self.tr_id, "was empty"
#                     QUERY_QUEUE[space].put(("query",
#                                             (self.n_id,
#                                              self.sub_id,
#                                              self.query_type,
#                                              self.query),
#                                             q))
#                     PENDING_SUBSCRIPTION.acquire()
#                     if PENDING_SUBSCRIPTION_TABLE[self.sub_id]:
#                         msg_queue_event[space].set()                    
#                     PENDING_SUBSCRIPTION.release()
#                     continue
                
                added, removed = self._create_diff(arg)

                if added == [] and removed == []:
                    debug(1, "    ... arg was _eq_to_previous", self)
                    #print "SUBSCRIBE", self.tr_id, "was eq to previous"
                    QUERY_QUEUE[space].put(("query",
                                            (self.n_id,
                                             self.sub_id,
                                             self.query_type,
                                             self.query),
                                            q))
                    PENDING_SUBSCRIPTION.acquire()
                    if PENDING_SUBSCRIPTION_TABLE[self.sub_id]:
                        msg_queue_event[space].set()                    
                    PENDING_SUBSCRIPTION.release()
                    continue

                if op == "triples":
                    msg = self._create_ind_rdf(self.n_id, self.tr_id,
                                               added, removed, self.sub_id)
                elif op == "wql-values" or op == "wql-nodetypes":
                    msg = self._create_ind_uri(self.n_id, self.tr_id,
                                               added, removed, self.sub_id)
                elif op == "wql-related" or op == "wql-istype" or op == "wql-issubtype":
                    msg = self._create_ind_bool(self.n_id, self.tr_id,
                                                added, removed, self.sub_id)

                # print "SUBSCRIBE", self.tr_id, ": sent response"
                self.conn.send(msg)
                debug(1, "SUBSCRIBE: Sent response to node", self)

                if self.one_result:
                    msg = self._create_unsub(self.n_id, self.tr_id,
                                             M3_SUCCESS,
                                             self.sub_id, False)
                    self.conn.send(msg)
                    self.conn.close()
            
                    REACTIVE_SESSIONS.acquire()
                    del REACTIVE_SESSIONS_TABLE[self.sub_id]
                    REACTIVE_SESSIONS.release()
    
                    debug(1, "%s unsubscribed." % self.sub_id, self)
                    return

                QUERY_QUEUE[space].put(("query",
                                        (self.n_id,
                                         self.sub_id,
                                         self.query_type,
                                         self.query),
                                        q))
                PENDING_SUBSCRIPTION.acquire()
                if PENDING_SUBSCRIPTION_TABLE[self.sub_id]:
                    msg_queue_event[space].set()                    
                PENDING_SUBSCRIPTION.release()

            elif op == "stop":
                msg = self._create_unsub(self.n_id, self.tr_id,
                                         M3_SUCCESS,
                                         self.sub_id, True)
                # print "UNSUBSCRIBE: sent"
                # print msg
                self.conn.send(msg)
                self.conn.close()
                
                REACTIVE_SESSIONS.acquire()
                del REACTIVE_SESSIONS_TABLE[self.sub_id]
                REACTIVE_SESSIONS.release()
                PENDING_SUBSCRIPTION.acquire()
                del PENDING_SUBSCRIPTION_TABLE[self.sub_id]
                PENDING_SUBSCRIPTION.release()
                # print "UNSUBSCRIBED", self.sub_id
                debug(1, "Reactive session stopped", self)
                return
            else:
                pass # Raise exception: unnown op
                            


class QueryHandler(TransactionHandler):
    "Class to handle a single QUERY transaction"
    def __init__(self, conn, array):
        TransactionHandler.__init__(self, conn, array)
        self.query_type = array["type"].lower()
        # Change tests to completely case-insensitive
        self.supported_query_types = ["wql-values", "rdf-m3", 
                                      "wql-related", "wql-istype", 
                                      "wql-nodetypes", "wql-issubtype"]

        self.wql_query_types = ["wql-values", "wql-related", "wql-istype", 
                                "wql-nodetypes", "wql-issubtype"]
        if self.query_type in self.wql_query_types:
            # print "WQL QUERY: got", array["query"]
            self.query = {}
            parser = make_parser()
            wql_mh = WqlHandler(self.query)
            parser.setContentHandler(wql_mh)
            parser.parse(cStringIO.StringIO(str(array["query"])))
            # print "WQL QUERY: parsed query:", self.query
        elif self.query_type.lower() == "rdf-m3":
            self.query = []
            pq_mh = M3RDFHandler(self.query, {})
            parser = make_parser()
            parser.setContentHandler(pq_mh)
            parser.parse(cStringIO.StringIO(str(array["query"])))
            # print "RDF QUERY: parsed query:", self.query

    def _create_header(self, n_id, tr_id):
        "Internal. Create the header (invariant part) of return messages"
        tmp = ["<SSAP_message>", "<node_id>", n_id, "</node_id>"]
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        return tmp

    def _create_rsp_rdf(self, n_id, tr_id, results, status = M3_SUCCESS):
        "Internal. Create a QUERY RESPONSE message for rdf template query."
        tmp = ["<SSAP_message><node_id>", n_id, "</node_id>"]
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        tmp.extend(["<transaction_type>","QUERY","</transaction_type>"])
        tmp.extend(["<message_type>","CONFIRM","</message_type>"])
        tmp.extend(['<parameter name = "results">'])
        tmp.append(self._encode(results))
        tmp.extend(['</parameter>',
                   '<parameter name = "status">%s</parameter>'%status])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)

    def _create_rsp_bool(self, n_id, tr_id, results, status = M3_SUCCESS):
        "Internal. Create a subscribe confirm message for wql subscription"
        tmp = self._create_header(n_id, tr_id)
        tmp.extend(["<transaction_type>", "QUERY", "</transaction_type>"])
        tmp.extend(["<message_type>", "CONFIRM", "</message_type>"])
        tmp.extend(['<parameter name = "status">', str(status), '</parameter>'])
        tmp.extend(['<parameter name = "results">'])
        if results[0]:
            tmp.append("TRUE")
        else:
            tmp.append("FALSE")
        tmp.extend(['</parameter>', "</SSAP_message>"])
        return ''.join(tmp)

    def _create_rsp_uri(self, n_id, tr_id, results, status = M3_SUCCESS):
        "Internal. Create a QUERY RESPONSE message for wql query."
        tmp = ["<SSAP_message>", "<node_id>", n_id, "</node_id>"]
        tmp.extend(["<space_id>", self.int_msg_rep["space_id"], "</space_id>"])
        tmp.extend(["<transaction_id>", tr_id, "</transaction_id>"])
        tmp.extend(["<transaction_type>", "QUERY", "</transaction_type>"])
        tmp.extend(["<message_type>", "CONFIRM", "</message_type>"])
        tmp.extend(['<parameter name = "results"><node_list>'])
        for i in results:
            node, litp = i
            if not litp:
                tmp.extend(['<uri>', str(node), '</uri>'])
            else:
                tmp.extend(['<literal>', str(node), '</literal>'])
        tmp.extend(['</node_list>', '</parameter>', 
                    '<parameter name = "status">%s</parameter>'%status])
        tmp.extend(["</SSAP_message>"])
        return ''.join(tmp)
        
    def handle(self):
        "Handle a single Query transaction"
        debug(2, "Handling QUERY operation", self)
        # debug(3, "    QUERY:"+str(self.tr_id), self)
        q = Queue.Queue(1)
        print "QUERY: got query of type:", self.query_type
        print "QUERY: Query expression is:", self.query
        QUERY_QUEUE[self.int_msg_rep["space_id"]].put(("query",
                                                       (self.n_id,
                                                        self.tr_id,
                                                        self.query_type,
                                                        self.query),
                                                       q))
        msg_queue_event[self.int_msg_rep["space_id"]].set()
        debug(3, "QUERYing %s at space %s"%(str(self.query), self.int_msg_rep["space_id"]), self)
        op, arg = q.get()
        # debug(3, "QUERY response read "+str(self), self)
        debug(3, "    QUERY: got result " + str(arg), self)
        # print "QUERY: Got operation", op
        if op in self.wql_query_types or op == "triples":
            if op == "triples":
                msg = self._create_rsp_rdf(self.n_id, self.tr_id, arg)
            elif op == "wql-values" or op == "wql-nodetypes":
                msg = self._create_rsp_uri(self.n_id, self.tr_id, arg)
            elif op == "wql-related" or op == "wql-istype" or op == "wql-issubtype":
                msg = self._create_rsp_bool(self.n_id, self.tr_id, arg)
            #print "QUERY sending:", msg
            self.conn.send(msg)
            self.conn.close()
        else:
            print "QUERY: Unrecognized response type"
            pass # Throw exception

    
class SIBRequestHandler(threading.Thread):
    """ Handles all kinds of communication (proactive,
    reactive, query, retraction) with nodes. One threaded
    instance for each transaction."""

    def __init__(self, socket, connector):
        threading.Thread.__init__(self)
        # Should be parametrized
        self.conn = connector(socket)
        
    def run(self):
        """Receives parsed message from Node and instantiates the respective
        transaction handler."""

        try:
            int_msg_rep = self.conn.receive()
        except SAXException:
            # If parsing the received msg is not succesful, drop the msg
            print "Incorrect protocol message dropped"
            return
            

        # First check if joining
        if int_msg_rep["transaction_type"].lower() == "join"\
               and int_msg_rep["message_type"].lower() == "request":
            handler = JoinHandler(self.conn, int_msg_rep)
            handler.handle()
            return
        # If not join msg, check that target space exists and that sender
        # has already joined
        # otherwise drop message silently
        if not int_msg_rep["space_id"] in SPACES:
            print "Dropped msg to non-existent space", int_msg_rep["space_id"]
            return
        MEMBER_SET_LOCK[int_msg_rep["space_id"]].acquire()
        if not int_msg_rep["node_id"] in MEMBER_SET[int_msg_rep["space_id"]]:
            # print MEMBER_SET[int_msg_rep["space_id"]]
            MEMBER_SET_LOCK[int_msg_rep["space_id"]].release()
            print "Dropped a message from a non-member node"
            for i in int_msg_rep:
                print i, ":", int_msg_rep[i]
            print
            return
        MEMBER_SET_LOCK[int_msg_rep["space_id"]].release()

        if int_msg_rep["message_type"].lower() == "request":
            # Handle INSERT session
            if int_msg_rep["transaction_type"].upper() == "INSERT":
                debug(2, "REQ_HANDLER: handling insert transaction", self)
                handler = InsertHandler(self.conn, int_msg_rep)
                handler.handle()

            # Handle QUERY session
            elif int_msg_rep["transaction_type"].upper() == "QUERY":
                debug(2, "REQ_HANDLER: handling query transaction", self)
                handler = QueryHandler(self.conn, int_msg_rep)
                handler.handle()

            # Handle UPDATE session
            elif int_msg_rep["transaction_type"].upper() == "UPDATE":
                debug(2, "REQ_HANDLER: handling update transaction", self)
                handler = UpdateHandler(self.conn, int_msg_rep)
                handler.handle()

            # Handle SUBSCRIBE session
            elif int_msg_rep["transaction_type"].upper() == "SUBSCRIBE":
                debug(2, "REQ_HANDLER: handling subscribe transaction", self)
                handler = SubscribeHandler(self.conn, int_msg_rep)
                handler.handle()
                    
            # Handle REMOVE session
            elif int_msg_rep["transaction_type"].upper() == "REMOVE":
                debug(2, "REQ_HANDLER: handling remove transaction", self)
                handler = RemoveHandler(self.conn, int_msg_rep)
                handler.handle()

            elif int_msg_rep["transaction_type"].upper() == "LEAVE":
                debug(2, "REQ_HANDLER: handling leave transaction", self)
                handler = LeaveHandler(self.conn, int_msg_rep)
                handler.handle()

            # Stop ongoing SUBSCRIPTION session
            # Fails if Node tries to stop a nonexistent session
            elif int_msg_rep["transaction_type"].upper() == "UNSUBSCRIBE":
                s_id = int_msg_rep["subscription_id"]
                REACTIVE_SESSIONS.acquire()
                debug(1, "Stop reactive Acquired react session lock", self)
                if s_id in REACTIVE_SESSIONS_TABLE:
                    debug(1, "Stopping REACTIVE"+str(s_id), self)
                    queue, t = REACTIVE_SESSIONS_TABLE[s_id]
                    REACTIVE_SESSIONS.release()
                    debug(1, "Stop Reactive released lock", self)
                    queue.put(("stop", None))
                else:
                    REACTIVE_SESSIONS.release()
                    # No such subscription
                    # Send error cnf back
                    node_id = int_msg_rep["node_id"]
                    debug(1, "Erroneous unsubscription from node %s, sub_id %s"%(node_id,s_id), self)
                    tmp = ["<SSAP_message><node_id>", node_id, "</node_id>"]
                    tmp.extend(["<space_id>", int_msg_rep["space_id"], 
                                "</space_id>"])
                    tmp.extend(["<transaction_id>", 
                                int_msg_rep["transaction_id"], 
                                "</transaction_id>"])
                    tmp.extend(["<transaction_type>","UNSUBSCRIBE",
                                "</transaction_type>"])
                    tmp.extend(["<message_type>","CONFIRM","</message_type>"])
                    tmp.extend(['<parameter name = "status">',
                                M3_SIB_ERROR,'</parameter>'])
                    tmp.extend(['<parameter name = "subscription_id">',
                                str(s_id), '</parameter>'])
                    tmp.extend(["</SSAP_message>"])

                    self.conn.send(''.join(tmp))
                    self.conn.close()
            else:
                print int_msg_rep["transaction_type"], " not supported"
        else:
            print "--- Malformed message" # Throw also exception

class Scheduler(threading.Thread):
    """Reads operation requests from msg_queue and performs
    the operations on the data store (currently wilbur)"""
    def __init__(self, sib_name):
        threading.Thread.__init__(self)
        self.sib_name = sib_name
    def run(self):
        updated = False
        name = self.sib_name
        writer = RDFWriter(name)
        reader = RDFReader(name)
        retractor = RDFRetractor(name)
        while True:
            # avoid busy waiting if no queued actions
            msg_queue_event[name].wait()
            msg_queue_event[name].clear()

            ASSERT_QUEUE[name].put(("end_of_batch", None, None))
            op, arg, addr = ASSERT_QUEUE[name].get()
            while op != "end_of_batch":
                updated = True
                if op == "assert":
                    debug(3, "asserting " + str(arg), self)
                    writer.write(arg)
                elif op == "assert_confirm":
                    debug(3, "asserting " + str(arg), self)
                    result = writer.write(arg)
                    # ASSUME SUCCESS FOR THIS
                    # FAILURE CHECKING NOT IMPLEMENTED YET
                    addr.put(("assert_confirm", M3_SUCCESS, result))
                elif op == "retract":
                    debug(3, "retracting " + str(arg), self)
                    retractor.retract(arg)
                elif op == "retract_confirm":
                    result = retractor.retract(arg)
                    addr.put(('retract_confirm', result))
                elif op == "update_confirm":
                    rem_result = retractor.retract(arg[0])
                    ins_result = writer.write(arg[1])
                    addr.put(("update_confirm", M3_SUCCESS, 
                              rem_result, ins_result))
                elif op == "update":
                    retractor.retract(arg[0])
                    writer.write(arg[1])
                else:
                    pass # ERROR
                op, arg, addr = ASSERT_QUEUE[name].get()

            if updated:
                PENDING_SUBSCRIPTION.acquire()
                for sub in PENDING_SUBSCRIPTION_TABLE:
                    PENDING_SUBSCRIPTION_TABLE[sub] = True
                PENDING_SUBSCRIPTION.release()

            QUERY_QUEUE[name].put(("end_of_batch", None, None))
            op, arg, addr = QUERY_QUEUE[name].get()
            while op != "end_of_batch":
                if op == "query":
                    debug(2, "Querying" + str(arg), self)
                    result = reader.read(arg)
                    node, session, query_type, query_list = arg
                    # Check for session as normal queries
                    # are not in the dict
                    if session in PENDING_SUBSCRIPTION_TABLE:
                        PENDING_SUBSCRIPTION.acquire()
                        PENDING_SUBSCRIPTION_TABLE[session] = False
                        PENDING_SUBSCRIPTION.release()
                    addr.put(result)
                op, arg, addr = QUERY_QUEUE[name].get()

class RDFReader:
    "Reads information from Wilbur RDF store"
    def __init__(self, space):
        self.space = space
    def open(self):
        pass
    def read(self, arg):
        space = self.space
        store = RDFSTORE[space]
        node, session, query_type, query = arg
        # print "RDFREADER: got query", query
        if query_type == "rdf-m3":
            triples = set([])

            RDFSTORELOCK[space].acquire()
            # query is a list of triples to be matched
            for q in query:
                #print "QUERY:", q
                literalp, tag, t = q
                s_str, p_str, o_str = t
                # Map node string to a piglet node
                # Expand if possible
                if not s_str:
                    s = 0
                else:
                    s_str = store.expand_m3(s_str)
                    s = store.node(s_str)

                if not p_str:
                    p = 0
                else:
                    p_str = store.expand_m3(p_str)
                    p = store.node(p_str)

                if not o_str:
                    o = 0
                else:
                    if literalp:
                        o = store.literal(o_str)
                    else:
                        o_str = store.expand_m3(o_str)
                        o = store.node(o_str)

                result = store.query(s, p, o)
                triples = triples.union(set([(r, frozenset('0')) for r in result]))
                    

            RDFSTORELOCK[space].release()
            #print "RDFREADER: Query result triples:"
            #print triples
            #print to_string_triple(space, list(triples))
            return ("triples", to_string_triple(space, list(triples)))

        elif query_type == "wql-values":
            # query is a dict with values start_node and path
            RDFSTORELOCK[space].acquire()
            start_node_str, sn_litp = query["start"]
            path_expr_str = eval(str(query["path"]))# Will be a list

            if not sn_litp:
                start_node_str = store.expand_m3(start_node_str)
                start_node = store.node(start_node_str)
            else:
                start_node = store.literal(start_node_str)

            path_expr = self._str_to_node_wql(path_expr_str)
            values = store.values(start_node, path_expr)
            #print "RDFREADER: values:", values
            values_str = to_string_node(space, values)
            RDFSTORELOCK[space].release()
            #print "WQL result:", values_str
            return ("wql-values", values_str)

        elif query_type == "wql-related":
            RDFSTORELOCK[space].acquire()
            start_node_str, sn_litp = query["start"]
            path_expr_str = eval(str(query["path"]))# Will be a list
            end_node_str, en_litp = query["end"]
                
            if not sn_litp:
                start_node_str = store.expand_m3(start_node_str)
                start_node = store.node(start_node_str)
            else:
                start_node = store.literal(start_node_str)
            if not en_litp:
                end_node_str = store.expand_m3(end_node_str)
                end_node = store.node(end_node_str)
            else:
                end_node = store.literal(end_node_str)

            path_expr = self._str_to_node_wql(path_expr_str)
            related = store.related(start_node, path_expr, end_node)
            RDFSTORELOCK[space].release()
            return ("wql-related", [related])

        elif query_type == "wql-nodetypes":
            RDFSTORELOCK[space].acquire()
            node_str, litp = query["node"]

            node_str = store.expand_m3(node_str)
            node = store.node(node_str)
            
            nodetypes = store.nodeTypes(node)

            nodetypes_str = to_string_node(space, nodetypes)
            RDFSTORELOCK[space].release()
            #print "WQL result:", values_str
            return ("wql-nodetypes", nodetypes_str)

        elif query_type == "wql-istype":
            RDFSTORELOCK[space].acquire()
            node_str, litp = query["start"]
            type_str, litp = query["type"]

            node_str = store.expand_m3(node_str)
            node = store.node(node_str)
            type_str = store.expand_m3(type_str)
            type = store.node(type_str)

            is_type = store.isType(node, type)
            RDFSTORELOCK[space].release()
            return ("wql-istype", [is_type])

        elif query_type == "wql-issubtype":
            RDFSTORELOCK[space].acquire()
            subtype_str, litp = query["subtype"]
            supertype_str, litp = query["supertype"]

            subtype_str = store.expand_m3(subtype_str)
            subtype = store.node(subtype_str)
            supertype_str = store.expand_m3(supertype_str)
            supertype = store.node(supertype_str)

            is_subtype = store.isSubtype(subtype, supertype)
            RDFSTORELOCK[space].release()
            return ("wql-issubtype", [is_subtype])

        else:
            print "RDFReader: unknown query type"
            RDFSTORELOCK[space].release()
            return ("unknown", [])
    
    def _str_to_node_wql(self, str_list):
        space = self.space
        path_expr = []
        for i_str in str_list:
            if type(i_str) == list:
                path_expr.append(self._str_to_node_wql(i_str))
            elif i_str in WQL_WORDS:
                path_expr.append(i_str)
            else:
                # i_str = expand(space, i_str)
                i_str = RDFSTORE[space].expand_m3(i_str)
                i = RDFSTORE[space].node(i_str)
                path_expr.append(i)
        return path_expr

    def close(self):
        pass
    
class RDFWriter:
    "Writes information to the rdf store"
    def __init__(self, space):
        self.space = space
        
    def open(self):
        pass
    
    def write(self, msg):
        n_id, s_id, payload = msg
        debug(3, "Node id: " + str(n_id), self)
        space = self.space
        store = RDFSTORE[space]
        # We use the space name as source for now, this may change
        source = store.node(space)
        #print "Triple count now", RDFSTORE[space].count(0,0,0)
        #print "Triple count for space now", RDFSTORE[space].count(0,0,0,source)

        # pl is (type, pl)
        # type == "rdf-m3" or "rdf-xml"
        # pl according to type
        
        for pl in payload:
            # Use M3 encoding
            if pl[0].lower() == "rdf-m3":
                triple_ids = []

                RDFSTORELOCK[space].acquire()
                store.db.transaction()

                for i in pl[1]:
                    #print "WRITE: inserting triple", i
                    lit, tag, t = i
                    s_str, p_str, o_str = t
                    # print "RDFWRITER: expanding nodes:"
                    # print "subject:", s_str
                    # print "predicate:",p_str
                    # print "object:", o_str
                    s_str = store.expand_m3(s_str)
                    p_str = store.expand_m3(p_str)
                    # print "RDFWRITER: getting ints for nodes:"
                    # print "subject:", s_str
                    # print "predicate:",p_str
                    # print "object:", o_str
                    s = store.node(s_str)
                    p = store.node(p_str)
                    if not lit:
                        o_str = store.expand_m3(o_str)
                        o = store.node(o_str)
                    else:
                        o = store.literal(o_str)
                    #print "RDFWRITER: adding ", s_str, p_str, o_str
                    #print "RDFWRITER: adding ", s, p, o
                    store.add(s, p, o, source)
                    # TODO: update to remove tid tag handling
                    triple_ids.append((tag, '0'))
                store.db.commit()
                RDFSTORELOCK[space].release()
                # print "RDFWRITER: inserted triples"
                return ("tagged", triple_ids)

            # Use RDFXML encoding
            elif pl[0].lower() == "rdf-xml":
                print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                print "X                           X"
                print "X RDF/XML not yet supported X"
                print "X                           X"
                print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                return ("untagged", [])

    def close(self):
        pass

class RDFRetractor:
    "Retracts information from the RDF store"
    def __init__(self, space):
        self.space = space

    def open(self):
        pass

    # pl is a list of tuples (pl_t, pl_c)
    # Currently only single triples can be deleted
    # add support for wildcard deletion
    def retract(self, rm_list):
        if MONOTONICITY == True:
            tbr = str(len(rm_list))
            debug(1, "Monotonic mode, retract ignored for %s elements"%tbr, self)
        else:
            return self.retract_triples(rm_list)

    def retract_triples(self, arg):
        space = self.space
        store = RDFSTORE[space]
        space_node = store.node(space)
        RDFSTORELOCK[space].acquire()
        n_id, tr_id, rm_list = arg
        removed_list = []
        for i in rm_list:
            # print "RDFRETRACTOR: removing", i
            lit, tag, t = i
            s_str, p_str, o_str = t
            s_str = store.expand_m3(s_str)
            p_str = store.expand_m3(p_str)
            s = store.node(s_str)
            p = store.node(p_str)
            if not lit:
                o_str = store.expand_m3(o_str)
                o = store.node(o_str)
            else:
                o = store.literal(o_str)
            removed_list.append((s, p, o))
            try:
                store.delete(s, p, o, space_node)
            except:
                for r in removed_triples:
                    s, p, o = r
                    store.add(s, p, o, space_node)
                return M3_SIB_ERROR
        RDFSTORELOCK[space].release()

        # print "RDFRETRACTOR: remove succesful"
        return M3_SUCCESS

    def close(self):
        pass


class WqlHandler(ContentHandler):
    "Handler for SAX events from wql query messages"
    def __init__(self, query):
        """query is a dictionary containing the parameters
        for the particular wql query. Keys:
        values: start, path
        related: start, end, path
        nodetypes: node
        istype: node, type
        issubtype: subtype, supertype"""
        self.query = query
        self.inNode = False
        self.inPath = False
        self.nodeName = ""
        self.literal = False
    def startElement(self, name, attrs):
        if name == "node":
            self.inNode = True
            self.node = ""
            self.nodeName = attrs.get('name', "node").lower()
            if attrs.get('type', "").lower() == "literal":
                self.literal = True
            return
        elif name == "path_expression":
            self.inPath = True
            self.path = ""
            return
        else:
            return

    def characters(self, ch):
        if self.inNode:
            self.node += ch
        elif self.inPath:
            self.path += ch

    def endElement(self, name):
        if name == "node":
            self.inNode = False
            self.query[self.nodeName] = (self.node, self.literal)
            return
        elif name == "path_expression":
            self.inPath = False
            self.query["path"] = self.path
            return
        else:
            return

class M3RDFHandler(ContentHandler):
    "Handler for SAX events from M3 RDF encoded triples"
    def __init__(self, template_list, bnodemap):
        # After parsing, template_list will contain tuples of form
        # (literal, tag, (s, p, o)) where 
        # literal is True (value, not str) if object is a literal
        # literal is False if object is a URI
        # Tag is None if no tag
        self.template_list = template_list
        self.inSubject = False
        self.inPredicate = False
        self.inObject = False
        self.inTriple = False
        self.literal = False
        self.bNode = False
        self.current_tag = None
        self.subject = ""
        self.predicate = ""
        self.object = ""
        self.bNodeMap = bnodemap

    def startElement(self, name, attrs):
        if name == "subject":
            self.inSubject = True
            if attrs.get('type', '').lower() == "bnode":
                self.bNode = True
            self.subject = ""
            return
        elif name == "predicate":
            self.inPredicate = True
            self.predicate = ""
            return
        elif name == "object":
            self.inObject = True
            self.object = ""
            if attrs.get('type', '').lower() == "literal":
                self.literal = True
            # literal can't be a bNode, hence elif
            elif attrs.get('type', '').lower() == "bnode":
                self.bNode = True
            return
        elif name == "triple":
            self.inTriple = True
            if attrs.has_key('tag'):
                self.current_tag = attrs.get('tag', '')
            return
        
    def characters(self, ch):
        if self.inSubject:
            self.subject += ch
        elif self.inPredicate:
            self.predicate += ch
        elif self.inObject:
            self.object += ch
            
    def endElement(self, name):
        sib_any = "sib:any"
        exp_sib_any = 'http://www.nokia.com/NRC/M3/sib#any'
        if name == "subject":
            self.inSubject = False
            if (sib_any in self.subject.lower())\
                   or (exp_sib_any in self.subject):
                self.subject = None
            # Handle named bNodes
            if self.bNode:
                if self.subject == "":
                    self.subject = str(uuid.uuid4())
                else:
                    self.current_tag  = self.subject
                    if not (self.subject in self.bNodeMap):
                        self.bNodeMap[self.subject] = str(uuid.uuid4())
                        self.subject = self.bNodeMap[self.subject]
                    else:
                        self.subject = self.bNodeMap[self.subject]
                self.bNode = False
            return
        elif name == "predicate":
            self.inPredicate = False
            if (exp_sib_any in self.predicate)\
                   or (sib_any in self.predicate.lower()):
                self.predicate = None
            return
        elif name == "object":
            self.inObject = False
            #self.objectType = self.objectType.lower()
            if (sib_any in self.object.lower())\
                   or (exp_sib_any in self.object):
                self.object = None
            # Handle named bNodes
            if self.bNode:
                if self.object == "":
                    self.object = str(uuid.uuid4())
                else:
                    self.current_tag  = self.object
                    if not (self.object in self.bNodeMap):
                        self.bNodeMap[self.object] = str(uuid.uuid4())
                        self.object = self.bNodeMap[self.object]
                    else:
                        self.object = self.bNodeMap[self.object]
                self.bNode = False
            return
        elif name == "triple":
            self.inTriple = False
            # print "M3 RDF PARSER: adding nodes"
            # print "s:", self.subject
            # print "p:", self.predicate
            # print "o:", self.object
            self.template_list.append((self.literal, self.current_tag, (self.subject, self.predicate, self.object)))
            self.literal = False
            self.current_tag = None
            return


def debug(verb, dbg_str, inst = ""):
    "Prints the debug information"
    if verb <= VERBOSITY:
        print "SIB--D %s in %s --> %s"% (str(verb), str(inst), dbg_str)


def main():
    """Main function"""
    usage = "%prog [options] SmartSpaceName"
    parser = OptionParser(usage = usage)
    parser.add_option("-B", "--discoverableBonjour", action="store_true", 
                      dest="discovery_b",
                      help="""Enable automatic discovery using mDNS
                              (needs Bonjour libraries)""")

    parser.add_option("-m", "--monotonic", action="store_true",
                      dest="monotonic",
                      help="""Set the SIB to be in monotonic mode, ie: ignores
                              retracts (set verbosity to 1 to see the ignored
                              retractions)""")
    parser.add_option("-t", "--tcp_port", type="int", dest="tcp_port",
                      help="""Set the listening port for tcp connections
                              (default is 10010)""")
    parser.add_option("-a", "--address", type="string", dest="address",
                      help="""Set the IP address to listen to
                              (default is the system default address)""")
    parser.add_option("-v", "--verbosity", type="int", dest="verbose",
                      help="""Set the verbosity of the debug report
                              (default is 0 - no reports,
                                          1-calls,
                                          2-parameters,
                                          3-lots)""")
    parser.add_option("-r", "--reasoning", action="store_true",
                      dest="reasoning", help="Use a reasoning triple store")

    parser.set_defaults(discovery_b = False,
                        tcp_port = 10010, verbose = 0, monotonic=False,
                        reasoning = True, address = "")

    (options, args) = parser.parse_args()

    global VERBOSITY, RDFSTORE, RDFSTORELOCK, ASSERT_QUEUE
    global QUERY_QUEUE, msg_queue_event, MEMBER_SET, MEMBER_SET_LOCK
    global SPACES, MONOTONICITY

    print args
    for ss in args:
        scheduler = Scheduler(ss)
        ASSERT_QUEUE[ss] = Queue.Queue(0)
        QUERY_QUEUE[ss] = Queue.Queue(0)
        msg_queue_event[ss] = threading.Event()
        if options.reasoning:
            RDFSTORE[ss] = DB(ss)
        else:
            RDFSTORE[ss] = DB(ss)
        RDFSTORELOCK[ss] = threading.Semaphore()
        MEMBER_SET[ss] = set([])
        MEMBER_SET_LOCK[ss] = threading.Semaphore()
        SPACES.add(ss)

        scheduler.setDaemon(True)
        scheduler.start()

    VERBOSITY = options.verbose
    MONOTONICITY = options.monotonic
    print "Debug verbosity set to ", VERBOSITY
    print "Monotonicity set to ", MONOTONICITY

    sib = SIB_main(options.address,
                   options.tcp_port,
                   options.discovery_b)

    sib.start()
    
if __name__ == "__main__":
    print "(C)2007-2009 Nokia Corporation"
    print "M3 SIB running on %s" % platform
    print "Use at own risk"
    print "\n"
    main()
    
