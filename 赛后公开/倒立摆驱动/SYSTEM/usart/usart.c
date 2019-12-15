#include "usart.h"	  
 /**************************************************************************
���ߣ�ƽ��С��֮�� 
�Ա����̣�http://shop114407458.taobao.com/
**************************************************************************/
//�������´���,֧��printf����,������Ҫѡ��use MicroLIB	  
#if 1
#pragma import(__use_no_semihosting)             
//��׼����Ҫ��֧�ֺ���                 
struct __FILE 
{ 
	int handle; 
	/* Whatever you require here. If the only file you are using is */ 
	/* standard output using printf() for debugging, no file handling */ 
	/* is required. */ 
}; 
/* FILE is typedef�� d in stdio.h. */ 
FILE __stdout;       
//����_sys_exit()�Ա���ʹ�ð�����ģʽ    
_sys_exit(int x) 
{ 
	x = x; 
} 
//�ض���fputc���� 
int fputc(int ch, FILE *f)
{      
	
	while((USART1->SR&0X40)==0);//Flag_Show!=0  ʹ�ô���1   
	USART1->DR = (u8) ch;      

	return ch;
}
#endif 
//end
//////////////////////////////////////////////////////////////////
/**************************ʵ�ֺ���**********************************************
*��    ��:		usart1����һ���ֽ�
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
	temp=(float)(pclk2*1000000)/(bound*16);//�õ�USARTDIV
	mantissa=temp;				 //�õ���������
	fraction=(temp-mantissa)*16; //�õ�С������	 
  mantissa<<=4;
	mantissa+=fraction; 
	RCC->APB2ENR|=1<<2;   //ʹ��PORTA��ʱ��  
	RCC->APB2ENR|=1<<14;  //ʹ�ܴ���ʱ�� 
	GPIOA->CRH&=0XFFFFF00F;//IO״̬����
	GPIOA->CRH|=0X000008B0;//IO״̬����
		  
	RCC->APB2RSTR|=1<<14;   //��λ����1
	RCC->APB2RSTR&=~(1<<14);//ֹͣ��λ	   	   
	//����������
 	USART1->BRR=mantissa; //����������	 
	USART1->CR1|=0X200C;  //1λֹͣ,��У��λ.
	//ʹ�ܽ����ж�
  USART1->CR1|=1<<8;    //PE�ж�ʹ��
  USART1->CR1|=1<<5;    //���ջ������ǿ��ж�ʹ�� 
	USART1->CR1|=1<<4;    //IDLE�ж�ʹ��	
  MY_NVIC_Init(0,0,USART1_IRQn,2);//��2 ������ȼ�
}

//����1�жϷ������      
u8 USART_RX_BUF[20];    //���ջ���,���100���ֽ�.
u8 USART_RX_CNT=0;       //���յ�����Ч�ֽ���Ŀ      
extern int16_t pwm_duty_given;
void USART1_IRQHandler(void)
{
    u8 clear=clear;
		if(USART1->SR&(1<<4))//IDLE�ж�
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
		else if(USART1->SR&(1<<5))//���յ�����
    {
			USART_RX_BUF[USART_RX_CNT] = USART1->DR;
			USART_RX_CNT++;			
    }
} 
