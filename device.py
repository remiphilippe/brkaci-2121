__author__ = 'rephilip'
## reuse rephilip's device.py.  modify parameter for the demo setup

# Core APIC imports
from core import commit
from core import get_vmm
from core import get_vmm_controller
from core import get_one

# ACI Logical Device Model imports
from cobra.model.vns import LDevVip
from cobra.model.vns import RsMDevAtt
from cobra.model.vns import RsDevEpg
from cobra.model.vns import RsALDevToDomP
from cobra.model.vns import CCredSecret
from cobra.model.vns import LIf
from cobra.model.vns import RsMetaIf
from cobra.model.vns import RsCIfAtt

# ACI Concrete Device Model imports
from cobra.model.vns import CDev
from cobra.model.vns import CIf
from cobra.model.vns import CMgmt
from cobra.model.vns import CCred


# device package dn
_device_package = dict(
    asav='uni/infra/mDev-CISCO-ASA-1.2',
    vpx='uni/infra/mDev-Citrix-NetScaler-1.0',
    bigip='uni/infra/mDev-F5-BIGIP-2.0')

# asav logical interface dn
_asav_lif = dict(
    internal=_device_package['asav'] + '/mIfLbl-internal',
    external=_device_package['asav'] + '/mIfLbl-external',
    failover_lan=_device_package['asav'] + '/mIfLbl-failover_lan',
    failover_link=_device_package['asav'] + '/mIfLbl-failover_link')

# VPX logical interface dn
_vpx_lif = dict(
    internal=_device_package['vpx'] + '/mIfLbl-inside',
)

# BIGIP interface dn
_bigip_lif = dict(
    internal=_device_package['bigip'] + '/mIfLbl-internal'
)

def get_logical_interface(logical_dn, name):
    """
    Gets the logical interface object for a specific name

    :param logical: Logical Device DN
    :type logical: str

    :param name: Name of the logical interface
    :type name: str

    :return: Logical Interface
    :rtype: cobra.model.vns.LIf
    """
    lif = get_one(str(logical_dn) + '/lIf-' + str.lower(name))
    return lif


def new_logical_interface(logical, device_type, intf_name, intf_type):
    """
    Create a new logical interface for a logical device

    :param logical: Logical Device
    :type logical: cobra.model.vns.LDevVip

    :param device_type: type of the device (asav or ns1kv)
    :type device_type: str

    :param intf_name: Name of the logical interface
    :type intf_name: str

    :param intf_type: Type of the interface (from _asav_lif or _ns1kv_lif)
    :type intf_type: str

    :return: Logical Interface
    :rtype: cobra.model.vns.LIf
    """
    print "Creating a logical interface " + intf_name + " for logical device " + logical.name + " (type " + intf_type + ")..."
    if device_type == 'asav':
        interfaces = _asav_lif
    elif device_type == 'vpx':
        interfaces = _vpx_lif
    elif device_type == 'bigip':
        interfaces = _bigip_lif

    lif = LIf(logical, intf_name)
    commit(lif)
    RsMetaIf(lif,
             tDn=interfaces[intf_type])

    commit(lif)
    return lif


def new_concrete_interface(concrete, logical, physical_intf, lif_name, vnic):
    """
    Create a new concrete interface for a concrete device

    :param concrete: Concrete device
    :type concrete: cobra.model.vns.CDev

    :param logical: Logical Device
    :type logical: cobra.model.vns.LDevVip

    :param physical_intf: Physical Interface name
    For ASAv: Gig0/0, Gig0/1 ...
    For NS1KV: 1/1
    :type physical_intf: str

    :param lif_name: Name of the logical interface of the Logical device cluster
    :type lif_name: str

    :param vnic: Name of the VMware vNic adapter. --- THIS IS CASE SENSITIVE ---
    Example: "Network adapter 1", "Network adapter 2" (without the quotes, note that adapter is all lower case)

    :return: Logical Interface
    :rtype: cobra.model.vns.LIf
    """
    print "Creating a concrete interface for physical " + physical_intf + " associated with logical interface " + lif_name + "..."
    print "Logical device is " + logical.name + "..."
    lif = get_logical_interface(logical.dn, lif_name)
    cif = CIf(concrete, physical_intf,
              vnicName=vnic)
    commit(cif)

    RsCIfAtt(lif,
             tDn=str(cif.dn))
    commit(lif)

    return cif


