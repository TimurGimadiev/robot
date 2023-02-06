#ifndef _TRANSACTER_H
#define _TRANSACTER_H

#include <wchar.h>
#define MAX_DEVICES 17

int   Init();
int   Exit();
int   List(unsigned short vid, unsigned short pid, wchar_t[][MAX_DEVICES]);
void* Open(unsigned short vid, unsigned short pid, const wchar_t*);
void  Close(void*);
int   Write(void*, const unsigned char*, unsigned int);
int   Read(void*, unsigned char*, unsigned int, unsigned int nTimeout);

int  Transact(void*, // return cntRecv
	const unsigned char*, unsigned,
	unsigned char* abRecv, unsigned, unsigned nTimeout);

#endif // _TRANSACTER_H