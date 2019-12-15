# coding=utf-8
import serial, time, sys
#import matplotlib.pyplot as plt
import serial.tools.list_ports
import numpy as np

bps = 115200  # 波特率
timex = None  # 超时设置,None：永远等待操作，0为立即返回请求结果，其他值为等待超时时间(单位为秒）

#####################################################################
#                         设备参数设置区域                             #
#####################################################################
portx='COM11'    #串口名称
useHandMode=False                   #是否启用手动设置
userSetADCaim=1000                  #手动设置的ADC目标值 *指回复到的初值
userSetENCaim=10000                 #手动设置的ENC目标值 *指回复到的初值
name='teamname'                     #队伍名字

#####################################################################
#                          比赛任务难度参数设置区域                     #
#####################################################################
endThresh=75                        #ENC的稳定阈值，正负 37.5
degreeThreshold = 170               #ADC的稳定阈值，正负   170
steadytime=1                        #1s
dropthrshold = 40                   #判断是不是倒了



ADCaim = 0000  # 平衡位置ADC
ENCaim = 10000  # 平衡位置ENC

point=0
points=5
t_old=0

def ADCinrange(adc, adc_aim):
    if (degreeThreshold < adc_aim and adc_aim < 4096 - degreeThreshold):
        if abs(adc - adc_aim) < degreeThreshold:
            return True
        else:
            return False
    elif (adc_aim <= degreeThreshold):
        if abs(adc - adc_aim) < degreeThreshold or adc > 4096 - (degreeThreshold - adc_aim):
            return True
        else:
            return False
    else:
        if abs(adc - adc_aim) < degreeThreshold or adc < degreeThreshold -(4096- adc_aim):
            return True
        else:
            return False

def ENCinrange(enc,enc_aim):
    if abs(enc-enc_aim)<endThresh:
        return True
    else:
        return False

def adc(adc1, adc2):
    ADC = adc1 * 64 + adc2
    data_ADC.write(str(ADC) + '\n')
    return ADC

def enc(enc1, enc2, enc3):
    ENC = enc1 * 4096 + enc2 * 64 + enc3
    data_ENC.write(str(ENC) + '\n')
    return ENC

def notdropdown(adc, adc_aim):
    degreeThreshold=1024
    if (degreeThreshold < adc_aim and adc_aim < 4096 - degreeThreshold):
        if abs(adc - adc_aim) < degreeThreshold:
            return True
        else:
            return False
    elif (adc_aim <= degreeThreshold):
        if abs(adc - adc_aim) < degreeThreshold or adc > 4096 - (degreeThreshold - adc_aim):
            return True
        else:
            return False
    else:
        if abs(adc - adc_aim) < degreeThreshold or adc < degreeThreshold -(4096- adc_aim):
            return True
        else:
            return False

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
                    ADC1 = ord(ser.read(1)) - 1
                    ADC2 = ord(ser.read(1)) - 1
                    ADC = adc(ADC1, ADC2)
                    ENC1 = ord(ser.read(1)) - 1
                    ENC2 = ord(ser.read(1)) - 1
                    ENC3 = ord(ser.read(1)) - 1
                    ENC = enc(ENC1, ENC2, ENC3)
                    ADCaim = ADC  # 上电初始位置为ADC_down
                    ENCaim = ENC
                    ###########################
                    # 是否需要把ENC给变成固定初值
                    # TODO: 目标计算是否合理，ENC
                    ###########################
                    if useHandMode:
                        ADCaim=userSetADCaim
                        ENCaim=userSetENCaim
                    ENClist = [ENCaim, ENCaim + 300, ENCaim - 300, ENCaim + 600, ENCaim-600]
                    print('>>>初始位置下，ADC=', ADCaim, 'ENC=', ENC)
                    print('>>>目标位置为，ADCaim=', ADCaim, 'ENCaim=', ENCaim)
                    continue
                else:
                    ADC1 = ord(ser.read(1)) - 1
                    ADC2 = ord(ser.read(1)) - 1
                    ADC = adc(ADC1, ADC2)
                    ENC1 = ord(ser.read(1)) - 1
                    ENC2 = ord(ser.read(1)) - 1
                    ENC3 = ord(ser.read(1)) - 1
                    ENC = enc(ENC1, ENC2, ENC3)
                    #print(ENC)
                    if start_flag == 0 and (not ADCinrange(ADC, ADCaim) or not ENCinrange(ENC,ENClist[point])):
                        print('>>>计时开始!')
                        start_flag = 1
                        t = 1
                        endThresh = 100
                        point += 1
                if notdropdown(ADC, ADCaim)==False:
                    print("摆杆倒了，任务失败")
                    exit()
                if t-t_old>200*15:
                    print("超时了，任务失败")
                    exit()
                '''
                判定是不是到达目标点
                '''
                if start_flag == 1 and ADCinrange(ADC, ADCaim) and ENCinrange(ENC,ENClist[point]):
                    endCount = endCount + 1
                else:
                    endCount = 0
                if endCount == 100:
                    point+=1
                    print("达到目标点:",point-1)
                    t_old=t
                if start_flag == 1:
                    ax.append(t*0.005)  # 添加 t 到 x 轴的数据中
                    ay.append(ADC)  # 添加 ADC到 y 轴的数据中
                    az.append(ENC)  # 添加 ADC到 y 轴的数据中
                if point == points:
                    data_ADC.close()
                    data_ADC = open(name + 'task2ADC.txt', 'a')
                    data_ENC.close()
                    data_ENC = open(name + 'task2ENC.txt', 'a')
                    break
    print('>>>结束！')
    ser.close()  # 关闭串口
    print('>>>最终耗时:', t * 0.005, 's')
    winflag=1
    degreeThreshold=1024
    count=0

    for y in ay:
        if(ADCinrange(y, ADCaim)):
            continue
        else:
            count+=1

    if count<40:
        print("没倒！")
    else:
        print("倒辣！有",count,"个点超出了水平线")

    degreeThreshold=170
    ADCMSE=0
    ENCMSE=0

except Exception as e:
    print("---异常---：", e)

#draw
'''
try:
    plt.subplot(1,2,1) #要生成两行两列，这是第一个图plt.subplot('行','列','编号')
    plt.plot(ax, ay)  # 画出当前 ax 列表和 ay 列表中的值的图形
    plt.ylabel('ADC')
    plt.xlabel('time/s')

    plt.subplot(1,2,2) #两行两列,这是第二个图
    plt.plot(ax, az)  # 画出当前 ax 列表和 ay 列表中的值的图形
    plt.ylabel('ENC')
    plt.xlabel('time/s')


    for ENC in ENClist:
        plt.plot(ax, np.ones(len(ax))*ENC)  # 画出当前 ax 列表和 ay 列表中的值的图形
    plt.ylabel('ENC')
    plt.xlabel('time/s')

    plt.show()
except Exception as e:
    print("---异常---：", e)
'''