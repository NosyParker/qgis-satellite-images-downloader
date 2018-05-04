from PyQt5.QtCore import *
from qgis.gui import *
from qgis.utils import *
from qgis.core import*

from .globals import AOI_COORDINATES

class CaptureCoordinates(QgsMapTool):
    def __init__(self, canvas, textEdit, layer=None, source_crs=None, destination_crs=None):
        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
        self.textEdit = textEdit
        self.layer = layer
        self.setCursor(Qt.CrossCursor)
        self.source_crs = source_crs
        self.destination_crs = destination_crs

    def transformCRS(self):
        return QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.source_crs),
                    QgsCoordinateReferenceSystem(self.destination_crs), 
                    QgsProject.instance())


    def canvasReleaseEvent(self, event):
        transform = self.transformCRS()
        point = self.toLayerCoordinates(self.layer, event.pos())
        tr_point = transform.transform(point)
        AOI_COORDINATES.append([round(tr_point.x(), 7), round(tr_point.y(), 7)])
