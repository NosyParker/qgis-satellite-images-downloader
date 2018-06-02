from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from satsearch.search import Search, Query
from satsearch.scene import Scenes
import datetime

class DownloadWorker(QThread):
    
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, scenes = None, filekeys=None, path = None, **kwargs):
        super(DownloadWorker, self).__init__()
        if scenes is not None:
            self.scenes = scenes
        else:
            self.scenes = []
        if filekeys is not None:
            self.filekeys = filekeys
        else:
            self.filekeys = []
        self.kwargs = kwargs
        self.running = True
        self.path = path
        self.isRunning = True


    def run(self):
        if not self.isRunning:
            self.isRunning = True
        
        if self.scenes == [] or self.scenes == None:
            self.data_downloaded.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" +" Отсутствуют сцены к загрузке")
            self.__del__()
        if self.filekeys == [] or self.filekeys == None:
            self.data_downloaded.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" +" Не выбран ни один файл к загрузке")
            self.__del__()

        breaker = False
        for scene in self.scenes:
            for key in self.filekeys:
                self.data_downloaded.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" +" Загружается файл (канал) " + str(key) + " для сцены " + str(scene.product_id))
                scene.download(key=key, path = self.path)
                if not self.isRunning:
                    breaker = True
                    break
            if breaker:
                break
        self.data_downloaded.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" + " Загрузка завершена!")
    
    
    def stop(self):
        self.isRunning = False


    def __del__(self):
        self.wait()

