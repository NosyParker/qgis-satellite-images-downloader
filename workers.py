from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication
from satsearch import Search
import datetime
import dateutil
import os

class DownloadWorker(QThread):
    
    data_downloaded = QtCore.pyqtSignal(object)
    work_finished = QtCore.pyqtSignal(object)

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

            if scene['collection'] == 'sentinel-2-l1c':
                scene_id = scene['sentinel:product_id']
            elif scene['collection'] == 'landsat-8-l1':
                scene_id = scene['landsat:product_id']
            date_time = dateutil.parser.parse(scene['datetime']).strftime ("%Y-%m-%d")

            for key in self.filekeys:

                self.data_downloaded.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" +" Загружается файл (канал) " + str(key) + " для сцены " + str(scene_id))

                filename = scene.download(key=key, path = f"{self.path}/{scene['collection']}/{date_time}")

                self.data_downloaded.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "] " + str(key) + " для сцены " + str(scene_id) + " был загружен и сохранен как " + str(filename))

                if not self.isRunning:
                    breaker = True
                    break
            if breaker:
                break
        self.work_finished.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" + " Загрузка завершена!")
    
    
    def stop(self):
        self.isRunning = False


    def __del__(self):
        self.wait()

