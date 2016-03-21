from snake import Target, Dir, Tool

warns = ['-W', '-Wall', '-pedantic', '-Wno-comment', '-Wno-variadic-macros', '-Wno-unused-function']
v7_flags = ['-DCS_ENABLE_UTF8']
cflags = warns + ['-g', '-O3', '-lm'] + v7_flags

cc = Tool('gcc {inp} -o {out}', flags=['-DV7_EXE'] + cflags)

v7 = Target('v7', tool=cc, deps=['v7.c'])
v7.build()

EXAMPLES_DIR = 'examples/'
FLAGS = '-W -Wall -I../.. -Wno-unused-function'
cc = Tool('gcc {inp} -o {out} {flags} -lm')
cc.flags(FLAGS)

call_c_from_js = Target(EXAMPLES_DIR + 'call_c_from_js/call_c_from_js', tool = cc, deps=['v7.c'])
call_c_from_js.depends_on(EXAMPLES_DIR + 'call_c_from_js/call_c_from_js.c')
call_c_from_js.build()

call_js_from_c = Target(EXAMPLES_DIR + 'call_js_from_c/call_js_from_c', tool = cc, deps=['v7.c'])
call_js_from_c.depends_on(EXAMPLES_DIR + 'call_js_from_c/call_js_from_c.c')
call_js_from_c.build()

js_oop = Target(EXAMPLES_DIR + 'js_oop/js_oop', tool = cc, deps=['v7.c'])
js_oop.depends_on(EXAMPLES_DIR + 'js_oop/js_oop.c')
js_oop.build()

load_json_config = Target(EXAMPLES_DIR + 'load_json_config/load_json_config', tool = cc, deps=['v7.c'])
load_json_config.depends_on(EXAMPLES_DIR + 'load_json_config/load_json_config.c')
load_json_config.build()
