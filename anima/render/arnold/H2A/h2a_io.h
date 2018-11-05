/*******************************************************************************
* -*- coding: utf-8 -*-
* Copyright (c) 2012-2018, Anima Istanbul
*
* This module is part of anima-tools and is released under the BSD 2
* License: http://www.opensource.org/licenses/BSD-2-Clause
*
/********************************************************************************/

/*! \file
*
*   \houdini to arnold ass file saver header  
*   \author Sergen Eren
*   
*   \version 0.1
*   \date March 2016
*
*/

#ifndef __h2a_io_h__
#define __h2a_io_h__

//C library
#include <stdio.h>
#include <iostream> 
#include <ostream>

//Houdini
#include <GU/GU_Detail.h>

namespace H2A {

	GA_Detail::IOStatus h2a_fileSave(const GU_Detail *gdp, 
									 const char *fname, 
									 const char *name, 
									 fpreal pwidth, 
									 fpreal shutter, 
									 int mode, 
									 bool motionb, 
									 bool color, 
									 int type,
									 int p_type,
									 fpreal radius,
									 int subdiv_type,
									 int subdiv_ite);

}

#endif