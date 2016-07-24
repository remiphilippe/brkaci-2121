__author__ = 'mihiguch'
## reuse rephilip's core.py.  modify parameter for the demo setup


# ACI Model Information Tree imports
from cobra.mit.access import MoDirectory
from cobra.mit.session import LoginSession
from cobra.mit.request import ConfigRequest
from cobra.mit.request import DnQuery
from time import gmtime
from calendar import timegm
import os

import requests
requests.packages.urllib3.disable_warnings()

# Global
_last_connection = None
_apic = None
_uniMo = None

## APIC URL and credential
_url = 'http://10.23.248.147/'
_apic_username = 'admin'
_apic_password = 'ins3965!'

## VMM configuration
_vmm_name = 'ACI-vDS'
_vmm_controller_name = 'vcenter6.poclab.local'


def get_apic():
    """
    Create or Maintain APIC session
    :return: APIC session
    :rtype: cobra.mit.access.MoDirectory
    """
    global _apic, _last_connection

    if not _apic:
        _apic = _create_session(_url, _apic_username, _apic_password)
        _last_connection = timegm(gmtime())
    # To avoid some timeout situations, re-authenticate every 5 minutes
    elif (timegm(gmtime()) - _last_connection) > 300:
        print 'Session expired, reconnecting...'
        _apic = _create_session(_url, _apic_username, _apic_password)
        _last_connection = timegm(gmtime())
    return _apic


def get_uniMo():
    """
    Get the uni base
    :return: uni
    :rtype: object
    """
    global _uniMo
    if not _uniMo:
        _uniMo = get_apic().lookupByDn('uni')
    return _uniMo

__all__ = [ 'get_apic', 'get_uniMo' ]


def commit(obj, moDir=''):
    """
    Commit the object to APIC
    :param obj: Object to be committed
    :type obj: object

    :param moDir: Optional moDir string
    :type moDir: str

    :return: Nothing
    :rtype: object
    """
    # function to commit
    md = get_apic()
    configReq = ConfigRequest()
    configReq.addMo(obj)
    md.commit(configReq)


def _create_session(apicUrl, username, password):
    """
    Create a new session to APIC
    :param apicUrl: URL of the APIC (https://x.x.x.x or fqdn)
    :type apicUrl: str

    :param username: Username of the APIC
    :type username: str

    :param password: Password of the APIC
    :type password: str

    :return: moDir object
    :rtype: cobra.mit.access.MoDirectory
    """
    # connect to a host (an APIC)
    print "Connecting to APIC..."
    loginSession = LoginSession(apicUrl, username, password)
    moDir = MoDirectory(loginSession)
    moDir.login()
    return moDir


def get_vmm(dn=False):
    """ Get the VMM domain name or DN
    :param dn: True if return string must be the dn, False if return string should be the VMM-Name
    :type dn: bool
    :return: VMM domain name or dn
    :rtype: str
    """
    if dn:
        return 'uni/vmmp-VMware/dom-' + _vmm_name
    else:
        return _vmm_name


def get_vmm_controller(dn=False):
    """ Get the VMM controller name or DN
    :param dn: True if return string must be the dn, False if return string should be the VMM-Name
    :type dn: bool
    :return: VMM controller name or dn
    :rtype: str
    """
    if dn:
        return 'uni/vmmp-VMware/dom-' + _vmm_name + '/ctrlr-' + _vmm_controller_name
    else:
        return _vmm_controller_name


def get_one(dn):
    """ Get one element of the MIT
    :param dn: dn of the element to be returned
    :type dn: str
    :return: queried object or None
    :rtype: object
    """
    md = get_apic()
    dnq = DnQuery(dn)
    dnq.queryTarget = 'subtree'
    obj = md.query(dnq)
    return obj.pop()

def filter_by_class(filter_class, parent_dn=None, prop_filter=None):
    md = get_apic()
    obj = md.lookupByClass(filter_class,
                           parentDn=parent_dn,
                           propFilter=prop_filter)

    if len(obj) < 1:
        return None
    else:
        return obj

def get_many(container, object):
    obj = filter_by_class('fvAEPg', container.dn)

    return obj

def get_folder_by_key(container, key_name):
    obj = filter_by_class('vnsFolderInst', container.dn, 'eq(vnsFolderInst.key, "' + key_name + '")')

    if obj == None:
        return None
    else:
        return obj.pop()