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
*   \point ass exporter  
*   \author Sergen Eren
*   
*   \version 1.0
*   \date March 2016
*
*/

#include <base_85.cpp>
#include <zlib.h>

#include <GU/GU_Detail.h>
#include <UT/UT_OFStream.h>
#include <OP/OP_Director.h>

using namespace b85;

bool point_write_normal_file(const GU_Detail *gdp,
							 UT_String fname,
							 const char * name,
							 fpreal shutter,
							 bool motionb,
							 bool color,
							 int p_type,
							 fpreal radius)
{

	UT_String render_type("disk"); 
	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();

	switch(p_type)
	{
	case 0:
		render_type = "disk";
		break;
	case 1:
		render_type = "sphere";
		break;
	case 2:
		render_type = "quad";
		break;
	}
	fpreal p_radius = radius; 

	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);


	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	GA_ROHandleF rad_h(gdp, GA_ATTRIB_POINT,"pscale");
	fpreal32 rad_val(1);

	UT_OFStream ass_file(fname);

	int sample_count = motionb&&v_h.isValid()? 2:1;

	ass_file<<"points\n{\n name "<<name;
	ass_file<<"\n points "<<gdp->getNumPoints()<<" "<<sample_count<<" POINT\n";

	GA_Offset	lcl_start, lcl_end, ptoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);
			ass_file<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";
			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	if(motionb  && v_h.isValid() ){
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				pos_val = pos_h.get(ptoff);
				if(v_h.isValid()) v_val = v_h.get(ptoff);
				pprime_val = pos_val + ((v_val / fps) * shutter);
				ass_file<<pprime_val.x()<<" "<<pprime_val.y()<<" "<<pprime_val.z()<<" ";
				if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
			}
		}
	}

	ass_file<<"\n radius "<<gdp->getNumPoints()<<" 1 FLOAT\n";

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(rad_h.isValid()) rad_val = rad_h.get(ptoff);
			//rad_val *= radius;
			ass_file<<rad_val * p_radius<<" ";
			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	ass_file<<"\n mode "<<render_type<<"\n min_pixel_width 0\n step_size 0\n visibility 243\n receive_shadows on\n self_shadows on\n"
		" shader initialParticleSE\n opaque on\n matte off\n id -838484804\n";

	if(color){
		ass_file<<" declare Cd uniform RGB\n Cd "<<gdp->getNumPoints()<<" 1 RGB\n";
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				if(cd_h.isValid()) cd_val = cd_h.get(ptoff);
				ass_file<<cd_val.x()<<" "<<cd_val.y()<<" "<<cd_val.z()<<" ";
				if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
			}
		}
	}
	ass_file<<"\n}";
	ass_file.close();

	return true;
}

bool point_write_gz_file(const GU_Detail *gdp,
							 UT_String fname,
							 const char * name,
							 fpreal shutter,
							 bool motionb,
							 bool color,
							 int p_type,
							 fpreal radius)
{

	UT_String render_type("disk"); 
	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();
	fpreal p_radius = radius;
	switch(p_type)
	{
	case 0:
		render_type = "disk";
		break;
	case 1:
		render_type = "sphere";
		break;
	case 2:
		render_type = "quad";
		break;
	}



	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);


	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	GA_ROHandleF rad_h(gdp, GA_ATTRIB_POINT,"pscale");
	fpreal32 rad_val(1);

	int sample_count = motionb&&v_h.isValid()? 2:1;

	gzFile ass_file;
	ass_file = gzopen(fname,"wb");

	gzprintf(ass_file,"points\n{\n name %s",name);
	gzprintf(ass_file,"\n points %d %d b85POINT\n",gdp->getNumPoints(),sample_count);

	GA_Offset	lcl_start, lcl_end, ptoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);
			gzprintf(ass_file,"%s%s%s",encode(pos_val.x()), encode(pos_val.y()), encode(pos_val.z()));
			if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n"); 
		}
	}

	if(motionb  && v_h.isValid() ){
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				pos_val = pos_h.get(ptoff);
				if(v_h.isValid()) v_val = v_h.get(ptoff);
				pprime_val = pos_val + ((v_val / fps) * shutter);
				gzprintf(ass_file,"%s%s%s",encode(pprime_val.x()), encode(pprime_val.y()), encode(pprime_val.z()));
				if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n"); 
			}
		}
	}

	gzprintf(ass_file,"\n radius %d 1 FLOAT\n",gdp->getNumPoints());

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(rad_h.isValid()) rad_val = rad_h.get(ptoff);
			//rad_val *= radius;
			gzprintf(ass_file,"%f ",rad_val * p_radius);
			if((ptoff+1) % 300 == 0 ) gzprintf(ass_file,"\n"); 
		}
	}

	gzprintf(ass_file,"\n mode %s\n min_pixel_width 0\n step_size 0\n visibility 243\n receive_shadows on\n self_shadows on\n"
		" shader initialParticleSE\n opaque on\n matte off\n id -838484804\n",render_type.toStdString());

	if(color){
		gzprintf(ass_file," declare Cd uniform RGB\n Cd %d 1 b85RGB\n", gdp->getNumPoints() );
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				if(cd_h.isValid()) cd_val = cd_h.get(ptoff);
				gzprintf(ass_file,"%s%s%s",encode(cd_val.x()), encode(cd_val.y()), encode(cd_val.z()));
				if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n"); 
			}
		}
	}
	gzprintf(ass_file,"\n}"); 
	gzclose_w(ass_file);

	return true;
}

bool point_writer(const GU_Detail *gdp,
				  UT_String fname, 
				  const char *name, 
				  fpreal shutter,
				  bool motionb,
				  bool color,
				  int p_type,
				  fpreal radius,
				  bool use_gzip)
{
	if(!use_gzip) point_write_normal_file(gdp,fname,name,shutter,motionb,color,p_type,radius);
	else point_write_gz_file(gdp,fname,name,shutter,motionb,color,p_type,radius);

	return true;
};