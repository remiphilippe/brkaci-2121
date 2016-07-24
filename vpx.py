__author__ = 'mihiguch'
## reuse rephilip's n1kv.py.  modify parameter for the demo setup(VPX).


# Core APIC imports
from core import commit
from core import get_one
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


def new_vpx(tenant, name, cluster_ip, devices, port, login, password, features, modes):
    """
    Create vpx for FEDnet environment
    :param tenant: Entity
    :type tenant: cobra.model.fv.Tenant

    :param name: vpx Logical Cluster Namef
    :type name: str

    :param cluster_ip: vpx Logical Cluster IP
    :type cluster_ip: str

    :param devices: vpx Instances, example:
    vpx = [
        dict(
            name='TAV2-LB-01',
            ip='10.238.135.13',
        ),
        dict(
            name='TAV2-LB-02',
            ip='10.238.135.14',
        )
    ]
    :type devices: list

    :param port: vpx Management Port (80 by default)
    :type port: int

    :param login: vpx admin username
    :type login: str

    :param password: vpx admin password
    :type password: str

    :param features: List of features to be enabled, for example: ['FR', 'CKA', 'TCPB', 'USNIP', 'PMTUD']
    :type features: list

    :param modes: List of modes to be enabled, for example: ['LB', 'SSL']
    :type modes: list

    :return: Logical Device
    :rtype: cobra.model.vns.LDevVip
    """
    print "Creating a new vpx for tenant " + tenant.name + "..."
    # Logical Interfaces
    linterfaces = [
        dict(
            name='intf_1_1',
            type='inside'
        )
    ]

    logical = new_logical_device(tenant, name, 'vpx', cluster_ip, port, login, password, linterfaces)
    # ['FR', 'CKA', 'TCPB', 'USNIP', 'PMTUD']
    enable_vpx_feature(logical, features)
    # ['LB', 'SSL']
    enable_vpx_mode(logical, modes)

    # Concrete Interfaces
    # Network adapter 1  - Mgmt0/0 - Mgmt
    # Network adapter 2  - 1/1 - Inside

    cinterfaces = [
        dict(
            vnic='Network adapter 2',
            physical='1/1',
            logical='intf_1_1'
        )
    ]

    # devices is a list of dictionaries
    for device in devices:
        ip = device['ip']
        name = device['name']
        concrete = new_concrete_device(logical, name, ip, port, login, password, cinterfaces)

    return logical


def vpx_ha():
    return None


def enable_vpx_mode(logical, modes):
    """
    Enable Modes on vpx
    :param logical: Logical Device
    :type logical: cobra.model.vns.LDevVip

    :param modes: Modes to be enabled
    :type modes: list

    :return: Logical device
    :rtype: cobra.model.vns.LDevVip
    """
    print "Enabling modes..."
    mode_folder = DevFolder(logical,
                            key='enableMode',
                            name='enableMode')
    for mode in modes:
        print "Enabling mode " + mode + " for device " + logical.name + "..."
        DevParam(mode_folder,
                 key=mode,
                 name=mode,
                 value='ENABLE')

    commit(logical)
    return logical


def enable_vpx_feature(logical, features):
    """
    Enable Features on vpx
    :param logical: Logical Device
    :type logical: cobra.model.vns.LDevVip

    :param features: Features to be enabled
    :type features: list

    :return: Logical device
    :rtype: cobra.model.vns.LDevVip
    """
    print "Enabling features..."
    feature_folder = DevFolder(logical,
                               key='enableFeature',
                               name='enableFeature')

    for feature in features:
        print "Enabling feature " + feature + " for device " + logical.name + "..."
        DevParam(feature_folder,
                 key=feature,
                 name=feature,
                 value='ENABLE')

    commit(logical)
    return logical


