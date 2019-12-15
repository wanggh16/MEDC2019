#include "sys.h"
  /**************************************************************************
作者：平衡小车之家
我的淘宝小店：http://shop114407458.taobao.com/
**************************************************************************/
u8 Flag_Stop=1,delay_50,delay_flag;         //停止标志位 50ms精准演示标志位
int Encoder,Position_Zero=10000;            //编码器的脉冲计数
int Moto;                                   //电机PWM变量 应是Motor的 向Moto致敬	
int Voltage;                                //电池电压采样相关的变量
float Angle_Balance;                        //角位移传感器数据
float Balance_KP=50,Balance_KD=244,Position_KP=25,Position_KD=600;  //PID系数
float Menu=1,Amplitude1=1,Amplitude2=10,Amplitude3=1,Amplitude4=10; //PID调试相关参数

/* ----- USER CODE BEGIN ----- */

char USART1_Buffer[8];
int16_t pwm_duty_given;
/* ----- USER CODE BEGIN ----- */

int main(void)
{ 
	Stm32_Clock_Init(9);            //=====系统时钟设置
	delay_init(72);                 //=====延时初始化
	JTAG_Set(JTAG_SWD_DISABLE);     //=====关闭JTAG接口
	JTAG_Set(SWD_ENABLE);           //=====打开SWD接口 可以利用主板的SWD接口调试
	delay_ms(1000);                 //=====延时启动，等待系统稳定 共
	LED_Init();                     //=====初始化与 LED 连接的硬件接口
	EXTI_Init();                    //=====按键初始化(外部中断的形式)
	OLED_Init();                    //=====OLED初始化
/* ----- USER CODE BEGIN ----- */
	// bound changeds
	uart_init(72,115200);           //=====初始化串口1
/* ----- USER CODE END ----- */
  MiniBalance_PWM_Init(7199,0);   //=====初始化PWM 10KHZ，用于驱动电机 
	Encoder_Init_TIM4();            //=====初始化编码器（TIM2的编码器接口模式） 
	Angle_Adc_Init();               //=====角位移传感器模拟量采集初始化
	Baterry_Adc_Init();             //=====电池电压模拟量采集初始化
	Timer1_Init(49,7199);           //=====定时中断初始化 
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
			  //DataScope();	            //===上位机
				delay_flag=1;	            //===5ms中断精准延时标志位

				printf("%s", USART1_Buffer);
				//oled_show();              //===显示屏打开	  	
				while(delay_flag);        //===5ms中断精准延时  主要是波形显示上位机需要严格的50ms传输周期   							
		} 
}
