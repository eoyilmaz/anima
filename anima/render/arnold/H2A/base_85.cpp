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
*   \string encoding in ASCII base85  
*   \author Sergen Eren
*   
*   \version 1.0
*   \date March 2016
*
*/

#ifndef __base_85_cpp__
#define __base_85_cpp__

#include <iostream>
#include <string>
#include <boost/cstdint.hpp>

typedef float fpreal32;
typedef unsigned char byte;

namespace b85{
	
	static const char* base85 = {"$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwx"};

	std::string encode(fpreal32 data)
	{
		
		std::string out; 
		
		boost::uint32_t x = reinterpret_cast<boost::uint32_t& >(data);
		if(x<0) x = 0x80000000 - x;

		out.append(base85, (int) (x/52200625) % 85 , 1);
		out.append(base85, (int) (x/614125) % 85 , 1);
		out.append(base85, (int) (x/7225) % 85 , 1);
		out.append(base85, (int) (x/85) % 85 , 1);
		out.append(base85, x%85 , 1);

		return out; 
	}
}

#endif