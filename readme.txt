This is a prototype tool for 3D bounding box annotation within baggage 3D CT volumes
by Qian Wang 2020
################# How to use ########################
--Install required python packages: vtk, itk, matlab.engine, pyqt5, numpy, glob;
--Hard code the "categories" in the script (line 59: self.labelComboBox.addItems([...]));
--Run the script: python3 3D_BB_Annotation_Tool.py;
--A dialog pops up to select the .img file for annotation. (if one wants to annotate all .img files in one folder, please select the first one in this folder);
--An initial bounding box will show within the CT volume, now you can adjust the sliders to move/resize the bounding box, select the proper category from the drop-down menu, once the bounding box is in a good position, click "save" button to save the coordinates of the bounding box.
A txt file with the name of "[filename]_[category].txt" will be created in the same folder as the .img file. The annotation txt file contains six float numbers which are x,y,z,w,h,l
--If there are more than one target objects in the volume, just re-adjust the bounding box and re-select the category and save again.
--Once finished with this volume (don't forget saving), click "next image" to annotate the next CT volume in the same folder.

################# How it works ######################
--The program is based on the CT inspection tool which aims to visualise a CT volume using a custom color mapping (Rapiscan style).
--The bounding boxes is drawn on the Volume by revising the voxels of the original CT volume to a value so that these revised voxels will be visualized in a specific color (e.g., Blue).
--The revised volume should be directly displayed as a VTK object and the user can see the CT baggae as well as the bounding box, HOWEVER, I didn't manage to find a way to convert a numpy matrix to a VTK volume. Instead, I'm currently using an ugly solution in this script: every time when the annotator move the sliders, the revised CT volume (numpy matrix) will be saved to local drive as a .hdr/.img file and the file will subsequently be read into the VTK for visualisation.


