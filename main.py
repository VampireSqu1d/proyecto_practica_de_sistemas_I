# importando modulos de sistema
import sys
import os
import threading
from threading import Thread
# importando lectores de text files
import PyPDF2
from docx import Document
from gtts import gTTS
# importando libreria de interfaz
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QMessageBox, QWidget
# import tts.sapi
# from translate import Translator
# importanto modulos de audio
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr


class App(QMainWindow, Thread):

    def __init__(self):
        super().__init__()
        self.title = 'Aplicacion sin nombre'
        self.left = 10
        self.top = 10
        self.width = 480
        self.height = 260
        self.button_width = 140
        self.button_height = 25
        self.button_x = 20
        self.button_y = 50
        Thread.__init__(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        # create button to get audio file
        get_audio_button = QPushButton('Traducir archivo de audio', self)
        get_audio_button.setGeometry(self.button_x, self.button_y, self.button_width, self.button_height)
        get_audio_button.clicked.connect(self.funcion_no_disponible)
        # create button to get pdf or text file
        text_button = QPushButton('Convertir texto a audio', self)
        text_button.setGeometry(self.button_x, self.button_y + 30, self.button_width, self.button_height)
        text_button.clicked.connect(self.start_text_file_processing_thread)
        # create button to transcribe audio file
        transcribe_button = QPushButton('Transcribir audio', self)
        transcribe_button.setGeometry(self.button_x, self.button_y + 60, self.button_width, self.button_height)
        transcribe_button.clicked.connect(self.start_transcribir_audio_thread)
        # create button to go to record audio
        record_audio_button = QPushButton('Empezar a grabar audio', self)
        record_audio_button.setGeometry(self.button_x, self.button_y + 90, self.button_width, self.button_height)
        record_audio_button.clicked.connect(self.funcion_no_disponible)
        # create button to go to record screen
        record_screen_button = QPushButton('Empezar a grabar pantalla', self)
        record_screen_button.setGeometry(self.button_x, self.button_y + 120, self.button_width, self.button_height)
        record_screen_button.clicked.connect(self.funcion_no_disponible)
        self.show()

    @pyqtSlot()
    def funcion_no_disponible(self):
        msg = QMessageBox()
        msg.setWindowTitle('Función no disponible!!')
        msg.setIcon(QMessageBox.Information)
        msg.setText('Esta función aun no está disponible para su uso. Sorry :)')
        msg.setInformativeText('Esta es una version no terminada del programa')
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        msg.exec_()

    @pyqtSlot()
    def start_transcribir_audio_thread(self):
        hilo = TranscribirAudio()
        hilo.start()

    @pyqtSlot()
    def start_text_file_processing_thread(self):
        hilo = TextToAudioProcessingThreadClass()
        hilo.start()


class TranscribirAudio(QWidget, threading.Thread):
    def __init__(self):
        super().__init__()
        threading.Thread.__init__(self)

    def run(self):
        print('Empezando hilo')
        audio_file_path = self.get_audio_file()
        if audio_file_path.endswith('mp3'):
            print('not ready yet')
        elif audio_file_path.endswith('wav'):
            text = self.wav_to_text(audio_file_path)
            self.save_text_in_txt(text, audio_file_path)

    def save_text_in_txt(self, text, path):
        file = open(path[0:-3] + 'txt', 'w')
        file.write(text)
        file.close()

    def wav_to_text(self, path):
        r = sr.Recognizer()
        sound = AudioSegment.from_wav(path)
        chunks = split_on_silence(sound,
                                  min_silence_len=500,
                                  silence_thresh=sound.dBFS - 14,
                                  keep_silence=500,
                                  )
        folder_name = "audio-chunks"
        # crea un directorio para guardar los chunks
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
        whole_text = ""
        # process each chunk
        for i, audio_chunk in enumerate(chunks, start=1):
            chunk_filename = os.path.join(folder_name, f"chunk{i}.wav")
            audio_chunk.export(chunk_filename, format="wav")
            with sr.AudioFile(chunk_filename) as source:
                audio_listened = r.record(source)
                try:
                    text = r.recognize_google(audio_listened)
                except sr.UnknownValueError as e:
                    print(str(e))
                else:
                    text = f"{text.capitalize()}. "
                    print(chunk_filename, ":", text)
                    whole_text += text
        # return the text for all chunks detected
        self.remove_chunks(folder_name)
        print('Done processing audio!!')
        return whole_text

    @staticmethod
    def remove_chunks(mydir):
        for f in os.listdir(mydir):
            os.remove(os.path.join(mydir, f))

    def get_audio_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        audio_file_name = ''
        try:
            audio_file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                       "Audio Files ( *.wav)", options=options)
        except Exception as e:
            print('get file abortado')
            print(str(e))
        return audio_file_name


