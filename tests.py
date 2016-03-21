import unittest
from snake import Target, Tool, Dir
import os
import time

TEST_FILES_DIR = 'test_files/'


def make_dirs():
    if not os.path.exists(TEST_FILES_DIR + 'bin'):
        os.makedirs(TEST_FILES_DIR + 'bin')
    if not os.path.exists(TEST_FILES_DIR + 'bin/use_cases'):
        os.makedirs(TEST_FILES_DIR + 'bin/use_cases')
    if not os.path.exists(TEST_FILES_DIR + 'obj'):
        os.makedirs(TEST_FILES_DIR + 'obj')
    for root, _, _ in os.walk(TEST_FILES_DIR + 'src'):
        if '/src/' in root:
            obj_dir = root.replace('/src/', '/obj/')
            if not os.path.exists(obj_dir):
                os.makedirs(obj_dir)


def clean():
    bin_ = TEST_FILES_DIR + 'bin/'
    out_ = TEST_FILES_DIR + 'obj/'
    for root, _, files in os.walk(bin_):
        for filename in files:
            if filename[0] != '.':
                os.remove(os.path.join(root, filename))

    for root, _, files in os.walk(out_):
        for filename in files:
            if filename[0] != '.':
                os.remove(os.path.join(root, filename))


class TestBasic(unittest.TestCase):
    def setUp(self):
        clean()

    def tearDown(self):
        clean()

    def test_single_c_file(self):
        out_file = TEST_FILES_DIR + 'bin/basic'
        target = Target(out_file)
        target.depends_on(TEST_FILES_DIR + 'src/basic.c')
        my_tool = Tool("gcc -c {inp} -o {out}")
        target.tool(my_tool)
        target.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_two_c_files(self):
        out_file = TEST_FILES_DIR + 'bin/basic'
        target = Target(out_file)
        target.depends_on(TEST_FILES_DIR + 'src/basic.c', TEST_FILES_DIR + 'src/basic2.c')
        my_tool = Tool("gcc {inp} -o {out}")
        target.tool(my_tool)
        target.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_basic_flags(self):
        out_file = TEST_FILES_DIR + 'bin/basic'
        target = Target(out_file)
        target.depends_on(TEST_FILES_DIR + 'src/basic.c')
        my_tool = Tool("gcc -c {inp} {flags} {out}")
        my_tool.flags("-o")
        target.tool(my_tool)
        target.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_flags_no_placeholder(self):
        out_file = TEST_FILES_DIR + 'bin/basic'
        target = Target(out_file)
        target.depends_on(TEST_FILES_DIR + 'src/basic.c')
        my_tool = Tool("gcc -c {inp} -o {out}")
        my_tool.flags("-Wall")
        target.tool(my_tool)
        target.build()
        self.assertTrue(os.path.isfile(out_file))


class TestDirs(unittest.TestCase):
    def setUp(self):
        clean()

    def tearDown(self):
        clean()

    def test_single_dir(self):
        out_file = TEST_FILES_DIR + 'obj/dir1/a.o'
        path = TEST_FILES_DIR + 'src/dir1/'
        dir1 = Dir(path)
        dir1.map(TEST_FILES_DIR + 'src/dir1/*.c', TEST_FILES_DIR + 'obj/dir1/*.o')
        my_tool = Tool("gcc -c {inp} -o {out}")
        dir1.tool(my_tool)
        dir1.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_single_dir_deps_single_file(self):
        out_file = TEST_FILES_DIR + 'obj/dir2/a.o'
        path = TEST_FILES_DIR + 'src/dir2/'
        dir1 = Dir(path)
        dir1.map(TEST_FILES_DIR + 'src/dir2/*.c', TEST_FILES_DIR + 'obj/dir2/*.o')
        dir1.depends_on(TEST_FILES_DIR + 'src/basic2.c')
        my_tool = Tool("gcc {inp} -o {out}")
        dir1.tool(my_tool)
        dir1.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_single_dir_deps_single_dir(self):
        out_file = TEST_FILES_DIR + 'obj/dir3/f1/a.o'
        path1 = TEST_FILES_DIR + 'src/dir3/f1'
        dir1 = Dir(path1)
        dir1.map(TEST_FILES_DIR + 'src/dir3/f1/*.c', TEST_FILES_DIR + 'obj/dir3/f1/*.o')

        path2 = TEST_FILES_DIR + 'src/dir3/f2'
        dir2 = Dir(path2)

        dir1.depends_on(dir2)

        my_tool = Tool("gcc {inp} -o {out}")
        dir1.tool(my_tool)
        dir1.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_single_dir_deps_single_dir_and_file(self):
        out_file = TEST_FILES_DIR + 'obj/dir3/f1/a.o'
        path1 = TEST_FILES_DIR + 'src/dir3/f1'
        dir1 = Dir(path1)
        dir1.map(TEST_FILES_DIR + 'src/dir3/f1/*.c', TEST_FILES_DIR + 'obj/dir3/f1/*.o')

        path2 = TEST_FILES_DIR + 'src/dir3/f2'
        dir2 = Dir(path2)

        dir1.depends_on(dir2)
        dir1.depends_on(TEST_FILES_DIR + 'src/basic2.c')

        my_tool = Tool("gcc {inp} -o {out}")
        dir1.tool(my_tool)
        dir1.build()
        self.assertTrue(os.path.isfile(out_file))

    def test_single_file_deps_single_dir_and_file(self):
        out_file = TEST_FILES_DIR + 'bin/basic'
        target = Target(out_file)
        target.depends_on(TEST_FILES_DIR + 'src/basic.c')

        path2 = TEST_FILES_DIR + 'src/dir3/f2'
        dir2 = Dir(path2)

        target.depends_on(dir2)
        target.depends_on(TEST_FILES_DIR + 'src/basic2.c')

        my_tool = Tool("gcc {inp} -o {out}")
        target.tool(my_tool)
        target.build()
        self.assertTrue(os.path.isfile(out_file))


