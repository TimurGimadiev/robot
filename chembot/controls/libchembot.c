#include "libchembot.h"

#include <memory.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#include "Transacter.h"

#define PACKET_SIZE 64

#define ERROR_COMMAND_SPECIFIC 0xA0
#define ERROR_INVALID_HEADER 0xC0
#define ERROR_INVALID_PACKET_SEQUENCE 0xC1
#define ERROR_WRONG_CRYPT_SIZE 0xD1
#define ERROR_CRYPT_CRC 0xD0
#define ERROR_UNKNOWN_COMMAND 0x05
#define ERROR_WRONG_ADDRESS 0x0A
#define ERROR_CLUSTER_CHANGED 0x0B

#define GET_DEVICE_INFO 0x01
#define SET_STEPPER_POS 0x02
#define INC_STEPPER_POS 0x03
#define GET_STEPPER_STATE 0x04
#define SET_OUTPUT_STATE 0x05
#define GET_INPUT_STATE 0x06
#define GET_OUTPUT_STATE 0x07
#define INIT_STEPPER 0x08
#define EMERGENCY_STOP 0xF0
#define INIT_MOTOR 0x09
#define DRIVE_MOTOR 0x0A
#define GET_MOTOR_STATE 0x0B
#define PHOTOINTERRUPTER_RESET 0x0C
#define PHOTOINTERRUPTER_GET_STATE 0x0D
#define PHOTOINTERRUPTER_GET_COUNT 0x0E
#define GET_ANALOG_INPUTS 0x0F
#define READ_BARCODE 0x10
#define LED_CONTROL 0x11
#define BUZZER_CONTROL 0x12
#define BUZZER_SET_PATTERN 0x13

#include "Transacter.h"
#include "hidapi.h"

void* g_hDevice = 0;
unsigned short g_nVid = 0x1209;
unsigned short g_nPid = 0xB151;
unsigned char* g_lpbAddress = 0;  // � ������ �� �����

unsigned int g_cntWrite = 0;
unsigned char g_abWrite[0xffff];

unsigned int g_cntRead = 0;
unsigned char g_abRead[0xffff];
unsigned int g_nReadTimeout = 2000;

enum Result {
    Success = 0,

    ClusterChanged = 0x0B,

    DeviceError = 0xFD,
    TransactError = 0xFE,
    Disconnect = 0xFF,
};

int Init() {
    return hid_init();
}

int Exit() {
    return hid_exit();
}

int List(unsigned short vid, unsigned short pid,
         wchar_t serials[][MAX_DEVICES]) {
    struct hid_device_info* lpHid = hid_enumerate(vid, pid);
    if (lpHid == 0 || serials == 0)
        return 0;

    struct hid_device_info* lpHidNext = lpHid;
    int nDevice = 0;
    do {
        if (lpHidNext->serial_number != 0) {
            serials[nDevice][0] = 0;
            wcscpy(lpHidNext->serial_number, serials[nDevice]);
        }
        nDevice++;
        lpHidNext = lpHidNext->next;
    } while (lpHidNext != 0);
    hid_free_enumeration(lpHid);
    return nDevice;
}

void* Open(unsigned short vid, unsigned short pid, const wchar_t* lpwszSerial) {
    return hid_open(vid, pid, lpwszSerial);
}

void Close(void* handle) {
    hid_close((hid_device*)handle);
}

int Write(void* handle, const unsigned char* abData, unsigned int cnt) {
    return hid_write((hid_device*)handle, abData, cnt);
}

int Read(void* handle, unsigned char* abData, unsigned int cnt,
         unsigned int nTimeout) {
    return hid_read_timeout((hid_device*)handle, abData, cnt, nTimeout);
}

int Transact(void* handle,
             const unsigned char* abSend, unsigned int cntSend,
             unsigned char* abRecv, unsigned int cntRecv, unsigned nTimeout) {
    if (Write(handle, abSend, cntSend)) {
        return Read(handle, abRecv, cntRecv, nTimeout);
    } else
        return 0;
}

bool _Connect() {
    const int cl0 = clock();
    // if (!g_aszSerial[0])
    //	return false;
    // Init();
    if (g_hDevice == 0) {
        g_hDevice = Open(0x1209, 0xB151, 0);
        if (g_hDevice == 0) {
            printf("cannot open the device\n");
            return false;
        }
    }

    const int cl1 = clock() - cl0;
    return true;
};

