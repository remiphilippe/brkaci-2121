__author__ = 'mihiguch'
## reuse rephilip's entity.py.  modify parameter for the demo setup


# Core APIC imports
import core
from core import commit
from core import get_vmm
from core import get_one

# Network imports
from network import new_l2bd_routing
from network import new_l2bd_routing_adv
from network import new_context
from network import new_epg
from network import new_ap

from tenant import new_tenant
from l3out import new_l3out

# ACI Model imports
from cobra.model.fv import RsDomAtt
from cobra.model.fv import RsBd


def new_entity(name, devtest=True, l3out_vlan=None):
    """
    Create a new tenant entity
    :param name: Name of the entity
    :type name: str

    :param l3out_vlan: L3out VLAN
    :type l3out_vlan: int

    :return: Tenant
    :rtype: cobra.model.fv.Tenant
    """
    print "Let's create a new Entity"
    networks = list()
    bd_networks = list()
    if devtest:
        vmm_tdn = get_vmm(True)
    else:
        vmm_tdn = 'uni/vmmp-VMware/dom-VMM-ACI-vDS'

    # Graph Names
    zone1_dmz_graph_name = "FW-ADC"
    zone2_adc_graph_name = "ADC"

    # Tenant
    tenant = new_tenant(name)
    # Context
    context = new_context(tenant, 'VRF1')
    # Outside
    outside_ap = new_ap(tenant, 'ANP')

    # create EPG
    web_network = dict(
        name='Web',
        svi ='192.168.11.254/24',
        scope = 'private'
    )
    networks.append(web_network)

    app_network = dict(
        name='App',
        svi ='192.168.12.254/24',
        scope = 'private'
    )
    networks.append(app_network)

    db_network = dict(
        name='DB',
        svi ='192.168.13.254/24',
        scope = 'private'
    )
    networks.append(db_network)

    for network in networks:
        print "Creating the network " + network['name'] + "..."
        bd_name = network['name']
        epg_name = network['name']
        svi_ip = network['svi']

        if network['scope'] == 'public':
            bd = new_l2bd_routing_adv(tenant, bd_name, context, svi_ip, 'L3out')
        else:
            bd = new_l2bd_routing(tenant, bd_name, context, svi_ip)
        epg = new_epg(outside_ap, epg_name)
        RsBd(epg, tnFvBDName=bd_name)

        print "Attaching the VMM domain " + vmm_tdn + "..."
        RsDomAtt(epg,
                 instrImedcy='immediate',
                 tDn=vmm_tdn,
                 resImedcy='immediate')

    # create BD
    asa_ext_network = dict(
        name='ASA-external',
        svi ='172.16.10.254/24',
        scope = 'public'
    )
    bd_networks.append(asa_ext_network)

    asa_int_network = dict(
        name='ASA-internal',
        svi ='172.16.11.254/24',
        scope = 'private'
    )
    bd_networks.append(asa_int_network)

    lb_network = dict(
        name='LB',
        svi ='192.168.10.254/24',
        scope = 'private'
    )
    bd_networks.append(lb_network)


    for bd_network in bd_networks:
        print "Creating the BD network " + bd_network['name'] + "..."
        bd_name = bd_network['name']
        svi_ip = bd_network['svi']

        if bd_network['scope'] == 'public':
            bd = new_l2bd_routing_adv(tenant, bd_name, context, svi_ip, 'L3out')
        else:
            bd = new_l2bd_routing(tenant, bd_name, context, svi_ip)

    # create L3out
    new_l3out(tenant, 'L3out', context, l3out_vlan)

    commit(tenant)
    return tenant
