__author__ = 'mihiguch'

import sys
sys.path.append("..")

from core import get_apic
from core import commit

from service_graph import new_graph_profile_group
from service_graph import new_graph_template
from service_graph import new_graph_profile
from device import new_logical_device
from device import new_concrete_device


from run_00_parameters import *



if __name__ == '__main__':
    md = get_apic()
    entity = get_one(entity_dn)

    name = entity_name

    ### Create new function profile
    zone1_dmz_group = new_graph_profile_group(entity, zone1_dmz_graph_name + '_Profiles')
    zone1_dmz_fw_profile = new_graph_profile(zone1_dmz_group, 'Firewall', 'uni/infra/mDev-CISCO-ASA-1.2/mFunc-Firewall')
    zone1_dmz_adc_profile = new_graph_profile(zone1_dmz_group, 'ADC', 'uni/infra/mDev-F5-BIGIP-2.0/mFunc-Virtual-Server')

    # Terminal seem to be per graph, so we need profiles per graph
    # Provider terminals are always T2 (in this configuration)
    # Consumer terminals are always T1 (in this configuration)
    zone1_dmz_fw_cons_t = 'uni/tn-' + name + '/AbsGraph-' + str(zone1_dmz_graph_name) + '/AbsTermNodeCon-T1/intmnl'
    zone1_dmz_fw_prov_t = 'uni/tn-' + name + '/AbsGraph-' + str(zone1_dmz_graph_name) + '/AbsTermNodeProv-T2/outmnl'

    ### FW-ADC Service Graph ###
    fw_adc_graph_parameters = dict(
        nodes=[
            dict(
                name='Firewall',
                type='GoTo',
                funcTemplateType='FW_ROUTED',
                function='uni/infra/mDev-CISCO-ASA-1.2/mFunc-Firewall',
                profile=str(zone1_dmz_fw_profile.dn)
            ),
            dict(
                name='ADC',
                type='GoTo',
                funcTemplateType='ADC_ONE_ARM',
                function='uni/infra/mDev-F5-BIGIP-2.0/mFunc-Virtual-Server',
                profile=str(zone1_dmz_adc_profile.dn)
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
                adjacency='L2',
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

    zone1_dmz_graph = new_graph_template(entity, zone1_dmz_graph_name, fw_adc_graph_parameters)


    ### ADC only Service Graph ###
    adc_graph_parameters = dict(
        nodes=[
            dict(
                name='ADC',
                type='GoTo',
                funcTemplateType='ADC_ONE_ARM',
                function='uni/infra/mDev-F5-BIGIP-2.0/mFunc-Virtual-Server',
                profile=str(zone1_dmz_adc_profile.dn)
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
                        node='ADC'
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
    zone2_adc_graph = new_graph_template(entity, zone2_adc_graph_name, adc_graph_parameters)


    #### Create ASA LdevVip (Logical Device) ###
    asa_linterfaces = [
        dict(
            name='external',
            type='external'
        ),
        dict(
            name='internal',
            type='internal'
            #       ),
            #        dict(
            #            name='fover_lan',
            #            type='failover_lan'
            #        ),
            #        dict(
            #            name='fover_link',
            #            type='failover_link'
        )
    ]

    asa_ldev = new_logical_device(entity, asav_mgmt['name'], 'asav', asav_mgmt['ip'], '443', asav_mgmt['username'], asav_mgmt['password'], asa_linterfaces)

    # ASA concrete interfaces
    asa_cinterfaces = [
        dict(
            vnic='Network adapter 2',
            physical='GigabitEthernet0/0',
            logical='external'
        ),
        dict(
            vnic='Network adapter 3',
            physical='GigabitEthernet0/1',
            logical='internal'
        )
    ]

    new_concrete_device(asa_ldev, asav_mgmt['vmname'], asav_mgmt['ip'], '443', asav_mgmt['username'], asav_mgmt['password'], asa_cinterfaces)


    #### Create bIGIPLdevVip (Logical Device) ###
    bigip_linterfaces = [
        dict(
            name='internal',
            type='internal'
        )
    ]

    bigip_ldev = new_logical_device(entity, bigip_mgmt['name'], 'bigip', bigip_mgmt['ip'], '443', bigip_mgmt['username'], bigip_mgmt['password'],bigip_linterfaces)

    # BIGIP concrete interfaces
    bigip_cinterfaces = [
        dict(
            vnic='Network adapter 2',
            physical='1_1',
            logical='internal'
        )
    ]

    new_concrete_device(bigip_ldev, bigip_mgmt['vmname'], bigip_mgmt['ip'], '443', bigip_mgmt['username'], bigip_mgmt['password'], bigip_cinterfaces)


    commit(entity)