def new_logical_device(tenant, name, type, ip, port, login, password, interfaces, mgmt=None):
    """
    Create a new Logical Device Cluster

    :param tenant: Tenant in which the logical device should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Name of the logical device
    :type name: str

    :param type: Type of the device being created (asav, vpx or bigip)
    :type type: str

    :param ip: Cluster IP of the device (IP of the active instance)
    :type ip: str

    :param port: Management port (443 for ASAv, 80 for NS1KV)
    :type port: int

    :param login: Admin user login
    :type login: str

    :param password: Admin user password
    :type password: str

    :param interfaces: List of interfaces to be created, format:
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
    type is from the _asav_lif or _ns1kv_lif
    :type interfaces: list

    :param mgmt: DN of the management EPG (optional, if empty device will use out of band connection)
    :type mgmt: str

    :return: Logical device
    :rtype: cobra.model.vns.LDevVip
    """
    print "Creating new logical device " + name + " for tenant " + tenant.name
    vmm_tdn = get_vmm(True)
    type = str.lower(type)
    if type == 'asav':
        svctype = 'FW'
    elif type == 'bigip':
        svctype = 'ADC'
    elif type == 'vpx':
        svctype = 'ADC'

    # Create a logical device
    # Default context awareness is Single
    # The values are case sensitive
    logical = LDevVip(tenant,
                      name,
                      devtype='VIRTUAL',
                      funcType='GoTo',
                      svcType=svctype
                      )

    # Attach a device package
    RsMDevAtt(logical,
              tDn=_device_package[type])

    # Attach a VMM Domain
    RsALDevToDomP(logical,
                  tDn=vmm_tdn)

    # Attach a Management EPG
    # if empty = OOB
    if mgmt:
        RsDevEpg(logical,
                 tDn=mgmt)

    # Set the management IP
    CMgmt(logical,
          host=ip,
          port=port)

    # Set Credentials
    CCred(logical,
          name='username',
          value=login)
    CCredSecret(logical,
                name='password',
                value=password)

    commit(logical)

    # Create the Logical Interfaces
    for interface in interfaces:
        lif_name = interface['name']
        lif_type = interface['type']

        new_logical_interface(logical, type, lif_name, lif_type)

    # Save
    commit(tenant)
    return logical


def new_concrete_device(logical, device_name, ip, port, login, password, interfaces):
    """
    Create a new concrete device for a logical device cluster

    :param logical: Logical Device
    :type logical: cobra.model.vns.LDevVip

    :param device_name: Name of the device, if the device is a virtual machine it must match the VM name in vCenter
    As usual, case sensitive
    :type device_name: str

    :param ip: Management IP of the concrete device
    :type ip: str

    :param port: Management port of the concrete device
    :type port: int

    :param login: Admin user login
    :type login: str

    :param password: Admin user password
    :type password: str

    :param interfaces: List of physical interfaces
new_concrete_
    :type interfaces: lists

    :return: Concrete device
    :rtype: cobra.model.vns.CDev
    """
    print "Creating new concrete device " + device_name + " for logical device " + logical.name + "..."
    vmm_controller = get_vmm_controller()

    concrete = CDev(logical,
                    device_name,
                    vcenterName=vmm_controller,
                    vmName=device_name)

    # Set the management IP
    CMgmt(concrete,
          host=ip,
          port=port)

    # Set Credentials
    CCred(concrete,
          name='username',
          value=login)
    CCredSecret(concrete,
                name='password',
                value=password)

    commit(logical)

    for interface in interfaces:
        vnic = interface['vnic']
        physical = interface['physical']
        lif_name = interface['logical']

        new_concrete_interface(concrete, logical, physical, lif_name, vnic)

    commit(logical)
    return concrete