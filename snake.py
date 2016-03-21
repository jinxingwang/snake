"""Snake Build Library.

    Alex Hernandez
    Jacob Estelle
    Jinxing Wang

"""
import os
import re
import subprocess
import __main__

ABS_DIR_PATH = os.path.realpath(os.path.dirname(__main__.__file__))


def flatten(lst):
    res = []
    for item in lst:
        if isinstance(item, str):
            res.append(item)
        if isinstance(item, list):
            res += item

    return res


def all_exist(dep):
    if isinstance(dep, list):
        return all(os.path.exists(path) for path in dep)
    return os.path.exists(dep)


def any_newer(dep, me):
    if isinstance(dep, list):
        return any(os.path.getmtime(path) > os.path.getmtime(me) for path in dep)
    return os.path.getmtime(dep) > os.path.getmtime(me)


class Dir:
    """A helpful wrapper around a group of files in a common directory."""
    def __init__(self, dir_name, recursive=False, tool=None, deps=()):
        """Constructs a directory target from the specified dirname. Every
        file in the directory is then treated as a dependency. The optional
        recursive specifies whether any directories within this directory
        should also become part of the target; any operations
        (depends_on(), map(), build()) will be applied accordingly.
        """

        # allow for full-paths to be used if they start with '/'
        self.recursive = recursive
        if dir_name[0] == "/":
            self.path = dir_name
        else:
            self.path = os.path.join(ABS_DIR_PATH, dir_name)
        if not os.path.isdir(self.path):
            raise Exception('specified directory does not exist')

        self.maps = []
        self.dependencies = []
        self._tool = None

        # handle optional short-cut args
        self.tool(tool)
        self.depends_on(*deps)

    def map(self, inp, out):
        """Sets the output of this directory by creating a set of in->out
        relationships. in is a string with at most one wildcard, and specifies
        all files to which this rule will apply. out is a string that specifies
        the output of all the input files matched by in. out must have the same
        number of wildcards as in (0 or 1). Only dependencies of this directory
        which are matched by a call to map() will be built on build()
        :param inp: binding input
        :param out: binding output
        """
        if "*" in out and "*" not in inp:
            raise Exception("In must have * if out has *")
        self.maps.append({"in": inp.replace("*", "(.+)"), "out": out})

    def depends_on(self, *deps):
        """Specifies the dependencies of this directory, i.e. its input in the
        dependency tree.
        """
        for dep in deps:
            if isinstance(dep, Target) or isinstance(dep, Dir):
                self.dependencies.append(dep)
            elif isinstance(dep, str):
                if dep[0] == "/":
                    self.dependencies.append(dep)
                else:
                    self.dependencies.append(os.path.join(ABS_DIR_PATH, dep))
            else:
                raise Exception('dependency must be one of: Target, Dir, or string')

    def tool(self, tool):
        """Specify the build tool for this Dir.
        :param tool: program with which to build files in this directory
        """
        self._tool = tool

    def has_tool(self):
        """Returns whether a build tool has been previously defined for this
        Dir.
        """
        return self._tool is not None

    def build(self, tool=None):
        """Build this directory with the specified tool. If no tool is specified
        here, a tool must have been previously specified by a call to tool().
        Only dependencies which are bound to an output will be built.
        :param tool: program with which to build the files in this directory
        """
        if tool:
            self._tool = tool
        # contents = scan dir
        contents = self._get_files()
        # contents[i] = Target if contents[i] matches a mapping
        for mapping in self.maps:
            for i in range(len(contents)):
                matches = re.search(mapping["in"], contents[i])
                if matches:
                    contents[i] = Target(mapping['out'].replace("*", matches.group(1)), deps=[contents[i]])

        for i in range(len(contents)):
            # everything that is not a Target becomes a Leaf
            if not isinstance(contents[i], Target):
                contents[i] = Leaf(contents[i])
            # everything that is a Target gets dependencies
            else:
                for dep in self.dependencies:
                    contents[i].depends_on(dep)

        return [res.build() if res.has_tool() else res.build(self._tool) for res in contents]

    def _get_files(self):
        """Returns list of files in this Dir."""
        contents = []
        if self.recursive:
            for dirname, _, files in os.walk(self.path):
                for filename in files:
                    if filename[0] != '.':
                        contents.append(os.path.join(dirname, filename))
        else:
            dirname, _, files = next(os.walk(self.path))
            for filename in files:
                if filename[0] != ".":
                    contents.append(os.path.join(dirname, filename))
        return contents

    @property
    def _out(self):
        # contents = scan dir
        contents = self._get_files()
        # contents[i] = Target if contents[i] matches a mapping
        for mapping in self.maps:
            for i in range(len(contents)):
                matches = re.search(mapping["in"], contents[i])
                if matches:
                    contents[i] = Target(mapping['out'].replace("*", matches.group(1)), deps=[contents[i]])

        for i in range(len(contents)):
            # everything that is not a Target becomes a Leaf
            if not isinstance(contents[i], Target):
                contents[i] = Leaf(contents[i])

        return [res._out for res in contents]


