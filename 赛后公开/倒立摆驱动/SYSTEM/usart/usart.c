#include "usart.h"	  
 /**************************************************************************
作者：平衡小车之家 
淘宝店铺：http://shop114407458.taobao.com/
**************************************************************************/
//加入以下代码,支持printf函数,而不需要选择use MicroLIB	  
#if 1
#pragma import(__use_no_semihosting)             
//标准库需要的支持函数                 
struct __FILE 
{ 
	int handle; 
	/* Whatever you require here. If the only file you are using is */ 
	/* standard output using printf() for debugging, no file handling */ 
	/* is required. */ 
}; 
/* FILE is typedef’ d in stdio.h. */ 
FILE __stdout;       
//定义_sys_exit()以避免使用半主机模式    
_sys_exit(int x) 
{ 
	x = x; 
} 
//重定义fputc函数 
int fputc(int ch, FILE *f)
{      
	
	while((USART1->SR&0X40)==0);//Flag_Show!=0  使用串口1   
	USART1->DR = (u8) ch;      

	return ch;
}
#endif 
//end
//////////////////////////////////////////////////////////////////
/**************************实现函数**********************************************
*功    能:		usart1发送一个字节
*********************************************************************************/
void usart1_send(u8 data)
{
	USART1->DR = data;
	while((USART1->SR&0x40)==0);	
}
void uart_init(u32 pclk2,u32 bound)
{  	 
	float temp;
	u16 mantissa;
	u16 fraction;	   
	temp=(float)(pclk2*1000000)/(bound*16);//得到USARTDIV
	mantissa=temp;				 //得到整数部分
	fraction=(temp-mantissa)*16; //得到小数部分	 
  mantissa<<=4;
	mantissa+=fraction; 
	RCC->APB2ENR|=1<<2;   //使能PORTA口时钟  
	RCC->APB2ENR|=1<<14;  //使能串口时钟 
	GPIOA->CRH&=0XFFFFF00F;//IO状态设置
	GPIOA->CRH|=0X000008B0;//IO状态设置
		  
	RCC->APB2RSTR|=1<<14;   //复位串口1
	RCC->APB2RSTR&=~(1<<14);//停止复位	   	   
	//波特率设置
 	USART1->BRR=mantissa; //波特率设置	 
	USART1->CR1|=0X200C;  //1位停止,无校验位.
	//使能接收中断
  USART1->CR1|=1<<8;    //PE中断使能
  USART1->CR1|=1<<5;    //接收缓冲区非空中断使能 
	USART1->CR1|=1<<4;    //IDLE中断使能	
  MY_NVIC_Init(0,0,USART1_IRQn,2);//组2 最高优先级
}

//串口1中断服务程序      
u8 USART_RX_BUF[20];    //接收缓冲,最大100个字节.
u8 USART_RX_CNT=0;       //接收到的有效字节数目      
extern int16_t pwm_duty_given;
void USART1_IRQHandler(void)
{
    u8 clear=clear;
		if(USART1->SR&(1<<4))//IDLE中断
		{
			clear=USART1->SR;
			clear=USART1->DR;
			USART_RX_BUF[USART_RX_CNT]=0;
			if (USART_RX_BUF[0]=='z') pwm_duty_given = ((u16)(USART_RX_BUF[1])<<8)+(USART_RX_BUF[2])-7200;
			if (pwm_duty_given>7200) pwm_duty_given=7200;
			else if (pwm_duty_given<-7200) pwm_duty_given=-7200;
			
			//printf("%d\n", pwm_duty_given);
			USART_RX_CNT = 0;
		}
		else if(USART1->SR&(1<<5))//接收到数据
    {
			USART_RX_BUF[USART_RX_CNT] = USART1->DR;
			USART_RX_CNT++;			
    }
} 
