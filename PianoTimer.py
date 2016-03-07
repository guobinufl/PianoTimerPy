import sys, os
from PyQt4 import QtCore, QtGui
from PianoKey import *
from PianoTimerUi_Main import Ui_MainWindow
from PianoTimerUi_About import Ui_DialogAbout
from PianoTimerUi_Setup import Ui_DialogSetup


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class AboutDialog(QtGui.QDialog, Ui_DialogAbout):
    def __init__(self):
        super(AboutDialog,self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.close)
        

class SetupDialog(QtGui.QDialog, Ui_DialogSetup):
    def __init__(self):
        super(SetupDialog,self).__init__()
        self.setupUi(self)
        

class MainForm(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainForm,self).__init__()
        self.bTimerRun = False
        self.bSaveWav = False
        self.nMethod = 0
        self.setupUi(self)
        
        self.myabout = AboutDialog()
        self.mysetup = SetupDialog()

        self.actionExit.triggered.connect(self.close)
        self.actionAbout.triggered.connect(self.showAbout)
        self.actionPerference.triggered.connect(self.showSetup)
        self.actionOpen.triggered.connect(self.openRefWav)
        
        self.pushButton_Begin.clicked.connect(self.beginTimer)
        self.pushButton_Stop.clicked.connect(self.stopTimer)
    
    def showAbout(self):
        self.myabout.show()

    def showSetup(self):
        self.mysetup.show()

    def openRefWav(self):
        pianokeyfreq = PianoKeyFreq()
        fwave = 'PianoKeys.wav'
        pianokeys_freq_std = pianokeyfreq.StandardFreq()
        pianokeys_freq_ref = pianokeyfreq.RecordFreq(fwave)
        
        rate, pianowav_tmp = wavfile.read(fwave)
        if(pianowav_tmp.dtype == 'int16'):
            if(len(pianowav_tmp.shape)>1):
                pianowav = pianowav_tmp[:,0].astype('float') / (2**15)
            else:
                pianowav = pianowav_tmp.astype('float') / (2**15)
        else:
            if(len(pianowav_tmp.shape)>1):
                pianowav = pianowav_tmp[:,0]
            else:
                pianowav = pianowav_tmp.copy()
        del pianowav_tmp
        pianowav = np.delete(pianowav, range(np.round(rate/2.0).astype('int')))
        dt = 1.0 / rate
        Nt = len(pianowav)
        tt = np.arange(Nt) * dt
        
        fig = plt.figure(figsize=(9,12))
        plt.subplot(3,1,1)
        plt.plot(tt, pianowav)
        plt.title('Waveform'); plt.xlabel=('Time (sec)'); plt.ylabel('Amp')
        plt.subplot(3,1,2)
        plt.plot(np.arange(88)+1, pianokeys_freq_std, 'bo');
        plt.plot(np.arange(88)+1, pianokeys_freq_ref, 'r.');
        plt.title('Freq of Each Key'); plt.xlabel=('Key ID'); plt.ylabel('Hz')
        plt.legend('Std', 'Ref')
        plt.subplot(3,1,3)
        plt.plot(np.arange(88)+1, pianokeys_freq_ref - pianokeys_freq_std, 'k.');
        plt.title('Different Freq between Std and Ref'); plt.xlabel=('Key ID'); plt.ylabel('Hz')
        plt.show()

    def checkSetup(self):
        if(self.mysetup.comboBox_SaveWav.currentIndex() == 0):
            self.bSaveWav = False
        else:
            self.bSaveWav = True
            if not os.path.exists("RecordWav"):
                os.makedirs("RecordWav")
        self.nMethod = self.mysetup.comboBox_SaveWav.currentIndex()
        if not os.path.exists("PianoKeys.wav"):
            print("PianoKeys.wav is missing!")
            self.nMethod = 0
        
    def stopTimer(self):
        self.bTimerRun = False

    def beginTimer(self):
        self.checkSetup()
        
        play_sec = self.spinBox_MinIn.value() * 60
        max_sec = 1 * play_sec
        self.bTimerRun = True
		
        remain_sec = play_sec
        str_min = np.floor(remain_sec/60.0).astype('int')
        str_sec = np.mod(remain_sec, 60).astype('int')
        str_time = str(str_min) + ':' + str(str_sec)
        self.labelTime.setText(_translate("MainWindow", str_time, None))
        
        CHUNK = 1024*2
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 1024*16
        fs = 1.0*RATE
    
        pianokeyfreq = PianoKeyFreq()
        fwave = 'PianoKeys.wav'
        if(self.nMethod == 1):
            pianokeys_freq = pianokeyfreq.RecordFreq(fwave)
        else:
            pianokeys_freq = pianokeyfreq.StandardFreq()
        pianokeyfreq.CalSingleKeyFFT(fwave)
    
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        wav_total = np.zeros((max_sec+10, RATE))
        xcorr_key_all = np.zeros((max_sec+10, 88))
        ispiano = []
        play_sec_count = 0
        all_sec_count = 0
        isec = 0
    
        print("* Piano Timer Start.")
        while(self.bTimerRun):
            frames = []
            for j in range(0, int(RATE / CHUNK)):
                chunk_wave = stream.read(CHUNK)
                data = np.fromstring(chunk_wave, dtype=np.int16)
                frames.append(data)
            wav_sec = np.hstack(frames)
            wav_total[isec, :] = wav_sec
            del frames
            isec += 1

            y = wav_sec.astype('float') / 2**15
            ymax = np.max(np.abs(y))
            if(ymax > 0.1):
                ispiano_amp = True
            else:
                ispiano_amp = False
			
            if((self.nMethod == 0) or (self.nMethod == 1)):
                yf, ff, df = PianoFFT(y, fs)
                fleft = 0
                fright = np.round(5000/df).astype('int')
                piano_fmax, piano_bw = pianofind(yf[fleft:fright], ff[fleft:fright])
			
                if(piano_bw <6):
                    ispiano_bw = True
                else:
                    ispiano_bw = False
		
                gap = 3 + np.floor(piano_fmax / 500.0)
                pianokeyfind = (np.abs(pianokeys_freq - piano_fmax) < gap).nonzero()
                if(len(pianokeyfind[0]) > 0):
                    ispiano_key = True
                else:
                    ispiano_key = False
                    
                if(ispiano_bw and ispiano_key):
                    ispiano_freq = True
                else:
                    ispiano_freq = False
            else:
                y = y / ymax
                xcorr_key = pianofind_xcorr_f(y, pianokeyfreq.SingleKeyFFT, isplot=False)
                xcorr_key = xcorr_key * pianokeyfreq.SingleKeyXcorrScale
                xcorr_key_all[isec, :] = xcorr_key
                if(np.max(xcorr_key) > 100):
                    ispiano_xcorr = True
                else:
                    ispiano_xcorr = False
                ispiano_freq = ispiano_xcorr
				
            if(ispiano_amp and ispiano_freq):
                all_sec_count += 1
                play_sec_count += 1
                ispiano.append(True)
            else:
                all_sec_count += 1
                ispiano.append(False)
			
            remain_sec = play_sec - play_sec_count
            print('Total Sec={0:}, Play Sec={1:}'.format(isec, play_sec_count))
            str_min = np.floor(remain_sec/60.0).astype('int')
            str_sec = np.mod(remain_sec, 60).astype('int')
            str_time = "%02d:%02d" % (str_min, str_sec) #str(str_min) + ':' + str(str_sec)
            self.labelTime.setText(_translate("MainWindow", str_time, None))
            QtGui.QApplication.processEvents()
    			
            if(remain_sec <= 0):
                self.bTimerRun = False

        print("* Piano Timer Stop.")
        self.labelTime.setText(_translate("MainWindow", "00:00", None))
    
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        if(self.bSaveWav):
            wav_data = np.hstack(wav_total[0:all_sec_count+2, :]) / 2**15
            cur_dt = str(datetime.now())
            wav_file = re.sub('(:|\.| )', '-', cur_dt)
            wavfile.write('RecordWav/'+wav_file+'.wav', RATE, wav_data)		
		
        


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    PianoTimerMain = MainForm()
    PianoTimerMain.show()
    sys.exit(app.exec_())

