import logging
import os

import vtk

import slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import VTKObservationMixin
from vtk.util import numpy_support
import numpy as np
import numpy.matlib
import math

#
# PTL_Registration
#

def AOPA_Major(X, Y, tol):
    """
    Computes the Procrustean fiducial registration between X and Y with
    anisotropic Scaling:

        Y = R * A * X + t

    where X is a mxn matrix, m is typically 3
          Y is a mxn matrix, same dimension as X

          R is a mxm rotation matrix,
          A is a mxm diagonal scaling matrix, and
          t is a mx1 translation vector

    based on the Majorization Principle
    """
    [m, n] = X.shape
    II = np.identity(n) - np.ones((n, n)) / n
    # demean X, and Y
    # and also normalize X (by row) after demean, in matlab:
    # mX = normr(X*II); mY = Y*II
    mX = np.nan_to_num(np.matmul(X, II) / np.linalg.norm(np.matmul(X, II), ord=2, axis=1, keepdims=True))
    mY = np.matmul(Y, II)

    # estimate the initial rotation
    # B = mY*mX'; [U,~,V] = svd( B );
    B = np.matmul(mY, mX.transpose())
    u, s, vh = np.linalg.svd(B)

    # check for flip
    # D   = eye(m); D(m,m) = det(U*V'); R = U*D*V';
    D = np.identity(m)
    D[m - 1, m - 1] = np.linalg.det(np.matmul(u, vh))
    R = np.matmul(u, np.matmul(D, vh))

    # loop
    # err = +Inf; E_old = 10000*ones(m,n);
    err = np.Infinity
    E_old = 1000000 * np.ones((m, n))
    while err > tol:
        # [U,~,V] = svd( B*diag(diag(R'*B)) );
        u, s, vh = np.linalg.svd(np.matmul(B, np.diag(np.diag(np.matmul(R.transpose(), B)))))
        # R = U*[1 0 0; 0 1 0; 0 0 det(U*V')]*V';
        D[m - 1, m - 1] = np.linalg.det(np.matmul(u, vh))
        R = np.matmul(u, np.matmul(D, vh))
        # E = R*mX-mY;
        E = np.matmul(R, mX) - mY
        # err = norm( E-E_old,'fro' ); E_old = E;
        err = np.linalg.norm(E - E_old)
        E_old = E
    # after rotation is computed, compute the scale
    # B = Y*II*X'; A = diag( diag(B'*R)./diag(X*II*X') );
    B = np.matmul(Y, np.matmul(II, X.transpose()))
    A = np.diag(np.divide(np.diag(np.matmul(B.transpose(), R)), np.diag(np.matmul(X, np.matmul(II, X.transpose())))))
    if (math.isnan(A[2, 2])):
        # special case for ultrasound calibration, where z=0
        A[2, 2] = .5 * (A[0, 0] + A[1, 1])  # artificially assign a number to the scale in z-axis
    # calculate translation
    # t = mean( Y-R*A*X, 2);
    t = np.mean(Y - np.matmul(R, np.matmul(A, X)), 1)
    t = np.reshape(t, [m, 1])
    return [R, t, A]


def p2l_s(X, Y, D, tol):
    """
    Computes the Procrustean point-line registration between X and Y+nD with
    anisotropic Scaling,


    where X is a mxn matrix, m is typically 3
          Y is a mxn matrix denoting line origin, same dimension as X
          D is a mxn normalized matrix denoting line direction

          R is a mxm rotation matrix,
          A is a mxm diagonal scaling matrix, and
          t is a mx1 translation vector
          Q is a mxn fiducial on line that is closest to X after registration
          fre is the fiducial registration error

    based on the Majorization Principle
    """

    [m, n] = X.shape
    err = np.Infinity
    E_old = 1000000 * np.ones((m, n))
    e = np.ones((1, n))
    # intialization
    Q = Y
    # normalize the line orientation just in case
    Dir = D / np.linalg.norm(D, ord=2, axis=0, keepdims=True)
    while err > tol:
        [R, t, A] = AOPA_Major(X, Q, tol)
        E = Q - np.matmul(R, np.matmul(A, X)) - np.matmul(t, e)
        # project point to line
        Q = Y + Dir * np.matlib.repmat(np.einsum('ij,ij->j', np.matmul(R, np.matmul(A, X)) + np.matmul(t, e) - Y, Dir),
                                       m, 1)
        err = np.linalg.norm(E - E_old)
        E_old = E
    E = Q - np.matmul(R, np.matmul(A, X)) - np.matmul(t, e)
    fre = np.sum(np.linalg.norm(E, ord=1, axis=0, keepdims=True)) / X.shape[1]
    return [R, t, A, Q, fre]