class TestUseCases(unittest.TestCase):
    def setUp(self):
        clean()

    def tearDown(self):
        clean()

    def test_advanced(self):
        gcc = Tool("gcc {inp} -o {out}")
        gcc.flags("-v")
        op_gcc = Tool("gcc {inp} -o {out}")
        op_gcc.flags("-O3", "-v")
        util_gcc = Tool("gcc -c {inp} -o {out}")

        util = Dir(TEST_FILES_DIR + 'src/use_cases/util', tool=util_gcc)
        util.map(TEST_FILES_DIR + 'src/use_cases/util/*.c', TEST_FILES_DIR + 'obj/use_cases/util/*.o')

        main_out = TEST_FILES_DIR + 'bin/use_cases/main'
        main_prog = Target(main_out, deps=[TEST_FILES_DIR + 'src/use_cases/main.c', util])

        test_out = TEST_FILES_DIR + 'bin/use_cases/test'
        test_prog = Target(test_out, deps=[TEST_FILES_DIR + 'src/use_cases/test.c', util])

        main_prog.build(op_gcc)
        test_prog.build(gcc)

        self.assertTrue(os.path.isfile(main_out))
        self.assertTrue(os.path.isfile(test_out))


class TestMemoization(unittest.TestCase):
    def setUp(self):
        clean()

    def tearDown(self):
        clean()

    def test_do_not_rebuild(self):
        out_file = TEST_FILES_DIR + 'bin/basic'
        target = Target(out_file, deps=[TEST_FILES_DIR + 'src/basic.c'])

        my_tool = Tool("gcc -c {inp} -o {out}")
        target.tool(my_tool)
        target.build()
        self.assertTrue(os.path.isfile(out_file))
        time = os.path.getmtime(out_file)
        target.build()
        self.assertEqual(time, os.path.getmtime(out_file), "file was rebuilt")

    def test_rebuild(self):
        gcc = Tool("gcc {inp} -o {out}")
        gcc.flags("-v")
        op_gcc = Tool("gcc {inp} -o {out}")
        op_gcc.flags("-O3", "-v")
        util_gcc = Tool("gcc -c {inp} -o {out}")

        util_out = TEST_FILES_DIR + 'obj/use_cases/util/utility.o'
        util_dir = TEST_FILES_DIR + 'src/use_cases/util'
        util = Dir(util_dir, tool=util_gcc)
        util.map(TEST_FILES_DIR + 'src/use_cases/util/*.c', TEST_FILES_DIR + 'obj/use_cases/util/*.o')

        main_out = TEST_FILES_DIR + 'bin/use_cases/main'
        main_prog = Target(main_out, deps=[TEST_FILES_DIR + 'src/use_cases/main.c', util])

        test_out = TEST_FILES_DIR + 'bin/use_cases/test'
        test_prog = Target(test_out, deps=[TEST_FILES_DIR + 'src/use_cases/test.c', util])

        main_prog.build(op_gcc)
        test_prog.build(gcc)

        self.assertTrue(os.path.isfile(main_out))
        self.assertTrue(os.path.isfile(test_out))
        original_time_util_in = os.path.getmtime(TEST_FILES_DIR + 'src/use_cases/util/utility.c')
        original_time_util = os.path.getmtime(util_out)
        original_time_main = os.path.getmtime(main_out)

        time.sleep(2)

        f = open(TEST_FILES_DIR + 'src/use_cases/util/utility.c', 'r')
        lines = f.readlines()
        f.close()
        f = open(TEST_FILES_DIR + 'src/use_cases/util/utility.c', 'w')
        for line in lines:
            f.write(line)

        f.close()

        main_prog.build()

        updated_time_util_in = os.path.getmtime(TEST_FILES_DIR + 'src/use_cases/util/utility.c')
        updated_time_util = os.path.getmtime(util_out)
        updated_time_main = os.path.getmtime(main_out)

        self.assertNotEqual(original_time_util_in, updated_time_util_in, "utility.c wasn't rebuilt")
        self.assertNotEqual(original_time_util, updated_time_util, "utility.o file wasn't rebuilt")
        self.assertNotEqual(original_time_main, updated_time_main, "main executable wasn't rebuilt")


if __name__ == '__main__':
    make_dirs()
    unittest.main()
