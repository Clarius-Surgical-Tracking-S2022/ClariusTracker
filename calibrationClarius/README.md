# calibrationClarius

This folder contains all materials used to calibrate the Clarius ultrasound probe for our Clarius Carotid artery segmentation project.\
To learn how to use this calibration folder, read the tutorial below.\
To understand the purpose of each folder, scroll to the end of this document until you reach the header "Folders"\

## Folders
### Aruco_PDFs
Contains PDF files of all 3 80mm Aruco trackers used for this project. Each tracker corresponds to the following objects:\
#0: Stylus\
#1: Clarius\
#2: Calibration Box

### Config_Clarius
Contains all XML files used to connect the Webcam and the Clarius to 2 Plus servers. These Plus servers allow you to calibrate and track the Clarius on 3DSlicer or the Python-only application. Here is some information about each file:\
**arucoTracking.xml:** Used to stream Webcam images, and use it to track the 3 Aruco sheets.\
**clariusConfig.xml:** Used to stream Clarius ultrasound images.\
**OpticalMarkerTracker:** Contains dependencies that are needed for arucoTracking.xml to actually track the Aruco sheets.

### CT_Calibration
Contains the CT scan of our calibration box in DICOM format. This can be opened on Slicer easily by dragging the file onto your Slicer scene.

### Current_Models
Contains the current iteration of each 3D model used in this project.

### Old_Models
Contains all old iterations of each 3D model used in this project. It also contains some external 3D files used to create our own 3D models (ex: "Apple" optical tracker frames).

### clariusSegment
This contains the Python-only program used to collect data and perform the Artery segmentations. It uses Python 3.9 with the following packages: pyigtl, vtk, PySide6.

### finalDesign
Contains the final STL files of models we want to 3D print; we were unable to print Solidworks SLDPRT files for some reason.

### leahCalibModified
This is a modified version of a Slicer ultrasound calibration module developed by Leah Groves. It is used to calibrate the Clarius' imaging stream with the tracked position of the Clarius Probe.
