#!/usr/bin/env python

import pyigtl  # pylint: disable=import-error
from time import sleep
import numpy as np
import os
from PIL import Image
from PySide2 import QtCore, QtGui, QtWidgets
from PySide2.QtCore import Qt, Signal, Slot
import sys
import vtk
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtk.util import numpy_support

class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()

        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        self.vl.addWidget(self.vtkWidget)

        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()

        conn = QtWidgets.QPushButton("Connect")
        quit = QtWidgets.QPushButton("Quit")

        # Create an actor
        actor = vtk.vtkImageActor()
        client = pyigtl.OpenIGTLinkClient(host="129.100.44.175", port=18945)

        self.ren.AddActor(actor)
        self.ren.ResetCamera()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.show()

        timestep = 0

        imdata = vtk.vtkImageData()
        imdata.SetSpacing([1, 1, 1])
        imdata.SetOrigin([0, 0, 0])

        actor.SetInputData(imdata)
        #self.iren.Initialize()

        self.vtkWidget.Initialize()
        #self.vtkWidget.Start()

        while True:
            timestep += 1
            message = client.wait_for_message("Image_Image", timeout=3)

            scalars = numpy_support.numpy_to_vtk(np.flip(message.image, axis=1).reshape(-1, 3), deep=True,
                                                 array_type=vtk.VTK_DOUBLE)
            imdata.SetDimensions(message.image.shape[2], message.image.shape[1], 1)
            imdata.GetPointData().SetScalars(scalars)

            self.vtkWidget.render(self)
            self.iren.ProcessEvents()

        sys.exit(app.exec_())


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()

    sys.exit(app.exec_())

