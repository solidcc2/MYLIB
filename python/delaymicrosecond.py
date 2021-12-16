# reference: https://zhuanlan.zhihu.com/p/364344742
# 微秒级delay
# 补偿regulate选择合适的情况，误差大约在 ±1微秒范围内

import time    # 导入time模块

def delayMicrosecond(t, regulate = 2):    # 微秒级延时函数
    start,end=0,0           # 声明变量
    start=time.time()       # 记录开始时间
    t=(t-regulate)/1000000     # 将输入t的单位转换为秒，regulate是时间补偿
    while end-start<t:  # 循环至时间差值大于或等于设定值时
        end=time.time()     # 记录结束时间

if __name__ == "__main__":
    a=time.time()   # 记录延时函数开始执行时的时间
    delayMicrosecond(1000)	#延时 35 微秒
    b=time.time()   # 记录延时函数结束时的时间

    print((b-a)*1000000)    # 将延时函数执行消耗的时间打印出来