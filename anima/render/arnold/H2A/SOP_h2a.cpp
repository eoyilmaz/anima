/*******************************************************************************
* PROPRIETARY INFORMATION.  This software is proprietary to
* Anima Istanbul, and is not to be reproduced,
* transmitted, or disclosed in any way without written permission.
* Permission is hereby granted, free of charge, to any person obtaining a
* copy of this software and/or associated documentation files (the
* "Materials"), to deal in the Materials without restriction, including
* without limitation the rights to use, copy, modify, merge, publish,
* distribute, sublicense, and/or sell copies of the Materials, and to
* permit persons to whom the Materials are furnished to do so, subject to
* the following conditions:
*
* The above copyright notice and this permission notice shall be included
* in all copies or substantial portions of the Materials.
*
* THE MATERIALS ARE PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
* EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
* MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
* CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
* TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
* MATERIALS OR THE USE OR OTHER DEALINGS IN THE MATERIALS.
*
* Produced by:
* Anima Istanbul
* AOS 51.st Maslak, Istanbul
* TURKEY
*
/********************************************************************************/

/*! \file
*
*   \houdini to arnold cpp SOP implementation  
*   \author Sergen Eren
*   
*   \version 1.0
*   \date June 2015
*
*/

#include <SOP_H2A.h>

// Houdini

#include <GU/GU_Detail.h>
#include <OP/OP_Operator.h>
#include <OP/OP_OperatorTable.h>
#include <OP/OP_Director.h>
#include <OP/OP_AutoLockInputs.h>
#include <PRM/PRM_Include.h>
#include <UT/UT_DSOVersion.h>
#include <UT/UT_Interrupt.h>
#include <UT/UT_OFStream.h>
#include <SYS/SYS_Math.h>
#include <SOP/SOP_Node.h>
#include <UT/UT_ThreadedAlgorithm.h>
#include <UT/UT_ThreadedIO.h>
#include <GA/GA_PageHandle.h>
#include <GA/GA_PageIterator.h>
#include <UT/UT_OFStream.h>
#include <UT/UT_KDTree.h>
#include <GEO/GEO_PointTree.h>

//C++
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

#define PRM_MENU_CHOICES	(PRM_ChoiceListType)(PRM_CHOICELIST_EXCLUSIVE |\
	PRM_CHOICELIST_REPLACE)

#define MAX_QUEUE_BYTES 128

using namespace H2A;
using namespace std;

void
	newSopOperator(OP_OperatorTable *table)
{
	table->addOperator(new OP_Operator(
		"HtoAC",
		"Houdini To Arnold C",
		SOP_h2a::myConstructor,
		SOP_h2a::myTemplateList,
		1,
		1,
		0));
}

static PRM_Name names[] = {
	PRM_Name("outputFile",     "Output File"),
	PRM_Name("name",   "Name"),
	PRM_Name("min_pixel_width",  "Min Pixel Width"),
	PRM_Name("mode",  "Mode"),
	PRM_Name("export_motion",  "Export Motion Blur"),
	PRM_Name("export_color",  "Export Color"),
	PRM_Name("export_type",  "Export Type"),
};

static PRM_Default	 theFileDefault(0, "defgeo.ass");
char *nameName = "`$OS`"; 
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
	PRM_Name(0)
};

static PRM_ChoiceList	sopOpMenu(PRM_MENU_CHOICES,	sopOpMenuNames);
static PRM_ChoiceList	sopTypeMenu(PRM_MENU_CHOICES,	sopTypeMenuNames);


PRM_Template SOP_h2a::myTemplateList[] = {
	PRM_Template(PRM_STRING,	1, &names[0], &theFileDefault),
	PRM_Template(PRM_STRING,	1, &names[1], &theNameDefault),
	PRM_Template(PRM_FLT_J, PRM_Template::PRM_EXPORT_TBX, 1, &names[2], PRMpointFiveDefaults),
	PRM_Template((PRM_Type) PRM_ORD, PRM_Template::PRM_EXPORT_MAX, 1, &names[3], 0, &sopOpMenu),
	PRM_Template(PRM_TOGGLE,    1, &names[4], PRMoneDefaults),
	PRM_Template(PRM_TOGGLE,    1, &names[5], PRMoneDefaults),
	PRM_Template((PRM_Type) PRM_ORD, PRM_Template::PRM_EXPORT_MIN, 1, &names[6], 0, &sopTypeMenu),
	PRM_Template()
};


OP_Node *
	SOP_h2a::myConstructor(OP_Network *net, const char *name, OP_Operator *op)
{
	return new SOP_h2a(net, name, op);
}

SOP_h2a::SOP_h2a(OP_Network *net, const char *name, OP_Operator *op)
	: SOP_Node(net, name, op)
{

	mySopFlags.setManagesDataIDs(true);

}

SOP_h2a::~SOP_h2a() {}


