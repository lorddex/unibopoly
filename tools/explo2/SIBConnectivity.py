import socket

# For XML parsing
from xml.sax import saxutils
from xml.sax import make_parser
#from xml.sax.handler import feature_namespaces
from xml.sax.handler import ContentHandler

import uuid
import cStringIO
import threading

#TCP = socket.getprotobyname("TCP")


# List of all listening sockets to prevent them from hanging after exit
LISTENING_SOCKETS_LIST = []
LISTENING_SOCKETS = threading.Lock()

def _list_socket(s):
    LISTENING_SOCKETS.acquire()
    LISTENING_SOCKETS_LIST.append(s)
    print "listening sockets: ", LISTENING_SOCKETS_LIST
    LISTENING_SOCKETS.release()

class TCPListener(threading.Thread):
    "Listener for TCP connections."
    def __init__(self, address, port, protocol, handler):
        threading.Thread.__init__(self)
        self.protocol = protocol
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _list_socket(self.socket)
        self.socket.bind((address, port))
        self.socket.listen(20)
        self.requesthandler = handler


    def run(self):
        handlers = ProtocolHandlers
        protocol = self.protocol
        while 1:
            try:
                (nodesocket, addr) = self.socket.accept()
                handler = self.requesthandler(nodesocket, handlers[protocol])
                handler.start()
            except error:
                break

    def close(self):
        self.socket.close()

class LocalListener(threading.Thread):
    "Listener for local connections (uses local BSD sockets)."
    def __init__(self, address, protocol, handler):
        threading.Thread.__init__(self)
        self.protocol = protocol
        self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        _list_socket(self.socket)
        self.socket.bind(address)
        self.socket.listen(10)
        self.requesthandler = handler


    def run(self):
        handlers = ProtocolHandlers
        protocol = self.protocol
        while 1:
            (nodesocket, addr) = self.socket.accept()
            handler = self.requesthandler(nodesocket, handlers[protocol])
            handler.start()

    def close(self):
        _rem_socket(self.socket)
        self.socket.close()

class SocketConnector:
    """Abstract connector to be used for receiving and sending responses
       on socket based network interfaces
       Operations:
       __init__(open socket from accept() or equiv
       string receive(): receives a message from network until shutdown
       send(string): sends a string, does not close socket afterwards
       close(): does a shutdown(write) and closes a socket"""
    def __init__(self, socket):
        pass

    def _parse(self, msg):
        # Parse received message
        parser = make_parser()
        #parser.setFeature(feature_namespaces, 0)
        int_msg_rep = {}
        smh = SSAPMsgHandler(int_msg_rep)
        parser.setContentHandler(smh)
        try:
            parser.parse(cStringIO.StringIO(msg))
        except:
            print msg
            raise
        return int_msg_rep
        
    def receive(self):
        "Abstract method"
        pass

    def send(self, msg):
        "Abstract method"
        pass

    def close(self):
        "Abstract method"
        pass


class HTTPConnector(SocketConnector):
    def __init__(self, socket):
        self.socket = socket
        # self.socket.setsockopt(TCP, socket.TCP_NODELAY, 1)

    def _parse_POST(self, msg):
        req_buf = cStringIO.StringIO(msg)
        for line in req_buf:
            if line == "\n": # CRLF
                break
        return ''.join(req_buf.readlines())
        
            
    def receive(self):
        rcvd = 0
        msg = ""
        # Receive a single message from Node
        # Not a perpetual loop
        # Ends when Node does a shutdown(write) on socket
        # Check indentation!
        while True:
            chunk = self.socket.recv(4096)
            if len(chunk) > 0:
                msg = msg + chunk
            else:
                print "RECEIVED FROM NODE: ", msg
                msg = self._parse_POST(msg)
                return self._parse(msg)
        if len(msg) == 0:
            return {} # No msg was received, return

    # New version
    def send(self, msg):
        sent = 0
        while sent < len(msg):
            print "SENDING: ", msg
            sent += self.socket.send(msg)

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()
    
class TCPConnector(SocketConnector):
    "Connector for TCP"
    def __init__(self, socket):
        self.socket = socket

    def receive(self):
        rcvd = 0
        msg = ""
        # Receive a single message from Node
        # Not a perpetual loop
        # Ends when Node does a shutdown(write) on socket
        # or when end tag </SSAP_message> is received
        while True:
            # Enable exit from receive
            try:
                chunk = self.socket.recv(4096)
            except socket.timeout:
                continue
            except socket.error:
                return {}
            except:
                raise
            
            if len(chunk) > 0:
                msg = msg + chunk
                if msg.endswith("</SSAP_message>"):
                    return self._parse(msg)
            else:
                #print "RECEIVED FROM NODE: ", msg
                return self._parse(msg)
        if len(msg) == 0:
            return {} # No msg was received, return

    # New version
    def send(self, msg):
        sent = 0
        while sent < len(msg):
            #print "SENDING: ", msg
            try:
                sent += self.socket.send(msg)
            except socket.error:
                break
            
    def close(self):
        try:
            self.socket.shutdown(socket.SHUT_WR)
            self.socket.close()
        except socket.error:
            self.socket.close()
    
