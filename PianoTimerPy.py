import matplotlib.pyplot as plt
import numpy as np
from numpy.fft import fft
from numpy import hanning
import scipy.io.wavfile as wavfile
import pyaudio
from datetime import datetime
import re
#import scipy.signal as signal

class PianoKeyFreq(object):
    def __init__(self):
        self.KeyFreqList_std = np.zeros(88)
        self.KeyFreqList_rcd = np.zeros(88)
        
    def StandardFreq(self):
        PianoKeyFreq = []
        for n in range(1, 89):
            KeyFreq = 2**((n-49.0)/12.0) * 440.0
            PianoKeyFreq.append(KeyFreq)
        self.KeyFreqList_std = np.asarray(PianoKeyFreq)
        
        return self.KeyFreqList_std
        
        
    def RecordFreq(self, fwave):
        rate, pianowav_tmp = wavfile.read(fwave)
        pianowav = pianowav_tmp[:,0].astype('float') / (2**15)
        pianowav = np.delete(pianowav, range(10000))
        fs = 1.0*rate
        del pianowav_tmp
        
        pianokeyind = self.KeySegment(pianowav)
        PianoKeyFreq = []
        for ii, i in enumerate(pianokeyind):
            yt = pianowav[i:i+20000]
            if(np.mod(ii, 10) == 15):
                KeyFreq = self.KeyFreqFind(yt, fs, ikey=ii, isplot=True)
            else:
                KeyFreq = self.KeyFreqFind(yt, fs, ikey=ii)
            PianoKeyFreq.append(KeyFreq)
        self.KeyFreqList_rcd = np.asarray(PianoKeyFreq)
        
        return self.KeyFreqList_rcd
        
        
    def KeySegment(self, yt):
        yind = (np.abs(yt) > 0.95).nonzero()
        yind1 = (np.diff(yind[0])>50000).nonzero()
        yind2 = np.hstack((0, yind1[0]+1))
        pianokeyind = yind[0][yind2]
        
        return pianokeyind
        

    def KeyFreqFind(self, yt, fs, ikey=0, isplot=False):        
        Nt = len(yt)
        Nf = np.int(fs)
        df = fs / Nf
        ff = np.arange(0,fs,df)
        if(Nt>=Nf):
            yt1 = yt[0:Nf]
        else:
            yt1 = np.zeros(Nf)
            tleft = np.floor((Nf-Nt)/2.0).astype('int')
            tright = tleft+Nt
            yt1[tleft:tright] = yt
            
        yf = np.abs(fft(yt1*hanning(Nf)))
        stdfreq = self.StandardFreq()[ikey]
        istdfreq = np.round(stdfreq/df).astype('int')
        fband = 0.1 * stdfreq
        ifband = np.max((np.round(fband/df).astype('int'), np.round(20.0/df).astype('int')))
        ifreqmax = np.argmax(yf[istdfreq-ifband : istdfreq+ifband])
        ff1 = ff[istdfreq-ifband : istdfreq+ifband]
        freqmax = ff1[ifreqmax]
        
        if(isplot):
            dt = 1.0 / fs
            tt = np.arange(Nt) * dt
            plt.figure()
            plt.subplot(211)
            plt.plot(tt, yt)
            plt.subplot(212)
            plt.plot(ff, yf)
            ylims = plt.ylim()
            plt.plot([stdfreq, stdfreq], ylims, 'r:')
            plt.xlim((0, 4000))
            plt.show()
            
        return freqmax
        
       
#piano = PianoKeyFreq()
#pianokey_std = piano.StandardFreq()
#fwave = 'pianokeys.wav'
#pianokey_rcd = piano.RecordFreq(fwave)
#plt.figure()
#plt.subplot(211)
#plt.plot(pianokey_std, '.b-')
#plt.plot(pianokey_rcd, 'or:')
#plt.subplot(212)
#plt.plot(pianokey_rcd - pianokey_std, '.k-')



