from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication

from satsearch import Search

import datetime
import dateutil
import os

class DownloadWorker(QThread):
    """
    Класс для реализации загрузчика эвент-эмиттера чтобы не подвешивать UI-поток
    """
    work_started = QtCore.pyqtSignal(object)
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
            self.data_downloaded.emit(f"[{str(datetime.datetime.now().strftime ('%H:%M:%S'))}] Отсутствуют сцены к загрузке")
            self.__del__()
        if self.filekeys == [] or self.filekeys == None:
            self.data_downloaded.emit(f"[{str(datetime.datetime.now().strftime ('%H:%M:%S'))}] Файлы не были выбраны для загрузки")
            self.__del__()
        
        self.work_started.emit(f"[{str(datetime.datetime.now().strftime ('%H:%M:%S'))}] Загрузка снимков вот-вот начнется...")
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

                if filename is not None:
                    info_out_str = f"[{str(datetime.datetime.now().strftime ('%H:%M:%S'))}] {str(key)} для сцены {str(scene_id)} был загружен и сохранен как {str(filename)}"
                else: 
                    info_out_str = f"[{str(datetime.datetime.now().strftime ('%H:%M:%S'))}] Не удалось загрузить {str(key)} для сцены {str(scene_id)}, т.к. на этот файл установлено ограничение на доступ источником снимков"
                self.data_downloaded.emit(info_out_str)

                if not self.isRunning:
                    breaker = True
                    break
            if breaker:
                break
        self.work_finished.emit(f"[{str(datetime.datetime.now().strftime ('%H:%M:%S'))}] Загрузка завершена!")
    
    
    def stop(self):
        self.isRunning = False


    def __del__(self):
        self.terminate()
        self.wait()



class FindWorker(QThread):
    """
    Класс для реализации поисковика эвент-эмиттера чтобы не подвешивать UI-поток
    """
    search_is_started = QtCore.pyqtSignal(object) # событие, когда происходит иинициализация поиска
    files_are_found = QtCore.pyqtSignal(int, str) # событие, когда поисковик выполнил запрос


    def __init__(self, intersects = None, time = None, query = None):
        super(FindWorker, self).__init__()
        self.intersects = intersects
        self.time = time
        self.query = query
        self.isRunning = True


    def run(self):
        if not self.isRunning:
            self.isRunning = True

        items_count = 0
        self.search_is_started.emit("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" +" Ищу...")

        # is really shit-shit code,
        # но ребятишки, сделавшие API, видимо не подумали о том, 
        # что может потребоваться передавать параметры через OR (||)
        if isinstance(self.query, dict):
            if self.intersects is not None:
                search = Search(intersects=self.intersects, time=self.time, query=self.query)
            else:
                search = Search(time=self.time, query=self.query)
            items_count = search.found()
            self.files_are_found.emit(items_count, self.query["collection"]["eq"])
        elif isinstance(self.query, list):
            for single_query in self.query:
                if self.intersects is not None:
                    search = Search(intersects=self.intersects, time=self.time, query=single_query)
                else:
                    search = Search(time=self.time, query=single_query)
                items_count += search.found()
            self.files_are_found.emit(items_count, self.query[0]["collection"]["eq"])


    def stop(self):
        self.isRunning = False


    def __del__(self):
        self.wait()