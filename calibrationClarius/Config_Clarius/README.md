## Config_Clarius
The purpose of this folder is to contain all configuration files used with the Plus server as you calibrate the Clarius probe.

### Calibration Tutorial: Part X
#### Prerequisites
- Part 2 completed (ClariusTracker/calibrationClarius/Current_Models)
- Latest Preview 3D Slicer Release[^1]
  - We used version 5.1.0-2022-07-17
- 3D Slicer Extensions used:
  -  SlicerIGT
  -  SlicerIGSIO
  -  SlicerOpenIGTLink
  -  VASSTAlgorithms
  -  SlicerOpenCV
- Two Plus Toolkit Launchers open
  - Use the Plus server version you downloaded & configured in Tutorial 1.
#### Steps
1. To start, load the CT scanned volume of your calibration platform onto Slicer. This can be done by simply dragging the full "Vol Body" folder onto Slicer. Our CT Scan folder was named "CT Vol Body Std. Volume 0.5 Non Contrast Vol". You should also view this model in each of the three 2D views on Slicer (Red, Green, Yellow).
2. Now, go to the "Volume Rendering" module and choose your Volume. Next, open the "Advanced" drop-down and adjust the Scalar Opacity Mapping and Color Mapping until the 3D model is visible. You should be able to scroll through the three 2D views of the model and find the Platform's 6mm holes are clearly visible. If they're not visible, readjust until they are. If you're having trouble with this, ask Shuwei Xing.
3. Now that you can see the four 6mm holes, create six Point (Markup) Lists in the module "Markups" to represent each of them, as well as the wire's holes. We named them "posHole1, ..., posHole4" and "trackerClipHole", "smallClipHole".
4. Now, select one of your Markup lists and add fiducials (we used 10 for high accuracy) to where you think the centre of the 6mm/wire hole is on the model. Repeat this process for all six Markup lists. **IMPORTANT: Remember which 6mm hole corresponds to each Markup List. They will be used later in this tutorial during our Fiducial Registration.**
5. Now, you'll need to take the average position of each Markup List. This can be done through the 3D Slicer Python Interactor using the commands in the file "MarkupCommands.txt" (calibrationClarius/Config_Clarius/MarkupCommands.txt). Once you've gotten the average position of each hole, make two seperate Markup lists to store them. One is used to store the final position of the four 6mm holes, and the other is to store the final positions of the two wire holes.
6. Now, we need to perform a Pivot Calibration on the stylus. To do this, find the Slicer Extension "IGT" and open the module "Pivot Calibration". Your input will be "Marker0ToTracker", while your output is "StylusTipToMarker0". Now, choose one of the 6mm holes, and position the stylus' 6mm bead into the hole. Also, ensure the stylus' Aruco marker is close to the camera to ensure it's being tracked accurately. Change the duration to 15 seconds, and just before pressing "Start Pivot Calibration", start rotating the stylus slowly around the hole. Repeat this calibration until you get as low error possible. For more instructions, see this guide[^2]. Also, look at the transform hirearchy if you're confused with any transformations [^3].
7. Now, you'll need to copy and paste the outputted Pivot Calibration values into the file "arucoTracking.xml" under the Transform "StylusTipToMarker0" (Note that the only elements you technically need to copy+paste are the outputted 4x4 matrix):
```
<!-- Original: -->
    <Transform From="StylusTip" To="Marker0"
      Matrix="
        0.999944 0 -0.010541 -2.56983 
-0.0104884 0.0997964 -0.994953 -242.563 
0.00105196 0.995008 0.0997909 24.3284 
0 0 0 1 "
       Error="3.93523" Date="112317_141120" />\
       
<!-- Edited (example): -->
    <Transform From="StylusTip" To="Marker0"
      Matrix="
        0.999944 0 -0.010541 -2.56983 
-0.0104884 0.0997964 -0.994953 -242.563 
0.00105196 0.995008 0.0997909 24.3284 
0 0 0 1 "
       Error="3.93523" Date="112317_141120" />\
```

8. Now

### References
[^1]: Download 3D Slicer: https://download.slicer.org/
[^2]: Stylus Pivot Calibration: https://andysbrainbook.readthedocs.io/en/latest/Slicer/Slicer_Short_Course/Slicer_05_Calibration.html
[^3]: Project Transform Hirearchy: https://lucid.app/lucidchart/f71f7c9d-9a9b-471f-91b0-3d2879e26078/edit?viewport_loc=-151%2C88%2C2219%2C1065%2C0_0&invitationId=inv_dbf6853b-f39a-49d0-966a-b78b702a4358#
