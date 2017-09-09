import os, sys
import unittest
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
import logging
import shutil

#
# Groups
#

class Groups(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Groups"  # TODO make this more human readable by adding spaces
        self.parent.categories = ["Quantification"]
        self.parent.dependencies = []
        self.parent.contributors = ["Mahmoud Mostapha (UNC), Ilwoo Lyu (UNC)"]
        self.parent.helpText = """
        ...
    """
        self.parent.acknowledgementText = """
        ...
    """  # replace with organization, grant and thanks.


#
# GroupsWidget
#

class GroupsWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)

        ###################################################################
        ##                                                               ##
        ##  Collapsible part for input/output parameters for Groups CLI  ##
        ##                                                               ##
        ###################################################################

        self.ioCollapsibleButton = ctk.ctkCollapsibleButton()
        self.ioCollapsibleButton.text = "IO"
        self.layout.addWidget(self.ioCollapsibleButton)
        self.ioQVBox = qt.QVBoxLayout(self.ioCollapsibleButton)

        # --------------------------------- #
        # ----- Group Box DIRECTORIES ----- #
        # --------------------------------- #
        self.directoryGroupBox = qt.QGroupBox("Groups Dircetories")
        self.ioQVBox.addWidget(self.directoryGroupBox)
        self.ioQFormLayout = qt.QFormLayout(self.directoryGroupBox)

        # Selection of the directory containing the input models (option: --surfaceDir) and option procalign shape
        self.inputMeshTypeHBox = qt.QVBoxLayout(self.directoryGroupBox)
        self.inputModelsDirectorySelector = ctk.ctkDirectoryButton()
        
        self.inputMeshTypeHBox.addWidget(self.inputModelsDirectorySelector)
        self.ioQFormLayout.addRow(qt.QLabel("Input Models Directory:"), self.inputMeshTypeHBox)

        # Selection of the directory which contains each spherical model (option: --sphereDir)
        self.sphericalModelsDirectorySelector = ctk.ctkDirectoryButton()
        self.ioQFormLayout.addRow("Spherical Models Directory:", self.sphericalModelsDirectorySelector)

        # Selection of the output directory for Groups (option: --outputDir)
        self.outputDirectorySelector = ctk.ctkDirectoryButton()
        self.ioQFormLayout.addRow(qt.QLabel("Output Directory:"), self.outputDirectorySelector)

        # CheckBox. If checked, Group Box 'Parameters' will be enabled
        self.enableRigidAlignmentCB = ctk.ctkCheckBox()
        self.enableRigidAlignmentCB.setText("Perform Rigid Alignment")
        self.ioQFormLayout.addRow(self.enableRigidAlignmentCB)

        # CheckBox. If checked, Group Box 'Parameters' will be enabled
        self.enableParamCB = ctk.ctkCheckBox()
        self.enableParamCB.setText("Personalize Groups parameters")
        self.ioQFormLayout.addRow(self.enableParamCB)

        # Connections
        self.inputModelsDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
        self.sphericalModelsDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
        self.outputDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
        self.enableRigidAlignmentCB.connect("stateChanged(int)", self.onCheckBoxRigidAlignment)
        self.enableParamCB.connect("stateChanged(int)", self.onCheckBoxParam)

        # Name simplification (string)
        self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
        self.sphericalmodelsDirectory = str(self.sphericalModelsDirectorySelector.directory)
        self.outputDirectory = str(self.outputDirectorySelector.directory)


        # ------------------------------------------ #
        # ----- RigidAlignment Box DIRECTORIES ----- #
        # ------------------------------------------ #

        self.rigidalignmentdirectoryGroupBox = qt.QGroupBox("Rigid Alignment Directories")
        self.ioQVBox.addWidget(self.rigidalignmentdirectoryGroupBox)
        self.ioQFormLayout = qt.QFormLayout(self.rigidalignmentdirectoryGroupBox)
        self.rigidalignmentdirectoryGroupBox.setEnabled(False)

        # Selection of the directory which contains each landmark fcsv file (option: --landmark)
        self.inputlandmarksfiducialfilesDirectorySelector = ctk.ctkDirectoryButton()
        self.ioQFormLayout.addRow("Input Landmarks Fiducial Files Directory:", self.inputlandmarksfiducialfilesDirectorySelector)

        # Selection of the directory which contains common unit sphere file (option: --sphere)
        self.inputunitspherefileDirectorySelector = ctk.ctkDirectoryButton()
        self.ioQFormLayout.addRow("Input Unit Sphere File Directory:", self.inputunitspherefileDirectorySelector)

        # Connections
        self.inputlandmarksfiducialfilesDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)
        self.inputunitspherefileDirectorySelector.connect("directoryChanged(const QString &)", self.onSelect)

        # Name simplification (string)
        self.landmarksDirectory = str(self.inputlandmarksfiducialfilesDirectorySelector.directory)
        self.sphereDirectory = str(self.inputunitspherefileDirectorySelector.directory)

        # -------------------------------- #
        # ----- Group Box PARAMETERS ----- #
        # -------------------------------- #
        self.parametersGroupBox = qt.QGroupBox("Groups Parameters")
        self.ioQVBox.addWidget(self.parametersGroupBox)
        self.paramQFormLayout = qt.QFormLayout(self.parametersGroupBox)
        self.parametersGroupBox.setEnabled(False)

        # Selection of the property we want to use 
        self.specifyPropertySelector = ctk.ctkCheckableComboBox()
        self.specifyPropertySelector.addItems(("Curvedness","Shape_Index"))
        self.paramQFormLayout.addRow(qt.QLabel("Properties name to use:"), self.specifyPropertySelector)

        # Weights of each property - Choices on 1 lines 
        self.weightLayout = qt.QVBoxLayout(self.parametersGroupBox)
        self.weightline1 = qt.QHBoxLayout(self.parametersGroupBox)  # Line 1
        self.weightLayout.addLayout(self.weightline1)

        # Fill out first line
        self.labelCurvedness = qt.QLabel("Curvedness")
        self.weightline1.addWidget(self.labelCurvedness)
        self.weightCurvedness = ctk.ctkDoubleSpinBox()
        self.weightCurvedness.enabled = False
        self.weightCurvedness.value = 1
        self.weightline1.addWidget(self.weightCurvedness)

        self.labelShape_Index = qt.QLabel(" Shape_Index")
        self.weightline1.addWidget(self.labelShape_Index)
        self.weightShape_Index = ctk.ctkDoubleSpinBox()
        self.weightShape_Index.enabled = False
        self.weightShape_Index.value = 1
        self.weightline1.addWidget(self.weightShape_Index)

        self.paramQFormLayout.addRow("Weight of each property:", self.weightLayout)

        # CheckBox. If checked, Landmarks enabled
        self.enableLandmarks = ctk.ctkCheckBox()
        self.enableLandmarks.setText("Enable Landmarks")
        self.paramQFormLayout.addRow(self.enableLandmarks)

        # Specification of the SPHARM decomposition degree (option: -d)
        self.degreeSpharm = ctk.ctkSliderWidget()
        self.degreeSpharm.minimum = 0
        self.degreeSpharm.maximum = 50
        self.degreeSpharm.value = 5        # initial value
        self.degreeSpharm.setDecimals(0)
        self.paramQFormLayout.addRow(qt.QLabel("Degree of SPHARM decomposition:"), self.degreeSpharm)

        # Maximum iteration (option: --maxIter)
        self.maxIter = qt.QSpinBox()
        self.maxIter.minimum = 0            # Check the range authorized
        self.maxIter.maximum = 100000
        self.maxIter.value = 5000
        self.paramQFormLayout.addRow("Maximum number of iteration:", self.maxIter)


        # Name simplification
        self.property = ""
        self.propertyValue = ""

        # Connections
        self.specifyPropertySelector.connect("checkedIndexesChanged()", self.onSpecifyPropertyChanged)

        # ------------------------------------------ #
        # ----- Apply button to launch the CLI ----- #
        # ------------------------------------------ #
        self.applyButton = qt.QPushButton("Apply")
        self.applyButton.enabled = False
        self.ioQVBox.addWidget(self.applyButton)

        self.errorLabel = qt.QLabel("Error: Invalide inputs")
        self.errorLabel.hide()
        self.errorLabel.setStyleSheet("color: rgb(255, 0, 0);")
        self.ioQVBox.addWidget(self.errorLabel)

        # Connections
        self.applyButton.connect('clicked(bool)', self.onApplyButtonClicked)

        # ----- Add vertical spacer ----- #
        self.layout.addStretch(1)



    ## Function cleanup(self):
    def cleanup(self):
        pass

    ## Function onSelect(self):
    # Check if each directory (Models, Property, Sphere and Output) have been chosen.
    # If they were, Apply button is enabled to call the CLI
    # Update the simplified names
    def onSelect(self):
        # Update names
        self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
        self.sphereDirectory = str(self.sphericalModelsDirectorySelector.directory)
        self.outputDirectory = str(self.outputDirectorySelector.directory)

        # Check if each directory has been choosen
        self.applyButton.enabled = self.modelsDirectory != "." and self.outputDirectory != "." and self.sphereDirectory != "."

        # Hide error message if printed
        self.errorLabel.hide()

    ## Function onSpecifyPropertyChanged(self):
    # Enable/Disable associated weights
    def onSpecifyPropertyChanged(self):
        if self.specifyPropertySelector.currentIndex == 0:
            self.weightCurvedness.enabled = not self.weightCurvedness.enabled

        if self.specifyPropertySelector.currentIndex == 1:
            self.weightShape_Index.enabled = not self.weightShape_Index.enabled

    ## Function onCheckBoxParam(self):
    # Enable the parameter Group Box if associated check box is checked
    def onCheckBoxRigidAlignment(self):
        if self.enableRigidAlignmentCB.checkState():
            self.rigidalignmentdirectoryGroupBox.setEnabled(True)
        else:
            self.rigidalignmentdirectoryGroupBox.setEnabled(False)

    def onCheckBoxParam(self):
        if self.enableParamCB.checkState():
            self.parametersGroupBox.setEnabled(True)
        else:
            self.parametersGroupBox.setEnabled(False)


    ## Function onApplyButtonClicked(self):
    # Update every parameters to call Groups
    # Check maxIter is an integer
    # Check if parameters group box enabled
    def onApplyButtonClicked(self):
        logic = GroupsLogic()

        self.errorLabel.hide()
        # Update names
        self.modelsDirectory = str(self.inputModelsDirectorySelector.directory)
        self.sphereDirectory = str(self.sphericalModelsDirectorySelector.directory)
        self.outputDirectory = str(self.outputDirectorySelector.directory)

        if not self.enableParamCB.checkState():
            endGroup = logic.runGroups(modelsDir=self.modelsDirectory, sphereDir=self.sphereDirectory, outputDir=self.outputDirectory)

        else:
            # ----- Creation of string for the specified properties and their values ----- #

            if self.weightCurvedness.enabled:
                self.CurvednessValue = self.weightCurvedness.value
                self.Curvedness = 1
            else:
                self.CurvednessValue = self.weightCurvedness.value
                self.Curvedness = 0


            if self.weightShape_Index.enabled:
                self.Shape_IndexValue = self.weightShape_Index.value
                self.Shape_Index = 1
            else:
                self.CurvednessValue = self.weightCurvedness.value
                self.Curvedness = 0

            d = int(self.degreeSpharm.value)
            m = int(self.maxIter.value)

            endGroup = logic.runGroups(modelsDir = self.modelsDirectory, sphereDir = self.sphereDirectory, outputDir = self.outputDirectory, 
                                    CurvednessOn = self.Curvedness, CurvednessWeight = self.CurvednessValue, Shape_IndexOn = self.Shape_Index, Shape_IndexWeight = self.Shape_IndexValue, Landmarks=self.enableLandmarks.checkState(), degree = d, maxIter = m)

        ## Groups didn't run because of invalid inputs
        if not endGroup:
            self.errorLabel.show()

