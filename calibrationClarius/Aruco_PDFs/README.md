## Aruco PDFs
This folder contains all Aruco marker files used to track and calibrate the Clarius ultrasound probe. The 3D Slicer Plus Toolkit is used to calibrate and track all devices.
### Files
aruco_calibration_board_a4.pdf - Used to calibrate the webcam with the Plus Toolkit [^1]

| arucoX.pdf  | Marker Device |
| ------------- | ------------- |
|0  | Stylus  |
| 1  | Platform  |
| 2  | Clarius  |
| Complete  | All Devices (0-2) | /

### Clarius Calibration Tutorial: Part 1
#### Prerequisites:
- A lab computer with Windows 10 and 64-bit Windows.
- A stationary webcam with auto-focus disabled.
  - We used a Logitech HD Pro Webcam C920. Also, we had to download the Logitech Capture software [^2] to change settings.
  - Other tweaks in the webcam's settings can likely be used to improve accuracy, such as increasing contrast. Test different setups to find the most accurate one for you.
- Plus Toolkit, Latest Win-64 Clarius Developmental Snapshot [^3].
- The files "arucoComplete.pdf" and "aruco_calibration_board_a4.pdf" in this folder printed at 100% size.
  - To improve accuracy, you should allow these printouts to dry for ~1 day.
- A glue stick and scissors.
- A rigid surface which can fit the Aruco calibration board printout and be held in front of a webcam.
  - We just cut out a cardboard rectangle for this.
#### Steps:
1. To start, we need to calibrate the webcam. The webcam is used to track each marker, and must be calibrated to improve tracking accuracy. To perform this calibration, follow the Plus Toolkit steps [^1] beneath the header "Calibration". Note that this folder already contains the Plus a4 calibration board PDF file for convenience.
2. Cut out and glue the calibration board onto a rigid surface. As mentioned before, we just used a cardboard rectangle for this. Also, try not to use excessive amounts of glue since it could deform the paper and reduce accuracy.
3. As mentioned in the Plus tutorial [^1], you need to execute the file "aruco_calibration.exe". This executable can be found in your Plus folder within the file path: (PlusApp-Version/bin/aruco_calibration.exe). To start this file, you can either double-click it or use the command prompt by changing directory to the correct file path and typing "start aruco_calibration.exe". 
4. Redo this calibration until you get as low of an error as possible. The webcam calibration file we used for this tutorial is titled "new_calibration.yml" in the file path (ClariusTracker/calibrationClarius/Config_Clarius/new_calibration.yml). Please note that your values and error will likely vary from this, especially if you're using a different webcam.
5. Once you've completed the webcam calibration and tried minimizing error, drag the output .yml file into the file path (PlusApp-Version/config/OpticalMarkerTracker). For future reference, this output webcam calibration .yml file will be named "webcam_calibration.yml".
6. Cut out each of the 3 Aruco markers from your "arucoComplete.pdf" printout and set them aside.
<!-- end of the list -->
To continue this tutorial, you can find Part 2 in the file path (ClariusTracker/calibrationClarius/Current_Models/README.md).
### References
[^1]: Plus Toolkit Optical Marker Trackers: http://perk-software.cs.queensu.ca/plus/doc/nightly/user/DeviceOpticalMarkerTracker.html
[^2]: Logitech Capture Software: https://www.logitech.com/en-ca/software/capture.html
[^3]: Plus Toolkit Latest Snapshots: http://perk-software.cs.queensu.ca/plus/packages/nightly/?_ga=2.65678765.2001696992.1661792522-2141715401.1657571144
