#!/usr/bin/python3
"""
Parser Module.
"""

import sys
import os
from functools import wraps


class MarkDown:
    """
    MarkDown class
    """
    def __init__(self):
        self.unrd_list = []
        self.ord_list = []

    def heading(self, text):
        markd = text.split(' ')
        return f'<h{len(markd[0])}>\
            {"".join(markd[1:]).strip()}\
            </h{len(markd[0])}>\n'

    def unordered_list(self, text):
        extracted = text.split(' ')
        self.unrd_list.append(f"<li>{''.join(extracted[1:]).strip()}</li>\n")
        if len(self.unrd_list) > 1:
            return f"<ul>\n{''.join(self.unrd_list)}</ul>\n"
        return ""

    def ordered_list(self, text):
        extracted = text.split(' ')
        self.ord_list.append(f"<li>{''.join(extracted[1:]).strip()}</li>\n")
        if len(self.ord_list) > 1:
            return f"<ol>\n{''.join(self.ord_list)}</ol>\n"
        return ""

    def parser(self, text):
        pointers = {
            "#": self.heading,
            "-": self.unordered_list,
            "*": self.ordered_list,
            "": "",
        }
        splited = text.split(' ')[0]
        if splited[0] in pointers.keys():
            return pointers[splited[0]](text)


def catch_error(f):
    """handle errors
    """
    @wraps(f)
    def catch(*args, **kwargs):
        try:
            f(*args, **kwargs)
        except (AssertionError, BaseException) as err:
            sys.stderr.write(str(err) + '\n')
            sys.exit(1)
    return catch


@catch_error
def main():
    """entry point
    """
    assert len(sys.argv) >= 3,\
        "Usage: ./markdown2html.py README.md README.html"
    # src && dest files
    src, dest = sys.argv[1], sys.argv[2]
    assert os.path.exists(src), f"Missing {src}"

    # markdown parser
    markdown = MarkDown()

    with open(src, 'r') as rf:
        with open(dest, 'w') as wf:
            for l in rf.readlines():
                wf.write(markdown.parser(l))


if __name__ == "__main__":
    main()
