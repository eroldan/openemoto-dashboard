def adctest():
    a = ADC(Pin(34))
    a.atten(ADC.ATTN_0DB)
    rlist = list()
    for x in range(10): rlist.append(a.read())
    rlist.sort()
    av = rlist[int(len(rlist) / 2)] # mean
    #av = sum(rlist) / len(rlist) # avg
    print(av)
    rlist = list()