class TextToAudioProcessingThreadClass(QWidget, Thread):

    def __init__(self):
        super().__init__()
        Thread.__init__(self)

    def run(self):
        print('Empezando hilo..')
        file_name = self.get_text_file()
        if file_name.endswith('.pdf'):
            t = threading.Thread(target=self.pdf_file_to_mp3(file_name))
            t.start()
        elif file_name.endswith('.txt'):
            t = threading.Thread(target=self.txt_file_to_mp3(file_name))
            t.start()
        elif file_name.endswith('.docx'):
            t = threading.Thread(target=self.docx_file_to_mp3(file_name))
            t.start()

    def get_text_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_name = ''
        try:
            file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                       "Text Files (*.pdf *.txt *.docx)", options=options)
        except Exception as e:
            print('get file abortado')
            print(str(e))
        return file_name

    # this method creates the file object, extracts the text from the pdf file and creates the mp3 file
    def pdf_file_to_mp3(self, path):
        pdf = open(path, 'rb')
        pdf_reader = PyPDF2.PdfFileReader(pdf)
        numero_paginas = pdf_reader.getNumPages()
        if numero_paginas > 5:
            self.threadShowTextFileDialog()
        else:
            print('generando archivo de audio pdf...')
            text = ''
            if numero_paginas > 1:
                for i in range(numero_paginas):
                    text += pdf_reader.getPage(i).extractText()
            else:
                text = pdf_reader.getPage(0).extractText()
            try:
                print(text)
                file_to_save = gTTS(text, lang='es-us')
                file_to_save.save(path[0:-3] + 'mp3')
                print('archivo mp3 generado!!!')
            except Exception as e:
                print(str(e))
                self.threadErrorDialog()

    # this method creates the file object, extracts the text from the .txt file and creates the mp3 file
    def txt_file_to_mp3(self, path):
        try:
            with open(path, 'r') as file:
                my_text = file.read().replace('\n', '')
            print('generando archivo de audio txt...')
            print(my_text)
            output = gTTS(text=my_text, lang='es-us')
            output.save(path[0:-3] + 'mp3')
            print('archivo mp3 generado!!!')
        except Exception as e:
            print(str(e))
            self.threadErrorDialog()

    # el modulo no sirve en el tiempo de desarrollo del proyecto
    def docx_file_to_mp3(self, path):
        try:
            print('procesando docmento')
            document = Document(path)
            parrafos = document.paragraphs
            whole_text = ''
            for i in parrafos:
                whole_text += i.text
                print(i.text)
            output = gTTS(text=whole_text, lang='es-us')
            output.save(path[0:-4] + 'mp3')
            print('archivo mp3 generado!!!')
        except Exception as e:
            print(str(e))
            self.threadErrorDialog()

    # this function shows a dialog saying the pdf document contains too many pages
    def showTextFileDialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("este documento es muy grande, intenta con otro.")
        msg.setWindowTitle("Demasiadas páginas")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        msg.show()
        msg.exec_()

    def threadShowTextFileDialog(self):
        t = threading.Thread(target=self.showTextFileDialog())
        t.start()

    # this method displays a dialog in case an error has ocurred
    def errorDialog(self):
        msg = QMessageBox()
        msg.setWindowTitle('Oh no!!')
        msg.setIcon(QMessageBox.Critical)
        msg.setText('Ha ocurrido un error, Comprueba tu conexión a internet.')
        msg.setInformativeText('Esta aplicación necesita una conexión a internet para funcionar')
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        msg.show()
        msg.exec_()

    def threadErrorDialog(self):
        t = threading.Thread(target=self.errorDialog())
        t.start()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    app.exec_()