void _Close() {
    if (g_hDevice) {
        Close(g_hDevice);
        g_hDevice = 0;
    }
}

int _Transact() {
    const auto cl0 = clock();
    if (!_Connect()) {
        return (int)Disconnect;
    }

    const auto clStart = clock();

    const auto iPacketHeaderSize = 7;

    const auto PACKET_DATA_SIZE = PACKET_SIZE - iPacketHeaderSize;

    for (int iWrited = 0; iWrited < (int)g_cntWrite;
         iWrited += PACKET_DATA_SIZE) {
        const int
            cntNow =
                (int)g_cntWrite - iWrited < PACKET_DATA_SIZE ? (int)g_cntWrite - iWrited : PACKET_DATA_SIZE;

        unsigned char abWriteRaw[1 + PACKET_SIZE];
        memset(abWriteRaw, 0, sizeof(abWriteRaw));
        memcpy((abWriteRaw + iPacketHeaderSize), (g_abWrite + iWrited), cntNow);

        auto nw = 1;  // ������ ��� 1 + PACKET_SIZE. ���������
        abWriteRaw[nw++] = (unsigned char)iWrited;
        abWriteRaw[nw++] = (unsigned char)(iWrited >> 8);

        abWriteRaw[nw++] = 1 + (unsigned char)g_cntWrite;
        abWriteRaw[nw++] = (unsigned char)(g_cntWrite >> 8);

        abWriteRaw[nw++] = 1 + cntNow;

        // ����� :
        // 0 ���(0x01) - ����� �� ����������.
        // 1 ���(0x02) - ����� �������� ������� �� ����������.
        // 7 ���(0x80) - ����� �������� ������� ������.
        abWriteRaw[nw++] = 1;

        // ����� ���������� �� ����.
        // 0 - ���������� ����������� �� USB.
        // 0xff �����������������.
        // �������������� ������ ����������� ����������� �������� ENUMERATE.
        // if (lpAddr != nullptr)
        // abWriteRaw[nw++] = lpAddr->nAddress;

        const auto cl2 = clock() - clStart;

        if (Write(g_hDevice, abWriteRaw, PACKET_SIZE + 1) == -1) {
            // const auto lpwzError = hid_error(_hDevice);
            _Close();
            return (int)Disconnect;
        }

        const auto cl3 = clock();
    }  // for (..write..)

    const auto clAfterWrite = clock() - clStart;

    unsigned char abReadRaw[PACKET_SIZE];
    memset(abReadRaw, 0, sizeof(abReadRaw));
    memset(g_abRead, 0, sizeof(g_abRead));
    g_cntRead = 0;

    //--------ReadFirstPacket--------
    if (Read(g_hDevice, abReadRaw, PACKET_SIZE, g_nReadTimeout) == -1) {
        // const auto lpwzError = hid_error(_hDevice);
        _Close();
        return (int)TransactError;
    }
    //--------ReadFirstPacket--------

    const auto clAfterPacket0 = clock() - clAfterWrite;

    if (abReadRaw[5] & 0x80) {
        switch (abReadRaw[8]) {
            case ERROR_COMMAND_SPECIFIC:
            case ERROR_INVALID_HEADER:
            case ERROR_INVALID_PACKET_SEQUENCE:
            case ERROR_WRONG_CRYPT_SIZE:
            case ERROR_CRYPT_CRC:
            case ERROR_UNKNOWN_COMMAND:
            case ERROR_WRONG_ADDRESS:
            default: {
                _Close();
                return abReadRaw[iPacketHeaderSize + 2];
            }
        }
    }

    if (abReadRaw[iPacketHeaderSize - 1] != g_abWrite[0]) {
        _Close();
        return (int)DeviceError;
    }

    g_cntRead = (unsigned short)abReadRaw[2] | (abReadRaw[3] << 8);
    const auto cntPayload = abReadRaw[4];

    memcpy(g_abRead + 1, abReadRaw + iPacketHeaderSize, cntPayload);

    for (int iReaded = abReadRaw[4]; iReaded < (int)g_cntRead;
         iReaded += PACKET_DATA_SIZE) {
        if (Read(g_hDevice, abReadRaw, PACKET_SIZE, g_nReadTimeout) == -1) {
            return (int)TransactError;
        }
        const auto cntPayload = abReadRaw[4];
        memcpy(g_abRead + 1 + iReaded,
               abReadRaw + iPacketHeaderSize, cntPayload);
    }

    const auto clAfterPackets = clock() - clAfterPacket0;

    _Close();
    const auto clEnd = clock();
    return (int)Success;
}