class LocalConnector(SocketConnector):
    "Connector for local socket (currently same as TCP connector)"
    def __init__(self, socket):
        self.socket = socket

    def receive(self):
        rcvd = 0
        msg = ""
        # Receive a single message from Node
        # Not a perpetual loop
        # Ends when Node does a shutdown(write) on socket

        while True:
            chunk = self.socket.recv(4096)
            if len(chunk) > 0:
                msg = msg + chunk
            else:
                #print "RECEIVED FROM NODE: ", msg
                return self._parse(msg)
        if len(msg) == 0:
            return {} # No msg was received, return

    # New version
    def send(self, msg):
        sent = 0
        while sent < len(msg):
            #print "SENDING: ", msg
            sent += self.socket.send(msg)

    def close(self):
        self.socket.shutdown(socket.SHUT_WR)
        self.socket.close()


class SSAPMsgHandler(ContentHandler):

    # Parser for received messages
    # Specification of different messages
    # Can be found from Smart Space wiki
    # http://swiki.nokia.com/SmartSpaces/AccessProtocol
    
    def __init__(self, array):
        self.array = array
        self.inNodeId = False
        self.inSpaceId = False
        self.inTransactionId = False
        self.inTransactionType = False
        self.inMessageType = False
        self.inParameter = False
        self.inICV = False
        self.parameterName = ""

    def startElement(self, name, attrs):
        # print "--- Starting to parse"
        if name == "SSAP_message":
            # print "SIB_message"
            self.array["timestamp"] = "123"
            # self.array["seq_num"] = "456"
            self.array["msg_id"] = str(uuid.uuid1())
            return
        #Common for all messages
        elif name == "node_id":
            self.inNodeId = True
            self.nodeId = ""
            return
        elif name == "space_id":
            self.inSpaceId = True
            self.spaceId = ""
            return
        elif name == "transaction_id":
            self.inTransactionId = True
            self.transactionId = ""
            return
        elif name == "transaction_type":
            self.inTransactionType = True
            self.transactionType = ""
            return
        elif name == "message_type":
            self.inMessageType = True
            self.messageType = ""
            return
        elif name == "parameter":
            self.inParameter = True
            self.parameterName = attrs.get("name",None)
            # Can have multiple triples parameters in INSERT REQUEST
            # A bit unsafe, should require Transaction type before
            # parameters in schema etc.
            if self.parameterName.lower() == "insert_graph" or \
               self.parameterName.lower() == "remove_graph":
                if attrs.has_key("encoding"):
                    self.triplesType = attrs.get("encoding", None)
                else:
                    self.triplesType = "rdf-m3"
                self.parameter = ""
            else:
                self.parameter = ""
            return
        elif name == "ICV":
            self.inICV = True
            self.ICV = ""
            return
        else:
            if self.inParameter:
                self.parameter = self.parameter + "<" + name
                for i in attrs.items():
                    self.parameter = self.parameter + " " + str(i[0]) + "=" + '"' + str(i[1]) + '"'
                self.parameter += ">"
            return

    def characters(self, ch):
        if self.inNodeId:
            self.nodeId = self.nodeId + ch
        elif self.inSpaceId:
            self.spaceId = self.spaceId + ch
        elif self.inTransactionId:
            self.transactionId = self.transactionId + ch
        elif self.inTransactionType:
            self.transactionType = self.transactionType + ch
        elif self.inMessageType:
            self.messageType = self.messageType + ch
        elif self.inParameter:
            self.parameter = self.parameter + ch
        elif self.inICV:
            self.ICV = self.ICV + ch
            
    def endElement(self, name):
        if name == "node_id":
            self.array["node_id"] = self.nodeId
            self.inNodeId = False
            return
        if name == "space_id":
            self.array["space_id"] = self.spaceId
            self.inSpaceId = False
            return
        elif name == "transaction_id":
            self.array["transaction_id"] = self.transactionId
            self.inTransactionId = False
            return
        elif name == "transaction_type":
            self.array["transaction_type"] = self.transactionType
            self.inTransactionType = False
            return
        elif name == "message_type":
            self.array["message_type"] = self.messageType
            self.inMessageType = False
            return
        elif name == "ICV":
            self.array["ICV"] = self.ICV
            self.inICV = False
            return
        elif name == "parameter":
            if self.parameterName.lower() == "insert_graph":
                # Initialize triples array if needed
                if not "insert_graph" in self.array:
                    self.array["insert_graph"] = []
                self.array[self.parameterName].append((self.triplesType, 
                                                       self.parameter))
            elif self.parameterName.lower() == "remove_graph":
                # Initialize triples array if needed
                if not "remove_graph" in self.array:
                    self.array["remove_graph"] = []
                self.array[self.parameterName].append((self.triplesType, 
                                                       self.parameter))
            #elif self.parameterName.lower() == "triples":
            #    # Initialize triples array if needed
            #    if not "triples" in self.array:
            #        self.array["triples"] = []
            #    self.array[self.parameterName].append((self.triplesType, 
            #                                           self.parameter))
            else:
                self.array[self.parameterName] = self.parameter
            self.inParameter = False
        else:
            if self.inParameter:
                self.parameter = self.parameter + "</" + name + ">"
            return


ProtocolHandlers = {"TCP":TCPConnector, "LOCAL":LocalConnector, "HTTP":HTTPConnector}
