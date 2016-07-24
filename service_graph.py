__author__ = 'mihiguch'
## reuse rephilip's service_graph.py.  modify parameter for the demo setup.

# Core APIC imports
from core import commit
from device import get_logical_interface

# Context imports
from cobra.model.vns import LDevCtx
from cobra.model.vns import RsLDevCtxToLDev
from cobra.model.vns import RsLIfCtxToBD
from cobra.model.vns import RsLIfCtxToLIf
from cobra.model.vns import LIfCtx

# Graph Template imports
from cobra.model.vns import AbsGraph
from cobra.model.vns import AbsTermNodeCon
from cobra.model.vns import AbsTermNodeProv
from cobra.model.vns import AbsTermConn
from cobra.model.vns import InTerm
from cobra.model.vns import OutTerm
from cobra.model.vns import AbsConnection
from cobra.model.vns import RsAbsConnectionConns
from cobra.model.vns import AbsNode
from cobra.model.vns import AbsFuncConn
from cobra.model.vns import RsMConnAtt
from cobra.model.vns import RsNodeToAbsFuncProf
from cobra.model.vns import RsNodeToMFunc
from cobra.model.vns import AbsFuncProf
from cobra.model.vns import RsProfToMFunc
from cobra.model.vns import AbsDevCfg
from cobra.model.vns import AbsFuncCfg
from cobra.model.vns import AbsFuncProfContr
from cobra.model.vns import AbsFuncProfGrp
from cobra.model.vns import AbsFolder
from cobra.model.vns import AbsParam
from cobra.model.vns import RsScopeToTerm
from cobra.model.vns import AbsCfgRel



def new_graph_terminal(graph_template, name, direction):
    """Create a service graph terminal connector

    :param graph_template: Service Graph Template
    :type graph_template: cobra.model.vns.AbsGraph

    :param name: Name of the terminal (T1, T2, T3...)
    :type name: str

    :param direction: Direction of the terminal (in or out), mapped by:
    provider = in
    consumer = out
    :type direction: str

    :return: Terminal Node object
    :rtype: cobra.model.vns.AbsTermNodeProv or cobra.model.vns.AbsTermNodeCon
    """
    print "Creating Graph Terminal for " + name + "..."
    if str.lower(direction) == 'provider':
        term_node = AbsTermNodeProv(graph_template,
                                    name=name)
    elif str.lower(direction) == 'consumer':
        term_node = AbsTermNodeCon(graph_template,
                                    name=name)

    AbsTermConn(term_node,
                name='1')
    # Seems to be default, no need to add it
    InTerm(term_node,
           name='input-terminal')
    OutTerm(term_node,
            name='output-terminal')

    commit(term_node)
    return term_node


def new_graph_connection(graph_template, name, adjacency, conn_type, unicast_route, connections):
    """Create a connection between 2 nodes

    :param graph_template: Service Graph Template
    :type graph_template: cobra.model.vns.AbsGraph

    :param name: Name of the connection
    :type name: str

    :param adjacency: Adjacency type (L2 or L3)
    :type adjacency: str

    :param conn_type: Connector type (seems always "external"??)
    :type conn_type: str

    :param unicast_route:
    :type unicast_route: bool

    :param connections: List of connections

    links=[
        dict(
            type='terminal',
            name='T1'
        ),
        dict(
            type='node',
            direction='external',
            node='Firewall'
        )
    ]

    :return: Connection Object
    :rtype: cobra.model.vns.AbsConnection
    """
    print "Creating Graph Connection for " + name + "..."
    abs_conn = AbsConnection(graph_template,
                             adjType=adjacency,
                             connType=conn_type,
                             name=name,
                             unicastRoute=unicast_route)

    for conn in connections:
        print "Attaching to " + conn + "..."
        RsAbsConnectionConns(abs_conn,
                             tDn=conn)

    commit(abs_conn)
    return abs_conn


