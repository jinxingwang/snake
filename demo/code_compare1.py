from snake import Target, Dir, Tool

warns = ['-W', '-Wall', '-pedantic', '-Wno-comment',
        '-Wno-variadic-macros', '-Wno-unused-function']
v7_flags = ['-DCS_ENABLE_UTF8']
cflags = warns + ['-g', '-O3', '-lm'] + v7_flags

cc = Tool('gcc {inp} -o {out}', flags=['-DV7_EXE'] + cflags)

v7 = Target('v7', tool=cc, deps=['v7.c'])
v7.build()
