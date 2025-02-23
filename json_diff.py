#!/usr/bin/env python

import pprint as pp
import json
import xmltodict
import difflib
from deepdiff import DeepDiff, Delta
from deepdiff import extract
from deepdiff.serialization import json_dumps, json_loads
from typing import Callable
from jycm.jycm import YouchamaJsonDiffer
from jycm.helper import make_ignore_order_func


# TODO:
# - verify DeepDiff handling of list items - maybe we need some knob to sort the list?
#

left_file = "network-payload-left.json"
right_file = "network-payload-right.json"

with open(left_file) as json_left:
    left = json.loads(json_left.read())
with open(right_file) as json_right:
    right = json.loads(json_right.read())

chg = {
    "iterable_item_added": "ADD",
    "list:add": "ADD",
    "dictionary_item_added": "ADD",
    "dict:add": "ADD",
    "iterable_item_removed": "DEL",
    "list:remove": "DEL",
    "dictionary_item_removed": "DEL",
    "dict:remove": "DEL",
    "values_changed": "CHG",
    "value_changes": "CHG",
}


def using_deepdiff(left, right):

    print("\n##### Using DeepDiff\n")

    def build_item_path(tree_list):
        return "/".join(str(x) for x in tree_list)

    def build_device_path(tree_list):
        return "root[" + "][".join(str(x) for x in tree_list) + "]"

    dd_tree = DeepDiff(
        left,
        right,
        ignore_order=True,
        report_repetition=True,
        view="tree",
        threshold_to_diff_deeper=0,
    )

    # print(dd_tree.pretty())
    for diff_action in sorted(dd_tree):
        print(25 * "-" + diff_action.upper() + 25 * "-" + "\n")
        for item in dd_tree[diff_action]:
            item_path_list = item.path(output_format="list")
            item_path = build_item_path(item_path_list)
            print(chg[diff_action] + " | PATH  :", item_path)
            print(chg[diff_action] + " | LEFT  :", item.t1)
            print(chg[diff_action] + " | RIGHT :", item.t2)
            print("\n")


def xml_using_deepdiff(left, right):

    print("\n##### We can use DeepDiff for xml comparison: xml->dict->json->diff\n")

    left_file = "left.xml"
    right_file = "right.xml"

    with open(left_file) as xml_left:
        left = json.loads(json.dumps((xmltodict.parse(xml_left.read()))))

    with open(right_file) as xml_right:
        right = json.loads(json.dumps((xmltodict.parse(xml_right.read()))))

    using_deepdiff(left, right)


def using_difflib(left, right):

    print("\n##### using difflib and coloured diff\n")

    RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
    GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"

    def get_edits_string(old: str, new: str) -> str:
        result = ""

        # lines = difflib.ndiff(old.splitlines(keepends=True), new.splitlines(keepends=True))
        lines = difflib.unified_diff(
            old.splitlines(keepends=True),
            new.splitlines(keepends=True),
            fromfile="before",
            tofile="after",
        )

        for line in lines:
            line = line.rstrip()
            if line.startswith("+"):
                result += GREEN(line) + "\n"
            elif line.startswith("-"):
                result += RED(line) + "\n"
            elif line.startswith("?"):
                continue
            else:
                result += line + "\n"

        return result

    print(
        get_edits_string(
            json.dumps(left, indent=4, sort_keys=True),
            json.dumps(right, indent=4, sort_keys=True),
        )
    )


def using_jycm(left, right):

    print("\n##### Using Jycm\n")

    ycm = YouchamaJsonDiffer(
        left, right, ignore_order_func=make_ignore_order_func([".*"])
    )

    diff_result = ycm.get_diff()

    for diff_action in sorted(diff_result):
        if diff_action == "just4vis:pairs":
            continue
        print(25 * "-" + diff_action.upper() + 25 * "-" + "\n")
        for item in diff_result[diff_action]:
            print(chg[diff_action] + " | PATH_LEFT  :", item["left_path"])
            print(chg[diff_action] + " | LEFT  :", item["left"])
            print(chg[diff_action] + " | PATH_RIGHT  :", item["right_path"])
            print(chg[diff_action] + " | RIGHT :", item["right"])
            print("\n")


if __name__ == "__main__":
    using_deepdiff(left, right)
    # xml_using_deepdiff(left, right)
    using_difflib(left, right)
    using_jycm(left, right)
