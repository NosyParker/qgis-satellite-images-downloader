from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import *
from qgis.gui import *
from qgis.utils import *
from qgis.core import *

from .globals import AOI_COORDINATES
import datetime

class CaptureCoordinates(QgsMapToolEmitPoint):
    canvasDoubleClicked = QtCore.pyqtSignal(object, object)

    def __init__(self, canvas, textEdit, layer=None, source_crs=None, destination_crs=None):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.textEdit = textEdit
        self.layer = layer
        self.setCursor(Qt.CrossCursor)
        self.source_crs = source_crs
        self.destination_crs = destination_crs
        self.rubberBand = QgsRubberBand(self.canvas, QgsWkbTypes.geometryType(QgsWkbTypes.Polygon))
        self.rubberBand.setColor(QColor("transparent"))
        self.rubberBand.setWidth(2)
        # self.rubberBand.setIcon(QgsRubberBand.ICON_FULL_DIAMOND)
        # self.rubberBand.setIconSize(75)
        # self.rubberBand.setBrushStyle(QBrush(Qt.FDiagPattern))
        self.rubberBand.setStrokeColor(Qt.red)
        self.reset()

    def reset(self):
        self.rubberBand.reset(QgsWkbTypes.geometryType(QgsWkbTypes.Polygon))


    def transformCRS(self):
        return QgsCoordinateTransform(QgsCoordinateReferenceSystem(self.source_crs),
                    QgsCoordinateReferenceSystem(self.destination_crs), 
                    QgsProject.instance())


    def canvasPressEvent(self, event):
        if event.button() == Qt.LeftButton:
            transform = self.transformCRS()
            point = self.toLayerCoordinates(self.layer, event.pos())
            self.rubberBand.addPoint(point,True)
            self.rubberBand.show()
            tr_point = transform.transform(point)
            AOI_COORDINATES.append([round(tr_point.x(), 7), round(tr_point.y(), 7)])
        elif event.button() == Qt.RightButton:
            self.reset()
            AOI_COORDINATES.clear()


    def canvasDoubleClickEvent(self, event):
        # self.reset()
        # AOI_COORDINATES.clear()
        if not self.rubberBand.asGeometry().isGeosValid():
            self.textEdit.appendPlainText("["+str(datetime.datetime.now().strftime ("%H:%M:%S")) + "]" +" ВНИМАНИЕ: Не валидный полигон! Дальнейший поиск будет осуществляться без учета выбранной территории")
        
        self.canvas.unsetMapTool(self)

