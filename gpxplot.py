import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import pyqtgraph
import gpxpy
import numpy

class TrackModel(QAbstractTableModel):
    headers = ["Name"]
    def __init__(self):
        QAbstractTableModel.__init__(self)
        self.tracks = []
        d = QDir()
        for fn in d.entryList(["*.gpx"]):
            fn = str(fn)
            with open(fn, 'r') as f:
                gpx = gpxpy.parse(f)
            gpx.filename = fn
            gpx.plot = False
            self.tracks.append(gpx)
        
    def rowCount(self, parent=None):
        return len(self.tracks)
    def columnCount(self, parent=None):
        return len(self.headers)
    def data(self, idx, role):
        if idx.column() == 0:
            track = self.tracks[idx.row()]
            if role == Qt.DisplayRole:
                return track.filename
            elif role == Qt.CheckStateRole:
                return Qt.Checked if track.plot else Qt.Unchecked
        return QVariant()
    def setData(self, idx, value, role):
        if idx.column() == 0 and role == Qt.CheckStateRole:
            track = self.tracks[idx.row()]
            track.plot = value.toBool()
            self.dataChanged.emit(idx, idx)
            return True
        return QAbstractTableModel.setData(self, idx, value, role)
    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
    def flags(self, idx):
        if idx.column() == 0:
            return QAbstractTableModel.flags(self, idx) | Qt.ItemIsUserCheckable
        return QAbstractTableModel.flags(self, idx)
    
class GpxPlot(QWidget):
    def __init__(self):
        QWidget.__init__(self, None)
        l = QVBoxLayout(self)
        self.plotWidget = pyqtgraph.PlotWidget()
        l.addWidget(self.plotWidget)
        self.tableView = QTableView()
        l.addWidget(self.tableView)

        self.trackModel = TrackModel()
        self.tableView.setModel(self.trackModel)
        self.trackModel.dataChanged.connect(self.updatePlots)
        
    def updatePlots(self, topLeft, bottomRight):
        pi = self.plotWidget.getPlotItem()
        pi.clear()

        # Select the tracks to plot:
        for gpx in self.trackModel.tracks:
            if gpx.plot:
                tracks = [track for track in gpx.tracks if track.length_2d() > 0]
                seg = tracks[0].segments[0]
                self.plotPoints(seg.points)
                                
    def plotPoints(self, pts):
        t0 = pts[0].time
        prev = pts[0]
        t, d  = [], []
        for pt in pts:
            t.append((pt.time - t0).total_seconds())
            d.append(pt.distance_3d(prev))
            prev = pt
        x, y = numpy.array(t), numpy.array(d)
        pi = self.plotWidget.getPlotItem()
        pen = pyqtgraph.mkPen({'color': "r", 'width': 2})
        pi.plot(x, y, pen=pen)

app = QApplication(sys.argv)
gp = GpxPlot()
gp.show()
app.exec_()