def new_graph_node(graph_template, name, type, function, profile):
    """Create a new Service Graph Template node

    :param graph_template: Service Graph Template
    :type graph_template: cobra.model.vns.AbsGraph

    :param name: Name of the node
    :type name: str

    :param type: Type of the node, GoTo or GoThrough
    :type type: str

    :param function: DN of the node function (from the device package).
    Common values are:
    NS1KV - Load Balancing : uni/infra/mDev-Cisco-NetScaler1KV-1.0/mFunc-LoadBalancing
    ASAv - Firewall : uni/infra/mDev-CISCO-ASA-1.2/mFunc-Firewall
    :type function: str

    :param profile: DN of the profile applied to the node
    :type profile: str

    :return: Node object
    :rtype: cobra.model.vns.AbsNode
    """
    print "Creating Node " + name + "..."
    node = AbsNode(graph_template,
                   funcType=type,
                   name=name)

    if name == 'ADC':
        internal = AbsFuncConn(node,
                           name="internal", attNotify='yes')
    else:
        internal = AbsFuncConn(node,
                               name="internal")

    RsMConnAtt(internal,
               tDn=str(function) + '/mConn-internal')

    external = AbsFuncConn(node,
                           name="external")
    RsMConnAtt(external,
               tDn=str(function) + '/mConn-external')

    RsNodeToAbsFuncProf(node,
                        tDn=profile)

    RsNodeToMFunc(node,
                  tDn=function)

    commit(node)
    return node


def new_graph_profile_group(tenant, name):
    """Create a new function profile group

    :param tenant: Tenant in which the device selection policy should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Name of the group
    :type name: str

    :return: Function profile group created
    :rtype: cobra.model.vns.AbsFuncProfGrp
    """
    print "Creating a Graph Profile Group " + name + "..."
    # Create a group container
    container = AbsFuncProfContr(tenant)
    # Create a new group in the group container
    group = AbsFuncProfGrp(container,
                           name=name)

    commit(container)
    return group


def new_graph_profile(group, name, function, device_cfg=None, function_cfg=None):
    """Create an empty function profile for a given function

    :param group: Service Graph profile group
    :type group: cobra.model.vns.AbsFuncProfGrp

    :param name: Name of the function profile to be created
    :type name: str

    :param function: DN of the function described by the profile (from the device package).
    Common values are:
    NS1KV - Load Balancing : uni/infra/mDev-Cisco-NetScaler1KV-1.0/mFunc-LoadBalancing
    ASAv - Firewall : uni/infra/mDev-CISCO-ASA-1.2/mFunc-Firewall
    :type function: str

    :param function_cfg: Parameters for the function level
    fw_parameters = [
        dict(
            type='folder',
            name='ConsIntf',
            key='Interface',
            children=[
                dict(
                    type='scopetoterm',
                    tdn=fw_cons_t
                )
            ]
        ),
        dict(
            type='folder',
            name='ConsACLIn',
            key='AccessList',
            children=[
                dict(
                    type='scopetoterm',
                    tdn=fw_cons_t
                )
            ]
        ),
        dict(
            type='folder',
            name='ConsRoute',
            key='StaticRoute',
            children=[
                dict(
                    type='scopetoterm',
                    tdn=fw_cons_t
                )
            ]
        ),
        dict(
            type='folder',
            name='ProvIntConfig',
            key='InIntfConfigRelFolder',
            children=[
                dict(
                    type='rel',
                    name='ProvInConfigrel',
                    key='InIntfConfigRel',
                    targetname=''
                )
            ]
        ),
        dict(
            type='folder',
            name='ConsIntConfig',
            key='ExIntfConfigRelFolder',
            children=[
                dict(
                    type='scopetoterm',
                    tdn=fw_cons_t
                ),
                dict(
                    type='rel',
                    name='ConsExtConfigrel',
                    key='ExIntfConfigRel',
                    targetname=''
                )
            ]
        )
    ]
    :type param: list

    :return: Function Profile Created
    :rtype: cobra.model.vns.AbsFuncProf
    """
    print "Creating a Graph Profile " + name + "..."
    # Creation of a new function profile
    profile = AbsFuncProf(group,
                          name=name)
    # Associate the profile to the function
    RsProfToMFunc(profile,
                  tDn=function)
    # Create an empty devConfig folder with an empty function parameter
    absdevcfg = AbsDevCfg(profile,
                          name='devConfig')

    absfunccfg = AbsFuncCfg(profile,
                            name='funcConfig')

    commit(profile)

    if function_cfg is not None:
        for f in function_cfg:
            new_graph_parameter(absfunccfg, f)

    if device_cfg is not None:
        for d in device_cfg:
            new_graph_parameter(absdevcfg, d)

    return profile