#
# GroupsLogic
#

class GroupsLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

    ## Function runGroups(...)
    #   Check if directories are ok
    #   Create the command line
    #   Call the CLI Groups
    def runGroups(self, modelsDir, propertyDir, sphereDir, outputDir, CurvednessOn = 0, CurvednessWeight = 0, Shape_IndexOn = 0, Shape_IndexWeight = 0, Landmarks=0, degree = 0, maxIter = 0):
        print "--- function runGroups() ---"

        """
        Calling Groups CLI
            Arguments:
             --surfaceDir: Directory with input models
             --sphereDir: Sphere folder
             --outputDir: Output directory
             --CurvednessOn 
             --CurvednessWeight  
             --Shape_IndexOn 
             --Shape_IndexWeight  
             --landmarksOn
             -d: Degree of deformation field
             --maxIter: Maximum number of iteration
        """
        # Groups Build Directory
        groups = "/Users/prisgdd/Documents/Projects/Groups/GROUPS-build/Groups-build/bin/Groups"

        arguments = list()
        arguments.append("--surfaceDir")
        arguments.append(modelsDir)
        arguments.append("--propertyDir")
        arguments.append(propertyDir)
        arguments.append("--sphereDir")
        arguments.append(sphereDir)
        arguments.append("--outputDir")
        arguments.append(outputDir)

        if CurvednessOn and CurvednessWeight:
            arguments.append("--CurvednessOn")
            arguments.append("--CurvednessWeight")
            arguments.append(CurvednessWeight)

        if Shape_IndexOn and Shape_IndexWeight:
            arguments.append("--Shape_IndexOn")
            arguments.append("--Shape_IndexWeight")
            arguments.append(Shape_IndexWeight)

        if Landmarks:
            arguments.append("--landmarksOn")

        if degree:
            arguments.append("-d")
            arguments.append(int(degree))
        else:           # Default: degree=5
            arguments.append("-d")
            arguments.append(5)

        if maxIter:
            arguments.append("--maxIter")
            arguments.append(maxIter)
        else:           # Default: # maximum of iteration = 5000
            arguments.append("--maxIter")
            arguments.append(5000)

        ############################
        # ----- Call the CLI ----- #
        self.process = qt.QProcess()
        self.process.setProcessChannelMode(qt.QProcess.MergedChannels)

        # print "Calling " + os.path.basename(groups)
        self.process.start(groups, arguments)
        self.process.waitForStarted()
        # # print "state: " + str(self.process.state())
        self.process.waitForFinished(-1)
        # print "error: " + str(self.process.error())

        processOutput = str(self.process.readAll())
        sizeProcessOutput = len(processOutput)

        finStr = processOutput[sizeProcessOutput - 10:sizeProcessOutput]
        print "finStr : " + finStr

        print "\n\n --------------------------- \n"
        print processOutput
        print "\n\n --------------------------- \n"
        if finStr == "All done!\n":
            return True

        return False


   