enum LifeBotResult LB_Sett(const struct LifeBotSett* lps) {
    if (lps)
        g_nReadTimeout = lps->nReadTimeout;
    return LBR_Success;
}

enum LifeBotResult LB_GetDeviceInfo(struct LifeBotDeviceInfo* lpdi) {
    memset(lpdi, 0, sizeof(struct LifeBotDeviceInfo));

    memset(g_abWrite, 0, sizeof(g_abWrite));
    g_abWrite[0] = GET_DEVICE_INFO;
    g_cntWrite = 1;
    const auto r = _Transact();
    // int r = 0;
    if (r == LBR_Success) {
        lpdi->nProtocolVersion = (g_abRead[1]) | (g_abRead[2] << 8);
        lpdi->nHardwareVersion = (g_abRead[3]) | (g_abRead[4] << 8);
        lpdi->nFirmwareVersion = (g_abRead[5]) | (g_abRead[6] << 8);

        // lpdi->nSerial = // ��� ��� ����� ��� ������
        //	(unsigned long long)g_abRead[9] << 56 |
        //	(unsigned long long)g_abRead[10] << 48 |
        //	(unsigned long long)g_abRead[11] << 40 |
        //	(unsigned long long)g_abRead[12] << 32 |
        //	(unsigned long long)g_abRead[13] << 24 |
        //	(unsigned long long)g_abRead[14] << 16 |
        //	(unsigned long long)g_abRead[15] << 8 |
        //	(unsigned long long)g_abRead[16];

        lpdi->nRevision =
            (g_abRead[7]) |
            (g_abRead[8] << 8) |
            (g_abRead[9] << 16) |
            (g_abRead[10] << 24);
    }
    return r;
}

enum LifeBotResult LB_StepperInit(unsigned char id)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = INIT_STEPPER;
	g_abWrite[1] = id;
	g_cntWrite = 1 + 1;

	auto r = _Transact();
	if (r == LBR_Success)
	{
		r = g_abRead[1];
	}
	return r;
}

enum LifeBotResult LB_SetStepperPos(const struct LifeBotStepperPos* lpsp)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = SET_STEPPER_POS;
	g_abWrite[1] = lpsp->id;
	g_abWrite[2] = (unsigned char)lpsp->iPos;
	g_abWrite[3] = (unsigned char)(lpsp->iPos >> 8);
	g_abWrite[4] = (unsigned char)(lpsp->iPos >> 16);
    g_abWrite[5] = (unsigned char)(lpsp->iPos >> 24);

	g_abWrite[6] = (unsigned char)lpsp->nSpeed;
	g_abWrite[7] = (unsigned char)(lpsp->nSpeed >> 8);

	g_abWrite[8] = (unsigned char)lpsp->mode;

	g_abWrite[9] = (unsigned char)lpsp->nSoftStartTime;
	g_abWrite[10] = (unsigned char)(lpsp->nSoftStartTime >> 8);

	g_cntWrite = 11;

    // auto r = NULL;
	auto r = _Transact();
	if (r == LBR_Success)
	{
		r = g_abRead[1];
	}
	return r;
}

enum LifeBotResult LB_GetStepperState(unsigned char id, int* lpPos)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = GET_STEPPER_STATE;
	g_abWrite[1] = id;
	g_cntWrite = 2;

	const auto r = _Transact();
	if (r == LBR_Success)
	{
		const auto nPos =
			(g_abRead[2]) |
			(g_abRead[3] << 8) |
			(g_abRead[4] << 16) |
			(g_abRead[5] << 24);
		if (lpPos)
			*lpPos = nPos;
		return g_abRead[1];
	}
	return r;
}

