__author__ = 'mihiguch'

# Core APIC imports
from core import commit
from core import get_folder_by_key

# ACI Model imports
from cobra.model.vns import FolderInst
from cobra.model.vns import ParamInst
from cobra.model.vns import CfgRelInst

def new_bigip_network(epg, graph_template_name, contract_name, node_name, bigip_networks):
    """
    Create a BIGIP Network
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param bigip_networks: BIGIP address configuration, example:
    bigip_networks = dict(
        network_name = 'Network-All',
        interface_key = 'InternalSelfIP',
        ip='192.168.10.200',
        mask='255.255.255.0'
    )
    :type bigip_networks: dictionary

    :return: Network Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Creating BIGIP Network " + bigip_networks['network_name'] + "IP: " + bigip_networks['ip'] + "mask: " + bigip_networks['mask'] + "..."
    # Create network_folder
    network_folder = FolderInst(epg,
                               name=bigip_networks['network_name'],
                               key='Network',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)


    # Create internal interface folder
    internal_folder = FolderInst(network_folder,
                                 name= bigip_networks['interface_key'],
                                 key= bigip_networks['interface_key'],
                                 nodeNameOrLbl=node_name,
                                 graphNameOrLbl=graph_template_name,
                                 ctrctNameOrLbl=contract_name)

    ParamInst(internal_folder,
              name='Floating',
              key='Floating',
              value='NO')

    ParamInst(internal_folder,
              name='PortLockdown',
              key='PortLockdown',
              value='NONE')

    ParamInst(internal_folder,
              name='SelfIPAddress',
              key='SelfIPAddress',
              value= bigip_networks['ip'])

    ParamInst(internal_folder,
              name='SelfIPNetmask',
              key='SelfIPNetmask',
              value= bigip_networks['mask'])


    commit(network_folder)
    return network_folder


def add_bigip_route(epg, graph_template_name, contract_name, node_name, bigip_routes):
    """
    Add static route on BGP
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param bigip_routes: bigip static route configuration, example:
    bigip_routes = dict(
        network_name='Network-All',
        destsubnet = '0.0.0.0',
        mask='0.0.0.0',
        nexthop='192.168.10.254'
    )
    :type bigip_routes: str

    :return: Network Folder
    :rtype: cobra.model.vns.FolderInst
    """

    print "Creating BIGIP route " + bigip_routes['network_name'] + "for destsubnet: " + bigip_routes['destsubnet'] + "..."

    # Specify network folder
    network_folder = FolderInst(epg,
                                name=bigip_routes['network_name'],
                                key='Network',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    # Create route folder
    route_folder = FolderInst(network_folder,
                                 name='Route',
                                 key='Route',
                                 nodeNameOrLbl=node_name,
                                 graphNameOrLbl=graph_template_name,
                                 ctrctNameOrLbl=contract_name)

    # Add static route
    ParamInst(route_folder,
              name='DestinationIPAddress',
              key='DestinationIPAddress',
              value=bigip_routes['destsubnet'])

    ParamInst(route_folder,
              name='DestinationNetmask',
              key='DestinationNetmask',
              value=bigip_routes['mask'])

    ParamInst(route_folder,
              name='NextHopIPAddress',
              key='NextHopIPAddress',
              value=bigip_routes['nexthop'])

    commit(network_folder)
    return network_folder


def apply_bigip_network(epg, graph_template_name, contract_name, node_name, network_folder_name):
    """
    Apply network folder
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param network_folder_name: Network Folder name which will be applied
    :type network_folder_name: str

    :return: Network Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Apply BIGIP network for " + network_folder_name + "..."
    networkrel_folder = FolderInst(epg,
                                   name='NetworkRelation',
                                   key='NetworkRelation',
                                   nodeNameOrLbl=node_name,
                                   graphNameOrLbl=graph_template_name,
                                   ctrctNameOrLbl=contract_name)


    CfgRelInst(networkrel_folder,
           name='NetworkRel',
           key='NetworkRel',
           targetName=network_folder_name)

    commit(networkrel_folder)
    return networkrel_folder


