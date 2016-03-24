/*******************************************************************************
* -*- coding: utf-8 -*-
* Copyright (c) 2012-2016, Anima Istanbul
*
* This module is part of anima-tools and is released under the BSD 2
* License: http://www.opensource.org/licenses/BSD-2-Clause
*
/********************************************************************************/

/*! \file
*
*   \poly ass exporter  
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

bool poly_write_normal_file(const GU_Detail *gdp,
							 UT_String fname,
							 const char * name,
							 fpreal shutter,
							 bool motionb,
							 bool color)
{
	int sample_count = motionb? 2:1;
	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();


	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);

	GA_ROHandleV3 uv_h(gdp,GA_ATTRIB_POINT,"uv");
	UT_Vector3F uv_val(0,0,0);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	UT_OFStream ass_file(fname);

	ass_file<<"polymesh\n{\n name "<<name;
	ass_file<<"\n nsides "<<gdp->getNumPrimitives()<<" 1 UINT\n";

	const GA_Primitive *prim;
	GA_Offset prim_off;

	for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
		prim = gdp->getPrimitive(*p_it);
		ass_file<<prim->getVertexCount()<<" ";
		if((*p_it+1) % 300 == 0) ass_file<<"\n"; 
	}

	ass_file<<"\n vidxs "<<gdp->getNumVertices()<<" 1 UINT\n";
	for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
		prim_off = p_it.getOffset();
		prim = gdp->getPrimitive(prim_off);
		for(GA_Iterator v_it(prim->getVertexRange()); !v_it.atEnd(); ++v_it){
			ass_file<<gdp->vertexPoint(v_it.getOffset())<<" ";	
		}
		if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
	}


	ass_file<<"\n vlist "<<gdp->getNumPoints()<<" "<<sample_count<<" POINT\n";

	GA_Offset	lcl_start, lcl_end, ptoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);
			ass_file<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";
			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	if(motionb){
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

	ass_file<<"\n smoothing on\n visibility 255\n sidedness 255\n invert normals off\n receive_shadows on\n self_shadows on\n"
		" opaque on\n matrix\n1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n";

	if(motionb) ass_file<<"1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n";
	ass_file<<"id 683108022";


	ass_file<<"\n declare uparamcoord uniform FLOAT\n uparamcoord "<<gdp->getNumPrimitives()<<" 1 FLOAT\n";
	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(uv_h.isValid()) uv_val = uv_h.get(ptoff);
			ass_file<<uv_val.x()<<" ";
			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	ass_file<<"\n declare vparamcoord uniform FLOAT\n vparamcoord "<<gdp->getNumPrimitives()<<" 1 FLOAT\n";
	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(uv_h.isValid()) uv_val = uv_h.get(ptoff);
			ass_file<<uv_val.y()<<" ";
			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
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



bool poly_write_gz_file(const GU_Detail *gdp,
							 UT_String fname,
							 const char * name,
							 fpreal shutter,
							 bool motionb,
							 bool color)
{
	int sample_count = motionb? 2:1;
	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();


	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);

	GA_ROHandleV3 uv_h(gdp,GA_ATTRIB_POINT,"uv");
	UT_Vector3F uv_val(0,0,0);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	gzFile ass_file;
	ass_file = gzopen(fname,"wb");

	gzprintf(ass_file, "polymesh\n{\n name %s", name);
	gzprintf(ass_file, "\n nsides %d 1 UINT\n", gdp->getNumPrimitives());

	const GA_Primitive *prim;
	GA_Offset prim_off;

	for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
		prim_off = p_it.getOffset();
		prim = gdp->getPrimitive(prim_off);
		gzprintf(ass_file," %d", prim->getVertexCount());
		if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n"); 
	}

	gzprintf(ass_file, "\n vidxs %d 1 UINT\n",gdp->getNumVertices());
	for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
		prim_off = p_it.getOffset();
		prim = gdp->getPrimitive(prim_off);
		for(GA_Iterator v_it(prim->getVertexRange()); !v_it.atEnd(); ++v_it){
			gzprintf(ass_file,"%d ",gdp->vertexPoint(v_it.getOffset()));
		}
		if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n");
	}


	gzprintf(ass_file,"\n vlist %d %d b85POINT\n",gdp->getNumPoints(),sample_count);

	GA_Offset	lcl_start, lcl_end, ptoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);
			gzprintf(ass_file,"%s%s%s",encode(pos_val.x()), encode(pos_val.y()), encode(pos_val.z()));
			if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n");
		}
	}

	if(motionb){
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

	gzprintf(ass_file,"\n smoothing on\n visibility 255\n sidedness 255\n invert normals off\n receive_shadows on\n self_shadows on\n"
		" opaque on\n matrix\n1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n");

	if(motionb) gzprintf(ass_file,"1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n");
	gzprintf(ass_file,"id 683108022\n");

	gzprintf(ass_file,"\n declare uparamcoord uniform FLOAT\n uparamcoord %d 1 b85FLOAT\n", gdp->getNumPrimitives());
	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(uv_h.isValid()) uv_val = uv_h.get(ptoff);
			gzprintf(ass_file,"%s",encode(uv_val.x()));
			if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n");
		}
	}

	gzprintf(ass_file,"\n declare vparamcoord uniform FLOAT\n vparamcoord %d 1 b85FLOAT\n", gdp->getNumPrimitives());
	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			if(uv_h.isValid()) uv_val = uv_h.get(ptoff);
			gzprintf(ass_file,"%s",encode(uv_val.y()));
			if((ptoff+1) % 300 == 0) gzprintf(ass_file,"\n");
		}
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


bool poly_writer(const GU_Detail *gdp,
				  UT_String fname, 
				  const char *name,
				  fpreal shutter,
				  bool motionb,
				  bool color,
				  bool use_gzip)
{
	if(!use_gzip) poly_write_normal_file(gdp,fname,name,shutter,motionb,color);
	else poly_write_gz_file(gdp,fname,name,shutter,motionb,color);

	return true;
};