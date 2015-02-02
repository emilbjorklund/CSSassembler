import os

import sublime, sublime_plugin
from .sass_parser import parse_snippet

# monkeypatch `Region` to be iterable
sublime.Region.totuple = lambda self: (self.a, self.b)
sublime.Region.__iter__ = lambda self: self.totuple().__iter__()

class CssAssemblerCommand(sublime_plugin.TextCommand):

    def run(self, edit):
        view = self.view

        lib_str = self.get_libraries(view)
        print(lib_str)

        if 'source.css' not in view.scope_name(view.sel()[0].b):
            return

        if not self.has_selection():
            line = view.full_line(view.sel()[0].b)
            print('line is ', view.substr(line))
            if view.substr(line) == "":
                return
            assembled = self.assemble(line, library_str=lib_str)
            view.replace(edit, line, assembled)
        for region in view.sel():
            if region.empty():
                continue
            originalBuffer = view.substr(region)
            assembled = self.assemble(originalBuffer, library_str=lib_str)
            if assembled:
                view.replace(edit, region, assembled)

    def get_libraries(self, view):
        """
        Try to find the closest `.cssassembler` dir,
        and concatenate all the files in it into one string.
        """
        current_file = view.file_name()
        if current_file is None:
            return ''

        current_dir = os.path.dirname(current_file)
        recursion = 0

        library_files = []
        result_string = ""

        def get_library_dir(thisdir, recursion=0, max_recursion_depth=10):
            result = None
            path_guess = os.path.join(thisdir, '.cssassembler')
            if os.path.isdir(path_guess):
                result = path_guess
            else:
                recursion += 1
                if recursion < max_recursion_depth:
                    get_library_dir(os.path.join(thisdir, os.path.pardir), recursion)
                else:
                    result = None
            return result

        library_dir = get_library_dir(current_dir)
        print('Closest library dir is', library_dir)

        if library_dir:
            for dirName, subdirList, fileList in os.walk(library_dir):
                print('Found directory: %s' % dirName)
                for fname in fileList:
                    if fname[-5:] in ['.scss']:
                        library_files.append(os.path.join(dirName, fname))
        for fname in library_files:
            with open(fname) as infile:
                result_string += infile.read()
        return result_string



    def assemble(self, str, library_str=""):
        return parse_snippet(str, libstr=library_str).strip()

    def has_selection(self):
        for sel in self.view.sel():
            if not sel.empty():
                return True
        return False
