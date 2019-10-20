/*******************************************************************************
* -*- coding: utf-8 -*-
* Copyright (c) 2012-2019, Anima Istanbul
*
* This module is part of anima-tools and is released under the MIT
* License: http://www.opensource.org/licenses/MIT
*
/********************************************************************************/

/*! \file
*
*   \houdini to arnold file linker for hcustom 
*   \author Sergen Eren
*   
*   \version 0.1
*   \date March 2016
*
*/

#if defined( WIN32 ) 
    #define OPENEXR_DLL 1
#endif

#include "h2a_io.cpp"
#include "ROP_h2a.cpp"
