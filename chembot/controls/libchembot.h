#ifndef LIBCHEMBOT_H_
#define LIBCHEMBOT_H_

#include "Transacter.h"

enum LifeBotResult {
    LBR_Success = 0,
    LBR_Ordered = 1,            
    LBR_NotReady = 3,           
    LBR_InvalidData = 0x81,     
    LBR_InvalidRType = 0x82,    
    LBR_IntercomFault = 0x83,   
    LBR_NotInitialized = 0x84,
    LBR_DeviceError = 0xFD,
    LBR_TransactError = 0xFE,
    LBR_Disconnect = 0xFF,
};

typedef struct LifeBotSett
	{
		unsigned short nReadTimeout;
	} LifeBotSett;

typedef struct LifeBotDeviceInfo
	{
		unsigned short     nProtocolVersion;
		unsigned short     nHardwareVersion;
		unsigned short     nFirmwareVersion;
		unsigned long long nSerial;
		unsigned int       nRevision;
	} LifeBotDeviceInfo;

enum LifeBotStepperMode
	{
		LBSM_Even = 0,    // �������
		LBSM_Smooth,      // ������� ������/����������
		LBSM_SmoothAccel,
	};

typedef struct LifeBotStepperPos
	{
		unsigned char id;
		int iPos;
		unsigned short nSpeed;
		enum LifeBotStepperMode mode;
		unsigned short nSoftStartTime;
	} LifeBotStepperPos;

typedef struct LifeBotDriveMotor {
		unsigned char id;
		unsigned char nPower; // 0..100
		unsigned char nDir; // 0, 1
		unsigned int  nTime;
	};

enum LifeBotOutputState
	{
		LBOS_Off = 0,
		LBOS_On,
		LBOS_CurrentProtection, // for get only
	};

enum LifeBotLedMode
	{
		LBLM_ProgressBar,
		LBLM_Manual,
	};

enum LifeBotResult LB_GetDeviceInfo(struct LifeBotDeviceInfo* lpdi);
enum LifeBotResult LB_StepperInit(unsigned char id);
enum LifeBotResult RB_GetDeviceInfo(struct LifeBotDeviceInfo* lpdi);
enum LifeBotResult RB_StepperInit(unsigned char id);
enum LifeBotResult LB_SetStepperPos(const struct LifeBotStepperPos* lpsp);
enum LifeBotResult LB_GetStepperState(unsigned char id, int* lpPos);
enum LifeBotResult LB_IncStepperPos(const struct LifeBotStepperPos* lpsp);
enum LifeBotResult LB_InitMotor(unsigned char id);
enum LifeBotResult LB_GetMotorState(unsigned char id, unsigned int* lpnTimePassed);
enum LifeBotResult LB_DriveMotor(const struct LifeBotDriveMotor* lpm);

#endif  // LIBCHEMBOT_H_
