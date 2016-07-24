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
    print "Setting up ASAv for Zone1..."
    # Let's get all our EPGs...
    vdc_zone1 = md.lookupByDn(ap_dn)

    # Configure ASAv Interface
    asa_intf_cfg(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'externalIf', asa_ext_ip, 0)
    asa_intf_cfg(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'dmz', asa_dmz_ip, 20)
    associate_asa_intf(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'external', 'externalIf')
    associate_asa_intf(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'internal', 'dmz')

    # Create ACL
    vdc_zone1_in = new_asa_acl(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'ACI-in-ext', [ace_permit_any])
    vdc_zone1_in2 = new_asa_acl(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'ACI-in-dmz', [ace_permit_any])

    # Interface Parameters for Zone1
    vdc_zone1_ext_intf = get_one(str(vdc_zone1.dn) + '/FI_C-Client-Web-G-FW-ADC-F-Firewall-N-externalIf')
    vdc_zone1_int_intf = get_one(str(vdc_zone1.dn) + '/FI_C-Client-Web-G-FW-ADC-F-Firewall-N-dmz')

    # Apply ACL
    apply_asa_acl(vdc_zone1_ext_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, 'in', vdc_zone1_in.name)
    apply_asa_acl(vdc_zone1_int_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, 'in', vdc_zone1_in2.name)

    # Add static route
    new_asa_route(vdc_zone1_ext_intf, zone1_dmz_graph_name, client_web_name, fw_node_name, '10.0.0.0', '255.0.0.0', '192.168.100.254')

    # Add network object
    item1 = [
        dict(
            type='host',
            value='192.168.10.110'
        ),
    ]
    new_asa_object(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'Private-VIP', item1)

    # Add network object
    item2 = [
        dict(
            type='host',
            value='192.168.100.110'
        ),
    ]
    new_asa_object(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'Public-VIP', item2)

    # Add NAT policy
    new_asa_natpolicy(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, 'NATPolicy')
    nat_lists = dict(
        name='NATRule',
        order='10',
        dstTrans=dict(
            mapped='Public-VIP',
            real='Private-VIP'
        )
    )
    new_asa_natlist(vdc_zone1, zone1_dmz_graph_name, client_web_name, fw_node_name, nat_lists)


    ############
    # Zone2   #
    ############
    print "Setting up ASAv for Zone2..."

    # Configure ASAv Interface
    asa_intf_cfg(vdc_zone1, zone2_fw_graph_name, web_app_name, fw_node_name, 'web', asa_web_ip, 40)
    asa_intf_cfg(vdc_zone1, zone2_fw_graph_name, web_app_name, fw_node_name, 'app', asa_app_ip, 60)
    associate_asa_intf(vdc_zone1, zone2_fw_graph_name, web_app_name, fw_node_name, 'external', 'web')
    associate_asa_intf(vdc_zone1, zone2_fw_graph_name, web_app_name, fw_node_name, 'internal', 'app')

    # Create ACL
    vdc_zone2_in = new_asa_acl(vdc_zone1, zone2_fw_graph_name, web_app_name, fw_node_name, 'ACI-in-web', [ace_permit_any])

    # Interface Parameters for Zone1
    vdc_zone2_ext_intf = get_one(str(vdc_zone1.dn) + '/FI_C-Web-App-G-FW-F-Firewall-N-web')

    # Apply ACL
    apply_asa_acl(vdc_zone2_ext_intf, zone2_fw_graph_name, web_app_name, fw_node_name, 'in', vdc_zone2_in.name)


    ############
    # Zone3   #
    ############
    print "Setting up ASAv for Zone3..."

    # Configure ASAv Interface
    asa_intf_cfg(vdc_zone1, zone2_fw_graph_name, app_db_name, fw_node_name, 'app', asa_app_ip, 60)
    asa_intf_cfg(vdc_zone1, zone2_fw_graph_name, app_db_name, fw_node_name, 'db', asa_db_ip, 80)
    associate_asa_intf(vdc_zone1, zone2_fw_graph_name, app_db_name, fw_node_name, 'external', 'app')
    associate_asa_intf(vdc_zone1, zone2_fw_graph_name, app_db_name, fw_node_name, 'internal', 'db')

    # Create ACL
    vdc_zone3_in = new_asa_acl(vdc_zone1, zone2_fw_graph_name, app_db_name, fw_node_name, 'ACI-in-app', [ace_permit_any])

    # Interface Parameters for Zone1
    vdc_zone3_ext_intf = get_one(str(vdc_zone1.dn) + '/FI_C-App-DB-G-FW-F-Firewall-N-app')

    # Apply ACL
    apply_asa_acl(vdc_zone3_ext_intf, zone2_fw_graph_name, app_db_name, fw_node_name, 'in', vdc_zone3_in.name)
