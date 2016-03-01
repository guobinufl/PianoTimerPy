import sys
from PyQt4 import QtCore, QtGui
from PianoKey import *
from PianoTimerUi_Main import Ui_MainWindow


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


class MainForm(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainForm,self).__init__()
        self.bTimerRun = False
        self.setupUi(self)
        
        #QtCore.QObject.connect(self.pushButton_End, QtCore.SIGNAL(_fromUtf8("clicked()")), self.stopTimer)
        #QtCore.QObject.connect(self.pushButton_Begin, QtCore.SIGNAL(_fromUtf8("clicked()")), self.beginTimer)
        self.pushButton_Begin.clicked.connect(self.beginTimer)
        self.pushButton_Stop.clicked.connect(self.stopTimer)
        

    def stopTimer(self):
        self.bTimerRun = False

    def beginTimer(self):
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
        RATE = 1024*16 #44100
        fs = 1.0*RATE
    
        pianokeyfreq = PianoKeyFreq()
        fwave = 'PianoKeys.wav'
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
            y = y / ymax
			
            xcorr_key = pianofind_xcorr_f(y, pianokeyfreq.SingleKeyFFT, isplot=False)
            xcorr_key = xcorr_key * pianokeyfreq.SingleKeyXcorrScale
            xcorr_key_all[isec, :] = xcorr_key
            if(np.max(xcorr_key) > 100):
                ispiano_xcorr = True
            else:
                ispiano_xcorr = False
				
            if(ispiano_amp and ispiano_xcorr):
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
        
        wav_data = np.hstack(wav_total[0:all_sec_count+2, :]) / 2**15
        cur_dt = str(datetime.now())
        wav_file = re.sub('(:|\.| )', '-', cur_dt)
        wavfile.write('RecordWav/'+wav_file+'.wav', RATE, wav_data)		
		
        


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    PianoTimerMain = MainForm()
    PianoTimerMain.show()
    sys.exit(app.exec_())

