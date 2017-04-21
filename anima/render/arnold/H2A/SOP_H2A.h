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
*   \houdini to arnold ass exporter header
*   \author Sergen Eren
*   
*   \version 1.0
*   \date June 2015
*
*/


#ifndef __H2A_h__
#define __H2A_h__

#include <SOP/SOP_Node.h>
#include <UT/UT_ThreadedAlgorithm.h>
#include <GU/GU_Detail.h>
#include <GA/GA_PageHandle.h>

namespace H2A {

	class SOP_h2a : public SOP_Node
	{
	public:

		//constructors and destructor
		static OP_Node		*myConstructor(OP_Network*, const char *, OP_Operator *);

		static PRM_Template		 myTemplateList[];
		void				     setColor();

	protected:

		SOP_h2a(OP_Network *net, const char *name, OP_Operator *op);
		virtual ~SOP_h2a();

		virtual OP_ERROR		 cookMySop(OP_Context &context);
		virtual const char       *inputLabel(unsigned idx) const;
		static int				 fileWriter(void *data, int index, float time, const PRM_Template *tplate); 
		

		bool shouldmultithread(const GU_Detail *gdp){ return gdp->getNumPoints() >= 1000;}

		THREADED_METHOD3(SOP_h2a, shouldmultithread(gdp) , write, GU_Detail*, gdp , const GA_SplittableRange &, range, GA_RWPageHandleV3 & , v);

		virtual void writePartial(GU_Detail * gdp, const GA_SplittableRange &range, GA_RWPageHandleV3 &v, const UT_JobInfo &jobInfo);


	private:

		//parameter accessors

		void	OUTPUT(UT_String &str, fpreal t)	{ return evalString(str,"outputFile",  0, t); }
		void	NAME(UT_String &str, fpreal t)	{ return evalString(str,"name",  0, t); }
		fpreal	PWIDTH(fpreal t) 		{ return evalFloat("min_pixel_width", 0, t); }
		fpreal  SHUTTER(fpreal t)		{ return evalFloat("shutter speed", 0, t);}
		int		MODE()					{ return evalInt  ("mode", 0, 0); }
		int		MOTIONB()				{ return evalInt  ("export_motion", 0, 0); }
		int		COLOR()					{ return evalInt  ("export_color", 0, 0); }
		int		TYPE()					{ return evalInt  ("export_type", 0, 0); }
		const GA_PointGroup *myGroup;
		
	};
} // End namespace

#endif