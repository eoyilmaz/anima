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
*   \houdini to arnold cpp ROP node implementation  
*   \author Sergen Eren
*   
*   \version 0.1
*   \date March 2016
*
*/

//Headers
#include <H2A_ROP.h>
#include <h2a_io.h>

#define PRM_MENU_CHOICES	(PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE | PRM_CHOICELIST_REPLACE)


using namespace H2A;
using namespace std;

// Custom template list

static PRM_Name names[] = {
	PRM_Name("outputFile",     "Output File"),
	PRM_Name("soppath", "SOP Path"),
	PRM_Name("name",   "Name"),
	PRM_Name("min_pixel_width",  "Min Pixel Width"),
	PRM_Name("shutter", "Shutter Speed"),
	PRM_Name("export_motion",  "Export Motion Blur"),
	PRM_Name("export_color",  "Export Color"),
	PRM_Name("export_type",  "Export Type"),
	PRM_Name("mode",  "Mode"),
	PRM_Name("prender_type",  "Particle Render Type"),
	PRM_Name("rad_mult",  "Radius Multiplier"),
	PRM_Name("subdiv_type",  "Subdivision Type"),
	PRM_Name("subdiv_ite",  "Iterations"),
};

static PRM_Default	 theFileDefault(0, "$HIP/Outputs/ass/defgeo.ass.gz");
const char *nameName = "`$OS`"; 
static PRM_Default	 theNameDefault(0, nameName);

static PRM_Name		sopOpMenuNames[] = {
	PRM_Name("ribbon",	"Ribbon"),
	PRM_Name("thick",	"Thick"),
	PRM_Name("oriented", "Oriented"),
	PRM_Name(0)
};

static PRM_Name		sopTypeMenuNames[] = {
	PRM_Name("curves",	"Curves"),
	PRM_Name("polygon",	"Polygon"),
	PRM_Name("particle","Particles"),
	PRM_Name("light","Lights"),
	PRM_Name(0)
};

static PRM_Name		pRenderTypeMenuNames[] = {
	PRM_Name("disk",	"Point"),
	PRM_Name("sphere",	"Sphere"),
	PRM_Name("quad",	"Quad"),
	PRM_Name(0)
};


static PRM_Name		subDivTypeMenuNames[] = {
	PRM_Name("none",	"None"),
	PRM_Name("cclark",	"Cat_Clark"),
	PRM_Name("linear",	"Linear"),
	PRM_Name(0)
};

static PRM_ChoiceList	sopOpMenu(PRM_MENU_CHOICES,	sopOpMenuNames);
static PRM_ChoiceList	sopTypeMenu(PRM_MENU_CHOICES,	sopTypeMenuNames);
static PRM_ChoiceList	pRenderTypeMenu(PRM_MENU_CHOICES,	pRenderTypeMenuNames);
static PRM_ChoiceList	subdivTypeMenu(PRM_MENU_CHOICES,	subDivTypeMenuNames);

PRM_Template H2A_Rop::myTemplateList[] = {
	PRM_Template(PRM_FILE_E,	1, &names[0], &theFileDefault , 0, 0 , 0 ,  &PRM_SpareData::fileChooserModeWrite),	// file Output
	PRM_Template(PRM_STRING, PRM_TYPE_DYNAMIC_PATH, 1, &names[1], 0, 0, 0, 0, &PRM_SpareData::sopPath ),			// sop path
	PRM_Template(PRM_STRING,	1, &names[2], &theNameDefault),														// Name
	PRM_Template(PRM_FLT_J, PRM_Template::PRM_EXPORT_TBX, 1, &names[3], PRMpointFiveDefaults),						// min pixel width
	PRM_Template(PRM_FLT_J, PRM_Template::PRM_EXPORT_TBX, 1, &names[4], PRMpointFiveDefaults),						// shutter speed
	PRM_Template(PRM_TOGGLE,    1, &names[5], PRMoneDefaults),														// motion blur ? 
	PRM_Template(PRM_TOGGLE,    1, &names[6], PRMoneDefaults),														// export color ? 
	PRM_Template((PRM_Type) PRM_ORD, PRM_Template::PRM_EXPORT_MIN, 1, &names[7], 0, &sopTypeMenu),					// polygon, curve, point?
	PRM_Template((PRM_Type) PRM_ORD, PRM_Template::PRM_EXPORT_MAX, 1, &names[8], 0, &sopOpMenu),					// export mode for curves
	PRM_Template((PRM_Type) PRM_ORD, PRM_Template::PRM_EXPORT_MIN, 1, &names[9], 0, &pRenderTypeMenu),				// disk, sphere, quad render for particles
	PRM_Template(PRM_FLT_J, PRM_Template::PRM_EXPORT_TBX, 1, &names[10], PRMoneDefaults),							// global point radius multiplier
	PRM_Template((PRM_Type) PRM_ORD, PRM_Template::PRM_EXPORT_MIN, 1, &names[11], 0, &subdivTypeMenu),				// subdivision type
	PRM_Template(PRM_INT, 1, &names[12], PRMoneDefaults),															// subdivision iterations
	PRM_Template()																									// placeholder
};

