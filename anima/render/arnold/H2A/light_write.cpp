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
*   \date February 2017
*
*/

#include <zlib.h>

#include <GU/GU_Detail.h>
#include <UT/UT_OFStream.h>
#include <OP/OP_Director.h>

bool light_write_normal_file(const GU_Detail *gdp, UT_String fname)
{

	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleF rad_h(gdp, GA_ATTRIB_POINT,"radius");
	fpreal32 rad_val(0);

	GA_ROHandleF exp_h(gdp, GA_ATTRIB_POINT,"exposure");
	fpreal32 exp_val(0);

	GA_Offset detail_off = GA_Offset(0);

	GA_ROHandleC cast_shdw_h(gdp, GA_ATTRIB_DETAIL,"cast_shadows");
	int8 cast_shdw(1);
	if(cast_shdw_h.isValid()) cast_shdw = cast_shdw_h.get(detail_off);

	GA_ROHandleC cast_v_shdw_h(gdp, GA_ATTRIB_DETAIL,"cast_volumetric_shadows");
	int8 cast_v_shdw(1);
	if(cast_shdw_h.isValid()) cast_v_shdw = cast_shdw_h.get(detail_off);

	GA_ROHandleF inten_h(gdp, GA_ATTRIB_DETAIL,"intensity");
	fpreal32 intensity(1);
	if(inten_h.isValid()) intensity = inten_h.get(detail_off);
	
	GA_ROHandleF shdw_den_h(gdp, GA_ATTRIB_DETAIL,"shadow_density");
	fpreal32 shdw_den(1);
	if(shdw_den_h.isValid()) shdw_den = shdw_den_h.get(detail_off);

	GA_ROHandleV3 shdw_col_h(gdp,GA_ATTRIB_DETAIL,"shadow_color");
	UT_Vector3F shdw_col(0,0,0);
	if(shdw_col_h.isValid()) shdw_col = shdw_col_h.get(detail_off);

	GA_ROHandleC sample_h(gdp, GA_ATTRIB_DETAIL,"samples");
	int8 samples(2);
	if(sample_h.isValid()) samples = sample_h.get(detail_off);

	GA_ROHandleC aff_diff_h(gdp, GA_ATTRIB_DETAIL,"affect_diffuse");
	int8 aff_diff(1);
	if(aff_diff_h.isValid()) aff_diff = aff_diff_h.get(detail_off);

	GA_ROHandleC aff_spec_h(gdp, GA_ATTRIB_DETAIL,"affect_specular");
	int8 aff_spec(1);
	if(aff_spec_h.isValid()) aff_spec = aff_spec_h.get(detail_off);

	GA_ROHandleC aff_vol_h(gdp, GA_ATTRIB_DETAIL,"affect_volumetrics");
	int8 aff_vol(1);
	if(aff_vol_h.isValid()) aff_vol = aff_vol_h.get(detail_off);

	GA_ROHandleF diff_con_h(gdp, GA_ATTRIB_DETAIL,"diffuse_contribution");
	fpreal32 diff_con(1);
	if(diff_con_h.isValid()) diff_con = diff_con_h.get(detail_off);

	GA_ROHandleF spec_con_h(gdp, GA_ATTRIB_DETAIL,"specular_contribution");
	fpreal32 spec_con(1);
	if(spec_con_h.isValid()) spec_con = spec_con_h.get(detail_off);

	GA_ROHandleF sss_con_h(gdp, GA_ATTRIB_DETAIL,"sss_contribution");
	fpreal32 sss_con(1);
	if(sss_con_h.isValid()) sss_con = sss_con_h.get(detail_off);

	GA_ROHandleF ind_con_h(gdp, GA_ATTRIB_DETAIL,"indirect_contribution");
	fpreal32 ind_con(1);
	if(ind_con_h.isValid()) ind_con = ind_con_h.get(detail_off);

	GA_ROHandleF vol_con_h(gdp, GA_ATTRIB_DETAIL,"volume_contribution");
	fpreal32 vol_con(1);
	if(vol_con_h.isValid()) vol_con = vol_con_h.get(detail_off);

	GA_ROHandleC vol_sample_h(gdp, GA_ATTRIB_DETAIL,"volume_samples");
	int8 vol_samples(2);
	if(vol_sample_h.isValid()) vol_samples = vol_sample_h.get(detail_off);

	uint max_bounces = 999; 
	uint light_shape = 0; 


	UT_OFStream ass_file(fname);
	
	GA_Offset	lcl_start, lcl_end, ptoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			
			ass_file<<"point_light\n{\n name pointLightShape "<<light_shape;
			
			if(rad_h.isValid()) rad_val = rad_h.get(ptoff);
			ass_file<<"\n radius "<<rad_val;
			ass_file<<"\n decay_type \"quadratic\"";
			ass_file<<"\n matrix\n 1 0 0 0\n 0 1 0 0\n 0 0 1 0\n";
						
			pos_val = pos_h.get(ptoff);
			ass_file<<" "<<pos_val.x()<<" "<<pos_val.y()<<" "<<pos_val.z()<<" ";
			
			if(cd_h.isValid()) cd_val = cd_h.get(ptoff);
			ass_file<<"\n color "<<cd_val.x()<<" "<<cd_val.y()<<" "<<cd_val.z()<<" ";

			ass_file<<"\n intensity "<<intensity;

			if(exp_h.isValid()) exp_val = exp_h.get(ptoff);
			ass_file<<"\n exposure "<<exp_val;

			if(cast_shdw>0) ass_file<<"\n cast_shadows on";
			else ass_file<<"\n cast_shadows off";

			if(cast_v_shdw>0) ass_file<<"\n cast_volumetric_shadows on";
			else ass_file<<"\n cast_volumetric_shadows off";

			ass_file<<"\n shadow_density "<<shdw_den;
			ass_file<<"\n shadow_color "<<shdw_col.x()<<" "<<shdw_col.y()<<" "<<shdw_col.z()<<" ";
			ass_file<<"\n samples "<<samples;
			ass_file<<"\n normalize on";
			
			if(aff_diff>0) ass_file<<"\n affect_diffuse on";
			else ass_file<<"\n affect_diffuse off";

			if(aff_spec>0) ass_file<<"\n affect_specular on";
			else ass_file<<"\n affect_specular off";

			if(aff_vol>0) ass_file<<"\n affect_volumetrics on";
			else ass_file<<"\n affect_volumetrics off";

			ass_file<<"\n diffuse "<<diff_con;
			ass_file<<"\n specular "<<spec_con;
			ass_file<<"\n sss "<<sss_con;
			ass_file<<"\n indirect "<<ind_con;
			ass_file<<"\n volume "<<vol_con;
			ass_file<<"\n volume_samples "<<vol_samples;
			ass_file<<"\n max_bounces "<<max_bounces;
			
			ass_file<<"\n}\n";
			light_shape++;
		}
	}

	ass_file.close();

	return true;
}