def create_listner(epg, graph_template_name, contract_name, node_name, listener_name, vip, dest_port):
    """
    Create VIP
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param listner_name: Listner Folder name "name='Listener-' + listener_name"
    :type listner_name: str

    :param vip: VIP IP address
    :type vip: str

    :param vip: dest_port
    :type vip: str

    :return: Listner Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Create BIGIP listner " + listener_name + " " + vip + ":" + dest_port + "..."

    # Create folder
    listner_folder = FolderInst(epg,
                               name='Listener-' + listener_name,
                               key='Listener',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    # Create VIP
    ParamInst(listner_folder,
              name='DestinationIPAddress',
              key='DestinationIPAddress',
              value=vip)

    ParamInst(listner_folder,
              name='DestinationPort',
              key='DestinationPort',
              value=dest_port)

    ParamInst(listner_folder,
              name='DestinationNetmask',
              key='DestinationNetmask',
              value='255.255.255.255')

    ParamInst(listner_folder,
              name='Protocol',
              key='Protocol',
              value='TCP')

    commit(listner_folder)
    return listner_folder


def create_localtraffic(epg, graph_template_name, contract_name, node_name, localtraffic_name):
    """
    Create Local Traffic
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param localtraffic_name: Local traffic Folder name
    :type localtraffic_name: str

    :return: LocalTraffic Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Create BIGIP local traffic " + localtraffic_name + "..."

    # Create LocalTraffic Folder
    localtraffic_folder = FolderInst(epg,
                               name='LocalTraffic-' + localtraffic_name,
                               key='LocalTraffic',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    # Configure Monitor
    monitor_folder = FolderInst(localtraffic_folder,
                               name='Monitor-' + localtraffic_name,
                               key='Monitor',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    ParamInst(monitor_folder,
              name='FailByAttempts',
              key='FailByAttempts',
              value='3')

    ParamInst(monitor_folder,
              name='FrequencySeconds',
              key='FrequencySeconds',
              value='3')

    ParamInst(monitor_folder,
              name='Type',
              key='Type',
              value='TCP')


    # Create Pool folder
    pool_folder = FolderInst(localtraffic_folder,
                                name='Pool-' + localtraffic_name,
                                key='Pool',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    # LB Method: round robin
    ParamInst(pool_folder,
              name='LBMethod',
              key='LBMethod',
              value='ROUND_ROBIN')

    # Pool type: dynamic
    ParamInst(pool_folder,
              name='PoolType',
              key='PoolType',
              value='DYNAMIC')

    # Associate Monitor to Pool
    poolmon_folder = FolderInst(pool_folder,
                             name='PoolMonitor',
                             key='PoolMonitor',
                             nodeNameOrLbl=node_name,
                             graphNameOrLbl=graph_template_name,
                             ctrctNameOrLbl=contract_name)

    CfgRelInst(poolmon_folder,
               name='PoolMonitorRel',
               key='PoolMonitorRel',
               targetName='LocalTraffic-' + localtraffic_name + '/Monitor-' + localtraffic_name)

    commit(localtraffic_folder)
    return localtraffic_folder



def create_pool(epg, graph_template_name, contract_name, node_name, pool_name, dest_port, poolrel):
    """
    Create Pool
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param pool_name: Pool name
    :type pool_name: str

    :param dest_port: destination port
    :type dest_port: str

    :param poolrel: pool name
    :type poolrel: str

    :return: Pool Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Create BIGIP pool " + pool_name + " " + dest_port + "..."

    pool_folder = FolderInst(epg,
                               name='Pool-' + pool_name,
                               key='Pool',
                               nodeNameOrLbl=node_name,
                               graphNameOrLbl=graph_template_name,
                               ctrctNameOrLbl=contract_name)

    CfgRelInst(pool_folder,
              name='PoolRel',
              key='PoolRel',
              targetName=poolrel)

    ParamInst(pool_folder,
              name='EPGDestinationPort',
              key='EPGDestinationPort',
              value=dest_port)

    ParamInst(pool_folder,
              name='EPGConnectionLimit',
              key='EPGConnectionLimit',
              value='0')

    ParamInst(pool_folder,
              name='EPGConnectionRateLimit',
              key='EPGConnectionrateLimit',
              value='0')

    ParamInst(pool_folder,
              name='EPGRatio',
              key='EPGRatio',
              value='1')

    commit(pool_folder)
    return pool_folder