def new_vpx_network_container(epg, graph_template_name, contract_name, node_name, name):
    """
    Create a vpx Network Container
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param name: Network Name
    :type name: str

    :return: Network Folder
    :rtype: cobra.model.vns.FolderInst
    """

    network_folder = FolderInst(epg,
                                name=name,
                                key='Network',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    commit(network_folder)

    return network_folder


def new_vpx_vserver(epg, graph_template_name, contract_name, node_name, name, vip, type, port):
    """
    Create a vpx Virtual Server
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param name: Name of the Virtual Server
    :type name: str

    :param vip: VIP IP address
    :type vip: str

    :param type: Service Type, possible values:
    ADNS
    DNS
    MSSQL
    RDP
    SSL
    TFTP
    ADNS_TCP
    DNS_TCP
    MYSQL
    RPCSVR
    SSL_BRIDGE
    UDP
    ANY
    DTLS
    NNTP
    RTSP
    SSL_DIAMETER
    DHCPRA
    FTP
    ORACLE
    SIP_UDP
    SSL_TCP
    DIAMETER
    HTTP
    RADIUS
    SNMP
    TCP
    :type type: str

    :param port: Service Port
    :type port: int

    :return: Virtual Server Folder
    :rtype: cobra.model.vns.FolderInst
    """

    vserver_folder = FolderInst(epg,
                                name='lbvserver-' + name,
                                key='lbvserver',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    ParamInst(vserver_folder,
              name='ipv46',
              key='ipv46',
              value=vip)

    ParamInst(vserver_folder,
              name='name',
              key='name',
              value=name)
    ParamInst(vserver_folder,
              name='servicetype',
              key='servicetype',
              value=type)
    ParamInst(vserver_folder,
              name='port',
              key='port',
              value=port)


    commit(epg)
    associate_vpx_vserver(epg, graph_template_name, contract_name, node_name, name)

    return vserver_folder


def new_vpx_vserver_ssl(epg, graph_template_name, contract_name, node_name, name, certificate):
    vserver_folder = FolderInst(epg,
                                name='sslvserver-' + name,
                                key='sslvserver',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    ParamInst(vserver_folder,
              name='vservername',
              key='vservername',
              value=name)
    ParamInst(vserver_folder,
              name='clientauth',
              key='clientauth',
              value='DISABLED')
    ParamInst(vserver_folder,
              name='snienable',
              key='snienable',
              value='DISABLED')

    commit(vserver_folder)
    associate_vpx_vserver_ssl(epg, graph_template_name, contract_name, node_name, name)

    return vserver_folder


def bind_vpx_certificate(vserver_folder, graph_template_name, contract_name, node_name, certificate):
    print "Binding certificate " + certificate + "..."
    sslcertkey_folder = FolderInst(vserver_folder,
                                   name='keybinding-' + certificate,
                                   key='sslvserver_sslcertkey_binding',
                                   nodeNameOrLbl=node_name,
                                   graphNameOrLbl=graph_template_name,
                                   ctrctNameOrLbl=contract_name)

    CfgRelInst(sslcertkey_folder,
               name='certkeyname',
               key='certkeyname',
               targetName='sslcertkey-' + certificate)

    commit(sslcertkey_folder)

    return sslcertkey_folder


def new_vpx_certificate(epg, graph_template_name, contract_name, node_name, name, cert, key):
    print "Creating a certificate entry for " + name + " with cert " + cert + " and key " + key + "..."
    sslcert_folder = FolderInst(epg,
                                name='sslcertkey-' + name,
                                key='sslcertkey',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    ParamInst(sslcert_folder,
              name='certkey',
              key='certkey',
              value=name)

    ParamInst(sslcert_folder,
              name='cert',
              key='cert',
              value=cert)

    ParamInst(sslcert_folder,
              name='key',
              key='key',
              value=key)

    commit(epg)

    # Associate the certificate to the provider EPG
    associate_vpx_certificate(epg, graph_template_name, contract_name, node_name, name)

    return sslcert_folder



def new_vpx_ip(network_folder, graph_template_name, contract_name, node_name, name, type, ip, mask):
    """
    Configure vpx IP address
    :param network_folder:Network Folder
    :type network_folder: cobra.model.vns.FolderInst

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param name: IP name
    :type name: str

    :param type: Type of IP (SNIP, VIP)
    :type type: str

    :param ip: IP address
    :type ip: str

    :param mask: Network Mask
    :type mask: str

    :return: Network Folder
    :rtype: cobra.model.vns.FolderInst
    """
    ip_folder = FolderInst(network_folder,
                           name=name,
                           key='nsip',
                           nodeNameOrLbl=node_name,
                           graphNameOrLbl=graph_template_name,
                           ctrctNameOrLbl=contract_name)

    ParamInst(ip_folder,
              name='dynamicrouting',
              key='dynamicrouting',
              value='DISABLED')
    ParamInst(ip_folder,
              name='hostroute',
              key='hostroute',
              value='DISABLED')
    ParamInst(ip_folder,
              name='icmp',
              key='icmp',
              value='ENABLED')
    ParamInst(ip_folder,
              name='ipaddress',
              key='ipaddress',
              value=ip)
    ParamInst(ip_folder,
              name='netmask',
              key='netmask',
              value=mask)
    #<vnsComparison name="NSIP" cmp="eq" value="NSIP" />
    #<vnsComparison name="VIP" cmp="eq" value="VIP" />
    #<vnsComparison name="SNIP" cmp="eq" value="SNIP" />
    #<vnsComparison name="GSLBsiteIP" cmp="eq" value="GSLBsiteIP" />
    #<vnsComparison name="ADNSsvcIP" cmp="eq" value="ADNSsvcIP" />
    #<vnsComparison name="CLIP" cmp="eq" value="CLIP" />
    ParamInst(ip_folder,
              name='type',
              key='type',
              value=str.upper(type))

    commit(network_folder)
    return network_folder


def new_vpx_route():
    return None


def new_vpx_realserver(servicegroup_folder, graph_template_name, contract_name, node_name, name, ip, port):
    """
    Create a new real server for a service group
    :param servicegroup_folder: Service Group Container Folder
    :type servicegroup_folder: cobra.model.vns.FolderInst

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param name: Real Server name
    :type name: str

    :param ip: Real Server IP address
    :type ip: str

    :param port: Destination Port
    :type port: int

    :return: Real Server Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Creating Real Server " + name + " for Service Group " + servicegroup_folder.name + "..."
    member = FolderInst(servicegroup_folder,
                        name=name,
                        key='servicegroup_servicegroupmember_binding',
                        nodeNameOrLbl=node_name,
                        graphNameOrLbl=graph_template_name,
                        ctrctNameOrLbl=contract_name)

    print "Creating Real Server " + ip

    ParamInst(member,
              name='ip',
              key='ip',
              value=ip)

    print "Creating Real Server " + port


    ParamInst(member,
              name='port',
              key='port',
              value=port)



    commit(member)
    return member


def new_vpx_servicegroup(epg, graph_template_name, contract_name, node_name, name, type):
    """
    Create a new Service Group
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param name: Service Group Name
    :type name: str

    :param type: Service Type, refer to Virtual Server for the list of possible options
    :type type: str

    :return: Service Group Folder
    :rtype: cobra.model.vns.FolderInst
    """
    print "Creating Service Group " + name + "..."
    servicegroup_folder = FolderInst(epg,
                                     name=name,
                                     key='servicegroup',
                                     nodeNameOrLbl=node_name,
                                     graphNameOrLbl=graph_template_name,
                                     ctrctNameOrLbl=contract_name)
    ParamInst(servicegroup_folder,
              name='servicegroupname',
              key='servicegroupname',
              value=name)
    ParamInst(servicegroup_folder,
              name='servicetype',
              key='servicetype',
              value=type)

    commit(epg)
    associate_vpx_servicegroup(epg, graph_template_name, contract_name, node_name, name)

    return servicegroup_folder


def bind_vpx_servicegroup(graph_template_name, contract_name, node_name, vserver_folder, servicegroup):
    """
    Bind a Service Group to a Virtual Server
    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param vserver_folder: Virtual Server Folder Instance
    :type vserver_folder: cobra.model.vns.FolderInst

    :param servicegroup: Service Group Name
    :type servicegroup: str

    :return: Virtual Server Folder
    :rtype: cobra.model.vns.FolderInst
    """

    # 'lbvserver_servicegroup_binding-' + name
    vserver_binding = FolderInst(vserver_folder,
                                 name=vserver_folder.name + '_' + servicegroup + '_binding',
                                 key='lbvserver_servicegroup_binding',
                                 nodeNameOrLbl=node_name,
                                 graphNameOrLbl=graph_template_name,
                                 ctrctNameOrLbl=contract_name)

    CfgRelInst(vserver_binding,
               name='servicename',
               key='servicename',
               targetName=servicegroup)

    commit(vserver_folder)
    return vserver_folder


def associate_vpx_vip(epg, graph_template_name, contract_name, node_name, vip_path):
    """
    Associate a VIP to vpx
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param vip_path: VIP path in the network folder, example: "network1/vip1"
    :type vip_path: str

    :return: mFCngNetwork Folder
    :rtype: cobra.model.vns.FolderInst
    """
    # vip_path = "network-folder/vip-name"
    vip_name = vip_path.split('/')[1]
    network_folder = vip_path.split('/')[0]

    mfcngnetwork_folder = FolderInst(epg,
                                     name='mFCngNetwork_' + vip_name,
                                     key='mFCngNetwork',
                                     nodeNameOrLbl=node_name,
                                     graphNameOrLbl=graph_template_name,
                                     ctrctNameOrLbl=contract_name)

    CfgRelInst(mfcngnetwork_folder,
               name='Network_key',
               key='Network_key',
               targetName=network_folder)

    commit(epg)
    return mfcngnetwork_folder


def associate_vpx_snip(epg, graph_template_name, contract_name, node_name, snip_path):
    """
    Associate a SNIP to vpx
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param snip_path: SNIP path in the network folder, example: "network1/snip1"
    :type snip_path: str

    :return: Internal Network Folder
    :rtype: cobra.model.vns.FolderInst
    """
    # snip_path = "network-folder/snip-name"
    snip_name = snip_path.split('/')[1]

    internal_network_folder = FolderInst(epg,
                                name='internal_network-' + snip_name,
                                key='internal_network',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    CfgRelInst(internal_network_folder,
               name='internal_network_key',
               key='internal_network_key',
               targetName=snip_path)

    commit(epg)
    return internal_network_folder


def associate_vpx_servicegroup(epg, graph_template_name, contract_name, node_name, servicegroup_name):
    """
    Associate a Service Group with vpx
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param servicegroup_name: Service Group name
    :type servicegroup_name: str

    :return: mFCngservicegroup Folder
    :rtype: cobra.model.vns.FolderInst
    """
    mfcngservicegroup_folder = FolderInst(epg,
                                name='mFCngservicegroup-' + servicegroup_name,
                                key='mFCngservicegroup',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    CfgRelInst(mfcngservicegroup_folder,
               name='servicegroup_key',
               key='servicegroup_key',
               targetName=servicegroup_name)

    commit(epg)
    return mfcngservicegroup_folder


def associate_vpx_vserver(epg, graph_template_name, contract_name, node_name, vserver_name):
    """
    Associate a Virtual Server with a vpx
    :param epg: Target EPG (Provider)
    :type epg: cobra.model.fv.AEPg

    :param graph_template_name: Service Graph Template name
    :type graph_template_name: str

    :param contract_name: Contract name
    :type contract_name: str

    :param node_name: Service Graph Template Node name
    :type node_name: str

    :param vserver_name: Virtual Server name
    :type vserver_name: str

    :return: mFCnglbvserver Folder
    :rtype: cobra.model.vns.FolderInst
    """

    mfcnglbvserver_folder = FolderInst(epg,
                                       name='mFCnglbvserver-' + vserver_name,
                                       key='mFCnglbvserver',
                                       nodeNameOrLbl=node_name,
                                       graphNameOrLbl=graph_template_name,
                                       ctrctNameOrLbl=contract_name)

    CfgRelInst(mfcnglbvserver_folder,
               name='lbvserver_key',
               key='lbvserver_key',
               targetName='lbvserver-' + vserver_name)

    commit(epg)
    return mfcnglbvserver_folder


def associate_vpx_vserver_ssl(epg, graph_template_name, contract_name, node_name, vserver_name):
    mfcngsslvserver_folder = FolderInst(epg,
                                        name='mFCngsslvserver-' + vserver_name,
                                        key='mFCngsslvserver',
                                        nodeNameOrLbl=node_name,
                                        graphNameOrLbl=graph_template_name,
                                        ctrctNameOrLbl=contract_name)

    CfgRelInst(mfcngsslvserver_folder,
               name='sslvserver_key',
               key='sslvserver_key',
               targetName='sslvserver-' + vserver_name)

    commit(epg)
    return mfcngsslvserver_folder


def associate_vpx_certificate(epg, graph_template_name, contract_name, node_name, certificate):
    mfcngsslcertkey_folder = FolderInst(epg,
                                        name='mFCngsslcertkey-' + certificate,
                                        key='mFCngsslcertkey',
                                        nodeNameOrLbl=node_name,
                                        graphNameOrLbl=graph_template_name,
                                        ctrctNameOrLbl=contract_name)

    CfgRelInst(mfcngsslcertkey_folder,
               name='sslcertkey_key',
               key='sslcertkey_key',
               targetName='sslcertkey-' + certificate)

    commit(epg)
    return mfcngsslcertkey_folder


def get_vpx_network(epg):
    return get_folder_by_key(epg, 'Network')


def new_vpx_vip(epg, graph_template_name, contract_name, node_name, name, ip, mask):
    print "Creating a new VIP with IP " + ip + "..."
    network_folder = get_vpx_network(epg)

#    graph_template_name = network_folder.nodeNameOrLbl
#    contract_name = network_folder.ctrctNameOrLbl
#    node_name = network_folder.nodeNameOrLbl

    ip_folder = new_vpx_ip(network_folder, graph_template_name, contract_name, node_name, name, 'VIP', ip, mask)
    associate_vpx_vip(epg, graph_template_name, contract_name, node_name, network_folder.name + '/' + name)

    return str(ip_folder.dn)


def new_vpx_snip(epg, graph_template_name, contract_name, node_name,name, ip, mask):
    print "Creating a new SNIP with IP " + ip + "..."
    network_folder = get_vpx_network(epg)

#    graph_template_name = network_folder.nodeNameOrLbl
#    contract_name = network_folder.ctrctNameOrLbl
#    node_name = network_folder.nodeNameOrLbl

    ip_folder = new_vpx_ip(network_folder, graph_template_name, contract_name, node_name, name, 'SNIP', ip, mask)
    associate_vpx_snip(epg, graph_template_name, contract_name, node_name, network_folder.name + '/' + name)

    return str(ip_folder.dn)


def new_vpx_lb(epg, graph_template_name, contract_name, node_name,
                 vserver_name, service_group_name, protocol, port, vip_ip, vip_path, certificate_name=None):
    print "Creating a new vserver for " + vserver_name + " with VIP " + vip_ip + " and protocol " + protocol + "..."
    # vServer configuration
    vserver_folder = new_vpx_vserver(epg, graph_template_name, contract_name, node_name, vserver_name, vip_ip, protocol, port)
    bind_vpx_servicegroup(graph_template_name, contract_name, node_name, vserver_folder, service_group_name)

    associate_vpx_vip(epg, graph_template_name, contract_name, node_name, vip_path)

    if protocol == "SSL":
        # TODO check that certificate_name is given
        # Associate VIP with SSL vServer
        sslvserver_folder = new_vpx_vserver_ssl(epg, graph_template_name, contract_name, node_name,
                                                  vserver_name, certificate_name)
        bind_vpx_certificate(sslvserver_folder, graph_template_name, contract_name, node_name,
                               certificate_name)

    return vserver_folder


def associate_vpx_monitor(epg, graph_template_name, contract_name, node_name,
                            monitor_name):
    mfcnglbmonitor_folder = FolderInst(epg,
                                name='mFCnglbmonitor-' + monitor_name,
                                key='mFCnglbmonitor',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)

    CfgRelInst(mfcnglbmonitor_folder,
               name='lbmonitor_key',
               key='lbmonitor_key',
               targetName=monitor_name)

    commit(epg)
    return mfcnglbmonitor_folder


# type is:
# ARP                  HTTP-ECV             POP3
# CITRIX-AAC-LAS       HTTP-INLINE          RADIUS
# CITRIX-AAC-LOGINPAGE LDAP                 RADIUS_ACCOUNTING
# CITRIX-AG            LDNS-DNS             RTSP
# CITRIX-WEB-INTERFACE LDNS-PING            SIP-UDP
# CITRIX-WI-EXTENDED   LDNS-TCP             SMTP
# CITRIX-XD-DDC        LOAD                 SNMP
# CITRIX-XML-SERVICE   MSSQL-ECV            STOREFRONT
# DIAMETER             MYSQL                TCP
# DNS                  MYSQL-ECV            TCP-ECV
# DNS-TCP              ND6                  UDP-ECV
# FTP                  NNTP                 USER
# FTP-EXTENDED         ORACLE-ECV
# HTTP                 PING
def new_vpx_monitor(epg, graph_template_name, contract_name, node_name,
                      monitor_name, monitor_type, monitor_state="ENABLED"):
    print "Creating Monitor " + monitor_name + "..."
    monitor_folder = FolderInst(epg,
                                name=monitor_name,
                                key='lbmonitor',
                                nodeNameOrLbl=node_name,
                                graphNameOrLbl=graph_template_name,
                                ctrctNameOrLbl=contract_name)
    ParamInst(monitor_folder,
              name='monitorname',
              key='monitorname',
              value=monitor_name)
    ParamInst(monitor_folder,
              name='type',
              key='type',
              value=monitor_type)
    ParamInst(monitor_folder,
              name='state',
              key='state',
              value=monitor_state)

    commit(epg)
    associate_vpx_monitor(epg, graph_template_name, contract_name, node_name, monitor_name)

    return monitor_folder


def bind_vpx_monitor(graph_template_name, contract_name, node_name, servicegroup_folder, monitor_name):
    servicegroup_binding = FolderInst(servicegroup_folder,
                                      name=servicegroup_folder.name + '_' + monitor_name + '_binding',
                                      key='servicegroup_lbmonitor_binding',
                                      nodeNameOrLbl=node_name,
                                      graphNameOrLbl=graph_template_name,
                                      ctrctNameOrLbl=contract_name)

    CfgRelInst(servicegroup_binding,
               name='monitor_name',
               key='monitor_name',
               targetName=monitor_name)

    commit(servicegroup_binding)
    return servicegroup_binding


def new_vpx_route(epg, graph_template_name, contract_name, node_name, network, netmask, gateway):
    """
    Configure vpx IP address
    :param name: route name
    :type name: str

    :param network: Network (0.0.0.0 for example)
    :type type: str

    :param netmask: Network Mask (255.255.255.0 for example)
    :type ip: str

    :param gateway: Gateway Address (1.2.3.4 for example)
    :type mask: str

    :return: Network Folder
    :rtype: cobra.model.vns.FolderInst
    """

    print("Creating route " + network + " with mask " + netmask + " to " + gateway + "...")

    network_folder = get_vpx_network(epg)

#    graph_template_name = network_folder.nodeNameOrLbl
#    contract_name = network_folder.ctrctNameOrLbl
#    node_name = network_folder.nodeNameOrLbl

    route_folder = FolderInst(network_folder,
                           name='route-' + network,
                           key='route',
                           nodeNameOrLbl=node_name,
                           graphNameOrLbl=graph_template_name,
                           ctrctNameOrLbl=contract_name)

    ParamInst(route_folder,
              name='network',
              key='network',
              value=network)
    ParamInst(route_folder,
              name='netmask',
              key='netmask',
              value=netmask)
    ParamInst(route_folder,
              name='gateway',
              key='gateway',
              value=gateway)

    commit(network_folder)
    return network_folder

def new_mgmt_pbr(epg, srcip, nexthop):
    print("Creating PBR " + srcip + " nexthop " + nexthop + "...")

    network_folder = get_vpx_network(epg)

    graph_template_name = network_folder.nodeNameOrLbl
    contract_name = network_folder.ctrctNameOrLbl
    node_name = network_folder.nodeNameOrLbl

    pbr_folder = FolderInst(network_folder,
                           name='pbr-mgmt',
                           key='nspbr',
                           nodeNameOrLbl=node_name,
                           graphNameOrLbl=graph_template_name,
                           ctrctNameOrLbl=contract_name)

    ParamInst(pbr_folder,
              name='name',
              key='name',
              value='pbr-mgmt')
    ParamInst(pbr_folder,
              name='nexthop',
              key='nexthop',
              value='true')
    ParamInst(pbr_folder,
              name='nexthopval',
              key='nexthopval',
              value=nexthop)
    ParamInst(pbr_folder,
              name='action',
              key='action',
              value='ALLOW')
    ParamInst(pbr_folder,
              name='state',
              key='state',
              value='ENABLED')
    ParamInst(pbr_folder,
              name='srcip',
              key='srcip',
              value='true')
    ParamInst(pbr_folder,
              name='srcipop',
              key='srcipop',
              value='EQ')
    ParamInst(pbr_folder,
              name='srcipval',
              key='srcipval',
              value=srcip)

    commit(network_folder)
    return network_folder