/*******************************************************************************
/*! \file
*
*   \header file for string encoding and decoding in ASCII base85  
*   \author Sergen Eren
*   
*   \version 0.1
*   \date March 2016
*
*/

#ifndef __base_85_h__
#define __base_85_h__

#include <string>
#include <array>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <stddef.h>

namespace b85{

	typedef unsigned int  uint32_t;
	typedef unsigned char byte;

	char* char_to_int = {"$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwx"};

}

#endif