void SOP_h2a::writePartial(GU_Detail *gdp, const GA_SplittableRange &range, GA_RWPageHandleV3 &v, const UT_JobInfo &jobInfo){

	for(GA_PageIterator pit = range.beginPages(jobInfo); !pit.atEnd(); ++pit){
		GA_Offset start, end, ptoff; 
		for(GA_Iterator it(pit.begin()); it.blockAdvance(start, end);){
			v.setPage(start);
			for(ptoff = start; ptoff<end; ++ptoff){
				v.set(ptoff, gdp->getPos3(ptoff));
				cout<<ptoff<<" "; 
			}
		}
	}
}

class My_IOTask : public UT_ThreadedIOTask {

public:
	UT_Vector3F N;
	UT_String os; 

	My_IOTask(UT_Vector3F &N, UT_String &os):N(N),os(os){};

	void doWrite(){ 
		os.sprintf("%f %f %f\n",N.x(),N.y(),N.z());
	}

	exint memoryEstimate() const
	{
		exint memory = 0;
		return memory;
	}
};




/*
class write_attr{
public:
const GA_ROPageHandleV3 my_v;
UT_ThreadedIO io2;
UT_String output;

write_attr(const GA_ROPageHandleV3 &v, UT_String &os, UT_ThreadedIO &io): my_v(v), output(os),io2(io){}

void operator()(const GA_SplittableRange &r) const 
{
GA_ROPageHandleV3 p_h(my_v.getAttribute());

for(GA_PageIterator pit = r.beginPages(); !pit.atEnd(); ++pit){
GA_Offset start, end; 

for(GA_Iterator it(pit.begin()); it.blockAdvance(start, end); ){
p_h.setPage(start);
for(GA_Offset i = start; i<end; ++i){

UT_Vector3F N = p_h.get(i); 
My_IOTask io_task(N , output);
io2.postTask(&io_task);
}
}
}
}
};


void multi_write(const GA_Range &range, const GA_ROPageHandleV3 &v, UT_String &output, UT_ThreadedIO &io){
UTparallelFor(GA_SplittableRange(range), write_attr(v, output, io));
};
*/



OP_ERROR SOP_h2a::cookMySop(OP_Context &context){

	OP_AutoLockInputs inputs(this);
	if (inputs.lock(context) >= UT_ERROR_ABORT)
		return error();

	duplicateSource(0, context);

	addMessage(SOP_MESSAGE , "This node exports the geo data in ass format"); 

	flags().timeDep = 1;

	fpreal t = context.getTime();
	GA_Index index;

	UT_String output;
	UT_String name;


	OUTPUT(output,t);
	NAME(name,t);

	float pwidth = PWIDTH(t);
	int mode = MODE();
	int motionb = MOTIONB();
	int color = COLOR();
	int type = TYPE();

	GA_ROPageHandleV3 p_ph(gdp, GA_ATTRIB_POINT, "P");

	GA_ROHandleV3 pos_h(gdp, GA_ATTRIB_POINT, "P");
	UT_Vector3F pos_val; 

	GA_RWPageHandleV3 cd_ph(gdp, GA_ATTRIB_POINT,"Cd"); 


	//multi_write(gdp->getPointRange(), p_ph, buffer, io);

	UT_OFStream file(output); 
	UT_String buffer; 

	//if(cd_ph.isValid()) write(gdp, gdp->getPointRange(), cd_ph);

	UT_Array<GA_OffsetArray> ring_zero;
	UT_Array<GA_OffsetArray>::iterator it; 
	gdp->buildRingZeroPoints(ring_zero);

	GA_Offset ptoff=0;
	
	UT_Vector3F delta(0,0,0); 
	UT_Vector3F neigh_pt(0,0,0); 
	UT_Vector3F neigh_edge_pt(0,0,0);
	exint neighbour_count; 

	for(UT_Array<GA_OffsetArray>::iterator it(ring_zero.begin()); !it.atEnd(); ++it){
		
		GA_OffsetArray neighbourArray = ring_zero(ptoff);
		neighbour_count = neighbourArray.entries();
		for(GA_OffsetArray::iterator pit(neighbourArray.begin());!pit.atEnd();++pit){
			neigh_pt += gdp->getPos3(*pit); 
			neigh_edge_pt += (gdp->getPos3(*pit) + gdp->getPos3(ptoff)) / 2; 
		}

		neigh_pt = neigh_pt / neighbour_count; 
		neigh_edge_pt = neigh_edge_pt / neighbour_count; 

		delta = (neigh_pt + neigh_edge_pt) / 2.00; 
		
		neigh_pt.assign(0,0,0); 
		neigh_edge_pt.assign(0,0,0); 

		gdp->setPos3(ptoff, delta);

		ptoff++;
	} 
	gdp->bumpAllDataIds();

	return error();
}


const char * SOP_h2a::inputLabel(unsigned) const
{
	return "Input geometry";
}

