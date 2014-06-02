from smart_m3.m3_kp import *
import uuid

rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
owl = "http://www.w3.org/2002/07/owl#"
xsd = "http://www.w3.org/2001/XMLSchema#"
rdfs = "http://www.w3.org/2000/01/rdf-schema#"
ns = "http://smartM3Lab/Ontology.owl#"

class SibLib(KP):

    # __init__: constructor method
    def __init__(self, server_ip, server_port):
        KP.__init__(self, str(uuid.uuid4()))
        self.ss_handle = ("X", (TCPConnector, (server_ip,server_port)))

    # join_sib: method to join the sib
    def join_sib(self):
        self.join(self.ss_handle)

    # leave_sib: method to leave the sib
    def leave_sib(self):
        self.leave(self.ss_handle)
                
    # insert: method to insert a triple in the sib
    def insert(self, triples):
        ins = self.CreateInsertTransaction(self.ss_handle)

        # NOTE: the following line calls the send function
        # without confirm, to avoid socket errors
        ins.send(triples, "python", confirm = True)

        self.CloseInsertTransaction(ins)

    # remove: method to remove a triple from the sib
    def remove(self, triples):
        rem = self.CreateRemoveTransaction(self.ss_handle)                                       
        rem.remove(triples)
        self.CloseRemoveTransaction(rem)

    # update: method to update a triple in the sib
    def update(self, triple_to_insert, triple_to_remove):
        # Update = Insert + Remove
        upd = self.CreateUpdateTransaction(self.ss_handle)                                        
        upd.update(triple_to_insert, "RDF-M3", triple_to_remove, "RDF-M3")
        self.CloseUpdateTransaction(upd)

    # create_subscription: method to subscribe to a triple
    def create_subscription(self, subject_field, predicate_field, object_field, HandlerClass):
        
        triple = [Triple(subject_field, predicate_field, object_field)]
        self.st = self.CreateSubscribeTransaction(self.ss_handle)

        initial_results = self.st.subscribe_rdf(triple, HandlerClass(self))
        print initial_results

    # create_triple: method used to create triple
    def create_triple(self, subject_field, predicate_field, object_field):
        triple = Triple(URI(ns + subject_field), 
                         URI(ns + predicate_field), 
                         URI(ns + object_field))
        return triple

    # execute_query: method to execute a query on the sib
    def execute_sparql_query(self, query):
        qt = self.CreateQueryTransaction(self.ss_handle)
        result = qt.sparql_query(query)
        self.CloseQueryTransaction(qt)
        return result

    def execute_rdf_query(self, query):
        self.rdf_query = self.CreateQueryTransaction(self.ss_handle)
        self.result_rdf_query = self.rdf_query.rdf_query(query)
        self.CloseQueryTransaction(self.rdf_query)
#        print str(self.result_rdf_query)
        return self.result_rdf_query

    # load_ontology: inject an ontology saved on a owl file into the sib
    def load_ontology(self, owl_file):
        ins = self.CreateInsertTransaction(self.ss_handle)
        ins.send(owl_file, encoding = "rdf-xml", confirm = True)
        self.CloseInsertTransaction(ins)
