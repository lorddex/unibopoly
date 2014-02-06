import sys
from smart_m3.m3_kp_api import *
import uuid
import time
import datetime
import os
import argparse


#Test configuration
sparql_subscribe = '\
PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#> \
PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> \
PREFIX owl:<http://www.w3.org/2002/07/owl#> \
PREFIX xsd:<http://www.w3.org/2001/XMLSchema#> \
PREFIX duca:<http://www.ducatienergia.com/SIIP2P.owl#> \
PREFIX ns1:<http://notauri/blank#> \
SELECT  ?Sensor_T ?T_Value \
WHERE { ?Sensor_T duca:HasSensorDataValue ?T_Value . \
	?Sensor_T duca:HasMeasurand duca:TEMPERATURE   \
      } \
'

file_rdf = "IoE_test_ontology.owl"


query_rdf_triples = [
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_549971617"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           None), #"None" is used insead of wildcard "sib:any",
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_829889475"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           None),
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_1583858572"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           None),
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_1891286719"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           None),
    ]  #"None" is used insead of wildcard "sib:any"

query_rdf_subscribe = [
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_549971617"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           None) #"None" is used insead of wildcard "sib:any"
    ]  #"None" is used insead of wildcard "sib:any"


sparql_query = '\
PREFIX duca:<http://www.ducatienergia.com/SIIP2P.owl#> \
SELECT  ?T_Value_1 ?T_Value_2 \
WHERE { \
	{ duca:SensorData_549971617 duca:HasSensorDataValue ?T_Value_1}  \
	UNION \
        { duca:SensorData_829889475 duca:HasSensorDataValue ?T_Value_2}  \
      } \
'

insert_rdf_triples = [
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_549971617"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           Literal("42")) 
    ]

delete_rdf_triples = [
    Triple(URI("http://www.ducatienergia.com/SIIP2P.owl#SensorData_549971617"), 
           URI("http://www.ducatienergia.com/SIIP2P.owl#HasSensorDataValue"), 
           None) 
    ] #"None" is used for wildcard even in remove operation.



insert_rdf_stupid_triples = [
    Triple(URI("http://ns#subject0"), 
           URI("http://ns#predicate0"), 
           URI("http://ns#objectURI")),
    Triple(URI("http://ns#subject1"), 
           URI("http://ns#predicate2"), 
           URI("http://ns#objectURI")),
    Triple(URI("http://ns#subject2"), 
           URI("http://ns#predicate2"), 
           URI("http://ns#objectLiteral"))
    ]


remove_rdf_stupid_triples_wildcards = [
    Triple(URI("http://ns#subject0"), 
           URI("http://ns#predicate0"), 
           URI("http://ns#objectURI")),
    Triple(URI("http://ns#subject1"), 
           None, 
           URI("http://ns#objectURI")),
    Triple(None, 
           URI("http://ns#predicate2"), 
           None) #"None" is used insead of wildcard "sib:any"
    ]

###Specific Example Code

#RDF and SPARQL subscriptions Handlers Example Threads ###############################
class RDF_handler():
    def __init__(self, KP = None):
        self.KP=KP

    def handle(self, added, removed):
        sys.stderr.write("\n\nRDF Subscription Indication:")
        for el in added:
            sys.stderr.write("\nAdded")
            sys.stderr.write("\n[%s][%s][%s]" % (str(el[0]), str(el[1]), str(el[2])))

        for el in removed:
            sys.stderr.write("\nRemoved")
            sys.stderr.write("\n[%s][%s][%s]" % (str(el[0]), str(el[1]), str(el[2])))

        sys.stderr.write("\n\n")

class sparql_handler():
    def __init__(self, KP = None):
        self.KP=KP

    def handle(self, added, removed):

        print "\n\nSparql Subscription Indication:"
        for results in added:
            print "Added"
            for result in results:
                print "     var [%s] type [%s] value [%s]" % (result[0], 
                                                              result[1],
                                                              result[2])

        for results in removed:
            print "Removed"
            for result in results:
                print "     var [%s] type [%s] value [%s]" % (result[0], 
                                                              result[1],
                                                              result[2])

#Main Code ##################################################################################

if __name__ == "__main__":

    print "\nExamples on m3_kp. \n\n"
    print "(You must have loaded a sib in this host,"
    print "if not you can do it typing first 'redsibd' "
    print "and 'sib-tcp' in two different terminal windows)\n\n"

    raw_input("\nContinue with a key..\n")

    kp_test =  m3_kp_api(PrintDebug = True)

	##############################################################################
    kp_test.clean_sib()

    raw_input("\nContinue with a key..\n")

	##############################################################################
    
    kp_test.load_rdfxml_insert_from_file(file_rdf)
    raw_input("\nContinue with a key..\n")
    kp_test.load_rdf_insert(insert_rdf_stupid_triples)
    raw_input("\nContinue with a key..\n")
    kp_test.load_rdf_remove(remove_rdf_stupid_triples_wildcards)
    raw_input("\nContinue with a key..\n")

	##############################################################################

	#Generate an handler first
    handler_RDF_subscribe=RDF_handler(kp_test)
	#Subscribe
    rdf_sub=kp_test.load_subscribe_RDF(query_rdf_subscribe, handler_RDF_subscribe)
    print "First RDF Subscribe Result (Query)"
    for el in kp_test.result_RDF_first_sub:
        print "[%s][%s][%s]" % (str(el[0]), str(el[1]), str(el[2]))
    print "\n\n"

    raw_input("\nContinue with a key..\n")

	##############################################################################

	#Generate an handler first
#    handler_sparql_subscribe=sparql_handler(kp_test)
	#Subscribe
#    sparql_sub=kp_test.load_subscribe_sparql(sparql_subscribe, handler_sparql_subscribe)
#    print "First Sparql Subscribe Result (Query)"
#    for res in kp_test.result_sparql_first_sub:
#        for result in res:
#            print "     var [%s] type [%s] value [%s]" % (result[0], 
#                                                          result[1],
#                                                          result[2])
#    print "\n\n"
#
#    raw_input("\nContinue with a key..\n")

	##############################################################################

    kp_test.load_query_rdf(query_rdf_triples)
    print "Query RDF results:"
    for el in kp_test.result_rdf_query:
        print "[%s][%s][%s]" % (str(el[0]), str(el[1]), str(el[2]))
    raw_input("\nContinue with a key..\n")

	##############################################################################

    kp_test.load_query_sparql(sparql_query)
    print "Getting the same values doing a SPARQL query, results:"
    for res in kp_test.result_sparql_query:
        for result in res:
            if str(result[1]) != "unbound":
                print "     var [%s] type [%s] value [%s]" % (result[0], 
                                                              result[1],
                                                              result[2])

    print "\n\n"

	
	##############################################################################

    print "A triple will now be updated, pay attention on the reaction"
    print "of subscriptions handlers threads"
    raw_input("\nContinue with a key..\n")
    
    kp_test.load_rdf_update(insert_rdf_triples, delete_rdf_triples)

	##############################################################################
    
    time.sleep(1);
    raw_input("\n\nTest succesfully loaded. \nType a key to end.\n\n")
    
	##############################################################################
	# Unsubscriptions and leave (OPTIONAL)
    
    kp_test.load_unsubscribe(rdf_sub)
#    kp_test.load_unsubscribe(sparql_sub)
    kp_test.leave()
	##############################################################################

    print "\nBye.\n"
    raise os._exit(99)
