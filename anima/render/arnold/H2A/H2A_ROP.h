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
*   \houdini to arnold cpp header file  
*   \author Sergen Eren
*   
*   \version 0.1
*   \date March 2016
*
*/


#ifndef __ROP_H2A_h__
#define __ROP_H2A_h__



//Houdini
#include <UT/UT_String.h>
#include <UT/UT_Vector2.h>
#include <UT/UT_Vector3.h>
#include <UT/UT_Vector4.h>
#include <UT/UT_Interrupt.h>
#include <UT/UT_DSOVersion.h>

#include <ROP/ROP_Node.h>
#include <ROP/ROP_Error.h>
#include <ROP/ROP_Templates.h>
#include <ROP/ROP_API.h>
#include <ROP/ROP_Error.h>

#include <PRM/PRM_Include.h>
#include <PRM/PRM_SpareData.h>
#include <PRM/PRM_ChoiceList.h>

#include <OP/OP_Operator.h>
#include <OP/OP_Director.h>
#include <OP/OP_OperatorTable.h>
#include <OP/OP_AutoLockInputs.h>

#include <SOP/SOP_Node.h>

#include <GU/GU_Detail.h>

#include <GA/GA_AIFTuple.h>
#include <GA/GA_Iterator.h>
#include <GA/GA_Types.h>
#include <GA/GA_AttributeFilter.h>

#include <SYS/SYS_Math.h>

namespace H2A {


	enum {
		ROP_H2A_RENDER,
		ROP_H2A_RENDERBACKGROUND,
		ROP_H2A_RENDER_CTRL,
		ROP_H2A_TRANGE,
		ROP_H2A_FRANGE,
		ROP_H2A_TAKE,
		ROP_H2A_SOPPATH,
		ROP_H2A_SOPOUTPUT,
		ROP_H2A_NAME,
		ROP_H2A_PWIDTH,
		ROP_H2A_SHUTTER,
		ROP_H2A_MODE,
		ROP_H2A_MOTIONB,
		ROP_H2A_COLOR,
		ROP_H2A_TYPE,
		ROP_H2A_P_RENDER_TYPE,
		ROP_H2A_P_RAD_MULT,
		ROP_H2A_SUBDIV_TYPE,
		ROP_H2A_SUBDIV_ITE,

		//render parameters
		ROP_H2A_INITSIM,
		ROP_H2A_MKPATH,
		ROP_H2A_ALFPROGRESS,
		ROP_H2A_TPRERENDER,
		ROP_H2A_PRERENDER,
		ROP_H2A_LPRERENDER,
		ROP_H2A_TPREFRAME,
		ROP_H2A_PREFRAME,
		ROP_H2A_LPREFRAME,
		ROP_H2A_TPOSTFRAME,
		ROP_H2A_POSTFRAME,
		ROP_H2A_LPOSTFRAME,
		ROP_H2A_TPOSTRENDER,
		ROP_H2A_POSTRENDER,
		ROP_H2A_LPOSTRENDER,

		ROP_H2A_MAXPARMS
	};

	class H2A_Rop : public ROP_Node
	{

	public:
		bool						updateParmsFlags();
		static OP_TemplatePair      *getTemplatePair();
		static OP_VariablePair      *getVariablePair();
		static PRM_Template			myTemplateList[];
		static OP_Node              *nodeConstructor( OP_Network *net, const char *name, OP_Operator *op );

	protected:

		H2A_Rop( OP_Network *net, const char *name, OP_Operator *op );

		virtual ~H2A_Rop();

	protected:

		virtual int             startRender(int nframes, fpreal s, fpreal e);
		virtual ROP_RENDER_CODE renderFrame(fpreal time, UT_Interrupt *boss);
		virtual ROP_RENDER_CODE endRender();

	private:
		void	OUTPUT(UT_String &str, fpreal t)	{ return evalString(str,"outputFile",  0, t); }
		void	SOPPATH(UT_String &str, fpreal t)	{ return evalString(str,"soppath",  0, t); }
		void	NAME(UT_String &str, fpreal t)		{ return evalString(str,"name",  0, t); }
		fpreal	PWIDTH(fpreal t) 					{ return evalFloat("min_pixel_width", 0, t); }
		fpreal  SHUTTER(fpreal t)					{ return evalFloat("shutter", 0, t);}
		int		MODE()								{ return evalInt  ("mode", 0, 0); }
		int		INITSIM()							{ return evalInt  ("initsim", 0, 0); }
		bool	MOTIONB()							{ return evalInt  ("export_motion", 0, 0); }
		bool	COLOR()								{ return evalInt  ("export_color", 0, 0); }
		int		TYPE()								{ return evalInt  ("export_type", 0, 0); }
		int		P_RENDER_TYPE()						{ return evalInt  ("prender_type", 0, 0); }
		int		SUBDIV_TYPE()						{ return evalInt  ("subdiv_type", 0, 0); }
		int		SUBDIV_ITE(fpreal t)				{ return evalInt  ("subdiv_ite", 0, 0); }
		fpreal  RADIUS(fpreal t)					{ return evalFloat("rad_mult", 0, t);}
		int		ALFPROGRESS()						{ return evalInt  ("alfprogress", 0, 0); }


		fpreal  startTime;
		fpreal  endTime;
	};
}
#endif