def PianoFFT(yt, fs):
#    dt = 1.0/fs
#    Nt = len(yt)
#    tt = np.arange(0, Nt*dt, dt)
    Nf = len(yt)
    df = fs / Nf
    ff = np.arange(0,fs,df)
    yf = np.abs(fft(yt*hanning(Nf)))
    
    return yf, ff, df


def pianofind(yf, ff):
    ifreqmax = np.argmax(yf)
    freqmax = ff[ifreqmax]
    yfmax = yf[ifreqmax]
    
    yfleft = yf[0:ifreqmax]
    ffleft = ff[0:ifreqmax]
    ifleft = (yfleft<0.75*yfmax).nonzero()
    
    yfright = yf[ifreqmax:]
    ffright = ff[ifreqmax:]
    ifright = (yfright<0.75*yfmax).nonzero()
    
    if((len(ifleft[0])==0) or (len(ifright[0])==0)):
        return 0.0, 0.0
    else:
        return freqmax, ffright[ifright[0][0]]-ffleft[ifleft[0][-1]]


def main_offline():
    rate, pianowav_tmp = wavfile.read('piano.wav')
    pianowav = np.delete(pianowav_tmp, range(4000), axis=0)
    Nsec = np.floor(pianowav.shape[0]/rate).astype('int')
    #Nsec = 10
    fs = 1.0*rate
    
    pianokeyfreq = PianoKeyFreq()
#    pianokey_std = pianokeyfreq.StandardFreq()
    fwave = 'pianokeys.wav'
    pianokey_rcd = pianokeyfreq.RecordFreq(fwave)
    print(pianokey_rcd)

    ispiano = [False]
    for isec in range(1, Nsec-1):
        ileft = np.round((isec-1.0)*rate).astype('int')
        iright = np.round((isec+0.0)*rate).astype('int')
        y = pianowav[ileft:iright, 0].astype('float')
        y = y / 2**15
        
        ymax = np.max(np.abs(y))
        if(ymax > 0.5):
            ispiano_amp = True
        else:
            ispiano_amp = False
            ispiano.append(ispiano_amp)
            print(isec, 'amp=false')
            continue
        
        yf, ff, df = PianoFFT(y, fs)
        fleft = 0
        fright = np.round(5000/df).astype('int')
        piano_fmax, piano_bw = pianofind(yf[fleft:fright], ff[fleft:fright])
        if(isec == 18):
            print('        piano_fmax={0:}, piano_bw={1:}'.format(piano_fmax, piano_bw))
            plt.figure()
            plt.plot(ff, yf)
            plt.show()
        
        if(piano_bw <6):
            ispiano_bw = True
        else:
            ispiano_bw = False
    
#        if piano_fmax < 500:
#            gap = 3
#        elif piano_fmax>=500 and piano_fmax<1500:
#            gap = 4
#        else:
#            gap = 5
        gap = 3 + np.floor(piano_fmax / 500.0)
        pianokeyfind = (np.abs(pianokey_rcd - piano_fmax) < gap).nonzero()
        if(len(pianokeyfind[0]) > 0):
            ispiano_key = True
        else:
            ispiano_key = False
            
        if(ispiano_bw and ispiano_key):
            ispiano.append(True)
            print('{0:} - piano key find. isbw={1:}, bw={2:}, iskey={3:}, gap={4:}, keyfind={5:}'.\
                  format(isec, ispiano_bw, piano_bw, ispiano_key, gap, pianokeyfind))
        else:
            ispiano.append(False)
            print('{0:} - isbw={1:}, bw={2:}, iskey={3:}, gap={4:}, keyfind={5:}'.\
                  format(isec, ispiano_bw, piano_bw, ispiano_key, gap, pianokeyfind))
    
    ispiano.append(False)     
    #print(ispiano)
    
    
    plt.figure(figsize=(12,9))
    dt = 1.0/fs
    for isec in range(1, Nsec):
        ileft = np.round((isec-1.0)*rate).astype('int')
        iright = np.round((isec+0.0)*rate).astype('int')
        y = pianowav[ileft:iright, 0].astype('float')
        y = y / 2**15
        tt = np.arange(isec-1.0, isec, dt)
        if(ispiano[isec]):
            plt.plot(tt[0::10], y[0::10], 'r')
        else:
            plt.plot(tt[0::10], y[0::10], 'b')