// End custom template list

static PRM_Name         MKPATH_PRM_NAME( "mkpath", "Create Intermediate Directories" );
static PRM_Name         INITSIM_PRM_NAME( "initsim", "Initialize Simulation OPs" );
static PRM_Name         ALFPROGRESS_PRM_NAME( "alfprogress", "Alfred Style Progress" );

static PRM_Template * getTemplates()
{
	static PRM_Template *prmTemplate        = 0;

	if( prmTemplate )
	{
		return prmTemplate;
	}

	prmTemplate                             = new PRM_Template[ROP_H2A_MAXPARMS + 1];

	prmTemplate[ROP_H2A_RENDER]             = theRopTemplates[ROP_RENDER_TPLATE];
	prmTemplate[ROP_H2A_RENDERBACKGROUND]   = theRopTemplates[ROP_RENDERBACKGROUND_TPLATE];
	prmTemplate[ROP_H2A_RENDER_CTRL]        = theRopTemplates[ROP_RENDERDIALOG_TPLATE];
	prmTemplate[ROP_H2A_TRANGE]             = theRopTemplates[ROP_TRANGE_TPLATE];
	prmTemplate[ROP_H2A_FRANGE]             = theRopTemplates[ROP_FRAMERANGE_TPLATE];
	prmTemplate[ROP_H2A_TAKE]               = theRopTemplates[ROP_TAKENAME_TPLATE];
	prmTemplate[ROP_H2A_SOPOUTPUT]          = H2A_Rop::myTemplateList[0];
	prmTemplate[ROP_H2A_SOPPATH]            = H2A_Rop::myTemplateList[1];
	prmTemplate[ROP_H2A_NAME]               = H2A_Rop::myTemplateList[2];
	prmTemplate[ROP_H2A_PWIDTH]             = H2A_Rop::myTemplateList[3];
	prmTemplate[ROP_H2A_SHUTTER]            = H2A_Rop::myTemplateList[4];
	prmTemplate[ROP_H2A_MODE]               = H2A_Rop::myTemplateList[5];
	prmTemplate[ROP_H2A_MOTIONB]            = H2A_Rop::myTemplateList[6];
	prmTemplate[ROP_H2A_COLOR]              = H2A_Rop::myTemplateList[7];
	prmTemplate[ROP_H2A_TYPE]               = H2A_Rop::myTemplateList[8];
	prmTemplate[ROP_H2A_P_RENDER_TYPE]		= H2A_Rop::myTemplateList[9];
	prmTemplate[ROP_H2A_P_RAD_MULT]			= H2A_Rop::myTemplateList[10];
	prmTemplate[ROP_H2A_SUBDIV_TYPE]		= H2A_Rop::myTemplateList[11];
	prmTemplate[ROP_H2A_SUBDIV_ITE]			= H2A_Rop::myTemplateList[12];

	prmTemplate[ROP_H2A_TPRERENDER]         = theRopTemplates[ROP_TPRERENDER_TPLATE];
	prmTemplate[ROP_H2A_PRERENDER]          = theRopTemplates[ROP_PRERENDER_TPLATE];
	prmTemplate[ROP_H2A_LPRERENDER]         = theRopTemplates[ROP_LPRERENDER_TPLATE];
	prmTemplate[ROP_H2A_TPREFRAME]          = theRopTemplates[ROP_TPREFRAME_TPLATE];
	prmTemplate[ROP_H2A_PREFRAME]           = theRopTemplates[ROP_PREFRAME_TPLATE];
	prmTemplate[ROP_H2A_LPREFRAME]          = theRopTemplates[ROP_LPREFRAME_TPLATE];
	prmTemplate[ROP_H2A_TPOSTFRAME]         = theRopTemplates[ROP_TPOSTFRAME_TPLATE];
	prmTemplate[ROP_H2A_POSTFRAME]          = theRopTemplates[ROP_POSTFRAME_TPLATE];
	prmTemplate[ROP_H2A_LPOSTFRAME]         = theRopTemplates[ROP_LPOSTFRAME_TPLATE];
	prmTemplate[ROP_H2A_TPOSTRENDER]        = theRopTemplates[ROP_TPOSTRENDER_TPLATE];
	prmTemplate[ROP_H2A_POSTRENDER]         = theRopTemplates[ROP_POSTRENDER_TPLATE];
	prmTemplate[ROP_H2A_LPOSTRENDER]        = theRopTemplates[ROP_LPOSTRENDER_TPLATE];
	prmTemplate[ROP_H2A_MKPATH]             = theRopTemplates[ROP_MKPATH_TPLATE];
	prmTemplate[ROP_H2A_INITSIM]            = theRopTemplates[ROP_INITSIM_TPLATE];
	prmTemplate[ROP_H2A_ALFPROGRESS]        = PRM_Template( PRM_TOGGLE, 1, &ALFPROGRESS_PRM_NAME, PRMzeroDefaults );

	prmTemplate[ROP_H2A_MAXPARMS]           = PRM_Template();

	return prmTemplate;
};




