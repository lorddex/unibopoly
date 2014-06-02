#!/usr/bin/python

import sys
from smart_m3.m3_kp_api import *
import uuid
import datetime
import os
import argparse
from time import time
from time import sleep
import random


owl_file= "files/monopolym3-ontology.owl"

# Args
if len(sys.argv) < 3:
    print "Wrong number of arguments. SIB ip and port required."
    sys.exit()

sib_ip = sys.argv[1]
sib_port = int(sys.argv[2])

# Initialize

kp_test =  m3_kp_api(PrintDebug = False,  IP=sib_ip, port=sib_port)
kp_test.clean_sib()
kp_test.load_rdfxml_insert_from_file(owl_file)

# Other triples
