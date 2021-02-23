from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import requests


def get_airfoil_coords(airfoil: str) -> tuple:
    """
    Get airfoild coords from UIUC website
    https://m-selig.ae.illinois.edu/ads/cood/__.dat
    :param airfoil:
    :return: tuple of ([x coords], [y coords], plot_title)
    """
    try:
        url = 'https://m-selig.ae.illinois.edu/ads/coord/{}.dat'.format(airfoil.lower())
        response_text = requests.get(url).text
        if 'Not Found' in response_text:
            return 0, 0, "Airfoil not found in UIUC database"

        all_text = response_text.split('\n')
        x_coordinates, y_coordinates = [], []
        plot_title = ''

        for index, line in enumerate(all_text):
            if index == 0:
                plot_title = line.strip()
            else:
                try:
                    line = line.strip()
                    x, y = line.split(' ' * line.count(' '))
                    x = float(x.strip())
                    y = float(y.strip())
                    if x <= 1 and y <= 1:
                        x_coordinates.append(x)
                        y_coordinates.append(y)
                except ValueError:
                    continue

        return x_coordinates, y_coordinates, plot_title
    except requests.ConnectionError:
        return 0, 0, "Can't connect to UIUC database"


class MatplotlibWidget(QMainWindow):

    def __init__(self):
        QMainWindow.__init__(self)

        loadUi("qt_designer.ui", self)

        self.setWindowTitle("Airfoil Plotter")

        self.plotAirfoilButton.clicked.connect(self.update_graph)

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

        self.lineEdit.textEdited.connect(self.process)

    def process(self):
        self.airfoilName = self.lineEdit.text()

    def update_graph(self):
        [xVal, yVal, plotTitle] = get_airfoil_coords(self.airfoilName)

        self.MplWidget.canvas.axes.clear()
        self.MplWidget.canvas.axes.plot(xVal, yVal)
        self.MplWidget.canvas.axes.set_xlim(-0.5, 1.25)
        self.MplWidget.canvas.axes.set_ylim(-1, 1)
        self.MplWidget.canvas.axes.set_title(plotTitle)
        self.MplWidget.canvas.draw()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