enum LifeBotResult LB_IncStepperPos(const struct LifeBotStepperPos* lpsp)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = INC_STEPPER_POS;
	g_abWrite[1] = lpsp->id;
	g_abWrite[2] = (unsigned char)lpsp->iPos;
	g_abWrite[3] = (unsigned char)(lpsp->iPos >> 8);
	g_abWrite[4] = (unsigned char)(lpsp->iPos >> 16);
	g_abWrite[5] = (unsigned char)(lpsp->iPos >> 24);

	g_abWrite[6] = (unsigned char)lpsp->nSpeed;
	g_abWrite[7] = (unsigned char)(lpsp->nSpeed >> 8);

	g_abWrite[8] = (unsigned char)lpsp->mode;

	g_abWrite[9] = (unsigned char)lpsp->nSoftStartTime;
	g_abWrite[10] = (unsigned char)(lpsp->nSoftStartTime >> 8);

	g_cntWrite = 11;

	auto r = _Transact();
	if (r == LBR_Success)
	{
		r = g_abRead[1];
	}
	return r;
}

enum LifeBotResult LB_InitMotor(unsigned char id)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = INIT_MOTOR;
	g_abWrite[1] = id;
	g_cntWrite = 2;

	const auto r = _Transact();
	return r;
}
enum LifeBotResult LB_GetMotorState(unsigned char id, unsigned int* lpnTimePassed)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = GET_MOTOR_STATE;
	g_abWrite[1] = id;
	g_cntWrite = 2;

	const auto r = _Transact();
	if (r == LBR_Success)
	{
		if (lpnTimePassed)
		{
			*lpnTimePassed = (unsigned int)
				(g_abRead[2]) |
				(g_abRead[3] << 8) |
				(g_abRead[4] << 16) |
				(g_abRead[5] << 24);
		}
	}
	return r;
}
enum LifeBotResult LB_DriveMotor(const struct LifeBotDriveMotor* lpm)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = DRIVE_MOTOR;
	g_abWrite[1] = (unsigned char)lpm->id;
	g_abWrite[2] = (unsigned char)lpm->nPower;
	g_abWrite[3] = (unsigned char)lpm->nDir;
	g_abWrite[4] = (unsigned char)lpm->nTime;
	g_abWrite[5] = (unsigned char)(lpm->nTime >> 8);
	g_abWrite[6] = (unsigned char)(lpm->nTime >> 16);
	g_abWrite[7] = (unsigned char)(lpm->nTime >> 24);
	g_cntWrite = 8;

	const auto r = _Transact();
	return r;
}

enum LifeBotResult LB_SetOutputState(unsigned char id, enum LifeBotOutputState st)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = SET_OUTPUT_STATE;
	g_abWrite[1] = id;
	g_abWrite[2] = (st == 1);
	g_cntWrite = 3;

	const auto r = _Transact();
	return r;
}

enum LifeBotResult LB_SetLed(enum LifeBotLedMode mode,
	unsigned char nParam, // ProgressValue / LedIndex
	unsigned char red, unsigned char green, unsigned char blue)
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = LED_CONTROL;
	g_abWrite[1] = (unsigned char)mode;
	g_abWrite[2] = (unsigned char)nParam;
	g_abWrite[3] = (unsigned char)(nParam >> 8);
	g_abWrite[4] = (unsigned char)red;
	g_abWrite[5] = (unsigned char)green;
	g_abWrite[6] = (unsigned char)blue;
	g_cntWrite = 7;

	const auto r = _Transact();
	return r;
}

enum LifeBotResult LB_GetAnalogInputs(unsigned short anStates[10])
{
	memset(g_abWrite, 0, sizeof(g_abWrite));
	g_abWrite[0] = GET_ANALOG_INPUTS;
	g_cntWrite = 1;

	const auto r = _Transact();
	if (r == LBR_Success)
	{
		if (anStates)
		{
			anStates[0] = (unsigned int)g_abRead[1] | (g_abRead[2] << 8);
			anStates[1] = (unsigned int)g_abRead[3] | (g_abRead[4] << 8);
			anStates[2] = (unsigned int)g_abRead[5] | (g_abRead[6] << 8);
			anStates[3] = (unsigned int)g_abRead[7] | (g_abRead[8] << 8);
			anStates[4] = (unsigned int)g_abRead[9] | (g_abRead[10] << 8);

			anStates[5] = (unsigned int)g_abRead[11] | (g_abRead[12] << 8);
			anStates[6] = (unsigned int)g_abRead[13] | (g_abRead[14] << 8);
			anStates[7] = (unsigned int)g_abRead[15] | (g_abRead[16] << 8);
			anStates[8] = (unsigned int)g_abRead[17] | (g_abRead[18] << 8);
			anStates[9] = (unsigned int)g_abRead[19] | (g_abRead[20] << 8);
		}
	}
	return r;
}