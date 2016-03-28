H2A
=====

H2A_ROP is the rop node for houdini 15 to export houdini geometry in arnold ass format. 

H2A_ROP is the cpp implementation of the anima pipeline houdini to arnold ass exporter "h2a.py"
written in C++ 11. 

To compile execute "hcustom path-to-project/H2A.cpp". It will create the H2A.dll
in HOUDINI_DSO_PATH (generally $HOME/HOUDINIX.Y/dso). If the dll is created at project folder move 
the dll to houdini DSO or custom dso path. 

Support files go to:
svg icon: $HOME/HOUDINIX.Y/config/icons/
h2a_rop and h2a.png: $HOME/HOUDINIX.Y/help/nodes/out/

(h2a_rop.txt and h2a.png are used for help card)

Usage: Create a ROP network or go to "out" network. place an H2A_ROP, enter the sop that contains 
the geometry that you want to export, choose the export type and click render. 

Can be used in connection with afanasy rop render or any other renderers. 


Loading in MAYA: create an arnold stand-in node and select the fies that you have exported. For color 
data, create an "aiusercolor" node and enter "Cd" as the data channel and connect the output color to 
your material color or other attributes. 

All attributes in houdini to be exported must be point attributes. User is responsible for attribute 
promotion. 

For further detail check out h2a_rop.txt

for any inquires e-mail @sergeneren@gmail.com