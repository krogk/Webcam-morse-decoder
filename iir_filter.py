# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 00:41:48 2020

@author: Kamil
"""

from scipy import signal
import numpy as np


def GenerateHighPassCoeff(cutOffFrequency, samplingFrequency, nSOS):
    # Normalise Frequencies
    normalisedCutOffFrequency = 2 * (cutOffFrequency / samplingFrequency) 
    # Calculate Coefficients
    sos = signal.butter(nSOS, normalisedCutOffFrequency, btype='highpass', analog=False, output='sos')
    # Return Coefficients
    return sos


def GenerateBandPassCoeff(cutOffFrequencyLow, cutOffFrequencyHigh, samplingFrequency, nSOS):
    # Normalise Frequencies
    normalisedCutOffFrequencyLow = 2 * (cutOffFrequencyLow / samplingFrequency)
    normalisedCutOffFrequencyHigh = 2 * (cutOffFrequencyHigh / samplingFrequency) 
    freqList = [normalisedCutOffFrequencyLow, normalisedCutOffFrequencyHigh]
    # Calculate Coefficients
    sos = signal.butter(nSOS, freqList, btype='bandpass', analog=False, output='sos')
    # Return Coefficients
    return sos


class IIR2Filter:

    """
    input sosCoefficients = [b0,b1,b2,a0,a1,a2]
    """
    def __init__( self, sosCoefficients ):
        # b coefficients, numerator coefficients, for the FIR Part
        self.b0 = sosCoefficients[0]
        self.b1 = sosCoefficients[1]
        self.b2 = sosCoefficients[2]
        
        # a coefficients, denominator coefficients, for the IIR Part 
        self.a1 =  sosCoefficients[4]
        self.a2 = sosCoefficients[5]
        
        self.buffer1 = 0
        self.buffer2 = 0

    def Filter(self, x):
        # Calculate input accumulator
        inputAccumulator = x
        # Delay step 1 
        inputAccumulator = inputAccumulator - (self.a1 * self.buffer1)
        # Delay step 2
        inputAccumulator = inputAccumulator - (self.a2 * self.buffer2) 
        
        # Calculate output accumulator
        outputAccumulator =  inputAccumulator * self.b0
        # Delay step 1 
        outputAccumulator = outputAccumulator + (self.b1 * self.buffer1)
        # Delay step 1 
        outputAccumulator = outputAccumulator + (self.b2 * self.buffer2)
        
        # Move output through delay steps
        self.buffer2 = self.buffer1
        self.buffer1 = inputAccumulator
        
        # return filter output
        return outputAccumulator


class IIRFilter:
    
    def __init__( self, sosCoefficients ):
        # Define number of filters
        self.nFilters = sosCoefficients.shape[0]

        # List to hold all IIR filter objects
        self.FilterArray = []
        
        # Create IIR filter object and append it to an array of filters.
        for i in range( self.nFilters ):
            # Ceate & Append
            self.FilterArray.append( IIR2Filter( sosCoefficients[i] ) )
            
    def Filter( self, x):
        y = x 
        # Run sample through filters
        for i in range( self.nFilters ):
            y = self.FilterArray[i].Filter(y)
            
        return y
    