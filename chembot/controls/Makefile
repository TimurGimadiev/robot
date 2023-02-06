export ARCH:=arm

CC=gcc
CFLAGS=-c -fPIC

all: main

main: libchembot.o hid.o
		$(CC) -shared libchembot.o hid.o -o libchembot.so -ludev

libchembot.o: libchembot.c
		$(CC) $(CFLAGS) -o libchembot.o libchembot.c

hid.o: hid.c
		$(CC) $(CFLAGS) -o hid.o hid.c -ludev

clean:
		rm -rf *.so
		rm -rf *.o

rebuild: clean all
	
