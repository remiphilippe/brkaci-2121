__author__ = "mihiguch"

# ACI Model imports
from cobra.model.fv import Ctx

from cobra.model.l3ext import Out
from cobra.model.l3ext import LNodeP
from cobra.model.l3ext import RsNodeL3OutAtt
from cobra.model.l3ext import LIfP
from cobra.model.l3ext import RsEctx
from cobra.model.l3ext import RsL3DomAtt
from cobra.model.l3ext import InstP
from cobra.model.l3ext import Subnet
from cobra.model.l3ext import RsPathL3OutAtt
from cobra.model.l3ext import Member
from cobra.model.l3ext import Ip
from cobra.model.ospf import IfP
from cobra.model.ospf import ExtP
from cobra.model.fv import RsCons

from network import attach_contract

def new_l3out(tenant, name, ctx, vlanid):
    """
    Create a new L3out
    :param tenant: Tenant where the l3out should be created
    :type tenant: cobra.model.fv.Tenant

    :param name: L3out name
    :return: str

    :param ctx: Context (aka Private Network)
    :type ctx: cobra.model.fv.Ctx

    :param vlanid: vlan id for L3out path (vlan-id)
    :type vlanid: int
    """

    # Create L3out #
    # Need to fix L3out name, router ID, node and interface number
    print "Creating the L3out " + name + "..."
    l3out = Out(tenant, name=name)
    rsectx = RsEctx(l3out, tnFvCtxName=ctx.name)
    l3dom = RsL3DomAtt(l3out, tDn = "uni/l3dom-L3out-A")
    ospfextp = ExtP(l3out,
                    areaCost="1",
                    areaCtrl="redistribute,summary",
                    areaId="backbone",
                    areaType="regular")

    nodep = LNodeP(l3out, name="NodeProfile")
    node1 = RsNodeL3OutAtt(nodep, rtrId="11.11.11.11", tDn="topology/pod-1/node-101")
    node2 = RsNodeL3OutAtt(nodep, rtrId="12.12.12.12", tDn="topology/pod-1/node-102")
    lifp = LIfP(nodep, name="InterfaceProfile")
    ifp = IfP(lifp, authType="none")
    path = RsPathL3OutAtt(lifp,
                          encap= 'vlan-' + str(vlanid),
                          encapScope="local",
                          ifInstT="ext-svi",
                          mac="00:22:BD:F8:19:FF",
                          mode="regular",
                          mtu="1500",
                          tDn="topology/pod-1/protpaths-101-102/pathep-[L3out-A_vPC]")

    member1 = Member(path, addr="10.1.1.11/24", side="A")
    ip1 = Ip(member1, addr="10.1.1.1/24")
    member2 = Member(path, addr="10.1.1.12/24", side="B")
    ip2 = Ip(member2, addr="10.1.1.1/24")

    instp = InstP(l3out, name=name)
    l3epg = Subnet(instp, ip="0.0.0.0/0", scope="import-security")
    return l3out
