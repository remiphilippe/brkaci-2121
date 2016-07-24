__author__ = 'mihiguch'
## reuse rephilip's network.py.  modify parameter for the demo setup. add create BD with subnet

# ACI Model imports
from cobra.model.fv import Ctx
from cobra.model.fv import AEPg
from cobra.model.fv import BD
from cobra.model.fv import RsCtx
from cobra.model.fv import Ap
from cobra.model.vz import BrCP
from cobra.model.vz import Subj
from cobra.model.vz import RsSubjFiltAtt
from cobra.model.vz import RsSubjGraphAtt
from cobra.model.fv import RsCons
from cobra.model.fv import RsProv

# ACI Model imports (Added)
from cobra.model.fv import Subnet
from cobra.model.fv import RsBDToOut

# Core APIC imports
from core import get_one
from core import filter_by_class
from core import commit


def new_epg(ap, name):
    """
    Create a new EPG
    :param ap: Application Profile
    :type ap: cobra.model.fv.Ap

    :param name: EPG name
    :type name: str

    :return: EPG object
    :rtype: cobra.model.fv.AEPg
    """
    print "Creating the EPG " + name + "..."
    epg = AEPg(ap, name)
    return epg


def get_epg(ap, name):
    """
    Get an EPG
    :param ap: Application Profile
    :type ap: cobra.model.fv.Ap

    :param name: EPG name
    :type name: str

    :return: EPG object
    :rtype: cobra.model.fv.AEPg
    """
    epg = get_one(str(ap.dn) + '/epg-' + name)
    return epg


def new_l2bd(tenant, name, ctx):
    """
    Create a new L2 Bridge Domain (Flooding enabled, no unicast routing)
    :param tenant: Tenant in which the bridge domain should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Name of the bridge domain
    :type name: str

    :param ctx: Context (aka Private Network)
    :type ctx: cobra.model.fv.Ctx

    :return: Bridge Domain
    :rtype: cobra.model.fv.BD
    """
    print "Creating the L2 Bridge Domain " + name + "..."
    bd = BD(tenant,
            name,
            arpFlood='yes',
            unicastRoute='no',
            unkMacUcastAct='flood',
            unkMcastAct='flood')
    RsCtx(bd, tnFvCtxName=ctx.name)
    return bd

def new_l2bd_routing(tenant, name, ctx, svi):
    """
    Create a new L2 Bridge Domain (Flooding enabled, unicast routing)
    :param tenant: Tenant in which the bridge domain should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Name of the bridge domain
    :type name: str

    :param ctx: Context (aka Private Network)
    :type ctx: cobra.model.fv.Ctx

    :param svi: svi IP/subnet (BD subnet)
    :type svi: str

    :return: Bridge Domain
    :rtype: cobra.model.fv.BD
    """
    print "Creating the L2 Bridge Domain with Unicast Routing enabled " + name + "..."
    bd = BD(tenant,
            name,
            arpFlood='yes',
            unicastRoute='yes',
            unkMacUcastAct='flood',
            unkMcastAct='flood')
    RsCtx(bd, tnFvCtxName=ctx.name)
    Subnet(bd, ip=svi, scope='private')
    return bd

def new_l2bd_routing_adv(tenant, name, ctx, svi, l3out):
    """
    Create a new L2 Bridge Domain (Flooding enabled, unicast routing) Advertised externally
    :param tenant: Tenant in which the bridge domain should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Name of the bridge domain
    :type name: str

    :param ctx: Context (aka Private Network)
    :type ctx: cobra.model.fv.Ctx

    :param svi: svi IP/subnet (BD subnet)
    :type svi: str

    :param l3out: Associated L3out
    :type l3out: str

    :return: Bridge Domain
    :rtype: cobra.model.fv.BD
    """
    print "Creating the L2 Bridge Domain with Unicast Routing enabled " + name + "..."
    bd = BD(tenant,
            name,
            arpFlood='yes',
            unicastRoute='yes',
            unkMacUcastAct='flood',
            unkMcastAct='flood')
    RsCtx(bd, tnFvCtxName=ctx.name)
    Subnet(bd, ip=svi, scope='public')
    RsBDToOut(bd, tnL3extOutName = l3out)
    return bd


def get_bd(tenant_name, bd_name):
    """
    Get a Bridge Domain
    :param tenant_name: Tenant name
    :type tenant_name: str

    :param bd_name: BD name
    :type bd_name: str

    :return: Bridge Domain
    :rtype: cobra.model.fv.BD
    """
    # We should only have one result
    bd = get_one('uni/tn-' + tenant_name + '/BD-' + bd_name)
    return bd


def new_ap(tenant, name):
    """
    Create a new Application Profile
    :param tenant: Tenant in which the application profile should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Application Profile name
    :type name: str

    :return: Application Profile
    :rtype: cobra.model.fv.Ap
    """
    print "Creating the Application Profile " + name + "..."
    ap = Ap(tenant, name)
    return ap


def new_context(tenant, name):
    """
    Create a new Context (aka Private Network), enforced contracts
    :param tenant: Tenant in which the context should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Name of the Context
    :type name: str

    :return: Context Object
    :rtype: cobra.model.fv.Ctx
    """
    print "Creating the Context " + name + "..."
    context = Ctx(tenant, name,
                  pcEnfPref='enforced')
    return context


def get_context(tenant):
    """
    Get a Context
    :param tenant: Tenant that hosts the context (in the FEDnet model, Context name is the same as tenant name)
    :type tenant: cobra.model.fv.Tenant

    :return: Context Object
    :rtype: cobra.model.fv.Ctx
    """
    print "Getting the Context for entity " + tenant.name + "..."
    return get_one(str(tenant.dn) + '/ctx-' + tenant.name)


def new_contract(tenant, name, graph_template_name=None):
    """
    Create a new contract
    :param tenant: Tenant in which the contract should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: Contract name
    :type name: str

    :param graph_template_name: Graph Template Name to apply to the contract
    :type graph_template_name: str

    :return: Contract object
    :rtype: cobra.model.vz.BrCP
    """
    print "Creating the contract " + name + "..."
    contract = BrCP(tenant, name)
    subject = Subj(contract, 'Subject')
    # Attach filter to subject
    RsSubjFiltAtt(subject,
                  tnVzFilterName='default')
    if graph_template_name:
        print "Attaching Service Graph " + graph_template_name + "..."
        # Attach service graph to subject
        RsSubjGraphAtt(subject,
                   tnVnsAbsGraphName=graph_template_name)
    commit(contract)
    return contract


def attach_contract(contract, epg, direction):
    """
    Attach contract to EPG
    :param contract: Contract name
    :type contract: str

    :param epg: Attachment EPG
    :type epg: cobra.model.fv.AEPg

    :param direction: Direction for the contract (provider or consumer)
    :type direction: str

    :return: EPG
    :rtype: cobra.model.fv.AEPg
    """
    print "Attaching the contract " + contract + " as " + direction + "..."
    if direction == 'consumer':
        RsCons(epg,
               tnVzBrCPName=contract)
        commit(epg)
    elif direction == 'provider':
        RsProv(epg,
               tnVzBrCPName=contract)

    commit(epg)
    return epg




def get_vlan_for_epg(epg):
    obj = filter_by_class('vmmEpPD', None, 'eq(vmmEpPD.epgPKey, "' + str(epg.dn) + '")')

    if obj:
        return obj.pop().encap
    else:
        return None