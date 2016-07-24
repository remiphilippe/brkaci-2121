import sys
sys.path.append("..")

from tenant import delete_tenant

from run_00_parameters import *

if __name__ == '__main__':
    ### delete tenant
    delete_tenant(entity_name)
