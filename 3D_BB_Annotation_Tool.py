#!/usr/bin/env python
 
import sys
import matlab.engine # It is interesting an error happened if import matlab.engine later than xxx
import vtk,itk
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QWidget, QPushButton, QFileDialog, QLabel, QSlider, QComboBox
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import os
import numpy as np
import sys
from vtk.util import numpy_support
import glob
import pdb

def drawBB(volMat, array):
    revisedVolMat = np.copy(volMat)
    if len(array)==0:
        return revisedVolMat
    else:
        c = 1
        bb = array
        bb[0] = min(bb[0],volMat.shape[0]-1)
        bb[1] = min(bb[1],volMat.shape[1]-1)
        bb[2] = min(bb[2],volMat.shape[2]-1)
        bb[3] = min(bb[3],volMat.shape[0]-bb[0]-1)
        bb[4] = min(bb[4],volMat.shape[1]-bb[1]-1)
        bb[5] = min(bb[5],volMat.shape[2]-bb[2]-1)
        #volMat[bb[0],bb[1],bb[2]:bb[2]+bb[5]] = i
        
        revisedVolMat[bb[0],bb[1],bb[2]:bb[2]+bb[5]] = c
        revisedVolMat[bb[0],bb[1]+bb[4],bb[2]:bb[2]+bb[5]] = c
        revisedVolMat[bb[0]+bb[3],bb[1],bb[2]:bb[2]+bb[5]] = c
        revisedVolMat[bb[0]+bb[3],bb[1]+bb[4],bb[2]:bb[2]+bb[5]] = c

        revisedVolMat[bb[0]:bb[0]+bb[3],bb[1],bb[2]] = c
        revisedVolMat[bb[0]:bb[0]+bb[3],bb[1]+bb[4],bb[2]] = c
        revisedVolMat[bb[0]:bb[0]+bb[3],bb[1],bb[2]+bb[5]] = c
        revisedVolMat[bb[0]:bb[0]+bb[3],bb[1]+bb[4],bb[2]+bb[5]] = c

        revisedVolMat[bb[0],bb[1]:bb[1]+bb[4],bb[2]] = c
        revisedVolMat[bb[0]+bb[3],bb[1]:bb[1]+bb[4],bb[2]] = c
        revisedVolMat[bb[0],bb[1]:bb[1]+bb[4],bb[2]+bb[5]] = c
        revisedVolMat[bb[0]+bb[3],bb[1]:bb[1]+bb[4],bb[2]+bb[5]] = c
    return revisedVolMat
 
