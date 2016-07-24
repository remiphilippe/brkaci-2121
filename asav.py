__author__ = 'rephilip'
## reuse rephilip's asa.py. Add NAT related function

# Core APIC imports
from core import commit
from core import get_folder_by_key

# Device imports
from device import new_logical_device
from device import new_concrete_device

# ACI Model imports
from cobra.model.vns import DevFolder
from cobra.model.vns import DevParam
from cobra.model.vns import FolderInst
from cobra.model.vns import ParamInst
from cobra.model.vns import CfgRelInst

def new_asav(tenant, name, cluster_ip, devices, port, login, password):
    """
    Create ASAv for FEDnet environment
    :param tenant: Entity
    :type tenant: cobra.model.fv.Tenant

    :param name: ASAv Logical Cluster Name
    :type name: str

    :param cluster_ip: ASAv Logical Cluster IP
    :type cluster_ip: str

    :param devices: ASAv Instances, example:
    asav = [
        dict(
            name='TAV2-FW-01',
            ip='10.238.134.13',
            unit='primary',
            stdbyIP='10.238.134.14'
        ),
        dict(
            name='TAV2-FW-02',
            ip='10.238.134.14',
            unit='secondary'
        )
    ]

    :type devices: list

    :param port: ASAv Management Port
    :type port: int

    :param login: ASAv admin username
    :type login: str

    :param password: ASAv admin password
    :type password: str

    :return: Logical Device
    :rtype: cobra.model.vns.LDevVip
    """
    print "Creating a new ASAv for tenant " + tenant.name + "..."
    # Logical Interfaces
    linterfaces = [
        dict(
            name='outside',
            type='external'
        ),
        dict(
            name='vpx',
            type='internal'
        ),
        dict(
            name='dmz',
            type='internal'
        ),
        dict(
            name='zone1',
            type='internal'
        ),
        dict(
            name='zone2',
            type='internal'
        ),
        dict(
            name='zone3',
            type='internal'
        ),
        dict(
            name='fover_lan',
            type='failover_lan'
        ),
        dict(
            name='fover_link',
            type='failover_link'
        )
    ]

    logical = new_logical_device(tenant, name, 'asav', cluster_ip, port, login, password, linterfaces)

    # Concrete Interfaces
    # Network adapter 1  - Mgmt0/0 - Mgmt
    # Network adapter 2  - Gig 0/0 - Outside
    # Network adapter 3  - Gig 0/1 - VPX
    # Network adapter 4  - Gig 0/2 - DMZ
    # Network adapter 5  - Gig 0/3 - Zone 1
    # Network adapter 6  - Gig 0/4 - Zone 2
    # Network adapter 7  - Gig 0/5 - Zone 3
    # Network adapter 8  - Gig 0/6 - N/A
    # Network adapter 9  - Gig 0/7 - FO State
    # Network adapter 10 - Gig 0/8 - FO LAN

    cinterfaces = [
        dict(
            vnic='Network adapter 2',
            physical='Gig0/0',
            logical='outside'
        ),
        dict(
            vnic='Network adapter 3',
            physical='Gig0/1',
            logical='vpx'
        ),
        dict(
            vnic='Network adapter 4',
            physical='Gig0/2',
            logical='dmz'
        ),
        dict(
            vnic='Network adapter 5',
            physical='Gig0/3',
            logical='zone1'
        ),
        dict(
            vnic='Network adapter 6',
            physical='Gig0/4',
            logical='zone2'
        ),
        dict(
            vnic='Network adapter 7',
            physical='Gig0/5',
            logical='zone3'
        ),
        dict(
            vnic='Network adapter 9',
            physical='Gig0/7',
            logical='fover_link'
        ),
        dict(
            vnic='Network adapter 10',
            physical='Gig0/8',
            logical='fover_lan'
        )
    ]

    # devices is a list of dictionaries
    for device in devices:
        ip = device['ip']
        name = device['name']
        concrete = new_concrete_device(logical, name, ip, port, login, password, cinterfaces)

        if 'unit' in device:
            unit = device['unit']
        else:
            unit = None

        if 'stdby_ip' in device:
            stdby_ip = device['stdby_ip']
        else:
            stdby_ip = None

        enable_asa_ha(concrete, unit, stdby_ip)

    return logical