class Leaf:
    """Wrapper class for files"""
    # pylint: disable=missing-docstring,no-self-use

    def __init__(self, filename):
        self._out = filename

    def has_tool(self):
        return True

    def build(self):
        return self._out


class Target:
    """Root of dependency tree."""

    def __init__(self, out=None, deps=(), tool=None):
        """Constructs a new target object, with an output optionally specified.
        """
        if out is None or out[0] == "/":
            self._out = out
        else:
            self._out = os.path.join(ABS_DIR_PATH, out)
        self.dependencies = []
        self._tool = None

        # Handle short-cut optional args
        self.depends_on(*deps)
        self.tool(tool)

    def out(self, out):
        """Sets this target's output. This will be the final artifact after
        build() is invoked on this target.
        :param out: specifies the filename of the output
        """
        if out[0] == "/":
            self._out = out
        else:
            self._out = os.path.join(ABS_DIR_PATH, out)

    def depends_on(self, *deps):
        """Specify the dependencies of this target."""
        for dep in deps:
            if isinstance(dep, Target) or isinstance(dep, Dir):
                self.dependencies.append(dep)
            elif isinstance(dep, str):
                if dep[0] == "/":
                    self.dependencies.append(Leaf(dep))
                else:
                    self.dependencies.append(Leaf(os.path.join(ABS_DIR_PATH, dep)))
            else:
                raise Exception('dependency must be one of: Target, Dir, or string')

    def tool(self, tool):
        """Specify the build tool for this target.
        :param tool: program with which to build this Target
        """
        self._tool = tool

    def has_tool(self):
        """Returns whether a build tool has been previously defined for this
        target.
        """
        return self._tool is not None

    def build(self, tool=None):
        """Build this target with the specified tool. If no tool is specified
        here, a tool must have been specified previously by a call to tool().
        This target's output must have been previously set either in the
        constructor or in map().
        :param tool: program with which to build this Target
        """
        if self._out is None:
            raise Exception('out was never specified')
        if tool is not None:
            self._tool = tool
        if self._tool is None:
            raise Exception('no tool specified for target')

        run_command = False
        if not os.path.exists(self._out):
            run_command = True
        if not run_command and not all(all_exist(dep._out) for dep in self.dependencies):
            run_command = True

        ins = [dep.build() if dep.has_tool() else dep.build(self._tool)
               for dep in self.dependencies]

        if not run_command and any(any_newer(dep, self._out) for dep in ins):
            run_command = True
        ins = flatten(ins)
        command = self._tool.command()
        in_string = " ".join(ins)
        command = command.format(inp=in_string, out=self._out)
        if run_command:
            subprocess.check_call(command.split(" "))

        return self._out


class Tool:
    """Represents a command-line tool command and its flags. Example, gcc."""
    def __init__(self, command, flags=None):
        """The specified 'command' will be the actual program executed. The
        string must contain 2 mandatory placeholders {inp} and {out} and may
        contain a third optional placeholder {flags}. At build-time, these
        will be replaced with the Target's or Dir's input and output, as well as
        with this tool's flags. If the {flags} placeholder is omitted, any
        flags will be appended to the end.
        """
        if "{inp}" not in command or "{out}" not in command:
            raise Exception('command specified to Tool must have {inp} and {out}')

        self._command = command.strip()

        if flags is None:
            self._flags = []
        else:
            self._flags = flags

    def flags(self, *fl):
        """Options specified when running this tool. One flag per argument."""
        self._flags.extend(fl)

    def command(self):
        """Return the current command string."""
        if "{flags}" not in self._command:
            self._command += " {flags}"
        return self._command.format(flags=" ".join(self._flags), inp='{inp}', out='{out}').strip()
