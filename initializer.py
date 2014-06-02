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

# Initialize

kp_test =  m3_kp_api(PrintDebug = False,  IP="127.0.0.1", port=10020)
kp_test.clean_sib()
kp_test.load_rdfxml_insert_from_file(owl_file)

# Other triples
