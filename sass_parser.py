import sys
import os
import sublime

sys.path.append(os.path.join(
        os.path.dirname(__file__),
        "lib",
        sublime.platform(),
        sublime.arch())
    )

import sass

def parse_snippet(str, libstr="", settings={}):
    is_wrapped = False
    is_braces = False

    def is_braces_only(str):
        if str.strip()[0] == '{':
            return True

    def unwrapped(str):
        """
        Remove dummy rule wrapper if existing.
        """
        if is_braces:
            return str[6:]
        if is_wrapped:
            return str[8:-2]
        return str

    if is_braces_only(str):
        str = ':root %s' % str
        is_braces = True

    try:
        sass.compile(string=str)
    except sass.CompileError:
        # If the first compilation fails, try wrapping the initial string in
        # a temp selector and re-parsing it.
        str = ':root { %s }' % str
        is_wrapped = True

    full_string = "%s%s" % (libstr, str)
    try:
        result = sass.compile(string=full_string)
        if result == '':
            return '/* %s */' % unwrapped(str)
    except sass.CompileError:
        return '/* %s */' % unwrapped(str)
    return unwrapped(result)