class PTL_Registration(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "PTL_Registration"  # TODO: make this more human readable by adding spaces
        self.parent.categories = ["Examples"]  # TODO: set categories (folders where the module shows up in the module selector)
        self.parent.dependencies = []  # TODO: add here list of module names that this module requires
        self.parent.contributors = ["John Doe (AnyWare Corp.)"]  # TODO: replace with "Firstname Lastname (Organization)"
        # TODO: update with short description of the module and a link to online module documentation
        self.parent.helpText = """
This is an example of scripted loadable module bundled in an extension.
See more information in <a href="https://github.com/organization/projectname#PTL_Registration">module documentation</a>.
"""
        # TODO: replace with organization, grant and thanks
        self.parent.acknowledgementText = """
This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc., Andras Lasso, PerkLab,
and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
"""

        # Additional initialization step after application startup is complete
        slicer.app.connect("startupCompleted()", registerSampleData)


#
# Register sample data sets in Sample Data module
#

def registerSampleData():
    """
    Add data sets to Sample Data module.
    """
    # It is always recommended to provide sample data for users to make it easy to try the module,
    # but if no sample data is available then this method (and associated startupCompeted signal connection) can be removed.

    import SampleData
    iconsPath = os.path.join(os.path.dirname(__file__), 'Resources/Icons')

    # To ensure that the source code repository remains small (can be downloaded and installed quickly)
    # it is recommended to store data sets that are larger than a few MB in a Github release.

    # PTL_Registration1
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='PTL_Registration',
        sampleName='PTL_Registration1',
        # Thumbnail should have size of approximately 260x280 pixels and stored in Resources/Icons folder.
        # It can be created by Screen Capture module, "Capture all views" option enabled, "Number of images" set to "Single".
        thumbnailFileName=os.path.join(iconsPath, 'PTL_Registration1.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95",
        fileNames='PTL_Registration1.nrrd',
        # Checksum to ensure file integrity. Can be computed by this command:
        #  import hashlib; print(hashlib.sha256(open(filename, "rb").read()).hexdigest())
        checksums='SHA256:998cb522173839c78657f4bc0ea907cea09fd04e44601f17c82ea27927937b95',
        # This node name will be used when the data set is loaded
        nodeNames='PTL_Registration1'
    )

    # PTL_Registration2
    SampleData.SampleDataLogic.registerCustomSampleDataSource(
        # Category and sample name displayed in Sample Data module
        category='PTL_Registration',
        sampleName='PTL_Registration2',
        thumbnailFileName=os.path.join(iconsPath, 'PTL_Registration2.png'),
        # Download URL and target file name
        uris="https://github.com/Slicer/SlicerTestingData/releases/download/SHA256/1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97",
        fileNames='PTL_Registration2.nrrd',
        checksums='SHA256:1a64f3f422eb3d1c9b093d1a18da354b13bcf307907c66317e2463ee530b7a97',
        # This node name will be used when the data set is loaded
        nodeNames='PTL_Registration2'
    )


#
# PTL_RegistrationWidget
#

class PTL_RegistrationWidget(ScriptedLoadableModuleWidget, VTKObservationMixin):
    """Uses ScriptedLoadableModuleWidget base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self, parent=None):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.__init__(self, parent)
        VTKObservationMixin.__init__(self)  # needed for parameter node observation
        self.logic = None
        self._parameterNode = None
        self._updatingGUIFromParameterNode = False

    '''
    def ApplyTransformMatrixToControlPoint(vtkMRMLMarkupsFiducialNode pointListNode, int index, vtkMatrix4x4 transformMatrix):
        position = pointListNode.GetNthControlPointPosition(index)
        position.append(1.0)
        transformMatrix.MultiplyPoint(position)

        return position
    '''

    def setup(self):
        """
        Called when the user opens the module the first time and the widget is initialized.
        """
        ScriptedLoadableModuleWidget.setup(self)

        ############################
        # slicer.util.loadScene("C:/d/ClariusTracker/calibrationClarius/putXYZonPython.mrb")
        # usPointsNode = slicer.util.getNode("usPoints")
        # X = slicer.util.arrayFromMarkupsControlPoints(usPointsNode)
        #print("US Points:\n", usPoints)


        # bigholePositions = np.zeros((wireSequenceNode.GetNumberOfDataNodes(), 3))

        wireSequenceNode = slicer.util.getNode('boxToProbe-boxToProbe-Seq')
        browserNode = slicer.modules.sequences.logic().GetFirstBrowserNodeForSequenceNode(wireSequenceNode)
        browserNode.SetSelectedItemNumber(0)


        shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
        #originalID = shNode.GetItemByDataNode(originalPoints)

        #originalPoints = slicer.util.getNode('trackLine')
        #originalArray = slicer.util.arrayFromMarkupsControlPoints(originalPoints)
        originListNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "originList")
        directionListNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLMarkupsFiducialNode", "directionList")

        print('START\n')
        #wireSequenceNode.GetNumberOfDataNodes()
        for count in range(3):  # Loops 22 times
            # Moves to current sequence
            browserNode.SetSelectedItemNumber(count)
            # Get the sequence's current transformed node
            currentNode = slicer.util.getNode('trackLine')
            currentPTMNode = slicer.util.getNode('PlatformToMarker2')

            # Clone the sequence's current transformed node
            #shNode = slicer.vtkMRMLSubjectHierarchyNode.GetSubjectHierarchyNode(slicer.mrmlScene)
            #itemIDToClone = shNode.GetItemByDataNode(currentNode)
            #clonedItemID = slicer.modules.subjecthierarchy.logic().CloneSubjectHierarchyItem(shNode, itemIDToClone)
            #clonedNode = shNode.GetItemDataNode(clonedItemID)

            # Harden the clone and copy its points onto each markup list
            currentNode.HardenTransform()
            print(slicer.util.arrayFromMarkupsControlPoints(currentNode))
            currentNode.SetAndObserveTransformNodeID(currentPTMNode.GetID())


            '''
            # Gets the current sequence's unique 'PlatformToMarker2' transform values
            currentPTMNode = slicer.util.getNode('PlatformToMarker2')
            currentTrackNode = slicer.util.getNode('Marker2ToTracker')

            # copyArray = slicer.util.arrayFromMarkupsControlPoints(originalPoints)
            platformVTK = currentPTMNode.GetMatrixTransformFromParent()

            trackerVTK = currentTrackNode.GetMatrixTransformFromParent()

            # The current origin point added to the list is originally just "bigHole" from the originalPoints list
            newOriginIndex = originListNode.AddControlPoint([originalArray[0][0], originalArray[0][1], originalArray[0][2]])
            #newOrigin = originListNode.GetNthControlPoint(newOriginIndex)
            originListNode.SetNthControlPointLabel(newOriginIndex, "origin" + str(count))

            # Applying the current transforms onto the origin
            currentPosition = list(originListNode.GetNthControlPointPosition(0))
            currentPosition.append(1.0)
            platformVTK.MultiplyPoint(currentPosition)

            #transformedPosition = trackerVTK.MultiplyPoint(platformVTK.MultiplyPoint(currentPosition))
            transformedPosition = platformVTK.MultiplyPoint(currentPosition)

            print(transformedPosition)

            #originListNode.SetNthControlPointPosition(newOrigin, 6.0, 7.0, 8.0)
            '''

            '''
            # This current origin point is referenced here by getting the control point at the current index [count]
            currentOrigin = originListNode().GetControlPoints()[count]
            
            # Creates a copy of the original untransformed line points
            #clonedItemID = slicer.modules.subjecthierarchy.logic().CloneSubjectHierarchyItem(shNode, originalID)
            #clonedNode = shNode.GetItemDataNode(clonedItemID)

            # Gets the current sequence's unique 'PlatformToMarker2' and 'Marker2ToTracker' transform values
            currentPTMNode = slicer.util.getNode('PlatformToMarker2')
            currentTrackNode = slicer.util.getNode('Marker2ToTracker')

            #copyArray = slicer.util.arrayFromMarkupsControlPoints(originalPoints)
            platformVTK = currentPTMNode.GetMatrixTransformFromParent().Invert()
            trackerVTK = currentTrackNode.GetMatrixTransformFromParent()

            print("ITERATION:", count+1, "\n")
            print("TRANSFORM PTM:", platformVTK, "\n")
            print("TRANSFORM TRACK:", trackerVTK, "\n")
            print("POINTS:", slicer.util.arrayFromMarkupsControlPoints(clonedNode), "\n")


            print("PTS TRANSFORMED:", slicer.util.arrayFromMarkupsControlPoints(clonedNode), "\n")
            #copyPoints.SetAndObserveTransformNodeID(currentTransformNode.GetID())

            #print(slicer.util.arrayFromMarkupsControlPoints(copyPoints))
            #print(slicer.util.arrayFromTransformMatrix(currentTransformNode))
            '''
        print('FINISH\n')
        ############################

        # Load widget from .ui file (created by Qt Designer).
        # Additional widgets can be instantiated manually and added to self.layout.
        uiWidget = slicer.util.loadUI(self.resourcePath('UI/PTL_Registration.ui'))
        self.layout.addWidget(uiWidget)
        self.ui = slicer.util.childWidgetVariables(uiWidget)

        # Set scene in MRML widgets. Make sure that in Qt designer the top-level qMRMLWidget's
        # "mrmlSceneChanged(vtkMRMLScene*)" signal in is connected to each MRML widget's.
        # "setMRMLScene(vtkMRMLScene*)" slot.
        uiWidget.setMRMLScene(slicer.mrmlScene)

        # Create logic class. Logic implements all computations that should be possible to run
        # in batch mode, without a graphical user interface.
        self.logic = PTL_RegistrationLogic()

        # Connections

        # These connections ensure that we update parameter node when scene is closed
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.StartCloseEvent, self.onSceneStartClose)
        self.addObserver(slicer.mrmlScene, slicer.mrmlScene.EndCloseEvent, self.onSceneEndClose)

        # These connections ensure that whenever user changes some settings on the GUI, that is saved in the MRML scene
        # (in the selected parameter node).
        self.ui.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.outputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)
        self.ui.imageThresholdSliderWidget.connect("valueChanged(double)", self.updateParameterNodeFromGUI)
        self.ui.invertOutputCheckBox.connect("toggled(bool)", self.updateParameterNodeFromGUI)
        self.ui.invertedOutputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.updateParameterNodeFromGUI)

        # Buttons
        self.ui.applyButton.connect('clicked(bool)', self.onApplyButton)

        # Make sure parameter node is initialized (needed for module reload)
        self.initializeParameterNode()

    def cleanup(self):
        """
        Called when the application closes and the module widget is destroyed.
        """
        self.removeObservers()

    def enter(self):
        """
        Called each time the user opens this module.
        """
        # Make sure parameter node exists and observed
        self.initializeParameterNode()

    def exit(self):
        """
        Called each time the user opens a different module.
        """
        # Do not react to parameter node changes (GUI wlil be updated when the user enters into the module)
        self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

    def onSceneStartClose(self, caller, event):
        """
        Called just before the scene is closed.
        """
        # Parameter node will be reset, do not use it anymore
        self.setParameterNode(None)

    def onSceneEndClose(self, caller, event):
        """
        Called just after the scene is closed.
        """
        # If this module is shown while the scene is closed then recreate a new parameter node immediately
        if self.parent.isEntered:
            self.initializeParameterNode()

    def initializeParameterNode(self):
        """
        Ensure parameter node exists and observed.
        """
        # Parameter node stores all user choices in parameter values, node selections, etc.
        # so that when the scene is saved and reloaded, these settings are restored.

        self.setParameterNode(self.logic.getParameterNode())

        # Select default input nodes if nothing is selected yet to save a few clicks for the user
        if not self._parameterNode.GetNodeReference("InputVolume"):
            firstVolumeNode = slicer.mrmlScene.GetFirstNodeByClass("vtkMRMLScalarVolumeNode")
            if firstVolumeNode:
                self._parameterNode.SetNodeReferenceID("InputVolume", firstVolumeNode.GetID())

    def setParameterNode(self, inputParameterNode):
        """
        Set and observe parameter node.
        Observation is needed because when the parameter node is changed then the GUI must be updated immediately.
        """

        if inputParameterNode:
            self.logic.setDefaultParameters(inputParameterNode)

        # Unobserve previously selected parameter node and add an observer to the newly selected.
        # Changes of parameter node are observed so that whenever parameters are changed by a script or any other module
        # those are reflected immediately in the GUI.
        if self._parameterNode is not None:
            self.removeObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)
        self._parameterNode = inputParameterNode
        if self._parameterNode is not None:
            self.addObserver(self._parameterNode, vtk.vtkCommand.ModifiedEvent, self.updateGUIFromParameterNode)

        # Initial GUI update
        self.updateGUIFromParameterNode()

    def updateGUIFromParameterNode(self, caller=None, event=None):
        """
        This method is called whenever parameter node is changed.
        The module GUI is updated to show the current state of the parameter node.
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        # Make sure GUI changes do not call updateParameterNodeFromGUI (it could cause infinite loop)
        self._updatingGUIFromParameterNode = True

        # Update node selectors and sliders
        self.ui.inputSelector.setCurrentNode(self._parameterNode.GetNodeReference("InputVolume"))
        self.ui.outputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolume"))
        self.ui.invertedOutputSelector.setCurrentNode(self._parameterNode.GetNodeReference("OutputVolumeInverse"))
        self.ui.imageThresholdSliderWidget.value = float(self._parameterNode.GetParameter("Threshold"))
        self.ui.invertOutputCheckBox.checked = (self._parameterNode.GetParameter("Invert") == "true")

        # Update buttons states and tooltips
        if self._parameterNode.GetNodeReference("InputVolume") and self._parameterNode.GetNodeReference("OutputVolume"):
            self.ui.applyButton.toolTip = "Compute output volume"
            self.ui.applyButton.enabled = True
        else:
            self.ui.applyButton.toolTip = "Select input and output volume nodes"
            self.ui.applyButton.enabled = False

        # All the GUI updates are done
        self._updatingGUIFromParameterNode = False

    def updateParameterNodeFromGUI(self, caller=None, event=None):
        """
        This method is called when the user makes any change in the GUI.
        The changes are saved into the parameter node (so that they are restored when the scene is saved and loaded).
        """

        if self._parameterNode is None or self._updatingGUIFromParameterNode:
            return

        wasModified = self._parameterNode.StartModify()  # Modify all properties in a single batch

        self._parameterNode.SetNodeReferenceID("InputVolume", self.ui.inputSelector.currentNodeID)
        self._parameterNode.SetNodeReferenceID("OutputVolume", self.ui.outputSelector.currentNodeID)
        self._parameterNode.SetParameter("Threshold", str(self.ui.imageThresholdSliderWidget.value))
        self._parameterNode.SetParameter("Invert", "true" if self.ui.invertOutputCheckBox.checked else "false")
        self._parameterNode.SetNodeReferenceID("OutputVolumeInverse", self.ui.invertedOutputSelector.currentNodeID)

        self._parameterNode.EndModify(wasModified)

    def onApplyButton(self):
        """
        Run processing when user clicks "Apply" button.
        """
        with slicer.util.tryWithErrorDisplay("Failed to compute results.", waitCursor=True):

            # Compute output
            self.logic.process(self.ui.inputSelector.currentNode(), self.ui.outputSelector.currentNode(),
                               self.ui.imageThresholdSliderWidget.value, self.ui.invertOutputCheckBox.checked)

            # Compute inverted output (if needed)
            if self.ui.invertedOutputSelector.currentNode():
                # If additional output volume is selected then result with inverted threshold is written there
                self.logic.process(self.ui.inputSelector.currentNode(), self.ui.invertedOutputSelector.currentNode(),
                                   self.ui.imageThresholdSliderWidget.value, not self.ui.invertOutputCheckBox.checked, showResult=False)


#
# PTL_RegistrationLogic
#

class PTL_RegistrationLogic(ScriptedLoadableModuleLogic):
    """This class should implement all the actual
    computation done by your module.  The interface
    should be such that other python code can import
    this class and make use of the functionality without
    requiring an instance of the Widget.
    Uses ScriptedLoadableModuleLogic base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def __init__(self):
        """
        Called when the logic class is instantiated. Can be used for initializing member variables.
        """
        ScriptedLoadableModuleLogic.__init__(self)

    def setDefaultParameters(self, parameterNode):
        """
        Initialize parameter node with default settings.
        """
        if not parameterNode.GetParameter("Threshold"):
            parameterNode.SetParameter("Threshold", "100.0")
        if not parameterNode.GetParameter("Invert"):
            parameterNode.SetParameter("Invert", "false")

    def process(self, inputVolume, outputVolume, imageThreshold, invert=False, showResult=True):
        """
        Run the processing algorithm.
        Can be used without GUI widget.
        :param inputVolume: volume to be thresholded
        :param outputVolume: thresholding result
        :param imageThreshold: values above/below this threshold will be set to 0
        :param invert: if True then values above the threshold will be set to 0, otherwise values below are set to 0
        :param showResult: show output volume in slice viewers
        """

        if not inputVolume or not outputVolume:
            raise ValueError("Input or output volume is invalid")

        import time
        startTime = time.time()
        logging.info('Processing started')

        # Compute the thresholded output volume using the "Threshold Scalar Volume" CLI module
        cliParams = {
            'InputVolume': inputVolume.GetID(),
            'OutputVolume': outputVolume.GetID(),
            'ThresholdValue': imageThreshold,
            'ThresholdType': 'Above' if invert else 'Below'
        }
        cliNode = slicer.cli.run(slicer.modules.thresholdscalarvolume, None, cliParams, wait_for_completion=True, update_display=showResult)
        # We don't need the CLI module node anymore, remove it to not clutter the scene with it
        slicer.mrmlScene.RemoveNode(cliNode)

        stopTime = time.time()
        logging.info(f'Processing completed in {stopTime-startTime:.2f} seconds')


#
# PTL_RegistrationTest
#

class PTL_RegistrationTest(ScriptedLoadableModuleTest):
    """
    This is the test case for your scripted module.
    Uses ScriptedLoadableModuleTest base class, available at:
    https://github.com/Slicer/Slicer/blob/main/Base/Python/slicer/ScriptedLoadableModule.py
    """

    def setUp(self):
        """ Do whatever is needed to reset the state - typically a scene clear will be enough.
        """
        slicer.mrmlScene.Clear()

    def runTest(self):
        """Run as few or as many tests as needed here.
        """
        self.setUp()
        self.test_PTL_Registration1()

    def test_PTL_Registration1(self):
        """ Ideally you should have several levels of tests.  At the lowest level
        tests should exercise the functionality of the logic with different inputs
        (both valid and invalid).  At higher levels your tests should emulate the
        way the user would interact with your code and confirm that it still works
        the way you intended.
        One of the most important features of the tests is that it should alert other
        developers when their changes will have an impact on the behavior of your
        module.  For example, if a developer removes a feature that you depend on,
        your test should break so they know that the feature is needed.
        """

        self.delayDisplay("Starting the test")

        # Get/create input data

        import SampleData
        registerSampleData()
        inputVolume = SampleData.downloadSample('PTL_Registration1')
        self.delayDisplay('Loaded test data set')

        inputScalarRange = inputVolume.GetImageData().GetScalarRange()
        self.assertEqual(inputScalarRange[0], 0)
        self.assertEqual(inputScalarRange[1], 695)

        outputVolume = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode")
        threshold = 100

        # Test the module logic

        logic = PTL_RegistrationLogic()

        # Test algorithm with non-inverted threshold
        logic.process(inputVolume, outputVolume, threshold, True)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], threshold)

        # Test algorithm with inverted threshold
        logic.process(inputVolume, outputVolume, threshold, False)
        outputScalarRange = outputVolume.GetImageData().GetScalarRange()
        self.assertEqual(outputScalarRange[0], inputScalarRange[0])
        self.assertEqual(outputScalarRange[1], inputScalarRange[1])

        self.delayDisplay('Test passed')