OP_TemplatePair * H2A_Rop::getTemplatePair()
{
	static OP_TemplatePair *ropPair     = 0;

	if( ropPair )
	{
		return ropPair;
	}

	ropPair = new OP_TemplatePair( getTemplates() );

	return ropPair;
};

OP_VariablePair * H2A_Rop::getVariablePair()
{
	static OP_VariablePair *varPair     = 0;

	if ( varPair )
	{
		return varPair;
	}

	varPair = new OP_VariablePair( ROP_Node::myVariableList );

	return varPair;
};

//Update parameters

bool H2A_Rop::updateParmsFlags(){

	fpreal time = CHgetEvalTime();
	bool changed = ROP_Node::updateParmsFlags();
	bool curve;
	bool polygon;
	bool point;

	int type = TYPE();

	switch (type)
	{
	case 0: // curve selected
		changed |= enableParm("prender_type",0);
		changed |= setVisibleState("prender_type",0);
		changed |= enableParm("rad_mult",0);
		changed |= setVisibleState("rad_mult",0);
		changed |= enableParm("mode",1);
		changed |= setVisibleState("mode",1);
		changed |= enableParm("subdiv_type",0);
		changed |= setVisibleState("subdiv_type",0);
		changed |= enableParm("subdiv_ite",0);
		changed |= setVisibleState("subdiv_ite",0);
		break;
	case 1: // polygon selected
		changed |= enableParm("prender_type",0);
		changed |= setVisibleState("prender_type",0);
		changed |= enableParm("rad_mult",0);
		changed |= setVisibleState("rad_mult",0);
		changed |= enableParm("mode",0);
		changed |= setVisibleState("mode",0);
		changed |= enableParm("subdiv_type",1);
		changed |= setVisibleState("subdiv_type",1);
		changed |= enableParm("subdiv_ite",1);
		changed |= setVisibleState("subdiv_ite",1);
		break;
	case 2: // point selected
		changed |= enableParm("prender_type",1);
		changed |= setVisibleState("prender_type",1);
		changed |= enableParm("rad_mult",1);
		changed |= setVisibleState("rad_mult",1);
		changed |= enableParm("mode",0);
		changed |= setVisibleState("mode",0);
		changed |= enableParm("subdiv_type",0);
		changed |= setVisibleState("subdiv_type",0);
		changed |= enableParm("subdiv_ite",0);
		changed |= setVisibleState("subdiv_ite",0);
		break;
	case 3: // light selected
		changed |= enableParm("prender_type",0);
		changed |= setVisibleState("prender_type",0);
		changed |= enableParm("rad_mult",0);
		changed |= setVisibleState("rad_mult",0);
		changed |= enableParm("mode",0);
		changed |= setVisibleState("mode",0);
		changed |= enableParm("subdiv_type",0);
		changed |= setVisibleState("subdiv_type",0);
		changed |= enableParm("subdiv_ite",0);
		changed |= setVisibleState("subdiv_ite",0);
		break;
	}


	return changed;
}



