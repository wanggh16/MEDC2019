#include "sys.h"
  /**************************************************************************
���ߣ�ƽ��С��֮��
�ҵ��Ա�С�꣺http://shop114407458.taobao.com/
**************************************************************************/
u8 Flag_Stop=1,delay_50,delay_flag;         //ֹͣ��־λ 50ms��׼��ʾ��־λ
int Encoder,Position_Zero=10000;            //���������������
int Moto;                                   //���PWM���� Ӧ��Motor�� ��Moto�¾�	
int Voltage;                                //��ص�ѹ������صı���
float Angle_Balance;                        //��λ�ƴ���������
float Balance_KP=50,Balance_KD=244,Position_KP=25,Position_KD=600;  //PIDϵ��
float Menu=1,Amplitude1=1,Amplitude2=10,Amplitude3=1,Amplitude4=10; //PID������ز���

/* ----- USER CODE BEGIN ----- */

char USART1_Buffer[8];
int16_t pwm_duty_given;
/* ----- USER CODE BEGIN ----- */

int main(void)
{ 
	Stm32_Clock_Init(9);            //=====ϵͳʱ������
	delay_init(72);                 //=====��ʱ��ʼ��
	JTAG_Set(JTAG_SWD_DISABLE);     //=====�ر�JTAG�ӿ�
	JTAG_Set(SWD_ENABLE);           //=====��SWD�ӿ� �������������SWD�ӿڵ���
	delay_ms(1000);                 //=====��ʱ�������ȴ�ϵͳ�ȶ� ��
	LED_Init();                     //=====��ʼ���� LED ���ӵ�Ӳ���ӿ�
	EXTI_Init();                    //=====������ʼ��(�ⲿ�жϵ���ʽ)
	OLED_Init();                    //=====OLED��ʼ��
/* ----- USER CODE BEGIN ----- */
	// bound changeds
	uart_init(72,115200);           //=====��ʼ������1
/* ----- USER CODE END ----- */
  MiniBalance_PWM_Init(7199,0);   //=====��ʼ��PWM 10KHZ������������� 
	Encoder_Init_TIM4();            //=====��ʼ����������TIM2�ı������ӿ�ģʽ�� 
	Angle_Adc_Init();               //=====��λ�ƴ�����ģ�����ɼ���ʼ��
	Baterry_Adc_Init();             //=====��ص�ѹģ�����ɼ���ʼ��
	Timer1_Init(49,7199);           //=====��ʱ�жϳ�ʼ�� 
	USART1_Buffer[0]='z';
	USART1_Buffer[6]=0xff;
	USART1_Buffer[7]='\0';
	while(1)
		{
				u16 Angle_Balance_temp=(u16)Angle_Balance;
				u16 Encoder_temp=(u16)Encoder;

				USART1_Buffer[1]=(char)((Angle_Balance_temp>>6)+1);
				USART1_Buffer[2]=(char)((Angle_Balance_temp&0x3f)+1);
				USART1_Buffer[3]=(char)((Encoder_temp>>12)+1);
				USART1_Buffer[4]=(char)(((Encoder_temp>>6)&0x3f)+1);
				USART1_Buffer[5]=(char)((Encoder_temp&0x3f)+1);
			  //DataScope();	            //===��λ��
				delay_flag=1;	            //===5ms�жϾ�׼��ʱ��־λ

				printf("%s", USART1_Buffer);
				//oled_show();              //===��ʾ����	  	
				while(delay_flag);        //===5ms�жϾ�׼��ʱ  ��Ҫ�ǲ�����ʾ��λ����Ҫ�ϸ��50ms��������   							
		} 
}