def new_graph_parameter(parent, parameters):
    for p in parameters:
        t = p['type']

        if t == 'folder':
            print "Adding a graph parameter of type " + t + " with name " + p['name'] + " for parent " + str(parent.dn) + "..."
            folder = AbsFolder(parent,
                               name=p['name'],
                               key=p['key'])
            commit(parent)

            if 'children' in p:
                new_graph_parameter(folder, p['children'])

        elif t == 'param':
            print "Adding a graph parameter of type " + t + " with name " + p['name'] + " for parent " + str(parent.dn) + "..."
            AbsParam(parent,
                     name=p['name'],
                     key=p['key'])
            commit(parent)

        elif t == 'scopetoterm':
            print "Adding a graph parameter of type " + t + " with tDn " + p['tdn'] + " for parent " + str(parent.dn) + "..."
            RsScopeToTerm(parent,
                          tDn=p['tdn'])
            commit(parent)

        elif t == 'rel':
            print "Adding a graph parameter of type " + t + " with name " + p['name'] + " for parent " + str(parent.dn) + "..."
            AbsCfgRel(parent,
                      name=p['name'],
                      key=p['key'],
                      targetName=p['targetname'])
            commit(parent)

    return parent


def new_graph_template(tenant, name, graph):
    """Create a new Service Graph Template

    :param tenant: Tenant in which the device selection policy should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Service Graph Template name
    :type name: str

    :param graph: Dictionary with the parameters of the graph to be configured:
    Each Service Graph template is described in the following way:

    fw_lb_graph = dict(
        nodes=[
            dict(
                name='Firewall',
                type='GoTo',
                function='uni/infra/mDev-CISCO-ASA-1.1/mFunc-Firewall',
                profile=str(fw_profile.dn)
            ),
            dict(
                name='ADC',
                type='GoTo',
                function='uni/infra/mDev-Cisco-NetScaler1KV-1.0/mFunc-LoadBalancing',
                profile=str(lb_profile.dn)
            )
        ],
        terminals=[
            dict(
                name='T1',
                direction='consumer'
            ),
            dict(
                name='T2',
                direction='provider'
            )
        ],
        connections=[
            dict(
                name='C1',
                adjacency='L2',
                connType='external',
                unicastRoute='yes',
                links=[
                    dict(
                        type='terminal',
                        name='T1'
                    ),
                    dict(
                        type='node',
                        direction='external',
                        node='Firewall'
                    )
                ]
            ),
            dict(
                name='C2',
                adjacency='L2',
                connType='external',
                unicastRoute='yes',
                links=[
                    dict(
                        type='node',
                        direction='external',
                        node='ADC'
                    ),
                    dict(
                        type='node',
                        direction='internal',
                        node='Firewall'
                    )
                ]
            ),
            dict(
                name='C3',
                adjacency='L3',
                connType='external',
                unicastRoute='yes',
                links=[
                    dict(
                        type='node',
                        direction='internal',
                        node='ADC'
                    ),
                    dict(
                        type='terminal',
                        name='T2'
                    )
                ]
            )
        ]
    )

    nodes (list) - list of nodes to be created as part of the graph
    connections (list) - list of the connections between the nodes
    terminals (list) - list of terminal point to the graph (usually 2)
    :type graph: dict

    :return: Graph Template Object
    :rtype: cobra.model.vns.AbsGraph
    """
    graph_template = AbsGraph(tenant,
                              name=name)
    commit(graph_template)

    terminal_connections = dict()
    nodes = dict()

    for node in graph['nodes']:
        node_name = node['name']
        node_type = node['type']
        node_function = node['function']
        node_profile = node['profile']

        node_device_param = ''
        node_function_param = ''
        if 'parameters' in node:
            if 'device' in node['parameters']:
                node_device_param = node['parameters']['device']
            if 'function' in node['parameters']:
                node_function_param = node['parameters']['function']

        print "Creating a new node " + node_name + "..."
        this_node = new_graph_node(graph_template, node_name, node_type, node_function, node_profile)
        if node_device_param:
            print "Adding node device Parameters..."
            devcfg = AbsDevCfg(this_node,
                               name='nodeDevConfig')
            new_graph_parameter(devcfg, node_device_param)

        if node_function_param:
            print "Adding node function Parameters..."
            funccfg = AbsFuncCfg(this_node,
                               name='nodeFuncConfig')
            new_graph_parameter(funccfg, node_function_param)

        nodes[node_name] = this_node

    for terminal in graph['terminals']:
        terminal_name = terminal['name']
        terminal_direction = terminal['direction']
        print "Creating a Terminal node..."
        terminal_connections[terminal_name] = new_graph_terminal(graph_template, terminal_name, terminal_direction)

    for conn in graph['connections']:
        adjacency = conn['adjacency']
        conn_type = conn['connType']
        unicast_route = conn['unicastRoute']
        conn_name = conn['name']
        conns = list()

        for link in conn['links']:
            link_type = link['type']
            if link_type == 'terminal':
                terminal_name = link['name']
                conns.append(str(terminal_connections[terminal_name].dn) + '/AbsTConn')
            elif link_type == 'node':
                node_name = link['node']
                node_direction = link['direction']
                conns.append(str(nodes[node_name].dn) + '/AbsFConn-' + node_direction)

        new_graph_connection(graph_template, conn_name, adjacency, conn_type, unicast_route, conns)

    commit(graph_template)
    return graph_template


