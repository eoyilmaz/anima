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
*   \curve ass exporter  
*   \author Sergen Eren
*   
*   \version 1.1
*   \date March 2016
*
*/

#include <base_85.cpp>
#include <zlib.h>

#include <GU/GU_Detail.h>
#include <UT/UT_OFStream.h>
#include <OP/OP_Director.h>

using namespace b85;

bool curve_write_normal_file(const GU_Detail *gdp,
							 UT_String fname,
							 const char * name,
							 fpreal pwidth,
							 fpreal shutter,
							 int mode,
							 bool motionb,
							 bool color)
{

	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();


	int number_of_curves = gdp->getNumPrimitives();
	int real_point_count = gdp->getNumPoints();

	int point_count = real_point_count + number_of_curves * 2;

	int real_number_of_points_in_one_curve = real_point_count / number_of_curves;
	int number_of_points_in_one_curve = real_number_of_points_in_one_curve + 2;

	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);

	GA_ROHandleF width_h(gdp, GA_ATTRIB_POINT,"width");
	fpreal32 width_val(0.1);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 uv_h(gdp,GA_ATTRIB_PRIMITIVE,"uv");
	UT_Vector3F uv_val(0,0,0);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	int sample_count = motionb&&v_h.isValid()? 2:1;

	UT_OFStream ass_file(fname);

	ass_file<<"curves\n{\n name "<<name;
	ass_file<<"\n num_points "<<number_of_curves<<" "<<sample_count<<" UINT\n";

	for(int i=0; i<number_of_curves; i++){
		ass_file<<number_of_points_in_one_curve<<" ";
		if(motionb) ass_file<<number_of_points_in_one_curve<<" ";
		if(i+1 % 300 == 0) ass_file<<"\n";
	}

	ass_file<<"\n points "<<point_count<<" "<<sample_count<<" POINT\n";

	GA_Offset	lcl_start, lcl_end, ptoff, primoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);

			if(ptoff % real_number_of_points_in_one_curve == 0) ass_file<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";
			ass_file<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";
			if(ptoff % real_number_of_points_in_one_curve == real_number_of_points_in_one_curve - 1) ass_file<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";

			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	if(motionb  && v_h.isValid() ){
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				pos_val = pos_h.get(ptoff);
				if(v_h.isValid()) v_val = v_h.get(ptoff);
				pprime_val = pos_val + ((v_val / fps) * shutter);

				if(ptoff % real_number_of_points_in_one_curve == 0) ass_file<<pprime_val.x()<<" "<<pprime_val.y()<<" "<<pprime_val.z()<<" ";
				ass_file<<pprime_val.x()<<" "<<pprime_val.y()<<" "<<pprime_val.z()<<" ";
				if(ptoff % real_number_of_points_in_one_curve == real_number_of_points_in_one_curve - 1) ass_file<<pprime_val.x()<<" "<<pprime_val.y()<<" "<<pprime_val.z()<<" ";

				if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
			}
		}
	}

	ass_file<<"\n radius "<<real_point_count<<" 1 FLOAT\n";

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(width_h.isValid()) width_val = width_h.get(ptoff);
			ass_file<<width_val<<" ";
			if((ptoff+1) % 300 == 0 ) ass_file<<"\n"; 
		}
	}

	ass_file<<"\n basis catmull-rom\n mode "<<mode<<"\n min_pixel_width "<< pwidth <<"\n visibility 65535\n receive_shadows on\n self_shadows on\n"
		" matrix 1 "<<sample_count<<" MATRIX\n1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n";

	if(motionb) ass_file<<"1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n";
	ass_file<<"opaque on";


	if (uv_h.isValid()) {
		ass_file << "\n declare uparamcoord uniform FLOAT\n uparamcoord " << number_of_curves << " 1 FLOAT\n";
		for (GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd(); ++p_it) {
			primoff = p_it.getOffset();
			if (uv_h.isValid()) uv_val = uv_h.get(primoff);
			ass_file << uv_val.x() << " ";
			if ((primoff + 1) % 300 == 0) ass_file << "\n";
		}
		ass_file << "\n declare vparamcoord uniform FLOAT\n vparamcoord " << number_of_curves << " 1 FLOAT\n";
		for (GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd(); ++p_it) {
			primoff = p_it.getOffset();
			if (uv_h.isValid()) uv_val = uv_h.get(primoff);
			ass_file << uv_val.y() << " ";
			if ((primoff + 1) % 300 == 0) ass_file << "\n";
		}
	}

	ass_file<<"\n declare curve_id uniform UINT\n curve_id "<<number_of_curves<<" 1 UINT\n";

	for(int i=0; i<number_of_curves; i++){
		ass_file<<i<<" ";
		if(i+1 % 300 == 0) ass_file<<"\n";
	}

	if(color){
		ass_file<<"\n declare Cd varying RGBA\n Cd "<<gdp->getNumPoints()<<" 1 RGBA\n";
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				if(cd_h.isValid()) cd_val = cd_h.get(ptoff);
				ass_file<<cd_val.x()<<" "<<cd_val.y()<<" "<<cd_val.z()<<" "<<1<<" ";
				if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
			}
		}
	}

	ass_file<<"\n}";
	ass_file.close();

	return true;
}


