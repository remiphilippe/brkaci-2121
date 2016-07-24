__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from run_00_parameters import *
from network import attach_contract


if __name__ == '__main__':
    md = get_apic()

    #######################
    # Lookup              #
    #######################
    web = md.lookupByDn(epg_base_dn + web_name)
    app = md.lookupByDn(epg_base_dn + app_name)
    db = md.lookupByDn(epg_base_dn + db_name)
    l3out = md.lookupByDn(l3out_base_dn + 'L3out/' + "instP-L3out")

    # client - web
    attach_contract(client_web_name, l3out, 'consumer')
    attach_contract(client_web_name, web, 'provider')

    # web-app
    attach_contract(web_app_name, web, 'consumer')
    attach_contract(web_app_name, app, 'provider')

    # app-db
    attach_contract(app_db_name, app, 'consumer')
    attach_contract(app_db_name, db, 'provider')

