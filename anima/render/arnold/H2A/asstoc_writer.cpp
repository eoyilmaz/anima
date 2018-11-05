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
*   \asstoc file writer  
*   \author Sergen Eren
*   
*   \version 1.0
*   \date March 2016
*
*/

#include <UT/UT_OFStream.h>
#include <GU/GU_Detail.h>
#include <FS/FS_Writer.h>

bool write_asstoc(UT_String baseName, const GU_Detail* gdp, fpreal pscale=1){

	UT_String asstoc_name;
	asstoc_name = baseName;
	asstoc_name.append(".asstoc");

	UT_OFStream tocFile(asstoc_name);

	if(tocFile.is_open()){
		UT_BoundingBoxF bbox;
		gdp->getPointAttribBBox("P",&bbox);
		tocFile<<"bounds "<<bbox.xmin() - pscale << " " <<bbox.ymin() - pscale << 
			" " <<bbox.zmin() - pscale << " " <<bbox.xmax() + pscale << 
			" " <<bbox.ymax() + pscale << " " <<bbox.zmax()+ pscale;
	}

	tocFile.close();
	return true;
}