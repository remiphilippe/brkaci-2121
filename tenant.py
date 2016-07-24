__author__ = 'rephilip'

from core import get_uniMo
from core import commit
from core import get_one

from cobra.model.fv import Tenant

def new_tenant(name):
    """
    Create a new Tenant
    :param name: Tenant name
    :type name: str

    :return: cobra.model.fv.Tenant
    """
    unimo = get_uniMo()
    tenant = Tenant(unimo, name)
    return tenant

def delete_tenant(name):
    print 'Deleting tenant ' + name + "..."
    tenant = get_one('uni/tn-' + name)
    tenant.delete()
    commit(tenant)
    