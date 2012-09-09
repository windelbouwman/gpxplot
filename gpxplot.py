from PyQt4.QtCore import *
from PyQt4.QtGui import *
import pyqtgraph, gpxpy, numpy, sys

class TrackModel(QAbstractListModel):
    def __init__(self):
        QAbstractListModel.__init__(self)
        self.tracks = []
        self.doFillModel()
    def doFillModel(self):
        """ Loads all gpx files in the current directory. """
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
    def data(self, idx, role):
        track = self.tracks[idx.row()]
        if role == Qt.DisplayRole:
            return track.filename
        elif role == Qt.CheckStateRole:
            return Qt.Checked if track.plot else Qt.Unchecked
        return QVariant()
    def setData(self, idx, value, role):
        if role == Qt.CheckStateRole:
            track = self.tracks[idx.row()]
            track.plot = value.toBool()
            self.dataChanged.emit(idx, idx)
            return True
        return QAbstractListModel.setData(self, idx, value, role)
    def flags(self, idx):
        return QAbstractListModel.flags(self, idx) | Qt.ItemIsUserCheckable
    
class GpxPlot(QWidget):
    def __init__(self):
        QWidget.__init__(self, None)
        l = QVBoxLayout(self)
        self.plotWidget = pyqtgraph.PlotWidget()
        l.addWidget(self.plotWidget)
        self.tableView = QListView()
        l.addWidget(self.tableView)

        self.trackModel = TrackModel()
        self.tableView.setModel(self.trackModel)
        self.trackModel.dataChanged.connect(self.updatePlots)
        
    def updatePlots(self, topLeft, bottomRight):
        pi = self.plotWidget.getPlotItem()
        pi.clear()
        pi.setLabel('bottom', text='Time', units='s')
        pi.setLabel('left', text='Distance', units='m')

        # Select the tracks to plot:
        for gpx in self.trackModel.tracks:
            if gpx.plot:
                tracks = [track for track in gpx.tracks if track.length_2d() > 0]
                seg = tracks[0].segments[0]
                self.plotPoints(seg.points)
                                
    def plotPoints(self, pts):
        t0, prev = pts[0].time, pts[0]
        t, d  = [], []
        for pt in pts:
            t.append((pt.time - t0).total_seconds())
            d.append(pt.distance_3d(prev))
            prev = pt
        x, y = numpy.array(t), numpy.array(d).cumsum()
        pi = self.plotWidget.getPlotItem()
        pen = pyqtgraph.mkPen({'color': "r", 'width': 2})
        pi.plot(x, y, pen=pen)

app = QApplication(sys.argv)
gp = GpxPlot()
gp.show()
app.exec_()
