#include "Transacter.h"

#include <hidapi.h>

int Init()
{
	return hid_init();
}

int Exit()
{
	return hid_exit();
}

int List(unsigned short vid, unsigned short pid,
	wchar_t serials[][MAX_DEVICES])
{
	struct hid_device_info* lpHid = hid_enumerate(vid, pid);
	if (lpHid == 0 || serials == 0)
		return 0;

	struct hid_device_info* lpHidNext = lpHid;
	int nDevice = 0;
	do
	{
		if (lpHidNext->serial_number != 0)
		{
			serials[nDevice][0] = 0;
			wcscpy(lpHidNext->serial_number, serials[nDevice]);
		}
		nDevice++;
		lpHidNext = lpHidNext->next;
	} while (lpHidNext != 0);
	hid_free_enumeration(lpHid);
	return nDevice;
}

void* Open(unsigned short vid, unsigned short pid, const wchar_t* lpwszSerial)
{
	return hid_open(vid, pid, lpwszSerial);
}

void Close(void* handle)
{
	hid_close((hid_device*)handle);
}

int Write(void* handle, const unsigned char* abData, unsigned int cnt)
{
	return hid_write((hid_device*)handle, abData, cnt);
}

int Read(void* handle, unsigned char* abData, unsigned int cnt,
	unsigned int nTimeout)
{
	return hid_read_timeout((hid_device*)handle, abData, cnt, nTimeout);
}

int  Transact(void* handle,
	const unsigned char* abSend, unsigned int cntSend,
	unsigned char* abRecv, unsigned int cntRecv,unsigned nTimeout)
{
	if (Write(handle, abSend, cntSend))
	{
		return Read(handle, abRecv, cntRecv, nTimeout);
	}
	else
		return 0;
}