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
*   \poly ass exporter  
*   \author Sergen Eren
*   
*   \version 1.0
*   \date March 2016
*
*/

#include <base_85.cpp>
#include <zlib.h>
#include <vector>

#include <GU/GU_Detail.h>
#include <UT/UT_OFStream.h>
#include <OP/OP_Director.h>

using namespace b85;

bool poly_write_normal_file(const GU_Detail *gdp,
							UT_String fname,
							const char * name,
							fpreal shutter,
							bool motionb,
							bool color,
							int subdiv_type,
							int subdiv_ite)
{

	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();


	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);

	GA_ROHandleV3 uv_h(gdp,GA_ATTRIB_VERTEX,"uv");
	UT_Vector3F uv_val(0,0,0);

	GA_ROHandleV3 n_h(gdp,GA_ATTRIB_VERTEX,"N");
	UT_Vector3F n_val(0,0,0);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	int sample_count = motionb&&v_h.isValid()? 2:1;

	const GA_Primitive *prim;
	GA_Offset prim_off,lcl_start, lcl_end, ptoff;
	GA_Primitive::const_iterator vertex_it;

	UT_OFStream ass_file(fname);
	ass_file<<"polymesh\n{\n name "<<name;
	ass_file<<"\n nsides "<<gdp->getNumPrimitives()<<" 1 UINT\n";

	for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
		prim = gdp->getPrimitive(*p_it);
		ass_file<<prim->getVertexCount()<<" ";
		if((*p_it+1) % 300 == 0) ass_file<<"\n"; 
	}

	ass_file<<"\n vidxs "<<gdp->getNumVertices()<<" 1 UINT\n";


	//Reverse iteration

	for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
		prim_off = p_it.getOffset();
		prim = gdp->getPrimitive(prim_off);
		std::vector<int> idx;  
		for(GA_Iterator v_it(prim->getVertexRange()); !v_it.atEnd(); ++v_it){
			idx.push_back(gdp->pointIndex(gdp->vertexPoint(v_it.getOffset())));	
		}

		for(std::vector<int>::reverse_iterator r_it = idx.rbegin(); r_it!=idx.rend();++r_it) ass_file<<*r_it<<" ";
		idx.clear();
		if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
	}

	ass_file<<"\n vlist "<<gdp->getNumPoints()<<" "<<sample_count<<" POINT\n";

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			pos_val = pos_h.get(ptoff);
			ass_file<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";
			if((ptoff+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	if(motionb && v_h.isValid()){
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


	if(n_h.isValid()){

		ass_file<<"\n nidxs "<<gdp->getNumVertices()<<" 1 UINT\n";
		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			for(GA_Iterator v_it(prim->getVertexRange()); !v_it.atEnd(); ++v_it){
				ass_file<<gdp->vertexIndex(v_it.getOffset())<<" ";
			}
			if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
		}

		ass_file<<"\n nlist "<<gdp->getNumVertices()<<" "<<sample_count<<" VECTOR\n";

		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			std::vector<UT_Vector3F> nidx;
			for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
				n_val = n_h(vertex_it.getVertexOffset());
				nidx.push_back(n_val); 
			}
			for(std::vector<UT_Vector3F>::reverse_iterator r_it = nidx.rbegin(); r_it!=nidx.rend();++r_it){
				UT_Vector3F val = *r_it;
				ass_file<<val.x()<<" "<<val.y()<<" "<<val.z()<<" "; 
			}
			nidx.clear();
			if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
		}

		if(motionb){
			for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
				prim_off = p_it.getOffset();
				prim = gdp->getPrimitive(prim_off);
				std::vector<UT_Vector3F> nidx;
				for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
					n_val = n_h(vertex_it.getVertexOffset());
					nidx.push_back(n_val); 
				}
				for(std::vector<UT_Vector3F>::reverse_iterator r_it = nidx.rbegin(); r_it!=nidx.rend();++r_it){
					UT_Vector3F val = *r_it;
					ass_file<<val.x()<<" "<<val.y()<<" "<<val.z()<<" ";
				}
				nidx.clear();
				if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
			}	
		}
	}


	if(uv_h.isValid()){
		ass_file<<"\n uvidxs "<<gdp->getNumVertices()<<" 1 UINT\n";
		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
				ass_file<<gdp->vertexIndex(vertex_it.getVertexOffset())<<" ";	
			}
			if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
		}
		ass_file<<"\n uvlist "<<gdp->getNumVertices()<<" 1 POINT2\n";

		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			std::vector<UT_Vector3F> uvidx;
			for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
				uv_val = uv_h(vertex_it.getVertexOffset());
				uvidx.push_back(uv_val);	
			}
			for(std::vector<UT_Vector3F>::reverse_iterator r_it = uvidx.rbegin(); r_it!=uvidx.rend();++r_it){
				UT_Vector3F val = *r_it;
				ass_file<<val.x()<<" "<<val.y()<<" "; 
			}
			uvidx.clear();
			if((prim_off+1) % 300 == 0) ass_file<<"\n"; 
		}
	}

	ass_file<<"\n smoothing on\n"; 
	switch (subdiv_type)
	{
	case 0: // none
		break;
	case 1: // cat-clark
		ass_file<<" subdiv_type \"catclark\"\n";
		break;
	case 2: // linear
		ass_file<<" subdiv_type \"linear\"\n";
		break;
	}
	if(subdiv_ite>1) ass_file<<" subdiv_iterations "<<subdiv_ite<<"\n";
	ass_file<<" visibility 255\n sidedness 255\n invert_normals off\n receive_shadows on\n self_shadows on\n"
		" opaque on\n matrix\n1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n";

	if(motionb) ass_file<<"1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n";
	ass_file<<"id 683108022";


	if(color && cd_h.isValid()){
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
						bool color,
						int subdiv_type,
						int subdiv_ite)
{

	fpreal fps = OPgetDirector()->getChannelManager()->getSamplesPerSec();


	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);
	UT_Vector3F pprime_val(0,0,0);

	GA_ROHandleV3 uv_h(gdp,GA_ATTRIB_VERTEX,"uv");
	UT_Vector3F uv_val(0,0,0);

	GA_ROHandleV3 n_h(gdp,GA_ATTRIB_VERTEX,"N");
	UT_Vector3F n_val(0,0,0);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleV3 v_h(gdp,GA_ATTRIB_POINT,"v");
	UT_Vector3F v_val(0,0,0);

	const GA_Primitive *prim;
	GA_Offset prim_off,lcl_start, lcl_end, ptoff;
	GA_Primitive::const_iterator vertex_it;

	int sample_count = motionb&&v_h.isValid()? 2:1;

	gzFile ass_file;
	ass_file = gzopen(fname,"wb");

	gzprintf(ass_file, "polymesh\n{\n name %s", name);
	gzprintf(ass_file, "\n nsides %d 1 UINT\n", gdp->getNumPrimitives());


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
		std::vector<int> idx;  
		for(GA_Iterator v_it(prim->getVertexRange()); !v_it.atEnd(); ++v_it){
			idx.push_back(gdp->pointIndex(gdp->vertexPoint(v_it.getOffset())));	
		}

		for(std::vector<int>::reverse_iterator r_it = idx.rbegin(); r_it!=idx.rend();++r_it) gzprintf(ass_file,"%d ",*r_it);
		idx.clear();
		if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n"); 
	}


	gzprintf(ass_file,"\n vlist %d %d b85POINT\n",gdp->getNumPoints(),sample_count);

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


	if(n_h.isValid()){

		gzprintf(ass_file,"\n nidxs %d 1 UINT\n",gdp->getNumVertices());
		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			for(GA_Iterator v_it(prim->getVertexRange()); !v_it.atEnd(); ++v_it){
				gzprintf(ass_file,"%d ",gdp->vertexIndex(v_it.getOffset()));
			}
			if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n");
		}

		gzprintf(ass_file, "\n nlist %d %d b85VECTOR\n",gdp->getNumVertices(),sample_count);

		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			std::vector<UT_Vector3F> nidx;
			for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
				n_val = n_h(vertex_it.getVertexOffset());
				nidx.push_back(n_val); 
			}
			for(std::vector<UT_Vector3F>::reverse_iterator r_it = nidx.rbegin(); r_it!=nidx.rend();++r_it){
				UT_Vector3F val = *r_it;
				gzprintf(ass_file,"%s%s%s",encode(val.x()),encode(val.y()),encode(val.z())); 
			}
			nidx.clear();
			if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n");
		}

		if(motionb){
			for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
				prim_off = p_it.getOffset();
				prim = gdp->getPrimitive(prim_off);
				std::vector<UT_Vector3F> nidx;
				for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
					n_val = n_h(vertex_it.getVertexOffset());
					nidx.push_back(n_val); 
				}
				for(std::vector<UT_Vector3F>::reverse_iterator r_it = nidx.rbegin(); r_it!=nidx.rend();++r_it){
					UT_Vector3F val = *r_it;
					gzprintf(ass_file,"%s%s%s",encode(val.x()),encode(val.y()),encode(val.z())); 
				}
				nidx.clear();
				if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n");
			}	
		}
	}

	if(uv_h.isValid()){
		gzprintf(ass_file,"\n uvidxs %d 1 UINT\n",gdp->getNumVertices());
		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
				gzprintf(ass_file,"%d ",gdp->vertexIndex(vertex_it.getVertexOffset()));	
			}
			if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n"); 
		}
		gzprintf(ass_file,"\n uvlist %d 1 b85POINT2\n",gdp->getNumVertices());

		for(GA_Iterator p_it(gdp->getPrimitiveRange()); !p_it.atEnd();++p_it){
			prim_off = p_it.getOffset();
			prim = gdp->getPrimitive(prim_off);
			std::vector<UT_Vector3F> uvidx;
			for(prim->beginVertex(vertex_it); !vertex_it.atEnd(); ++vertex_it){
				uv_val = uv_h(vertex_it.getVertexOffset());
				uvidx.push_back(uv_val);	
			}
			for(std::vector<UT_Vector3F>::reverse_iterator r_it = uvidx.rbegin(); r_it!=uvidx.rend();++r_it){
				UT_Vector3F val = *r_it;
				gzprintf(ass_file,"%s%s",encode(val.x()),encode(val.y())); 
			}
			uvidx.clear();
			if((prim_off+1) % 300 == 0) gzprintf(ass_file,"\n"); 
		}
	}

	gzprintf(ass_file,"\n smoothing on\n"); 
	
	switch (subdiv_type)
	{
	case 0: // none
		break;
	case 1: // cat-clark
		gzprintf(ass_file," subdiv_type \"catclark\"\n");
		break;
	case 2: // linear
		gzprintf(ass_file," subdiv_type \"linear\"\n");
		break;
	}
	
	if(subdiv_ite>1) gzprintf(ass_file," subdiv_iterations %d \n", subdiv_ite);
	gzprintf(ass_file, " visibility 255\n sidedness 255\n invert_normals off\n receive_shadows on\n self_shadows on\n"
		" opaque on\n matrix\n1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n");

	if(motionb) gzprintf(ass_file,"1 0 0 0\n0 1 0 0\n0 0 1 0\n0 0 0 1\n");
	gzprintf(ass_file,"id 683108022\n");

	if(color&&cd_h.isValid()){
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
				 int subdiv_type,
				 int subdiv_ite,
				 bool use_gzip)
{
	if(!use_gzip) poly_write_normal_file(gdp,fname,name,shutter,motionb,color,subdiv_type,subdiv_ite);
	else poly_write_gz_file(gdp,fname,name,shutter,motionb,color,subdiv_type,subdiv_ite);

	return true;
};