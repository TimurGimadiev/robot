#ifndef _LIFE_BOT_H
#define _LIFE_BOT_H

#ifdef LIFEBOTDLL_EXPORTS
#define LIFEBOT_API_EXPORT __declspec(dllexport)
#else
#define LIFEBOT_API_EXPORT __declspec(dllimport)
#endif

#ifdef __cplusplus
extern "C"
{
#endif

	enum LifeBotResult
	{
		LBR_Success = 0,
		LBR_Ordered = 1, // ��������� ������ �� ������ �������
		LBR_NotReady = 3, // ����������� �������������
		LBR_InvalidData = 0x81, // ������������ ������� ���������
		LBR_InvalidRType = 0x82, // �������� ��� �������
		LBR_IntercomFault = 0x83, // ������ ����� � ������ �������� ���������
		LBR_NotInitialized = 0x84, // ��������� �� ������������
		LBR_DeviceError = 0xFD,
		LBR_TransactError = 0xFE,
		LBR_Disconnect = 0xFF,
	};

	typedef struct LifeBotSett
	{
		unsigned short nReadTimeout;
	};
	enum LifeBotResult LIFEBOT_API_EXPORT LB_Sett(const struct LifeBotSett*);


	typedef struct LifeBotDeviceInfo
	{
		unsigned short     nProtocolVersion;
		unsigned short     nHardwareVersion;
		unsigned short     nFirmwareVersion;
		unsigned long long nSerial;
		unsigned int       nRevision;
	};
	enum LifeBotResult LIFEBOT_API_EXPORT LB_GetDeviceInfo(struct
		LifeBotDeviceInfo*);


	enum LifeBotResult LIFEBOT_API_EXPORT LB_Stop();

	enum LifeBotStepperMode
	{
		LBSM_Even = 0,    // �������
		LBSM_Smooth,      // ������� ������/����������
		LBSM_SmoothAccel,
	};
	typedef struct LifeBotStepperPos
	{
		unsigned char id;
		int iPos; // ����� �� �������� ��������� ���������
		unsigned short nSpeed; // ����� � �������
		enum LifeBotStepperMode mode;
		unsigned short nSoftStartTime; // ����� �������� �������/���������� � �������������. ���� �����������, ���� MODE = 0
	};
	enum LifeBotResult LIFEBOT_API_EXPORT LB_StepperInit(unsigned char id);
	enum LifeBotResult LIFEBOT_API_EXPORT 
		LB_SetStepperPos(const struct LifeBotStepperPos*);
	enum LifeBotResult LIFEBOT_API_EXPORT 
		LB_IncStepperPos(const struct LifeBotStepperPos*);
	enum LifeBotResult LIFEBOT_API_EXPORT LB_GetStepperState(unsigned char id,
		int* lpPos);


	enum LifeBotResult LIFEBOT_API_EXPORT LB_InitMotor(unsigned char id);
	typedef struct LifeBotDriveMotor
	{
		unsigned char id;
		unsigned char nPower; // 0..100
		unsigned char nDir; // 0, 1
		unsigned int  nTime;
	};
	enum LifeBotResult LIFEBOT_API_EXPORT LB_GetMotorState(unsigned char id,
		unsigned int* lpnTimePassed);
	enum LifeBotResult LIFEBOT_API_EXPORT LB_DriveMotor(const struct LifeBotDriveMotor*);


	enum LifeBotOutputState
	{
		LBOS_Off = 0,
		LBOS_On,
		LBOS_CurrentProtection, // for get only
	};
	enum LifeBotResult LIFEBOT_API_EXPORT
		LB_SetOutputState(unsigned char id, enum LifeBotOutputState);
	enum LifeBotResult LIFEBOT_API_EXPORT
		LB_GetOutputState(unsigned char id, enum LifeBotOutputState*);


	enum LifeBotResult LIFEBOT_API_EXPORT LB_PhotoInterrupterReset();
	enum LifeBotPhotoIntersect
	{
		No = 0,
		Yes,
	};
	enum LifeBotResult LIFEBOT_API_EXPORT 
		LB_PhotoInterrupterGetState(enum LifeBotPhotoIntersect*);
	enum LifeBotResult LIFEBOT_API_EXPORT 
		LB_PhotoInterrupterGetCount(unsigned short* lpnCount);


	enum LifeBotResult LIFEBOT_API_EXPORT 
		LB_GetAnalogInputs(unsigned short anStates[10]);

	enum LifeBotLedMode // ����������� �� ���������� ����� �� ����
	{
		LBLM_ProgressBar,
		LBLM_Manual,
	};
	enum LifeBotResult LIFEBOT_API_EXPORT LB_SetLed(enum LifeBotLedMode,
		unsigned char nParam, // ProgressValue / LedIndex
		unsigned char r, unsigned char g, unsigned char b);

#ifdef __cplusplus
}
#endif

#endif // _LIFE_BOT_H