
CC=gcc
OPTIMIZE_FLAGS=-O3
FLAGS=-v
UTIL_FLAGS=

UTIL_SRCS:=$(wildcard src/util/*.c)
UTIL_OBJS=$(patsubst src/util/%.c,obj/util/%.o,$(UTIL_SRCS))

.PHONY : set_util_flags set_util_flags_opt

main: set_util_flags_opt src/main.c $(UTIL_OBJS)
	$(CC) $(FLAGS) $(OPTIMIZE_FLAGS) $(UTIL_OBJS) src/main.c -o bin/main

test: set_util_flags src/test.c $(UTIL_OBJS)
	$(CC) $(FLAGS) $(UTIL_OBJS) src/test.c -o bin/test

set_util_flags_opt: UTIL_FLAGS += $(OPTIMIZE_FLAGS) + $(FLAGS)

set_util_flags: UTIL_FLAGS += $(FLAGS)

obj/util/%.o: src/util/%.c
	$(CC) $(UTIL_FLAGS) -c $< -o $@
