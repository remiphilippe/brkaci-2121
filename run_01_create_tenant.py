__author__ = 'mihiguch'
import sys
sys.path.append("..")

from core import get_apic
from run_00_parameters import *

from entity import new_entity

if __name__ == '__main__':
    md = get_apic()

    # First step - Create an entity(tenant) with external networks(L3out)
    entity = new_entity(entity_name,
                        True,
                        l3out_vlan
    )