def enable_asa_ha(concrete, unit, stdby_ip):
    """
    Enable ASA High Availability
    :param concrete: Concrete device
    :type concrete: cobra.model.vns.CDev

    :param unit: Unit role (primary, secondary)
    :type unit: str

    :param stdby_ip: Standby IP
    :type unit: str

    :return: None
    """
    print "Configuring HA for Concrete device " + concrete.name + "..."
    # Configure HA
    if unit == 'secondary' or (unit == 'primary' and stdby_ip):
        failover_config = DevFolder(concrete,
                                    key='FailoverConfig',
                                    name='FailoverConfig')
        DevParam(failover_config,
                 key='failover',
                 name='failover',
                 value='enable')

        DevParam(failover_config,
                 key='lan_unit',
                 name='lan_unit',
                 value=unit)

        failover_lan_interface = DevFolder(failover_config,
                                           key='failover_lan_interface',
                                           name='failover_lan_interface')
        DevParam(failover_lan_interface,
                 key='interface_name',
                 name='interface_name',
                 value='fover_lan')

        failover_link_interface = DevFolder(failover_config,
                                           key='failover_link_interface',
                                           name='failover_link_interface')
        DevParam(failover_link_interface,
                 key='interface_name',
                 name='interface_name',
                 value='fover_link')

        if stdby_ip:
            mgmt_standby_ip = DevFolder(failover_config,
                                        key='mgmt_standby_ip',
                                        name='mgmt_standby_ip')
            DevParam(mgmt_standby_ip,
                     key='standby_ip',
                     name='standby_ip',
                     value=stdby_ip)

        commit(failover_config)

        print "Configuration Failover LAN IP..."
        failover_lan_ip = DevFolder(failover_config,
                                key='failover_ip',
                                name='failover_lan_ip')
        DevParam(failover_lan_ip,
                 key='standby_ip',
                 name='standby_ip',
                 value='192.168.143.2')
        DevParam(failover_lan_ip,
                 key='active_ip',
                 name='active_ip',
                 value='192.168.143.1')
        DevParam(failover_lan_ip,
                 key='interface_name',
                 name='interface_name',
                 value='fover_lan')
        DevParam(failover_lan_ip,
                 key='netmask',
                 name='netmask',
                 value='255.255.255.252')
        commit(failover_lan_ip)

        print "Configuration Failover LINK IP..."
        failover_link_ip = DevFolder(failover_config,
                                key='failover_ip',
                                name='failover_link_ip')
        DevParam(failover_link_ip,
                 key='standby_ip',
                 name='standby_ip',
                 value='192.168.143.6')
        DevParam(failover_link_ip,
                 key='active_ip',
                 name='active_ip',
                 value='192.168.143.5')
        DevParam(failover_link_ip,
                 key='interface_name',
                 name='interface_name',
                 value='fover_link')
        DevParam(failover_link_ip,
                 key='netmask',
                 name='netmask',
                 value='255.255.255.252')
        commit(failover_link_ip)


def new_asa_object(epg, graph_template_name, contract_name, node_name, object_name, items):
    """
    Create a network object or object group
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param object_name: Network Object or Object Group name
    :type object_name: str

    :param items: Elements part of this Network Object or Object Group, example:
    items = [
        dict(
            type='host',
            value='1.1.1.1'
        ),
        dict(
            type='network',
            value='1.1.1.1/24'
        ),
        dict(
            type='range',
            value='1.1.1.1-2.2.2.2'
        ),
        dict(
            type='fqdn',
            value='v4 remiphilippe.fr'
        ),
        dict(
            type='object',
            value='myObject'
        ),
        dict(
            type='group',
            value='myObjectGroup'
        )
    ]
    :type items: list

    :return: Object or Object Group folder
    :rtype: cobra.model.vns.FolderInst
    """

    if len(items) == 1:
        key = 'NetworkObject'
    else:
        key = 'NetworkObjectGroup'

    object_folder = FolderInst(epg,
                               name=object_name,
                               key=key,
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)
    for item in items:
        # Type
        # host_ip_address = IP address format 1.1.1.1
        # network_ip_address = Network range format 1.1.1.1/24
        # ip_address_range = IP range format 1.1.1.1-1.1.1.2
        # fqdn = FQDN format v4 remiphilippe.fr or v6 remiphilippe.fr
        t = item['type']

        if t == 'host':
            type = 'host_ip_address'
        elif t == 'range':
            type = 'ip_address_range'
        elif t == 'network':
            type = 'network_ip_address'
        elif t == 'fqdn':
            type = 'fqdn'
        elif t == 'object':
            type = 'object_name'
        elif t == 'group':
            type = 'object_group_name'

        value = item['value']

        ParamInst(object_folder,
                  name=type,
                  key=type,
                  value=value)

    commit(object_folder)
    return object_folder


