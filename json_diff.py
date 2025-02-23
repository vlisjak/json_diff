#!/usr/bin/env python

import json
import xmltodict
import difflib
import argparse
from deepdiff import DeepDiff
from typing import Callable
from jycm.jycm import YouchamaJsonDiffer
from jycm.helper import make_ignore_order_func

"""
# Probably most popular library:
./json_diff.py -l network-payload-left.json -r network-payload-right.json -t json -m deepdiff

# Similar to DeepDiff:
./json_diff.py -l network-payload-left.json -r network-payload-right.json -t json -m jycm

# Result is similar to "legacy" diff, including red/green coloring in the terminal
./json_diff.py -l network-payload-left.json -r network-payload-right.json -t json -m difflib

# XML deepdiff:
./json_diff.py -l left.xml -r right.xml -t xml -m deepdiff
./json_diff.py -l left.xml -r right.xml -t xml -m jycm
./json_diff.py -l left.xml -r right.xml -t xml -m difflib
"""


class JsonDiff:
    """Base class for performing diff operations on JSON files."""

    CHG_ACTIONS = {
        "iterable_item_added": "ADD",
        "dictionary_item_added": "ADD",
        "iterable_item_removed": "DEL",
        "dictionary_item_removed": "DEL",
        "values_changed": "CHG",
        "list:add": "ADD",
        "dict:add": "ADD",
        "list:remove": "DEL",
        "dict:remove": "DEL",
        "value_changes": "CHG",
    }

    CHG_ACT_SHORT = {
        "iterable_item_added": "+",
        "dictionary_item_added": "+",
        "iterable_item_removed": "-",
        "dictionary_item_removed": "-",
        "values_changed": "#",
        "list:add": "+",
        "dict:add": "+",
        "list:remove": "-",
        "dict:remove": "-",
        "value_changes": "#",
    }

    def __init__(self, left_file: str, right_file: str, file_type: str):
        self.left_file = left_file
        self.right_file = right_file
        self.file_type = file_type
        self.left = self.load_data(left_file)
        self.right = self.load_data(right_file)

    def load_data(self, file_path: str):
        try:
            with open(file_path, "r") as file:
                if self.file_type == "json":
                    loaded = json.loads(file.read())
                elif self.file_type == "xml":
                    loaded = json.loads(json.dumps(xmltodict.parse(file.read())))
        except FileNotFoundError:
            print(f"Error: The file '{file_path}' was not found.")
            raise
        except (json.JSONDecodeError, xmltodict.expat.ExpatError) as e:
            print(
                f"Error: Failed to decode {self.file_type.upper()} from the file '{file_path}': {e}"
            )
            raise
        except Exception as e:
            print(f"An unexpected error occurred: {type(e).__name__}: {e}")
            raise
        else:
            return loaded

    def diff(self):
        raise NotImplementedError("Subclasses should implement this!")

    def show_diff(self, diff_result):
        raise NotImplementedError("Subclasses should implement this!")


class DeepDiffJsonDiff(JsonDiff):
    """Performs diff operations on JSON files using the DeepDiff library."""

    def diff(self):
        self.diff_result = DeepDiff(
            self.left,
            self.right,
            ignore_order=True,
            report_repetition=True,
            view="tree",
            threshold_to_diff_deeper=0,
        )

    # def show_diff(self):
    #     print("\n##### Using DeepDiff\n")
    #     for diff_action in sorted(self.diff_result):
    #         print(f"{'-' * 25}{diff_action.upper()}{'-' * 25}\n")
    #         for item in self.diff_result[diff_action]:
    #             item_path = "/".join(str(x) for x in item.path(output_format="list"))
    #             print(f"{self.CHG_ACTIONS[diff_action]} | PATH | {item_path}")
    #             print(f"{self.CHG_ACTIONS[diff_action]} |    L | {item.t1}")
    #             print(f"{self.CHG_ACTIONS[diff_action]} |    R | {item.t2}\n")

    def show_diff(self):
        for diff_action in sorted(self.diff_result):
            for item in self.diff_result[diff_action]:
                item_path = "/".join(str(x) for x in item.path(output_format="list"))
                print(f"{self.CHG_ACT_SHORT[diff_action]} | {item_path} | {item.t1} | {item.t2}")


class DifflibJsonDiff(JsonDiff):
    """
    Performs diff operations on JSON files using Python's difflib library.
    Result is similar to 'legacy' diff, color-coded in ANSI terminal.
    """

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

        self.diff_result = get_edits_string(
            json.dumps(self.left, indent=4, sort_keys=True),
            json.dumps(self.right, indent=4, sort_keys=True),
        )

    def show_diff(self):
        print("\n##### Using difflib and coloured diff\n")
        print(self.diff_result)


class JycmJsonDiff(JsonDiff):
    """Performs diff operations on JSON files using the Jycm library."""

    def diff(self):
        ycm = YouchamaJsonDiffer(
            self.left, self.right, ignore_order_func=make_ignore_order_func([".*"])
        )
        self.diff_result = ycm.get_diff()

    def show_diff(self):
        print("\n##### Using Jycm\n")
        for diff_action in sorted(self.diff_result):
            if diff_action == "just4vis:pairs":
                continue
            print(f"{'-' * 25}{diff_action.upper()}{'-' * 25}\n")
            for item in self.diff_result[diff_action]:
                print(
                    f"{self.CHG_ACTIONS[diff_action]} | PATH_L | {item['left_path']}"
                )
                print(
                    f"{self.CHG_ACTIONS[diff_action]} | PATH_R | {item['right_path']}"
                )
                print(f"{self.CHG_ACTIONS[diff_action]} |      L | {item['left']}")
                print(f"{self.CHG_ACTIONS[diff_action]} |      R | {item['right']}\n")


def main():
    parser = argparse.ArgumentParser(
        description="Diff two files using specified method and type."
    )
    parser.add_argument("-l", "--left", required=True, help="Left file name")
    parser.add_argument("-r", "--right", required=True, help="Right file name")
    parser.add_argument(
        "-t",
        "--type",
        choices=["json", "xml"],
        required=True,
        help="Type of the files (json or xml)",
    )
    parser.add_argument(
        "-m",
        "--method",
        choices=["deepdiff", "difflib", "jycm"],
        required=True,
        help="Method for diffing (deepdiff, difflib, jycm)",
    )

    args = parser.parse_args()

    diff_classes = {
        "deepdiff": DeepDiffJsonDiff,
        "difflib": DifflibJsonDiff,
        "jycm": JycmJsonDiff,
    }

    if args.method not in diff_classes:
        print(f"Error: Method '{args.method}' is not supported.")
        return

    diff_class = diff_classes[args.method]
    diff_instance = diff_class(args.left, args.right, args.type)
    diff_instance.diff()
    diff_instance.show_diff()

    # Normally you would pick a single diff method, such as:
    # differ = DeepDiffJsonDiff(args.left, args.right, args.type)
    # differ.diff()
    # differ.show_diff()


if __name__ == "__main__":
    main()
