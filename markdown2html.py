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
    def __init__(self, content):
        self.filecontent = content
        self.ord_list = []
        self.unrd_list = []

    def heading(self):
        text = self.filecontent[self.position]
        hdings = text.count("#")
        markd = text.split('#' * hdings + ' ')
        result = f'<h{hdings}>'
        result += "".join(markd).strip()
        result += f'</h{hdings}>\n'
        return result

    def unordered_list(self):
        text = self.filecontent[self.position]
        extracted = text.split('- ')
        self.unrd_list.append("<li>" + ''.join(extracted)
                                     + "</li>\n")

        if self.filecontent[self.position + 1].startswith('-'):
            self.position += 1
            self.unordered_list()
        if self.unrd_list:
            return f"<ul>\n{''.join(self.unrd_list)}</ul>\n"

    def ordered_list(self):
        text = self.filecontent[self.position]
        extracted = text.split('* ')
        self.ord_list.append("<li>" + ''.join(extracted) + "</li>\n")

        if self.filecontent[self.position + 1].startswith('*'):
            self.position += 1
            self.ordered_list()
        if self.ord_list:
            return f"<ol>\n{''.join(self.ord_list)}</ol>\n"

    def parser(self, text, position):
        self.position = position
        pointers = {
            "#": self.heading,
            "-": self.unordered_list,
            "*": self.ordered_list,
            "": "",
        }
        splited = text.split(' ')[0]
        if splited[0] in pointers.keys():
            return pointers[splited[0]](), self.position
        return None, self.position


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

    with open(src, 'r') as rf:
        content = [i.strip('\n') for i in rf.readlines()]

    markdown = MarkDown(content)
    with open(dest, 'w') as wf:
        position = 0
        while position < len(content):
            line = content[position]
            if line not in " \n\t":
                result, position = markdown.parser(line, position)
                wf.write(result) if result else ""
            position += 1


if __name__ == "__main__":
    main()
