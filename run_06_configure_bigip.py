__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from run_00_parameters import *

from bigip import *

if __name__ == '__main__':
    md = get_apic()

    # This interface is a provider
    print "Setting up BIGIP..."
    # Let's AP dn...
    vdc_zone1 = md.lookupByDn(ap_dn)

    # Configure BIGIP Interface
    # TODO fix interface name
    new_bigip_network(vdc_zone1, 'any', 'any', lb_node_name, bigip_networks)
    add_bigip_route(vdc_zone1, 'any', 'any', lb_node_name, bigip_routes)
    apply_bigip_network(vdc_zone1, 'any', 'any', lb_node_name, bigip_networks['network_name'])

    # Configure BIGIP VIP for Web
    create_listner(vdc_zone1, zone1_dmz_graph_name, client_web_name, lb_node_name, web_name, web_vip['ip'], web_vip['port'])
    create_localtraffic(vdc_zone1, zone1_dmz_graph_name, client_web_name, lb_node_name, web_name)
    create_pool(vdc_zone1, zone1_dmz_graph_name, client_web_name, lb_node_name, web_name, web_vip['port'], 'LocalTraffic-' + web_name + '/Pool-' + web_name)

    # Configure BIGIP VIP for App
    create_listner(vdc_zone1, zone2_adc_graph_name, web_app_name, lb_node_name, app_name, app_vip['ip'], app_vip['port'])
    create_localtraffic(vdc_zone1, zone2_adc_graph_name, web_app_name, lb_node_name, app_name)
    create_pool(vdc_zone1, zone2_adc_graph_name, web_app_name, lb_node_name, app_name, app_vip['port'], 'LocalTraffic-' + app_name + '/Pool-' + app_name)

    # Configure BIGIP VIP for DB
    create_listner(vdc_zone1, zone2_adc_graph_name, app_db_name, lb_node_name, db_name, db_vip['ip'], db_vip['port'])
    create_localtraffic(vdc_zone1, zone2_adc_graph_name, app_db_name, lb_node_name, db_name)
    create_pool(vdc_zone1, zone2_adc_graph_name, app_db_name, lb_node_name, db_name, db_vip['port'], 'LocalTraffic-' + db_name + '/Pool-' + db_name)
