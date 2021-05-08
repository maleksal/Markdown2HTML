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
        self.p_list = []

    def clear_cache(self):
        """Clear cache.
        """
        self.ord_list.clear()
        self.unrd_list.clear()
        self.p_list.clear()

    def heading(self, symbol):
        """Handle html heading parsing.
        """
        text = self.filecontent[self.position]
        hash_count = text.count(symbol)
        markd = text.split(symbol * hash_count + ' ')
        result = f'<h{hash_count}>'
        result += "".join(markd).strip()
        result += f'</h{hash_count}>\n'
        return result

    def html_lists(self, symbol):
        """Handle html ul ol parsing.
        """
        # settings
        tag_symnol = {"-": "ul", "*": "ol"}
        # initialize
        tag = tag_symnol[symbol]
        cache_list = self.unrd_list if symbol == 'ul' else self.ord_list

        text = self.filecontent[self.position]
        extracted = text.split(f'{symbol} ')
        cache_list.append("<li>" + ''.join(extracted)
                                 + "</li>\n")

        if (self.position + 1 < len(self.filecontent) and
                self.filecontent[self.position + 1].startswith(f'{symbol}')):
            self.position += 1
            self.html_lists(symbol)
        if cache_list:
            return f"<{tag}>\n{''.join(cache_list)}</{tag}>\n"

    def html_paragraph(self):
        """Handle html p tag.
        """
        text = self.filecontent[self.position]
        self.p_list.append(f"\n{text}\n")
        if (self.position + 1 < len(self.filecontent)
                and self.filecontent[self.position + 1] not in " \n\t"
                and self.filecontent[self.position + 1][0].isalpha()):
            self.position += 1
            self.html_paragraph()
        if self.p_list:
            return f"<p>{'<br/>'.join(self.p_list)}</p>\n"

    def parser(self, text, position):
        self.position = position
        pointers = {
            "#": self.heading,
            "-": self.html_lists,
            "*": self.html_lists
        }
        tag = text.split(' ')[0][0]
        if tag in pointers.keys():
            result, pos = pointers[tag](tag), self.position
        elif tag.isalpha():
            result, pos = self.html_paragraph(), self.position
        else:
            return None, self.position
        # clear cache
        self.clear_cache()
        return result, pos


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
