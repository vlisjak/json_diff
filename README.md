# Learning DeepDiff library

- Comes handy when comparing results (possibly huge json payload) of API calls from network controller.
- DeepDiff can deal with nesting: lists, lists of dicts, dicts of lists, etc.
- You can also transoform xml into json (xmltodict) and then compare xml files with DeepDiff 

Sample results
- pls. ignore the meaningless content ;) - I just wanted to check operation ..

```
    .........................ITERABLE_ITEM_ADDED.........................


ADD | PATH  : yang-model-lisko:network/interfaces/interface/1
ADD | LEFT  : not present
ADD | RIGHT : {'name': 'GigabitEthernet1/1', 'description': 'NEW LIST ITEM interface'}


ADD | PATH  : yang-model-lisko:network/interfaces/interface/3
ADD | LEFT  : not present
ADD | RIGHT : {'NEW DICT in LIST': {'nested1': 'nested1 value1', 'nested2': 'nested2 value2'}}

    .........................VALUES_CHANGED.........................


CHG | PATH  : yang-model-lisko:network/system/description
CHG | LEFT  : Example router
CHG | RIGHT : Example router CHANGED DICT VALUE

    .........................DICTIONARY_ITEM_ADDED.........................


ADD | PATH  : yang-model-lisko:network/router bgp
ADD | LEFT  : not present
ADD | RIGHT : {'asn': '100 NEW DICT'}