class MainWindow(QtWidgets.QMainWindow):
 
    def __init__(self,parent = None):
        
        QtWidgets.QMainWindow.__init__(self, parent)
        self.frame = QtWidgets.QFrame()
 
        self.vl = QtWidgets.QGridLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.labelComboBox = QComboBox()
        self.labelComboBox.addItems(['binocular','ipod','glock'])
        
        self.saveButton = QPushButton('Save')
        self.saveButton.clicked.connect(self.clickSaveMethod)
        self.nextImageButton = QPushButton('Next Image')
        self.nextImageButton.clicked.connect(self.clickNextImageMethod)
        self.tipnameLabel = QLabel()
        ################# Create sliders ###############33
        self.x1Slider = QSlider(Qt.Horizontal)
        self.x1Slider.valueChanged.connect(self.x1SliderValueChanged)
        self.x2Slider = QSlider(Qt.Horizontal)
        self.x2Slider.valueChanged.connect(self.x2SliderValueChanged)
        self.y1Slider = QSlider(Qt.Horizontal)
        self.y1Slider.valueChanged.connect(self.y1SliderValueChanged)
        self.y2Slider = QSlider(Qt.Horizontal)
        self.y2Slider.valueChanged.connect(self.y2SliderValueChanged)
        self.z1Slider = QSlider(Qt.Horizontal)
        self.z1Slider.valueChanged.connect(self.z1SliderValueChanged)
        self.z2Slider = QSlider(Qt.Horizontal)
        self.z2Slider.valueChanged.connect(self.z2SliderValueChanged)
        
        self.vl.setRowStretch(0,2)
        self.vl.addWidget(self.vtkWidget,0,0,1,3)
        self.vl.addWidget(self.labelComboBox,1,2)

        self.vl.addWidget(self.saveButton,2,2)
        self.vl.addWidget(self.nextImageButton,3,2)
        self.vl.addWidget(self.tipnameLabel,4,0,1,3)
        
        self.vl.addWidget(self.x1Slider,1,0)
        self.vl.addWidget(self.x2Slider,1,1)
        self.vl.addWidget(self.y1Slider,2,0)
        self.vl.addWidget(self.y2Slider,2,1)
        self.vl.addWidget(self.z1Slider,3,0)
        self.vl.addWidget(self.z2Slider,3,1)
        self.ren = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.ren)
        self.iren = self.vtkWidget.GetRenderWindow().GetInteractor()
 

        # Create a mapper
        # mapper = vtk.vtkPolyDataMapper()
        # mapper.SetInputConnection(source.GetOutputPort())
        # set volumeMapper
        self.mapper = vtk.vtkGPUVolumeRayCastMapper()

        # Create an actor
        # actor = vtk.vtkActor()
        # actor.SetMapper(mapper)
 
        # self.ren.AddActor(actor)
        # set volumeProperty
        self.volumeProperty = vtk.vtkVolumeProperty()
        # set opacity
        compositeOpacity = vtk.vtkPiecewiseFunction()
        compositeOpacity.AddPoint(0.0, 0.0)
        compositeOpacity.AddPoint(0.05, 0.01)
        compositeOpacity.AddPoint(0.1, 0.05)
        compositeOpacity.AddPoint(0.2, 0.3)
        compositeOpacity.AddPoint(0.4, 0.5)
        compositeOpacity.AddPoint(1, 0.8)
        self.volumeProperty.SetScalarOpacity(compositeOpacity)
        # set color
        color = vtk.vtkColorTransferFunction()
        color.SetColorSpaceToRGB()
        color.AddRGBPoint(0.1, 0.8, 0.5, 0.3)
        color.AddRGBPoint(0.13, 0.5, 0.5, 0.0)
        color.AddRGBPoint(0.15, 0.1, 0.7, 0.0)
        color.AddRGBPoint(0.17, 0.0, 0.8, 0.0)        
        color.AddRGBPoint(0.20, 0.0, 0.7, 0.1)
        color.AddRGBPoint(0.3, 0.0, 0.4, 0.1)
        color.AddRGBPoint(0.4, 0, 0.0, 0.5)
        color.AddRGBPoint(0.8, 0, 0.0, 0.5)
        color.AddRGBPoint(1, 0, 0, 0.8)
        self.volumeProperty.SetColor(color)
        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)
 
        fileName = self.openFileNameDialog()
        tip_path, this_file = os.path.split(fileName)
        fileName = os.path.join(tip_path,this_file) # \\ and /
        self.allImgs = glob.glob(os.path.join(tip_path,'*.img'))
        self.allImgs.sort()
        index = 0

        while self.allImgs[index]!=fileName:
            index+=1
        self.index = index-1
        self.annotated = False
        self.clickNextImageMethod()
        self.show()
        self.iren.Initialize()                 

    def clickNextImageMethod(self):
        if self.index<len(self.allImgs)-1:
            self.index += 1
            self.arrayBB = [20,20,20,20,20,20]
            self.imgfilename = self.allImgs[self.index]
            _, self.displayName = os.path.split(self.imgfilename)
            pdb.set_trace()
            itkReader = itk.ImageFileReader.New(FileName = self.imgfilename)
            itkReader.Update()
            self.volMat = itk.GetArrayFromImage(itkReader.GetOutput())
            self.x1Slider.setMaximum(self.volMat.shape[0])
            self.x2Slider.setMaximum(self.volMat.shape[0])
            self.y1Slider.setMaximum(self.volMat.shape[1])
            self.y2Slider.setMaximum(self.volMat.shape[1])
            self.z1Slider.setMaximum(self.volMat.shape[2])
            self.z2Slider.setMaximum(self.volMat.shape[2])
            self.refreshView()
        else:
            self.tipnameLabel.setText('This is the last image!')
        
    def clickSaveMethod(self):
        labelFile = self.imgfilename[:-4]+'_'+self.labelComboBox.currentText()+'.txt'
        with open(labelFile,'w') as f:
            for i in range(5):
                f.write('{:d},'.format(self.arrayBB[i]))
            f.write('{:d}\n'.format(self.arrayBB[5]))
        
        
    def x1SliderValueChanged(self):
        self.arrayBB[0] = self.x1Slider.value()
        self.refreshView()
        self.annotated = True
        
    def x2SliderValueChanged(self):
        self.arrayBB[3] = self.x2Slider.value()
        self.refreshView()
        self.annotated = True
        
    def y1SliderValueChanged(self):
        self.arrayBB[1] = self.y1Slider.value()
        self.refreshView()
        self.annotated = True

    def y2SliderValueChanged(self):
        self.arrayBB[4] = self.y2Slider.value()
        self.refreshView()
        self.annotated = True
        
    def z1SliderValueChanged(self):
        self.arrayBB[2] = self.z1Slider.value()
        self.refreshView()
        self.annotated = True

    def z2SliderValueChanged(self):
        self.arrayBB[5] = self.z2Slider.value()
        self.refreshView()
        self.annotated = True

    def refreshView(self):
            # revise the voxels values to draw a bounding box
            revisedVolMat = drawBB(self.volMat,self.arrayBB)
            # write the revised volume with the bounding box
            revisedVolFilename = self.imgfilename[:-4]+'_bb.hdr'
            itk.imwrite(itk.GetImageFromArray(revisedVolMat.astype(np.float32)),revisedVolFilename)
            imgfilename = revisedVolFilename
            # read the revised volume using vtk
            # Create source
            vtkReader = vtk.vtkNIFTIImageReader()
            vtkReader.SetFileName(imgfilename)
            vtkReader.Update()
            # set a vtkvolume
            self.mapper.SetInputData(vtkReader.GetOutput())
            #self.mapper.Update()
            vtkvolume = vtk.vtkVolume()
            vtkvolume.SetMapper(self.mapper)
            vtkvolume.SetProperty(self.volumeProperty)
            # set renderer
            self.ren.SetBackground(1,1,1)
            self.ren.AddVolume(vtkvolume)
            self.ren.ResetCamera()
            #self.ren.GetActiveCamera().Zoom(1.5)

            self.tipnameLabel.setText(self.displayName)
            self.frame.setLayout(self.vl)
            self.setCentralWidget(self.frame)
        
            self.show()
            self.iren.Initialize()
        
    def openFileNameDialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "/mnt/HD2T/3D_ObjectDetection/PR2015Dataset/test","All Files (*);;Python Files (*.py)", options=options)
        return fileName

if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
 
    window = MainWindow()
 
    sys.exit(app.exec_())
