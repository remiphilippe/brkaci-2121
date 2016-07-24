__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from run_00_parameters import *
from vpx import *

if __name__ == '__main__':
    md = get_apic()

    # This interface is a provider
    print "Setting up VPX..."
    # Let's AP dn...
    vdc_vpx = md.lookupByDn(ap_dn)

    ## Monitor Configuration
    new_vpx_monitor(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, "myhttp", "HTTP")

    ## Service Group Configuration
    zone1_servicegroup_folder = new_vpx_servicegroup(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, 'servicegroup-web', 'HTTP')
    for web_rs in web_realservers:
        new_vpx_realserver(zone1_servicegroup_folder, zone1_dmz_graph_name, client_web_name, lb_node_name, web_rs['name'], web_rs['ip'], web_rs['port'])
    bind_vpx_monitor(zone1_dmz_graph_name, client_web_name, lb_node_name, zone1_servicegroup_folder, "myhttp")

    # Configure VPX Interface
    network_folder = new_vpx_network_container(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, 'Network')

    # SNIP
    new_vpx_snip(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, 'snip', vpx_networks['ip'], vpx_networks['mask'])

    # VIP
    new_vpx_vip(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, web_vip['name'], web_vip['ip'], web_vip['mask'])

    # Add static route
    new_vpx_route(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, vpx_ext_routes['destsubnet'], vpx_ext_routes['mask'], vpx_ext_routes['nexthop'])
    new_vpx_route(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, vpx_int_routes['destsubnet'], vpx_int_routes['mask'], vpx_int_routes['nexthop'])

    new_vpx_lb(vdc_vpx, zone1_dmz_graph_name, client_web_name, lb_node_name, web_vip['name'], 'servicegroup-web', 'HTTP', 80, web_vip['ip'], 'Network/web')
