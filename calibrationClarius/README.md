# calibrationClarius

This folder contains all materials used to calibrate the Clarius ultrasound probe for our Clarius Carotid artery segmentation project.
- To learn how to perform this calibration, begin the tutorial in the folder "Aruco_PDFs".
- For a brief overview of each folder, look under the header below titled "Folders".

## Folders
### Aruco_PDFs
Contains PDF files of all three 80mm Aruco trackers used for this project. It also contains an a4 Aruco checkerboard, which is used to calibrate the webcam.
Each Aruco marker PDF corresponds to the following devices:
| arucoX.pdf  | Marker Device |
| ------------- | ------------- |
|0  | Stylus  |
| 1  | Platform  |
| 2  | Clarius  |
| Complete  | All Devices (0-2) |

### clariusSegment
This contains the Python-only program used to collect data and perform the Artery segmentations. It uses Python 3.9 with the following packages: pyigtl, vtk, PySide6. At the moment, it can only Use pyigtl to stream the webcam's image onto a VTK display.

### Config_Clarius
Contains all XML files used to connect the Webcam and the Clarius to twoservers. These Plus servers allow you to calibrate and track the Clarius on 3DSlicer or the Python-only application. Here is some information about each file:
| File  | Info |
| ------------- | ------------- |
|arucoTracking.xml  | Used to stream the webcam image and track the three Aruco markers. |
| clariusConfig.xml  | Used to stream Clarius ultrasound images. |
| new_calibration.yml  | The webcam calibration file used in the Tutorial. |

### Current_Models
Contains the current iteration of each 3D model used in this project. To find printable 3D models, go to file path (Current_Models/final_designs).

### Old_Models
Contains all old iterations of each 3D model used in this project. It also contains some external 3D files used to create our own 3D models (ex: "Apple" optical tracker frames), which can be used to modify current designs.

### Procrustean_PTLR
This contains the Python scripted 3D Slicer module used to perform the actual Point-To-Line calibration. This is done at the end once all necessary data has been collected.
