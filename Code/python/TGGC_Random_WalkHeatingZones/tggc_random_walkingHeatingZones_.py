import numpy as np
import pandas as pd
import random as rnd
import matplotlib.pyplot as plt
import HelperFunctionsR as hfr
import math
import seaborn as sns
########################
###   NEW EQUATION
####################
#Rdata = np.loadtxt("mydata.txt" , delimiter = '\t')
#plt.figure(3)
#plt.plot(Rdata)
#plt.show()
colors = np.array(["red","green","magenta","black","blue","gray"])
markers = np.array(["o","^","P","x","D","v","s"])
j = 2.0 #number of compounds
n_mol = 100.0
cols = ['red','green','magenta','black','blue','grey10']
sig_sq = 4.073e-6 #3.792*exp(-4) #1*exp(-6)
taylor = 1.647*10**(-1)

#C = [-12.5075, -12.7202]
#h = [11416, 11521]
X = np.array([10,11]) #alkane length
C =  - 0.47406*X - 7.22173
h = 2284 + 819*X

delta_t = 0.0001 # time step: number of n's per second
R = 1.987 # Boltzman's constant
col_length = 200 # column length [cm]

T0 = 300.0 # initial temperature [K]  ******Samuel T.0 should be about 310***********
#T0 = 270
u_m = 55.0 # velocity of mobile phase [cm/sec]
w = 6.0 # velocity of gradient [cm/sec]
tp_rate = 0.5 #degrees C per second
#s = 0.1
#c = 0.0005

col_length = 200

ramp_length = 200.0 # cm
ramp_height = 80.0 # degree C

zone_len = 1.0 #cm
window = 2000
factor = 1.08**(1.0/40)
kern = factor**(-abs(np.arange(-window,window+1,1)))
kern = kern/sum(kern)
holder = np.linspace(ramp_height,0,ramp_length/zone_len)
if((col_length-int(ramp_length))//int(zone_len) > 0): #creates an empty array WHY??
    holder = np.concatenate( holder , np.zeros((col_length-int(ramp_length))//int(zone_len))-1 ) #does this do anything???
Temp_vec = np.repeat(holder, zone_len*1e4)
tmp = hfr.rolling_mult(Temp_vec[0:int(ramp_length*1e4) + window], kern)
Temp_vec[window:len(tmp)+window] = tmp

run_time = 15000000

##### Start Standard Execution
detector = np.zeros((int(j),int(n_mol)))
#samp_pop = np.linspace(1,n_mol,int(n_mol))/10
#x = np.array([rnd.sample(list(samp_pop),int(n_mol)),]*int(j))
x = np.loadtxt('xdata.txt')
res_end = np.zeros((int(j),2))
eluted_1 = 1
eluted_2 = 1
detected_1 = 0
detected_2 = 0

for n in range(0,run_time):
    temp_arr = x*1e4+1
    temp_arr[temp_arr > col_length*1e4] = col_length*1e4
    temp_arr = temp_arr.flatten().astype(int)
    T_all = Temp_vec[temp_arr] + tp_rate*n*delta_t+T0
    C_all = C
    tmp_h = np.repeat(h,len(T_all)/len(h))
    tmp_C_all = np.repeat(C_all,len(T_all)/len(C_all))
    k_all = np.exp(tmp_h/(R*T_all) + tmp_C_all)
    D_t = ( (T_all**1.75)*sig_sq + ((1+6*k_all+11*k_all**2)/((1+k_all)**2))*(u_m**2)*taylor/(T_all**1.75) )*delta_t
    x = np.reshape(x.flatten('F') + (u_m*delta_t + hfr.pyRNorm(j*n_mol,0,(2*D_t)**(.5))) * ((np.random.rand(int(j*n_mol)) < (1.0/(1+k_all))) + 0) , np.shape(x)) #adding the zero makes it numeric
    if(n%500==0):
        if(max(x[0,])>col_length):
            all_detected_1 = np.where(x[0,] > col_length)
            new_detected_1 = all_detected_1[all_detected != detected_1]
            detected_1 = np.concatenate(detected_1,new_detected_1)
            detector[0,new_detected_1] = n*delta_t
        if(max(x[1,])>col_length):
            all_detected_2 = np.where(x[1,] > col_length)
            new_detected_2 = all_detected_2[all_detected_2 != detected_2]
            detected_2 = np.concatenate(detected_2,new_detected_2)
            detector[1, new_detected_2] = n*delta_t
            if(len(detected_2)+len(detected_1)-2 >= 2*n.mol):
                 break
    if(n%50000 == 0):
        if(np.amin(x)>col_length):
            break
        f,(ax1,ax2) = plt.subplots(2, sharex=True)
        plt.xlim(0,col_length)
        plt.ylim(0,1)
        ax1.yaxis.set_label_position("right")
        ax2.yaxis.set_label_position("right")
        ax1.set_ylabel(' Time:\n ' + str(n*delta_t) + ' s')
        for i in range(0,int(j)):
            print("i: ",i,"color: ",colors[i])
            lab = round(4*np.std(x[i,],axis=0,ddof=1) , 2)
            print(x[i,])
            ax1.scatter(x[i,], np.arange(1,n_mol+1)/n_mol,color = colors[i],s = 0.5,  marker = markers[i],label =lab)
        ax1.legend()
        xx = np.linspace(0,col_length-1,(col_length-1)/.1 + 1)
        tmpp = (xx*1e4).astype(int)
        #tmpp[tmpp > len(Temp_vec)] = -1
        #tmpp = np.setdiff1d(tmpp,-1).astype(int)
        yy = (Temp_vec[tmpp]+tp_rate*delta_t*n)/200.0
        ax1.plot(xx,yy,color = 'red')
        top_pks = np.zeros(int(j))
        pk_head = np.zeros(int(j))
        pk_tail = np.zeros(int(j))
        peakx = 0
        for i in range(0,int(j)):
            sns.kdeplot(x[i,],color=colors[i],ax=ax2) #density plot
            [ydata,xdata] = ax2.lines[i].get_data()
            peakx = np.argmax(ydata)
            top_pks[i] = xdata[peakx]
            pk_head[i] = xdata[max(np.where(ydata[0:peakx+1] < ydata[peakx]/2.0)[0])]
            pk_tail[i] = xdata[min(np.where(ydata[peakx:len(ydata)]<ydata[peakx]/2+peakx)[0])]
        res = np.zeros(int(j)-1)
        for i in range(1,int(j)):
            res[i-1] = abs( (top_pks[i]-top_pks[i-1]) / (( 1.7*(pk_head[i-1]-pk_tail[i-1]) + 1.7 * (pk_head[i]-pk_tail[i]))/2.0) )
        ax2.set_ylabel( ' Ave \n Res:\n ' + str(round(np.mean(res),2)) )
        plt.show()
par(mfrow=c(1,1), mar=c(5,4,4,2)+0.1)

### End Standard Execution
#
# dev.off()
#
# retention.time <- rowMeans(detector)
# stand.dev <- apply(detector,1,sd)
# resolutions <- rep(0,j)
# for(i in 2:j)
# {
#    resolutions[i] <- (retention.time[i]-retention.time[i-1])/(2*(stand.dev[i]+stand.dev[i-1]))
# }
# (rbind(stand.dev,retention.time, resolutions))
