from snake import Dir, Target, Tool

my_tool = Tool("gcc {inp} -o {out}", flags=('-O3', '-std=c11'))
target = Target('example/a')
target.depends_on('example/a.c', 'example/b.c')
target.build(my_tool)
