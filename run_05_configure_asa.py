__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from asav import *
from run_00_parameters import *

from asav import associate_asa_intf
from asav import asa_intf_cfg
from core import get_one

if __name__ == '__main__':
    md = get_apic()

    ## ACE - permit any
    ace_permit_any = dict(
        name='permit_any',
        action='permit',
        order='10',
        protocol='ip',
        dport=None,
        dstObject=dict(
            type='any',
            value='any'
        ),
        srcObject=dict(
            type='any',
            value='any'
        )
    )


    ############
    # Zone1    #
    ############
    # This interface is a provider
    print "Setting up ASAv for Zone1..."
    # Let's get all our EPGs...
    vdc_zone1 = md.lookupByDn(ap_dn)

    # Configure ASAv Interface
    asa_intf_cfg(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'externalIf', asa_ext_ip, 50)
    asa_intf_cfg(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'internalIf', asa_int_ip, 100)
    associate_asa_intf(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'external', 'externalIf')
    associate_asa_intf(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'internal', 'internalIf')

    # Create ACL
    vdc_zone1_in = new_asa_acl(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'ACI-in', [ace_permit_any])
    vdc_zone1_out = new_asa_acl(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'ACI-out', [ace_permit_any])

    # Interface Parameters for Zone1
    # TODO fix interface name
    print vdc_zone1.dn
    vdc_zone1_ext_intf = get_one(str(vdc_zone1.dn) + '/FI_C-Client-Web-G-FW-ADC-F-Firewall-N-externalIf')
    vdc_zone1_int_intf = get_one(str(vdc_zone1.dn) + '/FI_C-Client-Web-G-FW-ADC-F-Firewall-N-internalIf')

    # Apply ACL
    apply_asa_acl(vdc_zone1_ext_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, 'in', vdc_zone1_in.name)
    apply_asa_acl(vdc_zone1_ext_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, 'out', vdc_zone1_out.name)

    # Add static route
    new_asa_route(vdc_zone1_ext_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, '0.0.0.0', '0.0.0.0', '172.16.10.254')
    new_asa_route(vdc_zone1_int_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, '192.168.0.0', '255.255.0.0', '172.16.11.254')

    # Add network object
    item1 = [
        dict(
            type='host',
            value='172.16.11.110'
        ),
    ]
    new_asa_object(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'L3out-Client-Private', item1)

    # Add network object
    item2 = [
        dict(
            type='network',
            value='10.0.0.0/255.0.0.0'
        ),
    ]
    new_asa_object(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'L3out-Client', item2)

    # Add network object
    item3 = [
        dict(
            type='host',
            value='192.168.10.110'
        ),
    ]
    new_asa_object(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'Private-VIP', item3)

    # Add network object
    item4 = [
        dict(
            type='host',
            value='172.16.10.110'
        ),
    ]
    new_asa_object(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'Public-VIP', item4)

    # Add Net policy
    new_asa_natpolicy(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'NATPolicy')

    nat_lists = dict(
        name='NATRule',
        order='10',
        dstTrans=dict(
            mapped='Public-VIP',
            real='Private-VIP'
        ),
        srcTrans=dict(
            mapped='L3out-Client',
            real='L3out-Client-Private',
            nat_type='dynamic'
        )
    )

    # Add Net list
    new_asa_natlist(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, nat_lists)