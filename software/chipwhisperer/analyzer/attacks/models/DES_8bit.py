#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2013-2014, NewAE Technology Inc
# All rights reserved.
#
# Authors: Colin O'Flynn
#
# Find this and more at newae.com - this file is part of the chipwhisperer
# project, http://www.assembla.com/spaces/chipwhisperer
#
#    This file is part of chipwhisperer.
#
#    chipwhisperer is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    chipwhisperer is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with chipwhisperer.  If not, see <http://www.gnu.org/licenses/>.

import sys
import chipwhisperer.common.des_tables as des_tables
import chipwhisperer.common.hamming_weight as hw
import numpy

numSubKeys = 8

# We attack the outputs of the eight DES sboxes.
# These are the inputs to the sboxes, named SubKey round 1, 1-8

intermediates = [
                    {'name': 'Sub Key 1/1', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/2', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/3', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/4', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/5', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/6', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/7', 'range': (0, 63)}, 
                    {'name': 'Sub Key 1/8', 'range': (0, 63)}
                ]

def getKeyRange(bnum):
    return intermediates[bnum]['range']

def selectSBoxInput(IP_output, sbox):
    mask = 0b111111
    mask <<= (7-sbox) * 6
    #print "mask = %016x"%mask
    return (IP_output & mask) >> (7 - sbox) * 6

def HypHW(pt, ct, sub_key_part, sbox):
    """Given either plaintext or ciphertext (not both) + a key guess, return hypothetical hamming weight of result"""
    if pt != None:
        # pt contains the 64 bit plaintext which goes into the initial permutation
        # pt is an array of bytes
        # sub_key_part is the input to a specific s-box of round 1
        # sbox is the number of the chosen sbox
        pt = pt[:8]
        if len(pt) != 8:
            raise ValueError("The plain text must be 64 bit long")
       
        input = numpy.uint64()
        for x in pt:
            input <<= numpy.uint8(8)
            input |= x
        
        ip = des_tables.IP(input)
        right = des_tables.Right(ip)
        expand = des_tables.Expand(right)
        pt_part = selectSBoxInput(expand, sbox)
        sbox_input = pt_part ^ sub_key_part
        x = des_tables.SBoxLookup(sbox_input, sbox)
        
        print "input: %016x, ip: %016x, right: %08x, expand: %012x, sbox: %d, pt_part: %02x, key_guess: %02x, sbox_input: %02x, sbox output: %02x" % (input, ip, right, expand, sbox + 1, pt_part, sub_key_part, sbox_input, x)

        return hw.getHW(x)

    elif ct != None:        
        raise ValueError("Attack on the ciphertext is not implemented")
    else:
        raise ValueError("Must specify PT or CT")

if __name__ == "__main__":
    pt = [numpy.uint8(0)] * 8
    pt[0] = numpy.uint8(0x80)
    HypHW(pt, None, 0, 0)
    pt[0] = numpy.uint8(0x01)
    HypHW(pt, None, 0, 0)
    pt = [numpy.uint8(0xFF)] * 8
    HypHW(pt, None, 0, 0)
    pt = [numpy.uint8(0x77)] * 8
    HypHW(pt, None, 0, 0)
    HypHW(pt, None, 1, 0)
    HypHW(pt, None, 2, 0)
    HypHW(pt, None, 3, 0)
    HypHW(pt, None, 0, 0)
    HypHW(pt, None, 0, 2)
    HypHW(pt, None, 0, 3)
    HypHW(pt, None, 0, 7)