def main_online():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 1024*16 #44100
    max_sec = 50
    play_sec = 30
    fs = 1.0*RATE
    
    pianokeyfreq = PianoKeyFreq()
#    pianokey_std = pianokeyfreq.StandardFreq()
    fwave = 'pianokeys.wav'
    pianokey_rcd = pianokeyfreq.RecordFreq(fwave)
    
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK)

    wav_total = np.zeros((max_sec, RATE))
    ispiano = []
    play_sec_count = 0
    all_sec_count = 0
    
    print("* Piano Timer Start.")
    for isec in range(max_sec+1):
        frames = []
        for j in range(0, int(RATE / CHUNK)):
            chunk_wave = stream.read(CHUNK)
            data = np.fromstring(chunk_wave, dtype=np.int16)
            frames.append(data)
        wav_sec = np.hstack(frames)
        wav_total[isec, :] = wav_sec
        del frames

        y = wav_sec.astype('float') / 2**15
        ymax = np.max(np.abs(y))
        if(ymax > 0.5):
            ispiano_amp = True
        else:
            ispiano_amp = False
        
        yf, ff, df = PianoFFT(y, fs)
        fleft = 0
        fright = np.round(5000/df).astype('int')
        piano_fmax, piano_bw = pianofind(yf[fleft:fright], ff[fleft:fright])
#        if(isec == 18):
#            print('        piano_fmax={0:}, piano_bw={1:}'.format(piano_fmax, piano_bw))
#            plt.figure()
#            plt.plot(ff, yf)
#            plt.show()
        
        if(piano_bw <6):
            ispiano_bw = True
        else:
            ispiano_bw = False
    
        gap = 3 + np.floor(piano_fmax / 500.0)
        pianokeyfind = (np.abs(pianokey_rcd - piano_fmax) < gap).nonzero()
        if(len(pianokeyfind[0]) > 0):
            ispiano_key = True
        else:
            ispiano_key = False
            
        if(ispiano_amp and ispiano_bw and ispiano_key):
            all_sec_count += 1
            play_sec_count += 1
            ispiano.append(True)
#            print('{0:} - piano key find. isbw={1:}, bw={2:}, iskey={3:}, gap={4:}, keyfind={5:}'.\
#                  format(isec, ispiano_bw, piano_bw, ispiano_key, gap, pianokeyfind))
        else:
            all_sec_count += 1
            ispiano.append(False)
#            print('{0:} - isbw={1:}, bw={2:}, iskey={3:}, gap={4:}, keyfind={5:}'.\
#                  format(isec, ispiano_bw, piano_bw, ispiano_key, gap, pianokeyfind))
        
        print('isec={0:}, play_sec={1:}'.format(isec, play_sec_count))
        
        if(play_sec_count > play_sec):
            break

    print("* Piano Timer Stop.")

    stream.stop_stream()
    stream.close()
    p.terminate()
    
    wav_data = np.hstack(wav_total)
    cur_dt = str(datetime.now())
    wav_file = cur_dt.replace(':', '-').replace(' ', '-').replace('.', '-')
    wavfile.write(wav_file+'.wav', RATE, wav_data)
    
    plt.figure(figsize=(12,9))
    dt = 1.0/fs
    for isec in range(0, all_sec_count-1):
        y = wav_total[isec, :].astype('float') / 2**15
        tt = np.arange(isec, isec+1.0, dt)
        if(ispiano[isec]):
            plt.plot(tt[0::10], y[0::10], 'r')
        else:
            plt.plot(tt[0::10], y[0::10], 'b')
    plt.show()


if __name__ == "__main__":
#    main_offline()
    main_online()