def new_logical_interface_context(context, connector_name, bd_dn, lif_dn):
    """Create a new logical interface context

    :param context: Context in which the logical interface will be created
    :type context: cobra.model.vns.LDevCtx

    :param connector_name: name of the connector
    :type connector_name: str

    :param bd_dn: dn of the bridge domain attached to the logical interface
    :type bd_dn: str

    :param lif_dn: logical interface (from the logical device cluster)
    :type lif_dn: str

    :return: logical interface context
    :rtype: cobra.model.vns.LIfCtx
    """
    print "Creating a new Logical Interface Context for connector " + connector_name + "..."

    # Create a new Logical Interface Context
    lif_ctx = LIfCtx(context,
                     connNameOrLbl=connector_name)

    # Attach the Logical Interface Context to a BD
    print "Attaching to BD " + str(bd_dn) + "..."
    RsLIfCtxToBD(lif_ctx,
                 tDn=str(bd_dn))

    # Attach the Logical Interface Context to a Logical Interface
    print "Attaching to lIf " + str(lif_dn) + "..."
    RsLIfCtxToLIf(lif_ctx,
                  tDn=str(lif_dn))

    commit(lif_ctx)
    return lif_ctx


def new_graph_context(tenant, contract_name, graph_template_name, logical_dn, logical_contexts, node):
    """Create a new device selection policy (also known as Device Context)

    :param tenant: Tenant in which the device selection policy should be created
    :type tenant: cobra.model.fv.Tenant

    :param contract_name: Contract selector
    :type contract_name: str

    :param graph_template_name: Service Graph Template selector
    :type graph_template_name: str

    :param logical: Logical Device selector DN
    :type logical: str

    :param logical_contexts: list of logical contexts, should be exactly 2 (external and internal).
    Each logical context is in the following format:

    contexts = [
        dict(
            connector="internal",
            bd=vdc_1_vpx_bd.dn,
            lif="vpx"
        ),
        dict(
            connector="external",
            bd=outside_bd.dn,
            lif="outside"
        )
    ]

    connector (str) - internal or external
    bd (str) - DN of the BD associated with the connector
    lif (str) - name of the logical interface

    :type logical_contexts: list

    :param node: Node selector (Firewall, ADC, ...)
    :type node: str

    :return: Logical Device Cluster Selection Policy
    :rtype: cobra.model.vns.LDevCtx
    """
    print "Creating a new Service Graph Context for Contract " + contract_name + "..."

    context = LDevCtx(tenant,
                      ctrctNameOrLbl=contract_name,
                      graphNameOrLbl=graph_template_name,
                      nodeNameOrLbl=node
                      )

    # Relation between context and device cluster
    print 'Attaching Service Graph Context to Logical device ' + logical_dn + '...'
    RsLDevCtxToLDev(context,
                    tDn=logical_dn)

    commit(context)

    # logicalContext is a list of dictionaries
    for lif_ctx in logical_contexts:
        connector = lif_ctx['connector']
        bd_dn = str(lif_ctx['bd'])
        lif_name = str(lif_ctx['lif'])
        lif_dn = get_logical_interface(logical_dn, lif_name).dn

        new_logical_interface_context(context, connector, bd_dn, lif_dn)

    commit(context)
    return context