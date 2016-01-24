import sys
from PyQt4 import QtCore, QtGui
from PianoTimerPy import *

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

class Ui_PianoTimerWidget(object):
    def __init__(self):
        self.bTimerRun = False
    
    def setupUi(self, PianoTimerWidget):
        PianoTimerWidget.setObjectName(_fromUtf8("PianoTimerWidget"))
        PianoTimerWidget.resize(675, 775)
        self.spinBox_MinIn = QtGui.QSpinBox(PianoTimerWidget)
        self.spinBox_MinIn.setGeometry(QtCore.QRect(360, 490, 171, 61))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.spinBox_MinIn.setFont(font)
        self.spinBox_MinIn.setProperty("value", 20)
        self.spinBox_MinIn.setObjectName(_fromUtf8("spinBox_MinIn"))
        self.label = QtGui.QLabel(PianoTimerWidget)
        self.label.setGeometry(QtCore.QRect(130, 480, 191, 81))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label.setFont(font)
        self.label.setObjectName(_fromUtf8("label"))
        self.label_2 = QtGui.QLabel(PianoTimerWidget)
        self.label_2.setGeometry(QtCore.QRect(130, 30, 411, 111))
        font = QtGui.QFont()
        font.setPointSize(26)
        self.label_2.setFont(font)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.pushButton_Begin = QtGui.QPushButton(PianoTimerWidget)
        self.pushButton_Begin.setGeometry(QtCore.QRect(120, 640, 170, 80))
        font = QtGui.QFont()
        font.setPointSize(16)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_Begin.setFont(font)
        self.pushButton_Begin.setObjectName(_fromUtf8("pushButton_Begin"))
        self.pushButton_End = QtGui.QPushButton(PianoTimerWidget)
        self.pushButton_End.setGeometry(QtCore.QRect(370, 640, 170, 80))
        font = QtGui.QFont()
        font.setPointSize(18)
        self.pushButton_End.setFont(font)
        self.pushButton_End.setObjectName(_fromUtf8("pushButton_End"))
        self.labelTime = QtGui.QLabel(PianoTimerWidget)
        self.labelTime.setGeometry(QtCore.QRect(140, 200, 411, 181))
        font = QtGui.QFont()
        font.setPointSize(48)
        font.setBold(True)
        font.setWeight(75)
        self.labelTime.setFont(font)
        self.labelTime.setObjectName(_fromUtf8("labelTime"))

        self.retranslateUi(PianoTimerWidget)
        QtCore.QObject.connect(self.pushButton_End, QtCore.SIGNAL(_fromUtf8("clicked()")), self.stopTimer)
        QtCore.QObject.connect(self.pushButton_Begin, QtCore.SIGNAL(_fromUtf8("clicked()")), self.beginTimer)
        QtCore.QMetaObject.connectSlotsByName(PianoTimerWidget)

    def retranslateUi(self, PianoTimerWidget):
        PianoTimerWidget.setWindowTitle(_translate("PianoTimerWidget", "Piano Timer", None))
        self.label.setText(_translate("PianoTimerWidget", "Minuts", None))
        self.label_2.setText(_translate("PianoTimerWidget", "Piano Timer", None))
        self.pushButton_Begin.setText(_translate("PianoTimerWidget", "&Begin", None))
        self.pushButton_Begin.setShortcut(_translate("PianoTimerWidget", "Alt+B", None))
        self.pushButton_End.setText(_translate("PianoTimerWidget", "&Stop", None))
        self.pushButton_End.setShortcut(_translate("PianoTimerWidget", "Alt+S", None))
        self.labelTime.setText(_translate("PianoTimerWidget", "20:00", None))

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
        self.labelTime.setText(_translate("PianoTimerWidget", str_time, None))
        
        CHUNK = 1024*2
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 1024*16 #44100
        fs = 1.0*RATE
    
        pianokeyfreq = PianoKeyFreq()
        fwave = 'pianokeys.wav'
        if(os.path.isfile(fwave) == True):
            pianokeys_freq = pianokeyfreq.RecordFreq(fwave)
        else:
            pianokeys_freq = pianokeyfreq.StandardFreq()
    
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        wav_total = np.zeros((max_sec+10, RATE))
        print(wav_total.shape)
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
            if(ymax > 0.5):
                ispiano_amp = True
            else:
                ispiano_amp = False
			
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
				
            if(ispiano_amp and ispiano_bw and ispiano_key):
                all_sec_count += 1
                play_sec_count += 1
                ispiano.append(True)
            else:
                all_sec_count += 1
                ispiano.append(False)
			
            remain_sec = play_sec - isec
            print('isec={0:}, play_sec={1:}'.format(isec, remain_sec))
            str_min = np.floor(remain_sec/60.0).astype('int')
            str_sec = np.mod(remain_sec, 60).astype('int')
            str_time = str(str_min) + ':' + str(str_sec)
            self.labelTime.setText(_translate("PianoTimerWidget", str_time, None))
            QtGui.QApplication.processEvents()
    			
            if(remain_sec <= 0):
                self.bTimerRun = False

        print("* Piano Timer Stop.")
        self.labelTime.setText(_translate("PianoTimerWidget", "00:00", None))
    
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        wav_data = np.hstack(wav_total[0:all_sec_count+2, :]) / 2**15
        cur_dt = str(datetime.now())
#        wav_file = cur_dt.replace(':', '-').replace(' ', '-').replace('.', '-')
        wav_file = re.sub('(:|\.| )', '-', cur_dt)
        wavfile.write(wav_file+'.wav', RATE, wav_data)		
		
        


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    PianoTimerWidget = QtGui.QWidget()
    ui = Ui_PianoTimerWidget()
    ui.setupUi(PianoTimerWidget)
    PianoTimerWidget.show()
    sys.exit(app.exec_())

