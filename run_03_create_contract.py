__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from core import get_one
from network import new_contract

from run_00_parameters import *



if __name__ == '__main__':
    md = get_apic()
    entity = get_one(entity_dn)

    client_web = new_contract(entity, client_web_name, zone1_dmz_graph_name)
    web_app = new_contract(entity, web_app_name, zone2_adc_graph_name)
    app_db = new_contract(entity, app_db_name, zone2_adc_graph_name)