// start, end and render frames are auto invoked by houdini

int H2A_Rop::startRender(int /*nframes*/, fpreal tstart, fpreal tend)
{
	int			 rcode = 1;

	endTime = tend;
	startTime = tstart;

	if (INITSIM())
	{
		initSimulationOPs();
		OPgetDirector()->bumpSkipPlaybarBasedSimulationReset(1);
	}

	if (error() < UT_ERROR_ABORT)
	{
		if( !executePreRenderScript(tstart) )
			return 0;
	}

	return rcode;
}

ROP_RENDER_CODE H2A_Rop::renderFrame(fpreal time, UT_Interrupt *)
{

	SOP_Node		*sop;
	UT_String		 soppath, savepath, name;

	OUTPUT(savepath, time);
	NAME(name,time);

	if( !executePreFrameScript(time) )
		return ROP_ABORT_RENDER;

	// From here, establish the SOP that will be rendered, if it cannot
	// be found, return 0.
	// This is needed to be done here as the SOPPATH may be time
	// dependent (ie: OUT$F) or the perframe script may have
	// rewired the input to this node.

	sop = CAST_SOPNODE(getInput(0));
	if( sop )
	{
		// If we have an input, get the full path to that SOP.
		sop->getFullPath(soppath);
	}
	else
	{
		// Otherwise get the SOP Path from our parameter.
		SOPPATH(soppath, time);
	}

	if( !soppath.isstring() )
	{
		addError(ROP_MESSAGE, "Invalid SOP path");
		return ROP_ABORT_RENDER;
	}

	sop = getSOPNode(soppath, 1);
	if (!sop)
	{
		addError(ROP_COOK_ERROR, (const char *)soppath);
		return ROP_ABORT_RENDER;
	}
	OP_Context		context(time);
	GU_DetailHandle gdh;
	gdh = sop->getCookedGeoHandle(context);

	GU_DetailHandleAutoReadLock	 gdl(gdh);
	const GU_Detail		*gdp = gdl.getGdp();

	if (!gdp)
	{
		addError(ROP_COOK_ERROR, (const char *)soppath);
		return ROP_ABORT_RENDER;
	}

	if(evalInt("mkpath",0,0)) {
		ROP_Node::makeFilePathDirs(savepath);
	}

	h2a_fileSave(gdp, (const char *) savepath, (const char *) name, PWIDTH(time), SHUTTER(time), MODE(), MOTIONB(), COLOR(), TYPE(), P_RENDER_TYPE(), RADIUS(time), SUBDIV_TYPE(), SUBDIV_ITE(time));

	if (ALFPROGRESS() && (endTime != startTime))
	{
		fpreal		fpercent = (time - startTime) / (endTime - startTime);
		int		percent = (int)SYSrint(fpercent * 100);
		percent = SYSclamp(percent, 0, 100);
		fprintf(stdout, "ALF_PROGRESS %d%%\n", percent);
		fflush(stdout);
	}

	if (error() < UT_ERROR_ABORT)
	{
		if( !executePostFrameScript(time) )
			return ROP_ABORT_RENDER;
	}

	return ROP_CONTINUE_RENDER;
}

ROP_RENDER_CODE H2A_Rop::endRender()
{
	if (INITSIM())
		OPgetDirector()->bumpSkipPlaybarBasedSimulationReset(-1);

	if (error() < UT_ERROR_ABORT)
	{
		if( !executePostRenderScript(endTime) )
			return ROP_ABORT_RENDER;
	}
	return ROP_CONTINUE_RENDER;
}

H2A_Rop::~H2A_Rop(){}

OP_Node * H2A_Rop::nodeConstructor( OP_Network *net, const char *name, OP_Operator *op )
{
	return new H2A_Rop( net, name, op );
};


H2A_Rop::H2A_Rop( OP_Network *net, const char *name, OP_Operator *op )

	:ROP_Node( net, name, op )
	,endTime( 0 )

{};


void newDriverOperator( OP_OperatorTable *table )
{
	table->addOperator(new OP_Operator("H2A_ROP",
		"H2A ROP",
		H2A_Rop::nodeConstructor,
		H2A_Rop::getTemplatePair(),
		0,
		0,
		H2A_Rop::getVariablePair(),
		OP_FLAG_GENERATOR));
};