bool light_write_gz_file(const GU_Detail *gdp, UT_String fname)
{
		
	GA_ROHandleV3 pos_h(gdp,GA_ATTRIB_POINT,"P");
	UT_Vector3F pos_val(0,0,0);

	GA_ROHandleV3 cd_h(gdp,GA_ATTRIB_POINT,"Cd");
	UT_Vector3F cd_val(1,1,1);

	GA_ROHandleF rad_h(gdp, GA_ATTRIB_POINT,"radius");
	fpreal32 rad_val(0);

	GA_ROHandleF exp_h(gdp, GA_ATTRIB_POINT,"exposure");
	fpreal32 exp_val(0);

	GA_Offset detail_off = GA_Offset(0);

	GA_ROHandleC cast_shdw_h(gdp, GA_ATTRIB_DETAIL,"cast_shadows");
	int8 cast_shdw(1);
	if(cast_shdw_h.isValid()) cast_shdw = cast_shdw_h.get(detail_off);

	GA_ROHandleC cast_v_shdw_h(gdp, GA_ATTRIB_DETAIL,"cast_volumetric_shadows");
	int8 cast_v_shdw(1);
	if(cast_shdw_h.isValid()) cast_v_shdw = cast_shdw_h.get(detail_off);

	GA_ROHandleF inten_h(gdp, GA_ATTRIB_DETAIL,"intensity");
	fpreal32 intensity(1);
	if(inten_h.isValid()) intensity = inten_h.get(detail_off);

	GA_ROHandleF shdw_den_h(gdp, GA_ATTRIB_DETAIL,"shadow_density");
	fpreal32 shdw_den(1);
	if(shdw_den_h.isValid()) shdw_den = shdw_den_h.get(detail_off);

	GA_ROHandleV3 shdw_col_h(gdp,GA_ATTRIB_DETAIL,"shadow_color");
	UT_Vector3F shdw_col(0,0,0);
	if(shdw_col_h.isValid()) shdw_col = shdw_col_h.get(detail_off);

	GA_ROHandleC sample_h(gdp, GA_ATTRIB_DETAIL,"samples");
	int8 samples(2);
	if(sample_h.isValid()) samples = sample_h.get(detail_off);

	GA_ROHandleC aff_diff_h(gdp, GA_ATTRIB_DETAIL,"affect_diffuse");
	int8 aff_diff(1);
	if(aff_diff_h.isValid()) aff_diff = aff_diff_h.get(detail_off);

	GA_ROHandleC aff_spec_h(gdp, GA_ATTRIB_DETAIL,"affect_specular");
	int8 aff_spec(1);
	if(aff_spec_h.isValid()) aff_spec = aff_spec_h.get(detail_off);

	GA_ROHandleC aff_vol_h(gdp, GA_ATTRIB_DETAIL,"affect_volumetrics");
	int8 aff_vol(1);
	if(aff_vol_h.isValid()) aff_vol = aff_vol_h.get(detail_off);

	GA_ROHandleF diff_con_h(gdp, GA_ATTRIB_DETAIL,"diffuse_contribution");
	fpreal32 diff_con(1);
	if(diff_con_h.isValid()) diff_con = diff_con_h.get(detail_off);

	GA_ROHandleF spec_con_h(gdp, GA_ATTRIB_DETAIL,"specular_contribution");
	fpreal32 spec_con(1);
	if(spec_con_h.isValid()) spec_con = spec_con_h.get(detail_off);

	GA_ROHandleF sss_con_h(gdp, GA_ATTRIB_DETAIL,"sss_contribution");
	fpreal32 sss_con(1);
	if(sss_con_h.isValid()) sss_con = sss_con_h.get(detail_off);

	GA_ROHandleF ind_con_h(gdp, GA_ATTRIB_DETAIL,"indirect_contribution");
	fpreal32 ind_con(1);
	if(ind_con_h.isValid()) ind_con = ind_con_h.get(detail_off);

	GA_ROHandleF vol_con_h(gdp, GA_ATTRIB_DETAIL,"volume_contribution");
	fpreal32 vol_con(1);
	if(vol_con_h.isValid()) vol_con = vol_con_h.get(detail_off);

	GA_ROHandleC vol_sample_h(gdp, GA_ATTRIB_DETAIL,"volume_samples");
	int8 vol_samples(2);
	if(vol_sample_h.isValid()) vol_samples = vol_sample_h.get(detail_off);

	uint max_bounces = 999; 
	uint light_shape = 0; 

	gzFile ass_file;
	ass_file = gzopen(fname,"wb");
	
	GA_Offset	lcl_start, lcl_end, ptoff;

	for (GA_Iterator lcl_it((gdp)->getPointRange()); lcl_it.blockAdvance(lcl_start, lcl_end); ){
		for (ptoff = lcl_start; ptoff < lcl_end; ++ptoff){
			
			gzprintf(ass_file,"point_light\n{\n name pointLightShape%d",light_shape);
			
			if(rad_h.isValid()) rad_val = rad_h.get(ptoff);
			gzprintf(ass_file,"\n radius %f",rad_val);
			gzprintf(ass_file,"\n decay_type \"quadratic\"");
			gzprintf(ass_file,"\n matrix\n 1 0 0 0\n 0 1 0 0\n 0 0 1 0\n");
						
			pos_val = pos_h.get(ptoff);
			gzprintf(ass_file," %f %f %f",pos_val.x(), pos_val.y(), pos_val.z());
			
			if(cd_h.isValid()) cd_val = cd_h.get(ptoff);
			gzprintf(ass_file,"\n color %f %f %f",cd_val.x(),cd_val.y(),cd_val.z());

			gzprintf(ass_file,"\n intensity %f", intensity);

			if(exp_h.isValid()) exp_val = exp_h.get(ptoff);
			gzprintf(ass_file,"\n exposure %f",exp_val);

			if(cast_shdw>0) gzprintf(ass_file,"\n cast_shadows on");
			else gzprintf(ass_file,"\n cast_shadows off");

			if(cast_v_shdw>0) gzprintf(ass_file,"\n cast_volumetric_shadows on");
			else gzprintf(ass_file,"\n cast_volumetric_shadows off");

			gzprintf(ass_file,"\n shadow_density %f",shdw_den);
			gzprintf(ass_file,"\n shadow_color %f %f %f",shdw_col.x(), shdw_col.y(), shdw_col.z());
			gzprintf(ass_file,"\n samples %d",samples);
			gzprintf(ass_file,"\n normalize on");
			
			if(aff_diff>0) gzprintf(ass_file,"\n affect_diffuse on");
			else gzprintf(ass_file,"\n affect_diffuse off");

			if(aff_spec>0) gzprintf(ass_file,"\n affect_specular on");
			else gzprintf(ass_file,"\n affect_specular off");

			if(aff_vol>0) gzprintf(ass_file,"\n affect_volumetrics on");
			else gzprintf(ass_file,"\n affect_volumetrics off");

			gzprintf(ass_file,"\n diffuse %f",diff_con);
			gzprintf(ass_file,"\n specular %f",spec_con);
			gzprintf(ass_file,"\n sss %f",sss_con);
			gzprintf(ass_file,"\n indirect %f",ind_con);
			gzprintf(ass_file,"\n volume %f",vol_con);
			gzprintf(ass_file,"\n volume_samples %d",vol_samples);
			gzprintf(ass_file,"\n max_bounces %d",max_bounces);
			
			gzprintf(ass_file,"\n}\n");
			light_shape++;
		}
	}

	gzclose_w(ass_file);

	return true;



}

bool light_writer(const GU_Detail *gdp,
				  UT_String fname,
				  bool use_gzip)
{
	if(!use_gzip) light_write_normal_file(gdp,fname);
	else light_write_gz_file(gdp,fname);

	return true;
};