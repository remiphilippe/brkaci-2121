__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from service_graph import new_graph_context

from run_00_parameters import *

from core import get_one

if __name__ == '__main__':
    md = get_apic()
    entity = get_one(entity_dn)


    ## Create Firewall Device Selection Policy for Client-Web Contract
    asa_contexts = None
    asa_contexts = [
        dict(
            connector="external",
            bd=asa_ext_bd,
            lif="external"
        ),
        dict(
            connector="internal",
            bd=asa_int_bd,
            lif="internal"
        )
    ]
    new_graph_context(entity, client_web_name, zone1_dmz_graph_name, asav_dn, asa_contexts, fw_node_name)


    ## Create BIGIP Device Selection Policy for any contract and any service graph
    bigip_contexts = None
    bigip_contexts = [
        dict(
            connector="internal",
            bd=bigip_int_bd,
            lif="internal"
        ),
        dict(
            connector="external",
            bd=bigip_int_bd,
            lif="internal"
        )
    ]
    new_graph_context(entity, "any", "any", bigip_dn, bigip_contexts, lb_node_name)