bool curve_write_gz_file(const GU_Detail *gdp,
						 UT_String fname,
						 const char * name,
						 fpreal pwidth,
						 fpreal shutter,
						 int mode,
						 bool motionb,
						 bool color)
{

	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();


	int number_of_curves = gdp->getNumPrimitives();
	int real_point_count = gdp->getNumPoints();

	int point_count = real_point_count + number_of_curves * 2;

	int real_number_of_points_in_one_curve = real_point_count / number_of_curves;
	int number_of_points_in_one_curve = real_number_of_points_in_one_curve + 2;

	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);

	GA_ROHandleF width_h(gdp, GA_ATTRIB_POINT,"width");
	fpreal32 width_val(0.1);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 uv_h(gdp, GA_ATTRIB_PRIMITIVE, "uv");
	UT_Vector3F uv_val(0,0,0);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	int sample_count = motionb&&v_h.isValid()? 2:1;

	gzFile ass_file;
	ass_file = gzopen(fname,"wb");

	gzprintf(ass_file,"curves\n{\n name %s",name);
	gzprintf(ass_file,"\n num_points %d %d UINT\n",number_of_curves,sample_count);

	for(int i=0; i<number_of_curves; i++){
		gzprintf(ass_file,"%d ",number_of_points_in_one_curve);
		if(motionb) gzprintf(ass_file,"%d ",number_of_points_in_one_curve);
		if(i+1 % 300 == 0) gzprintf(ass_file,"\n");
	}

	gzprintf(ass_file,"\n points %d %d b85POINT\n",point_count,sample_count);

	GA_Offset	lcl_start, lcl_end, ptoff, primoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);

			if(ptoff % real_number_of_points_in_one_curve == 0) gzprintf(ass_file,"%s%s%s",encode(pos_val.x()), encode(pos_val.y()), encode(pos_val.z()));
			gzprintf(ass_file,"%s%s%s",encode(pos_val.x()), encode(pos_val.y()), encode(pos_val.z()));
			if(ptoff % real_number_of_points_in_one_curve == real_number_of_points_in_one_curve - 1) gzprintf(ass_file,"%s%s%s",encode(pos_val.x()), encode(pos_val.y()), encode(pos_val.z()));

			if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n");
		}
	}

	if(motionb  && v_h.isValid() ){
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				pos_val = pos_h.get(ptoff);
				if(v_h.isValid()) v_val = v_h.get(ptoff);
				pprime_val = pos_val + ((v_val / fps) * shutter);

				if(ptoff % real_number_of_points_in_one_curve == 0) gzprintf(ass_file,"%s%s%s",encode(pprime_val.x()), encode(pprime_val.y()), encode(pprime_val.z()));
				gzprintf(ass_file,"%s%s%s",encode(pprime_val.x()), encode(pprime_val.y()), encode(pprime_val.z()));
				if(ptoff % real_number_of_points_in_one_curve == real_number_of_points_in_one_curve - 1) gzprintf(ass_file,"%s%s%s",encode(pprime_val.x()), encode(pprime_val.y()), encode(pprime_val.z()));

				if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n");
			}
		}
	}

	gzprintf(ass_file,"\n radius %d 1 b85FLOAT\n",real_point_count);

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(width_h.isValid()) width_val = width_h.get(ptoff);
			gzprintf(ass_file,"%s",encode(width_val));
			if((ptoff+1) % 300 == 0 ) gzprintf(ass_file,"\n");
		}
	}

	gzprintf(ass_file,"\n basis catmull-rom\n mode %d\n min_pixel_width %f\n visibility 65535\n receive_shadows on\n self_shadows on\n"
		" matrix 1 %d MATRIX\n1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n",mode,pwidth,sample_count);

	if(motionb) gzprintf(ass_file,"1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n");
	gzprintf(ass_file,"opaque on");


	if (uv_h.isValid()) {
		gzprintf(ass_file, "\n declare uparamcoord uniform FLOAT\n uparamcoord %d 1 b85FLOAT\n", number_of_curves);
		for (GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd(); ++p_it) {
			primoff = p_it.getOffset();
			if (uv_h.isValid()) uv_val = uv_h.get(primoff);
			gzprintf(ass_file, "%s", encode(uv_val.x()));
			if ((primoff + 1) % 300 == 0) gzprintf(ass_file, "\n");
		}
		gzprintf(ass_file, "\n declare vparamcoord uniform FLOAT\n vparamcoord %d 1 b85FLOAT\n", number_of_curves);
		for (GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd(); ++p_it) {
			primoff = p_it.getOffset();
			if (uv_h.isValid()) uv_val = uv_h.get(primoff);
			gzprintf(ass_file, "%s", encode(uv_val.y()));
			if ((primoff + 1) % 300 == 0) gzprintf(ass_file, "\n");
		}
	}

	gzprintf(ass_file,"\n declare curve_id uniform UINT\n curve_id %d 1 UINT\n",number_of_curves);

	for(int i=0; i<number_of_curves; i++){
		gzprintf(ass_file,"%d ",i);
		if(i+1 % 300 == 0) gzprintf(ass_file,"\n");
	}

	if(color){
		gzprintf(ass_file," declare Cd varying RGBA\n Cd %d 1 b85RGBA\n", gdp->getNumPoints() );
		for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
			for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
				if(cd_h.isValid()) cd_val = cd_h.get(ptoff);
				gzprintf(ass_file,"%s%s%s%s",encode(cd_val.x()), encode(cd_val.y()), encode(cd_val.z()), encode(1.0));
				if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n"); 
			}
		}
	}

	gzprintf(ass_file,"\n}"); 
	gzclose_w(ass_file);

	return true;
}

bool curve_writer(const GU_Detail *gdp,
				  UT_String fname, 
				  const char *name,
				  fpreal pwidth,
				  fpreal shutter,
				  int mode,
				  bool motionb,
				  bool color,
				  bool use_gzip)
{
	if(!use_gzip) curve_write_normal_file(gdp, fname, name, pwidth, shutter, mode, motionb, color);
	else curve_write_gz_file(gdp, fname, name, pwidth, shutter, mode, motionb, color);

	return true;
};