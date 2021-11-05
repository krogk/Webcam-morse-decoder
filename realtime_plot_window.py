# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 17:22:01 2020

@author: Kamil
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import morse_decoder
import iir_filter


class RealtimeWindow:

    def __init__(self, channel: str):
        # create a plot window
        self.fig, (self.ax, self.ax1)= plt.subplots(2)
        plt.title(f"Channel: {channel}")
        self.ax.set_title('Lumiannce')
        self.ax1.set_title('Filtered Signal')
        self.plotbuffer = np.zeros(800)
        self.plotbuffer1 = np.zeros(800)
        # Create empty lines
        line, = self.ax.plot(self.plotbuffer)
        line2, = self.ax1.plot(self.plotbuffer1)
        self.line = [line, line2]
        # Set axis limits
        self.ax.set_ylim(-1, 1)
        self.ax1.set_ylim(-1, 1)
        # Initalize Ringbuffers
        self.ringbuffer = []
        self.ringbuffer1 = []
        # add any initialisation code here (filters etc)
        # start the animation        
        self.decodedSequence = ''

        # Design High Pass filter
        samplingFrequency = 30
        # Define cut off frequency
        cutOfFrequencyHighPass = 0.1 #Hz
        # Number order that IIR filter array will be equivalent to
        order = 2
        
        # Genereate second order sections
        sos = np.array(iir_filter.GenerateHighPassCoeff( cutOfFrequencyHighPass, samplingFrequency, order ))

        # Initalize morse code decoder object
        self.decoder = morse_decoder.MorseCodeDecoder()
    
        # Create IIR Array object
        self.iirFilter = iir_filter.IIRFilter(sos)
    
        # Initialize filter output variable
        self.filterOutput = 0
        # start the animation    
        self.ani = animation.FuncAnimation(self.fig, self.update, interval=100)


    # updates the plot
    def update(self, data):
        # add new data to the buffer
        self.plotbuffer = np.append(self.plotbuffer, self.ringbuffer)
        self.plotbuffer1 = np.append(self.plotbuffer1, self.ringbuffer1)
        # only keep the 500 newest ones and discard the old ones
        self.plotbuffer = self.plotbuffer[-800:]
        self.plotbuffer1 = self.plotbuffer1[-800:]
        self.ringbuffer = []
        self.ringbuffer1 = []
        # set the new 500 points of channel 9
        self.line[0].set_ydata(self.plotbuffer)
        self.line[1].set_ydata(self.plotbuffer1)
        self.ax.set_ylim((min(self.plotbuffer)-1), max(self.plotbuffer)+1)
        self.ax1.set_ylim((min(self.plotbuffer1)-1), max(self.plotbuffer1)+1)
        # Update the decoded sequence
        self.ax.set_title('Lumiannce - Detected Sequence: '+ self.decoder.morseSequence)
        self.ax1.set_title('Filtered Signal - Decoded Sequence: '+ self.decoder.decodedLetters)

        return self.line

    # appends data to the ringbuffer
    def addData(self, signal):
        self.ringbuffer.append(signal)
        self.filterOutput = self.iirFilter.Filter(signal)
        self.ringbuffer1.append(self.filterOutput)
        self.decoder.Detect(self.filterOutput)
        