## Procrustean_PTLR
The purpose of this folder is to store the 3D Slicer module we created to perform the Point-To-Line registration of the Clarius image stream.

### Calibration Tutorial: Part 4
#### Prerequisites
- Part 3 completed (ClariusTracker/calibrationClarius/Config_Clarius)
  - Ensure you have the Plus servers and Slicer open (see Part 3)
- A Clarius ultrasound probe with Aruco marker attached (see Part 2)
- An Android Tablet with the Clarius app installed
  - Ensure the app is the same version as your Clarius probe
#### Steps
1. To start, take your Clarius ultrasound probe and turn it on using the Power button on the front. Next, open the VASST Android tablet (for the password, ask Adam Rankin) and open the Clarius app. Select your scanner (we used the "c7hd3" probe) and wait for the Clarius to connect with the tablet.
2. Connect your PC to the Clarius' local wifi network. To find the name and password of this network, go to "About" in the Clarius Android app. Also, you might need a wifi adapter if your PC only uses ethernet, like the PCs at VASST Lab. Ask Adam Rankin for this adapter.
3. Open one of your two Plus servers and select the config file "PlusServer: Tracked Clarius ultrasound probe". Now, go to the IGT module "OpenIGTLinkIF" and add a Connector with port 18945. Click "Active", and you should be able to see the Clarius' image stream. If not, try disabling your computer's Public firewall or writing a rule to allow it through.
4. 
