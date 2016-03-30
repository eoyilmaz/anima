H2A
=====

H2A_ROP is the rop node for houdini 15 to export houdini geometry in arnold stand-in ass format. 

H2A is the cpp implementation of the anima pipeline houdini to arnol ass exporter "h2a.py"
Written in C++ 11. To compile execute "hcustom path-to-project/H2A.cpp". It will create the H2A.dll
in HOUDINI_DSO_PATH (generally $HOME/HOUDINIX.Y/dso). If the dll is created at project folder move 
the dll to DSO path. 

Support files go to:
svg icon: $HOME/HOUDINIX.Y/config/icons
h2a_rop and h2a.png: $HOME/HOUDINIX.Y/help/nodes/out

(h2a_rop.txt and h2a.png are used for help card)

Usage: Create a ROP network or go to "out" network. place H2A_ROP, enter the sop that contains 
the geometry that you want to export, choose the export type and click render. 

Can be used in connected to afanasy rop render or any other renderers. 

Loading in MAYA: create an arnold stand-in node and select the files that you have exported. for color 
data create a "aiusercolor" node and enter "Cd" and connect the output color to your used data channel. 

All attributes in houdini to be exported must be point attributes (with the exception of poly rendering: "uv" and 
"N" attributes should be vertex attributes). User is responsible for attribute promotion. 

For further detail check out h2a_rop.txt

for any inquires e-mail @sergeneren@gmail.com

