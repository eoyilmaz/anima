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
*   \houdini to arnold ass file saver cpp implementation  
*   \author Sergen Eren
*   
*   \version 0.1
*   \date March 2016
*
*/


#include "h2a_io.h"

#include "asstoc_writer.cpp"
#include "point_write.cpp"
#include "poly_write.cpp"
#include "curve_write.cpp"
#include "light_write.cpp"

using namespace std;

namespace H2A{

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
		int subdiv_ite)

	{

		bool use_gzip = 0;

		UT_String filename(fname);
		use_gzip = filename.matchFileExtension(".gz"); 
		UT_String baseName(filename.pathUpToExtension());

		switch (type)
		{
		case 0:
			curve_writer(gdp, filename, name, pwidth, shutter, mode, motionb, color, use_gzip);
			break;
		case 1:
			poly_writer(gdp,filename, name, shutter, motionb, color,subdiv_type, subdiv_ite, use_gzip);
			break;
		case 2:
			point_writer(gdp,fname, name, shutter,motionb,color,p_type,radius,use_gzip);
			break;
		case 3:
			light_writer(gdp,fname,use_gzip);
			break;
		}

		//Write asstoc file

		if(use_gzip) baseName = baseName.pathUpToExtension();
		write_asstoc(baseName,gdp);

		return true;
	}
}