def new_asa_ace(acl, graph_template_name, contract_name, node_name, ace_name, action, order, protocol, dport, dst_object, src_object):
    """
    Create an ASA ACL Access Control Entry (ACE)
    :param acl: ACL container folder
    :type acl: cobra.model.vns.FolderInst

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param ace_name: Name of the ACE
    :type ace_name: str

    :param action: Action of the ACE (permit, deny)
    :type action: str

    :param order: Order of the ACE
    :type order: int

    :param protocol: Protocol
    :type protocol: str

    :param dport: Optional - Destination Port
    :type dport: int

    :param dst_object: Destination Object example:
    any = dict(
        type='any',
        value='any'
    )

    any4 = dict(
        type='any',
        value='any4'
    )

    any6 = dict(
        type='any',
        value='any6'
    )

    object = dict(
        type='object',
        value='object-name'
    )

    group = dict(
        type='group',
        value='objectgroup-name'
    )
    :type dst_object: dict

    :param src_object: Source Object, see Destination Object for examples
    :type src_object: dict

    :return: ACE folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Creating a new ACE ' + ace_name + '...'
    ace_folder = FolderInst(acl,
                            name=ace_name,
                            key='AccessControlEntry',
                            nodeNameOrLbl=node_name,
                            graphNameOrLbl=graph_template_name,
                            ctrctNameOrLbl=contract_name)

    ParamInst(ace_folder,
              name='action-' + str(action),
              key='action',
              value=action)

    ParamInst(ace_folder,
              name='order-' + str(order),
              key='order',
              value=order)

    protocol_folder = FolderInst(ace_folder,
                                 name='protocol-' + str(protocol),
                                 key='protocol',
                                 nodeNameOrLbl=node_name,
                                 graphNameOrLbl=graph_template_name,
                                 ctrctNameOrLbl=contract_name)
    ParamInst(protocol_folder,
              name=protocol,
              key='name_number',
              value=protocol)

    if dport:
        dst_svc_folder = FolderInst(ace_folder,
                                    name='destination_service',
                                    key='destination_service',
                                    nodeNameOrLbl=node_name,
                                    graphNameOrLbl=graph_template_name,
                                    ctrctNameOrLbl=contract_name)
        ParamInst(dst_svc_folder,
                  name='operator',
                  key='operator',
                  value='eq')

        ParamInst(dst_svc_folder,
                  name='low_port',
                  key='low_port',
                  value=dport)

    dst_ip_folder = FolderInst(ace_folder,
                               name='destination_address',
                               key='destination_address',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    # key = any, object_name or object_group_name
    # value = any, any4 or any6
    t = dst_object['type']
    dst_value = dst_object['value']

    if t == 'any':
        dst_type = 'any'
    elif t == 'object':
        dst_type = 'object_name'
    elif t == 'group':
        dst_type = 'object_group_name'

    ParamInst(dst_ip_folder,
          name=dst_type,
          key=dst_type,
          value=dst_value)


    src_ip_folder = FolderInst(ace_folder,
                               name='source_address',
                               key='source_address',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    # key = any, object_name or object_group_name
    # value = any, any4 or any6
    s = src_object['type']
    src_value = src_object['value']

    if s == 'any':
        src_type = 'any'
    elif s == 'object':
        src_type = 'object_name'
    elif s == 'group':
        src_type = 'object_group_name'

    ParamInst(src_ip_folder,
          name=src_type,
          key=src_type,
          value=src_value)

    commit(ace_folder)
    return ace_folder


def new_asa_acl(epg, graph_template_name, contract_name, node_name, acl_name, access_entries):
    """
    Create an ASA Access Control List (ACL)
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param acl_name: ACL Name
    :type acl_name: str

    :param access_entries: List of ACE, example:
    vdc_1_zone1_ace_1 = dict(
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
    :type access_entries: list

    :return: ACL Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Creating a new ACL ' + acl_name + '...'
    order = 0

    acl_folder = FolderInst(epg,
                           name=acl_name,
                           key='AccessList',
                           nodeNameOrLbl=node_name,
                           graphNameOrLbl=graph_template_name,
                           ctrctNameOrLbl=contract_name)

    commit(acl_folder)

    for ace in access_entries:
        name = ace['name']
        action = ace['action']
        order += 10
        protocol = ace['protocol']
        dport = ace['dport']
        dst_object = ace['dstObject']
        src_object = ace['srcObject']

        new_asa_ace(acl_folder, graph_template_name, contract_name, node_name, name, action, order, protocol, dport, dst_object, src_object)

    return acl_folder


def new_asa_route(intf_folder, graph_template_name, contract_name, node_name, network, mask, gateway):
    """
    Create an ASA route
    :param intf_folder: Target interface folder
    :type intf_folder: cobra.model.vns.FolderInst

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param network: Network (format 192.168.0.0)
    :type network: str

    :param mask: Network Mask (format 255.255.255.0)
    :type mask: str

    :param gateway: Gateway IP
    :type gateway: str

    :return: Route Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Creating a new route for network ' + network + '...'
    folder = get_folder_by_key(intf_folder, 'StaticRoute')

    if folder is None:
        print 'Creating a StaticRoute folder...'
        static_route_folder = FolderInst(intf_folder,
                                         name='staticroute',
                                         key='StaticRoute',
                                         nodeNameOrLbl=node_name,
                                         graphNameOrLbl=graph_template_name,
                                         ctrctNameOrLbl=contract_name)
    else:
        print 'Hey! I\'ve found a StaticRoute folder...'
        static_route_folder = folder

    route = FolderInst(static_route_folder,
                       name='route-' + network,
                       key='route',
                       nodeNameOrLbl=node_name,
                       graphNameOrLbl=graph_template_name,
                       ctrctNameOrLbl=contract_name)

    ParamInst(route,
              name='gateway',
              key='gateway',
              value=gateway)
    ParamInst(route,
              name='network',
              key='network',
              value=network)
    ParamInst(route,
              name='netmask',
              key='netmask',
              value=mask)
    commit(static_route_folder)
    return route


def apply_asa_acl(intf_folder, graph_template_name, contract_name, node_name, direction, acl):
    """
    Apply ACL to an Interface
    :param intf_folder: Target interface folder
    :type intf_folder: cobra.model.vns.FolderInst

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param direction: Direction of the ACL (in or out)
    :type direction: str

    :param acl: ACL name
    :type acl: str

    :return: Interface Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Applying ACL ' + acl + ' to interface ' + intf_folder.name + ' - ' + direction

    if direction == 'in':
        key = 'inbound_access_list_name'
    elif direction == 'out':
        key = 'outbound_access_list_name'

    agFolder = FolderInst(intf_folder,
                           name=intf_folder.name + '-accessgroup',
                           key='AccessGroup',
                           nodeNameOrLbl=node_name,
                           graphNameOrLbl=graph_template_name,
                           ctrctNameOrLbl=contract_name)

    CfgRelInst(agFolder,
               name=acl,
               key=key,
               targetName=acl)

    commit(intf_folder)
    return intf_folder


def asa_intf_cfg(container, graph_template_name, contract_name, node_name, intf_name, intf_ip=None, security_lvl=None):
    """
    Configure an Interface
    :param container: Target EPG (Provider)
    :type container: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param intf_name: Interface Name
    :type intf_name: str

    :param intf_ip: Optional - Interface IP
    :type intf_ip: str

    :param security_lvl: Optional - Interface Security Level
    :type security_lvl: int

    :return: Interface Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Creating ASA interface " + intf_name + "..."

    intf_folder = FolderInst(container,
                             name=intf_name,
                             key='Interface',
                             nodeNameOrLbl=node_name,
                             graphNameOrLbl=graph_template_name,
                             ctrctNameOrLbl=contract_name)

    intf_config = FolderInst(intf_folder,
                             name=intf_name + '-intfcfg',
                             key='InterfaceConfig',
                             nodeNameOrLbl=node_name,
                             graphNameOrLbl=graph_template_name,
                             ctrctNameOrLbl=contract_name)

    ipv4_config = FolderInst(intf_config,
                             name='IPv4Address',
                             key='IPv4Address',
                             nodeNameOrLbl=node_name,
                             graphNameOrLbl=graph_template_name,
                             ctrctNameOrLbl=contract_name)

    if security_lvl:
        print "With Security Level " + str(security_lvl) + "..."
        ParamInst(intf_config,
                  name=intf_name + '-security_level',
                  key='security_level',
                  value=str(security_lvl))

    if intf_ip:
        print "With IP " + intf_ip + "..."
        ParamInst(ipv4_config,
                  name='ipv4_address',
                  key='ipv4_address',
                  value=intf_ip)

    commit(container)

    return intf_folder


def associate_asa_intf(epg, graph_template_name, contract_name, node_name, direction, target):
    """
    Associate an ASA Interface to a connector
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param direction: Direction (internal or external)
    :type direction: str

    :param target: Target Interface Name
    :type target: str

    :return: Interface Folder
    :rtype: cobra.model.vns.FolderInst
    """
    # target is interface name
    print "Assigning ASA interface " + target + " to EPG " + epg.name + "..."

    # direction is internal or external
    if direction == 'internal':
        folder_name = 'IntConfig'
        folder_key = 'InIntfConfigRelFolder'
        inst_name = 'InConfigrel'
        inst_key = 'InIntfConfigRel'
    else:
        folder_name = 'ExtConfig'
        folder_key = 'ExIntfConfigRelFolder'
        inst_name = 'ExtConfigrel'
        inst_key = 'ExIntfConfigRel'

    intf_folder = FolderInst(epg,
                             name=folder_name,
                             key=folder_key,
                             nodeNameOrLbl=node_name,
                             graphNameOrLbl=graph_template_name,
                             ctrctNameOrLbl=contract_name)

    CfgRelInst(intf_folder,
               name=inst_name,
               key=inst_key,
               targetName=target)

    commit(intf_folder)
    return intf_folder



def new_asa_natpolicy(epg, graph_template_name, contract_name, node_name, nat_name):
    """
    Create ASA NAT policy
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param nat_name_: NAT List name
    :type nat_name: str

    :return: NAT Policy folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Creating NAT List' + nat_name

    # NAT policy folder
    nat_folder = FolderInst(epg,
                                name=nat_name,
                                key='NATPolicy',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    # NAT List in NAT policy
    CfgRelInst(nat_folder,
               name='nat_list_name',
               key='nat_list_name',
               targetName='NATList')

    commit(nat_folder)
    return nat_folder



def new_asa_natlist(epg, graph_template_name, contract_name, node_name, nat_rules=None):
    """
    Create ASA NAT list
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param nat_rules: List of NAT, example:
    :type nat_rules: list
    nat_list = dict(
        name='NATRule',
        order='10'
        dstTrans=dict(
            mapped='Public-VIP'
            real='Private-VIP'
        ),
        srcTrans=dict(
            mapped='L3out-Client-Private'
            real='L3out-Client'
            nat_type='dynamic',
        )
    )
    :return: NAT List folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Creating NAT List'

    nat_folder = FolderInst(epg,
                            name='NATList',
                            key='NATList',
                            nodeNameOrLbl=node_name,
                            graphNameOrLbl=graph_template_name,
                            ctrctNameOrLbl=contract_name)

    commit(nat_folder)

    # Add NAT rule
    new_asa_entry(nat_folder, graph_template_name, contract_name, node_name, '10')

    return nat_folder


def new_asa_entry(nat_folder, graph_template_name, contract_name, node_name, order):
    """
    Create ASA NAT entry
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param order: NAT order number
    :type order: str

    :return: NAT List folder
    :rtype: cobra.model.vns.FolderInst
    """
    print 'Creating NAT entry'
    # Need to modify parameters

    rule_folder = FolderInst(nat_folder,
               name='NATRule',
               key='NATRule',
               nodeNameOrLbl=node_name,
               graphNameOrLbl=graph_template_name,
               ctrctNameOrLbl=contract_name)

    ParamInst(rule_folder,
              name='order',
              key='order',
              value=order)

    dest_folder = FolderInst(rule_folder,
               name='destination_translation',
               key='destination_translation',
               nodeNameOrLbl=node_name,
               graphNameOrLbl=graph_template_name,
               ctrctNameOrLbl=contract_name)

    dest_mapped = FolderInst(dest_folder,
                               name='mapped_object',
                               key='mapped_object',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    CfgRelInst(dest_mapped,
           name='object_name',
           key='object_name',
           targetName='Public-VIP')

    dest_real = FolderInst(dest_folder,
                         name='real_object',
                         key='real_object',
                         nodeNameOrLbl=node_name,
                         graphNameOrLbl=graph_template_name,
                         ctrctNameOrLbl=contract_name)

    CfgRelInst(dest_real,
           name='object_name',
           key='object_name',
           targetName='Private-VIP')


    source_folder = FolderInst(rule_folder,
               name='source_translation',
               key='source_translation',
               nodeNameOrLbl=node_name,
               graphNameOrLbl=graph_template_name,
               ctrctNameOrLbl=contract_name)

    ParamInst(source_folder,
              name='nat_type',
              key='nat_type',
              value="dynamic")

    source_mapped = FolderInst(source_folder,
               name='mapped_object',
               key='mapped_object',
               nodeNameOrLbl=node_name,
               graphNameOrLbl=graph_template_name,
               ctrctNameOrLbl=contract_name)

    CfgRelInst(source_mapped,
              name='object_name',
              key='object_name',
              targetName='L3out-Client-Private')

    source_real= FolderInst(source_folder,
                               name='real_object',
                               key='real_object',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    CfgRelInst(source_real,
               name='object_name',
               key='object_name',
               targetName='L3out-Client')

    commit (nat_folder)
    return nat_folder