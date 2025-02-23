# JSON and XML diffs

## DeepDiff - probably most popular library:
`./json_diff.py -l network-payload-left.json -r network-payload-right.json -t json -m deepdiff`
```
+ | yang-model-lisko:network/router bgp | not present | {'asn': '100'}
- | yang-model-lisko:network/interfaces/interface/0/mtu | 1999 | not present
- | yang-model-lisko:network/nodes/node/2 | {'name': 'n3', 'description': 'd3'} | not present
# | yang-model-lisko:network/system/description | Example router | Example router R1
# | yang-model-lisko:network/interfaces/interface/3/name | GigabitEthernet1/1 | GigabitEthernet1/4
# | yang-model-lisko:network/nodes/node/0/description | d1 | d11
```

## Jycm - similar results to DeepDiff:
`./json_diff.py -l network-payload-left.json -r network-payload-right.json -t json -m jycm`

```
##### Using Jycm

-------------------------DICT:ADD-------------------------

+ | PATH_L | 
+ | PATH_R | yang-model-lisko:network->router bgp
+ |      L | __NON_EXIST__
+ |      R | {'asn': '100'}

-------------------------DICT:REMOVE-------------------------

- | PATH_L | yang-model-lisko:network->interfaces->interface->[0]->mtu
- | PATH_R | 
- |      L | 1999
- |      R | __NON_EXIST__

-------------------------LIST:REMOVE-------------------------

- | PATH_L | yang-model-lisko:network->nodes->node->[2]
- | PATH_R | 
- |      L | {'name': 'n3', 'description': 'd3'}
- |      R | __NON_EXIST__

-------------------------VALUE_CHANGES-------------------------

# | PATH_L | yang-model-lisko:network->interfaces->interface->[3]->name
# | PATH_R | yang-model-lisko:network->interfaces->interface->[3]->name
# |      L | GigabitEthernet1/1
# |      R | GigabitEthernet1/4

# | PATH_L | yang-model-lisko:network->nodes->node->[0]->description
# | PATH_R | yang-model-lisko:network->nodes->node->[1]->description
# |      L | d1
# |      R | d11

# | PATH_L | yang-model-lisko:network->system->description
# | PATH_R | yang-model-lisko:network->system->description
# |      L | Example router
# |      R | Example router R1
```
## DiffLib - result is similar to "legacy" diff, including red/green coloring in the terminal

`./json_diff.py -l network-payload-left.json -r network-payload-right.json -t json -m difflib`

![DiffLib results](difflib_coloured_results.jpg)

## XML deepdiff:
`./json_diff.py -l left.xml -r right.xml -t xml -m deepdiff`

```
+ | config/vrf/vrf-list/1/address-family/ipv4/unicast/export/route-target/address-list/name111 | not present | 1:2
- | config/vrf/vrf-list/1/address-family/ipv4/unicast/export/route-target/address-list/name | 1:2 | not present
# | config/vrf/vrf-list/1/rd | 1:2 | 1:3
# | config/vrf/vrf-list/1/address-family/ipv4/unicast/import/route-target/address-list/name | 1:2 | 1:3
# | config/router/bgp/bgp-no-instance/vrf/1/neighbor/id | 9.2.2.2 | 9.2.2.3
```
