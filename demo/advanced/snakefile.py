
from snake import Target, Dir, Tool
import sys

# Main GCC
gcc = Tool("gcc {inp} -o {out}")
# Object gcc
obj_gcc = Tool("gcc -c {inp} -o {out}")

# Util directory
util = Dir('src/util', tool=obj_gcc)
util.map('src/util/*.c', 'obj/util/*.o')

# Main exectuable
main_out = 'bin/main'
main_prog = Target(main_out, deps=['src/main.c', util])

# Test executable
test_out = 'bin/test'
test_prog = Target(test_out, deps=['src/test.c', util])

# Command line options
if len(sys.argv) == 1 or sys.argv[1] == 'main':
    gcc.flags("-v -O3")
    obj_gcc.flags("-v -O3")
    main_prog.build(gcc)
elif sys.argv[1] == 'test':
    gcc.flags("-v")
    obj_gcc.flags("-v")
    test_prog.build(gcc)
else:
    print("No such target '{}'".format(sys.argv[1]))
