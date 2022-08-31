## Config_Clarius
The purpose of this folder is to contain all configuration files used with the Plus server as you calibrate the Clarius probe.

### Calibration Tutorial: Part 3
#### Prerequisites
- Part 2 completed (ClariusTracker/calibrationClarius/Current_Models), including all constructed models.
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
2. Now, go to the "Volume Rendering" module and choose your Volume. Next, open the "Advanced" drop-down and adjust the Scalar Opacity Mapping and Color Mapping until the 3D model is visible. You should be able to scroll through CT image slices in the three 2D views of the model and find the platform's 6mm holes and fishwire holes are clearly visible. If they're not visible, readjust the Advanced options until they are. If you're having trouble with this, ask Shuwei Xing.
3. Now that you can see the four 6mm holes and the two fishwire holes, create six Point (Markup) Lists in the module "Markups" to represent each of these holes. We named them "posHole1, ..., posHole4" for the 6mm holes and "trackerClipHole", "smallClipHole" for the fishwire holes.
4. Now, select one of your Markup lists and add fiducials (we used 10 for high accuracy) to where you think the centre of the 6mm/wire hole is on the model. Repeat this process for all six Markup lists. **IMPORTANT: Remember which 6mm hole corresponds to each Markup List. They will be used later in this tutorial during our Fiducial Registration.**
5. Now, you'll need to take the average position of each Markup List. This can be done through the 3D Slicer Python Interactor using the commands in the file "MarkupCommands.txt" (calibrationClarius/Config_Clarius/MarkupCommands.txt). Once you've gotten the average position of all 6 holes, make two seperate Markup lists to store them. One is used to store the final positions of the four 6mm holes, and the other is to store the final positions of the two fishwire holes.
6. Now, we need to perform a Pivot Calibration on the stylus. To do this, find the Slicer Extension "IGT" and open the module "Pivot Calibration". Your input will be "Marker0ToTracker", while your output is "StylusTipToMarker0". Now, choose one of the 6mm holes on the platform (we used the hole on the model "smallClip"), and position the stylus' 6mm bead into the hole. Also, ensure the stylus' Aruco marker is close to the camera to ensure it's being tracked accurately. Change the duration to 13 seconds, and just before pressing "Start Pivot Calibration", start pivoting the stylus very slowly around the hole. Try not to pivot it too far away from the center, and ensure the marker is always clearly visible by the camera. Repeat this calibration until you get as low error possible (We got ~2.28, but this can be improved). For more instructions, see this guide[^2]. Also, look at the transform hirearchy if you're confused with any transformations [^3]. And if you're having trouble getting low error, ask Dan Allen for tips.
7. Now, your "StylusTipToMarker0" Slicer transform should have the output values from the Pivot Calibration. You need to copy and paste these Slicer transform values into the file "arucoTracking.xml" under the Transform "StylusTipToMarker0" (Note that the only elements you technically need to copy+paste are the outputted 4x4 matrix). To find this Slicer transform, go to the module "Transform" and select "StylusTipToMarker0" in the drop-down "Active Transform:". When you change the transform in the XML, it should look like this:
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
<!-- Please note that we manually changed the text in "Error" and "Date". This format is automatically created when you save the Slicer transform as a ".h5" file. -->
<!-- Normally, you can just copy and paste the 4x4 transform values directly from the Slicer "Transforms" module. -->
    <Transform From="StylusTip" To="Marker0"
      Matrix="
        0.999944 0 -0.010541 -2.56983 
-0.0104884 0.0997964 -0.994953 -242.563 
0.00105196 0.995008 0.0997909 24.3284 
0 0 0 1 "
       Error="2.28" Date="135700_310822" />\
```

8. Now, you should turn off the Aruco tracker Plus server, refresh it, and turn it back on. The XML file will automatically create the transform "StylusTipToTracker", which provides the rotation/translation of the pivot calibrated stylus with respect to the camera. In the Slicer module "Data", drag your "stylusV2" model onto "StylusTipToTracker", then drag "StylusTipToTracker" onto "StylusTipToMarker1". Now, you can track the stylus' tip with respect to the camera and the platform's marker.
9. Next, we want to calibrate the position of the platform with respect to the camera. To do this, we will take tracked stylus points corresponding to the 6mm holes on the uncalibrated platform. To start this, go to the module "Collect Points" within extension "IGT". Your sampling node should be "StylusTipToMarker1", while your outside node should be a new Point/Markup list that we named "trackedAruco".
10. At this point, your StylusV2 model should only be transformed to "StylusTipToTracker". Now, place the stylus tip into each of the four 6mm holes, and press "Collect". **IMPORTANT: First, remember to take these points in the order you made in Step 4. Second, ensure the stylus' marker is visible to the camera. Third, do NOT move the Platform at all in Steps 10-11; this will cause error.**
11. You should now have 4 experimental 6mm hole positions. Now, go to the Slicer module "Fiducial Registration Wizard" in extension "IGT". Under "From fiducials", select the Markup list containing the four "theoretical" 6mm hole points you manually placed onto the CT model (we named this "arucoPoints"). Under "To fiducials", select the Markup list you just took containing the "experimental" tracked 6mm hole positions (we named this "trackedAruco"). Under "Registration result", create a new transform to contain the output (we named this "StylusPlatformMove") and press "Update".
12. Go to "Transforms", and find "StylusPlatformMove". Copy and paste these values into the XML file "arucoTracking.xml" under the transform "PlatformToMarker1". This process is identical to Step 7. It should look like this:
```
<!-- Original -->
	<Transform From="Platform" To="Marker1"
      Matrix="
        -0.0796121 -0.07292 0.994155 1201.53 
-0.0841652 0.994251 0.0661871 -0.266575 
-0.993266 -0.078404 -0.0852917 -158.032 
0 0 0 1  "
       Error="1.65" Date="112317_141120" />
       
<!-- Edited -->
	<Transform From="Platform" To="Marker1"
      Matrix="
        -0.0796121 -0.07292 0.994155 1201.53 
-0.0841652 0.994251 0.0661871 -0.266575 
-0.993266 -0.078404 -0.0852917 -158.032 
0 0 0 1  "
       Error="7.3498" Date="112317_141120" />
```

13. Transform your CT model with "PlatformToTracker"
14. Transform your theoretical fishwire Markup list with "PlatformToMarker2".
15. Drag the Clarius probe model ("c7hd3.stl") into Slicer and transform it with "Marker2ToTracker". Remember, Marker 2 is on the Clarius probe platform.
16. Now we have all components needed to start taking calibration data and take the Point-To-Line registration. Continue this tutorial in the file path (calibrationClarius/Procrustean_PTLR).

### References
[^1]: Download 3D Slicer: https://download.slicer.org/
[^2]: Stylus Pivot Calibration: https://andysbrainbook.readthedocs.io/en/latest/Slicer/Slicer_Short_Course/Slicer_05_Calibration.html
[^3]: Project Transform Hirearchy: https://lucid.app/lucidchart/f71f7c9d-9a9b-471f-91b0-3d2879e26078/edit?viewport_loc=-151%2C88%2C2219%2C1065%2C0_0&invitationId=inv_dbf6853b-f39a-49d0-966a-b78b702a4358#
