# coding=utf-8
import serial, time, sys
#import matplotlib.pyplot as plt
import serial.tools.list_ports
from queue import Queue

bps = 115200  # 波特率
timex = None  # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）
isENCsteady=False
isADCsteady=False

#####################################################################
#                         设备参数设置区域                             #
#####################################################################
portx='COM11'    #串口名称
useHandMode=False                   #是否启用手动设置
userSetADCaim=1940               #手动设置的ADC目标值 *指回复到的初值
userSetdown=0                  #手动设置的ADC目标值 *指回复到的初值
#userSetENDaim=10000                #手动设置的ENC目标值 *指回复到的初值
                                    #已改为任意位置稳定超过3s
name='teamname'                     #队伍名字
#####################################################################
#                          比赛任务难度参数设置区域                     #
#####################################################################
endThresh=75*2                      #ENC的稳定阈值，正负 75
degreeThreshold = 170               #ADC的稳定阈值，正负 170
steadytime=3                        #3s



down = 0000  # 倒立位置ADC，和ADCaim差2014
ADCaim = 0000  # 平衡位置ADC

ENCqueue=Queue()

def ADCinrange(adc, adc_aim):
    if (degreeThreshold < adc_aim and adc_aim < 4095 - degreeThreshold):
        if abs(adc - adc_aim) < degreeThreshold:
            return True
        else:
            return False
    elif (adc_aim < degreeThreshold):
        if abs(adc - adc_aim) < degreeThreshold or adc > 4095 - (degreeThreshold - adc_aim):
            return True
        else:
            return False
    else:
        if abs(adc - adc_aim) < degreeThreshold or adc < degreeThreshold - adc_aim:
            return True
        else:
            return False

def ENCsteady():
    listQ = ENCqueue.queue
    if len(listQ)<200*steadytime:
        return False
    while (len(ENCqueue.queue) >= 199 * steadytime):
        listQ = ENCqueue.queue
        if abs(max(listQ) - min(listQ)) < endThresh:
            return True
        ENCqueue.get()
    return False

def adc(adc1, adc2):
    ADC = adc1 * 64 + adc2
    data_ADC.write(str(ADC) + '\n')
    return ADC

def enc(enc1, enc2, enc3):
    ENC = enc1 * 4096 + enc2 * 64 + enc3
    data_ENC.write(str(ENC) + '\n')
    return ENC

data_ADC = open(name+'task2ADC.txt','w')
data_ENC = open(name+'task2ENC.txt','w')

#main
try:
    ser = serial.Serial(portx, bps, timeout=timex)  # 打开串口，并得到串口对象
    ax = []  # 定义一个 x 轴的空列表用来接收动态的数据
    ay = []  # 定义一个 y 轴的空列表用来接收动态的数据
    az = []  # 定义一个 y2 轴的空列表用来接收动态的数据

    t = -1  # 5ms
    endCount = 0
    start_flag = 0
    #plt.show()

    if ser.is_open:
        print("串口详情参数：", ser)
        time.sleep(0.1)
        while True:
            time.sleep(0.001)
            a = ord(ser.read(1))
            if a == 0x7a:
                t = t + 1
                if t == 0:
                    ###########################
                    #上电记录初值，并以一圈4096的
                    #assuption计算终值
                    #TODO: 目标计算是否合理
                    ###########################
                    ADC1 = ord(ser.read(1)) - 1
                    ADC2 = ord(ser.read(1)) - 1
                    ADC = adc(ADC1, ADC2)
                    ENC1 = ord(ser.read(1)) - 1
                    ENC2 = ord(ser.read(1)) - 1
                    ENC3 = ord(ser.read(1)) - 1
                    ENC = enc(ENC1, ENC2, ENC3)
                    down = ADC  # 上电初始位置为ADC_down
                    print('>>>初始位置下，ADC=', down, 'ENC=', ENC)
                    ADCaim = (2048 + down) % 4095  #终值
                    if useHandMode:
                        ADCaim = userSetADCaim
                        down = userSetdown
                    print('>>>目标位置为，ADCaim=', ADCaim)
                    continue
                else:
                    ###########################
                    # 判定是否开始计时
                    # 如果开始计时，判定是否稳定于目标
                    # TODO: 稳定区域和开始区域的参数调整
                    ###########################
                    ADC1 = ord(ser.read(1)) - 1
                    ADC2 = ord(ser.read(1)) - 1
                    ADC = adc(ADC1, ADC2)
                    ENC1 = ord(ser.read(1)) - 1
                    ENC2 = ord(ser.read(1)) - 1
                    ENC3 = ord(ser.read(1)) - 1
                    ENC = enc(ENC1, ENC2, ENC3)
                    if start_flag == 0 and not ADCinrange(ADC, down):
                        print('>>>计时开始!')
                        start_flag = 1
                        t = 1
                if start_flag==1:
                    ENCqueue.put(ENC)
                    if ADCinrange(ADC, ADCaim):
                        endCount = endCount + 1
                    else:
                        endCount = 0
                    ax.append(t*0.005)  # 添加 t 到 x 轴的数据中
                    ay.append(ADC)  # 添加 ADC到 y 轴的数据中
                    az.append(ENC)  # 添加 ADC到 y 轴的数据中
                    isENCsteady= ENCsteady()
                    isADCsteady= endCount >= 200*steadytime
                ###########################
                # 稳定1s停止
                # TODO: 3*200*5ms==3s。3s是否合理
                ###########################
                if isENCsteady and isADCsteady:
                    data_ADC.close()
                    data_ADC = open(name + 'task2ADC.txt', 'a')
                    data_ENC.close()
                    data_ENC = open(name + 'task2ENC.txt', 'a')
                    break
    print('>>>结束！')
    ser.close()  # 关闭串口
    print('>>>最终耗时:', t * 0.005, 's')
except Exception as e:
    print("---异常---：", e)

#draw
''''
try:
    plt.subplot(1,2,1) #要生成两行两列，这是第一个图plt.subplot('行','列','编号')
    plt.plot(ax, ay)  # 画出当前 ax 列表和 ay 列表中的值的图形
    plt.ylabel('ADC')
    plt.xlabel('time/s')
    for i in range(0, t-1):
        if ADCinrange(ay[i], ADCaim):
            plt.annotate(s='.', xy=(round(ax[i], 3), ay[i]),
                xytext=(0, 0), textcoords='offset points')

    plt.subplot(1,2,2) #两行两列,这是第二个图
    plt.plot(ax, az)  # 画出当前 ax 列表和 ay 列表中的值的图形
    plt.ylabel('ENC')
    plt.xlabel('time/s')
    plt.show()
except Exception as e:
    print("---异常---：", e)
'''