from smart_m3.m3_kp import KP, Triple, URI, Literal, bNode, TCPConnector
import uuid

###Main Library Class
class m3_kp_api():
################################ Join/Leave OPs  ###########################
    def __init__(self, 
		 PrintDebug = False, 
		 IP = "localhost", 
		 port = 10010, 
		 SS_name = "X", 
		 KP_name = None):
	    
        self.PrintDebug = PrintDebug

        if (self.PrintDebug == True):
            print "Joining SIB on instance creation.. "

        if (KP_name == None):
            self.theNode = KP("KP_M3_"+ str(uuid.uuid4()))
        else:
            self.theNode = KP(KP_name)					

        self.theSmartSpace = (SS_name, (TCPConnector, ( IP, port )))
        self.theNode.join(self.theSmartSpace)

        if (self.PrintDebug == True):
            print "Done.\n"
	

    def leave(self):
        if (self.PrintDebug == True):
            print "Leaving SIB.. "

        ans = self.theNode.leave(self.theSmartSpace)

        if (self.PrintDebug == True):
            print "Done.\n"

	################################ Ins/Rm/Upd OPs  #############################

    def load_rdfxml_insert_from_file (self, file_rdf_in):
        if (self.PrintDebug == True):
            print "Inserting RDF-XML from file :  " + file_rdf_in 

        self.test_rdfxml = self.theNode.CreateInsertTransaction(self.theSmartSpace)
        self.test_rdfxml.insert(file_rdf_in, encoding = "rdf-xml", confirm = True)
        self.theNode.CloseInsertTransaction(self.test_rdfxml)

        if (self.PrintDebug == True):
            print "Done.\n"

    def load_rdf_insert (self, triples_insert_in ):
        if (self.PrintDebug == True):
            print "Inserting RDF-M3 triples :  "
            print "Inserting: " + str(triples_insert_in)

        self.test_rdf_insert = self.theNode.CreateInsertTransaction(self.theSmartSpace)
        self.test_rdf_insert.insert(triples_insert_in,"rdf-m3", confirm = True)
        self.theNode.CloseInsertTransaction(self.test_rdf_insert)

        if (self.PrintDebug == True):
            print "Done.\n"
	
    def load_rdf_remove (self, triples_remove_in):
        if (self.PrintDebug == True):
            print "Removing RDF-M3 triples :  "
            print "Removing:  " + str(triples_remove_in)

        self.test_rdf_remove = self.theNode.CreateRemoveTransaction(self.theSmartSpace)
        self.test_rdf_remove.remove(triples_remove_in, "rdf-m3", confirm = True)
        self.theNode.CloseRemoveTransaction(self.test_rdf_remove)

        if (self.PrintDebug == True):
            print "Done.\n"

    def load_rdf_update (self, triples_insert_in , triples_remove_in):
        if (self.PrintDebug == True):
            print "Updating RDF-M3 triples :  "
            print "Inserting: " + str(triples_insert_in)
            print "Removing:  " + str(triples_remove_in)

        self.test_rdf_update = self.theNode.CreateUpdateTransaction(self.theSmartSpace)
        self.test_rdf_update.update(triples_insert_in, 
                                    "rdf-m3", 
                                    triples_remove_in, 
                                    "rdf-m3", 
                                    confirm = True)
        self.theNode.CloseUpdateTransaction(self.test_rdf_update)

        if (self.PrintDebug == True):
            print "Done.\n"

    # 3 Wildcard Remove will clean the SIB
    def clean_sib (self):
        if (self.PrintDebug == True):
            print "Cleaning the sib.. "

        all_wc = [Triple(None, None, None) ]
        self.cleaner = self.theNode.CreateRemoveTransaction(self.theSmartSpace)
        self.cleaner.remove(all_wc, "rdf-m3", confirm = True)
        self.theNode.CloseRemoveTransaction(self.cleaner)

        if (self.PrintDebug == True):
            print "Done.\n"

	################################ Subscribe OPs ###############################

    def load_subscribe_RDF(self, query_triples_in, handler):	
        if (self.PrintDebug == True):			
            print "Loading RDF Subscribe : \n" + str(query_triples_in) 

        self.test_RDF = self.theNode.CreateSubscribeTransaction(self.theSmartSpace)
        self.result_RDF_first_sub = self.test_RDF.subscribe_rdf(query_triples_in, handler)

        if (self.PrintDebug == True):
            print "Done.\n"

        return self.test_RDF

    def load_subscribe_sparql(self, query_str, handler):		
        if (self.PrintDebug == True):		
            print "Loading Sparql Subscribe : \n" + query_str 

        self.test_sparql = self.theNode.CreateSubscribeTransaction(self.theSmartSpace)
        self.result_sparql_first_sub = self.test_sparql.subscribe_sparql(query_str, handler)

        if (self.PrintDebug == True):
            print "Done.\n"

        return self.test_sparql

	################################ Unsubscribe OPs ###############################

    def load_unsubscribe(self, sub):	
        if (self.PrintDebug == True):
            print "Unsubscribing.."

        self.theNode.CloseSubscribeTransaction(sub)

        if (self.PrintDebug == True):
            print "Done."

	################################ Query OPs ###################################

    def load_query_rdf (self, query_triples_in):
        if (self.PrintDebug == True):
            print "Loading RDF query : \n "+ str(query_triples_in) 

        self.rdf_query = self.theNode.CreateQueryTransaction(self.theSmartSpace)
        self.result_rdf_query = self.rdf_query.rdf_query(query_triples_in)
        self.theNode.CloseQueryTransaction(self.rdf_query)
        
        if (self.PrintDebug == True):
            print "Done.\n"
	
    def load_query_sparql (self, query_sparql_in):
        if (self.PrintDebug == True):
            print "Loading SPARQL query : \n"+ str(query_sparql_in) 

        self.sparql_query = self.theNode.CreateQueryTransaction(self.theSmartSpace)
        self.result_sparql_query = self.sparql_query.sparql_query(query_sparql_in)
        self.theNode.CloseQueryTransaction(self.sparql_query)

        if (self.PrintDebug == True):
            print "Done.\n"

	##############################################################################

