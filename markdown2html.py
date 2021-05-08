#!/usr/bin/python3
"""
Parser Module.
"""

import sys
import os
import hashlib
import re
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

    @staticmethod
    def tomd5_hash(string):
        md5 = hashlib.md5()
        md5.update(string.encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def translate_str(string):
        return string.translate(string.maketrans('cC', 'cc')).replace('c', '')

    def html_format_font(self):
        text = self.filecontent[self.position]
        templates = {
            "**": "<b>@</b>",
            "__": "<em>@</em>",
            "[[": self.tomd5_hash,
            "((": self.translate_str}
        to_replace = []
        for k in templates.keys():
            if k in text:
                k = '\\*\\*' if k == '**' else k

                k = '\\[\\[' if k == '[[' else k
                kk = '\\]\\]' if k == '\\[\\[' else k

                k = '\\(\\(' if k == '((' else k
                kk = '\\)\\)' if k == '\\(\\(' else kk

                result = re.search('%s(.*)%s' % (k, kk), text)
                if result:
                    to_replace.append(
                        (result.group(1), k.replace('\\', '')))
        for tr in to_replace:
            if tr[1] == '[[':
                text = text.replace(
                    f"{tr[1]}{tr[0]}]]", templates[tr[1]](tr[0]))
            elif tr[1] == '((':
                text = text.replace(
                    f"{tr[1]}{tr[0]}))", templates[tr[1]](tr[0]))
            else:
                text = text.replace(
                    f"{tr[1]}{tr[0]}{tr[1]}",  # ex **hel**
                    templates[tr[1]].replace('@', tr[0]))
        return text

    def heading(self, symbol):
        """Handle html heading parsing.
        """
        text = self.html_format_font()
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

        text = self.html_format_font()
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
        text = self.html_format_font()
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
            "# ": self.heading,
            "- ": self.html_lists,
            "* ": self.html_lists
        }
        tag = text.split(' ')[0]
        if tag + ' ' in pointers.keys() or tag.startswith('#'):
            result, pos = pointers[tag[0] + ' '](tag[0]), self.position
        else:
            result, pos = self.html_paragraph(), self.position
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
