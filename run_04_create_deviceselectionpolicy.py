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
    asa_contexts_web = None
    asa_contexts_web = [
        dict(
            connector="external",
            bd=asa_ext_bd,
            lif="external"
        ),
        dict(
            connector="internal",
            bd=dmz_bd,
            lif="dmz"
        )
    ]
    new_graph_context(entity, client_web_name, zone1_dmz_graph_name, asav_dn, asa_contexts_web, fw_node_name)

    ## Create Firewall Device Selection Policy for Web-App Contract
    asa_contexts_app = None
    asa_contexts_app = [
        dict(
            connector="external",
            bd=web_bd,
            lif="web"
        ),
        dict(
            connector="internal",
            bd=app_bd,
            lif="app"
        )
    ]
    new_graph_context(entity, web_app_name, zone2_fw_graph_name, asav_dn, asa_contexts_app, fw_node_name)

    ## Create Firewall Device Selection Policy for App-DB Contract
    asa_contexts_db = None
    asa_contexts_db = [
        dict(
            connector="external",
            bd=app_bd,
            lif="app"
        ),
        dict(
            connector="internal",
            bd=db_bd,
            lif="db"
        )
    ]
    new_graph_context(entity, app_db_name, zone2_fw_graph_name, asav_dn, asa_contexts_db, fw_node_name)

    ## Create VPX Device Selection Policy for Web-App Contract
    vpx_contexts = None
    vpx_contexts = [
        dict(
            connector="internal",
            bd=dmz_bd,
            lif="internal"
        ),
        dict(
            connector="external",
            bd=dmz_bd,
            lif="internal"
        )
    ]
    new_graph_context(entity, client_web_name, zone1_dmz_graph_name, vpx_dn, vpx_contexts, lb_node_name)
