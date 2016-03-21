WARNS = -W -Wall -pedantic -Wno-comment -Wno-variadic-macros -Wno-unused-function
V7_FLAGS = -DCS_ENABLE_UTF8
CFLAGS = $(WARNS) -g -O3 -lm $(V7_FLAGS) $(CFLAGS_PLATFORM) $(CFLAGS_EXTRA)

.PHONY: examples

all: v7 examples

examples:
	@$(MAKE) -C examples

v7: v7.c v7.h Makefile
	$(CC) v7.c -o $@ -DV7_EXE $(CFLAGS) -lm

clean:
	@$(MAKE) -C examples clean
	rm -fr v7 v7.dSYM

