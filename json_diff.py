#!/usr/bin/env python

import json
import xmltodict
import difflib
from deepdiff import DeepDiff
from typing import Callable
from jycm.jycm import YouchamaJsonDiffer
from jycm.helper import make_ignore_order_func


class DiffResult:
    def __init__(self, diff_data, show_func):
        self.diff_data = diff_data
        self.show_func = show_func

    def show_diff(self):
        self.show_func(self.diff_data)


class JsonDiff:
    def __init__(self, left_file: str, right_file: str):
        self.left_file = left_file
        self.right_file = right_file
        self.left = self.load_json(left_file)
        self.right = self.load_json(right_file)
        self.chg = {
            # DeepDiff actions
            "iterable_item_added": "ADD",
            "dictionary_item_added": "ADD",
            "iterable_item_removed": "DEL",
            "dictionary_item_removed": "DEL",
            "values_changed": "CHG",
            # DiffLib actions
            "list:add": "ADD",
            "dict:add": "ADD",
            "list:remove": "DEL",
            "dict:remove": "DEL",
            "value_changes": "CHG",
        }

    @staticmethod
    def load_json(file_path: str):
        try:
            with open(file_path, "r") as file:
                json_string = json.loads(file.read())
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            raise
        except json.JSONDecodeError as e:
            print(f"Error: Failed to decode JSON from the file '{file_path}': {e}")
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__}: {e}")
            raise
        else:
            return json_string

    def diff(self):
        raise NotImplementedError("Subclasses should implement this!")

    def show_diff(self, diff_result):
        raise NotImplementedError("Subclasses should implement this!")


class DeepDiffJsonDiff(JsonDiff):
    def diff(self):
        diff_data = DeepDiff(
            self.left,
            self.right,
            ignore_order=True,
            report_repetition=True,
            view="tree",
            threshold_to_diff_deeper=0,
        )
        return DiffResult(diff_data, self.show_diff)

    def show_diff(self, diff_result):
        print("\n##### Using DeepDiff\n")
        for diff_action in sorted(diff_result):
            print(25 * "-" + diff_action.upper() + 25 * "-" + "\n")
            for item in diff_result[diff_action]:
                item_path_list = item.path(output_format="list")
                item_path = "/".join(str(x) for x in item_path_list)
                print(self.chg[diff_action] + " | PATH  :", item_path)
                print(self.chg[diff_action] + " | LEFT  :", item.t1)
                print(self.chg[diff_action] + " | RIGHT :", item.t2)
                print("\n")


class DifflibJsonDiff(JsonDiff):
    def diff(self):
        RED: Callable[[str], str] = lambda text: f"\u001b[31m{text}\033\u001b[0m"
        GREEN: Callable[[str], str] = lambda text: f"\u001b[32m{text}\033\u001b[0m"

        def get_edits_string(old: str, new: str) -> str:
            result = ""
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
                else:
                    result += line + "\n"
            return result

        diff_data = get_edits_string(
            json.dumps(self.left, indent=4, sort_keys=True),
            json.dumps(self.right, indent=4, sort_keys=True),
        )
        return DiffResult(diff_data, self.show_diff)

    def show_diff(self, diff_result):
        print("\n##### Using difflib and coloured diff\n")
        print(diff_result)


class JycmJsonDiff(JsonDiff):
    def diff(self):
        ycm = YouchamaJsonDiffer(
            self.left, self.right, ignore_order_func=make_ignore_order_func([".*"])
        )
        diff_data = ycm.get_diff()
        return DiffResult(diff_data, self.show_diff)

    def show_diff(self, diff_result):
        print("\n##### Using Jycm\n")
        for diff_action in sorted(diff_result):
            if diff_action == "just4vis:pairs":
                continue
            print(25 * "-" + diff_action.upper() + 25 * "-" + "\n")
            for item in diff_result[diff_action]:
                print(self.chg[diff_action] + " | PATH_LEFT  :", item["left_path"])
                print(self.chg[diff_action] + " | LEFT  :", item["left"])
                print(self.chg[diff_action] + " | PATH_RIGHT  :", item["right_path"])
                print(self.chg[diff_action] + " | RIGHT :", item["right"])
                print("\n")


class DeepDiffXmlDiff(DeepDiffJsonDiff):
    def load_json(self, file_path: str):
        with open(file_path) as file:
            return json.loads(json.dumps(xmltodict.parse(file.read())))

    def show_diff(self, diff_result):
        print("\n##### Using DeepDiff for XML\n")
        super().show_diff(diff_result)


if __name__ == "__main__":
    left_file = "network-payload-left.json"
    right_file = "network-payload-right.json"

    deepdiff_diff = DeepDiffJsonDiff(left_file, right_file)
    dd_result = deepdiff_diff.diff()
    dd_result.show_diff()

    difflib_diff = DifflibJsonDiff(left_file, right_file)
    df_result = difflib_diff.diff()
    df_result.show_diff()

    # jycm_diff = JycmJsonDiff(left_file, right_file)
    # jycm_result = jycm_diff.diff()
    # jycm_result.show_diff()

    # Example for XML diff
    left_xml = "left.xml"
    right_xml = "right.xml"

    # deepdiff_xml_diff = DeepDiffXmlDiff(left_xml, right_xml)
    # xml_result = deepdiff_xml_diff.diff()
    # xml_result.show_diff()
