# -*- coding: utf-8 -*-
"""
Created on Sat Nov 14 01:16:39 2020

@author: Kamil
"""

import realtime_plot_window
import webcam2rgb
import time

        
if __name__ == "__main__":

    # Initialize Pealtime window Containt graph, filter and decoder
    realTimeWindow = realtime_plot_window.RealtimeWindow("Morse Decoder")
        
    # Create callback method reading camera and plotting in windows
    def hasData(retval, data):
        # Calculate brightness b = data[0],  g = data[1], r = data[2]
        luminance = ( (0.2126*data[2]) + (0.7152*data[1]) + (0.0722*data[0]) )
        # Pass signal to realtime window
        realTimeWindow.addData(luminance)
        
    # def hasData(retval, data):     
    #     #Measure SampleTime
    #     if 10 >= (time.time() - realTimeWindow.decoder.timerStart):
    #         realTimeWindow.decoder.SamplingTimerCounter += 1
    #     #Measure jitter
    #     if (1/30) > (time.time() - realTimeWindow.decoder.timerStart):
    #         realTimeWindow.decoder.nSamplesLate += 1
    #     realTimeWindow.decoder.timerStart = time.time()

        
    # Create instances of camera
    camera = webcam2rgb.Webcam2rgb()
    # Start the thread and stop it when we close the plot windows
    realTimeWindow.decoder.timerStart = time.time()
    camera.start(callback = hasData, cameraNumber=0)
    print("Camera Sample Rate: ", camera.cameraFs(), "Hz")
    realtime_plot_window.plt.show()
    camera.stop()

    # Debug
    #print('\n Time Pos-to-Neg Peak:')  
    #print(realTimeWindow.decoder.nSamplesBetwenPosNegPeakList)
    timeElapsed = time.time() - realTimeWindow.decoder.timerStart
    print('\n Measured Sampling Rate: ' + str(realTimeWindow.decoder.totalSampleCount / timeElapsed))
    
    # Print Sequences
    print('\nSequence Detected:')  
    print(realTimeWindow.decoder.morseSequence)
    print('\nDecoded Morse Code Sequence: '+ realTimeWindow.decoder.decodedLetters )
 