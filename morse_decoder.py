# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 20:19:10 2020

@author: Kamil
"""

class MorseCodeDecoder():
    
    def __init__(self):
        # Initialize binary tree
        self.tree = MorseCodeBinaryTree()
        
        # Definie Timinings
        self.nSamplesDotDuration = 10
        self.nSamplesMinDashDuration = 16
        self.nSamplesMaxDashDuration = 35
        self.nSamplesErrorMargin = 4

        # Define Strings for sequences
        self.sequence = ''
        self.morseSequence = ''
        self.decodedLetters = ''
        
        # Define Counters
        self.nSamplesBetwenPosNegPeakList = []
        self.nSamplesBetweenPeaks = 0
        self.nSymbols = 0
        self.nSamplesLow = 0
        self.totalSampleCount = 0

        # Define thresholds
        self.posAmplitudeThreshold = 10
        self.negAmplitudeThreshold = -10
        self.pulseSettlingSamplecCnt = 5
        
        # Define Flags for peaks detector
        self.posPeakFlag = False
        self.negPeakFlag = False
        self.posPeakFound = False
        
        # Sample Hold
        self.previousSample = 0

        # Variable for measuring sampling time
        self.timerStart = 0
        self.SamplingTimerCounter = 0
        self.nSamplesLate = 0 

    def Detect(self, sample):
        # Give 5 Seconds for filter to settle
        if (self.totalSampleCount >= 150):
            
            # Detect positive peaks - light turning on
            # If sample amplitude is above threshold and positive the peak hasn't been detected before
            if( sample > self.posAmplitudeThreshold and self.posPeakFlag == False ):
                # In the vicinity of the positive peak
                self.posPeakFlag = True
                # If signal low for long enough to not be a space between letters
                if( self.nSamplesLow >= 20):
                    # If sequence is not empty
                    if (self.sequence):
                        # Decode Letter
                        self.decodedLetters += self.tree.DecodeString(self.sequence)
                        if (self.nSamplesLow >= 40):
                            self.decodedLetters += ' '
                        # Update Morse Sequence
                        self.morseSequence += self.sequence + ' '
                        # Reset sequence 
                        self.sequence = ''
                    self.nSamplesLow = 0
                    
            # If the amplitude exceeded threshold and previous sample was higher that must've been the peak
            if( sample > self.posAmplitudeThreshold and self.previousSample > sample and self.posPeakFlag == True):
                # Set flag
                self.posPeakFound = True
                
            # Detect negative Peaks - light turning off
            # If sample amplitude is below threshold and negative the peak hasn't been detected before
            if( sample < self.negAmplitudeThreshold and self.negPeakFlag == False ):
                # In the vicinity of the negative peak
                self.negPeakFlag = True
     
            # If the amplitude is below the threshold and previous sample was lower, that must've been the peak
            if( sample < self.negAmplitudeThreshold and self.previousSample < sample and self.posPeakFlag == True and self.nSamplesBetweenPeaks >= self.pulseSettlingSamplecCnt):
                # reset detector flags
                self.posPeakFound = False
                self.posPeakFlag = False
                self.negPeakFlag = False
                self.nSamplesBetwenPosNegPeakList.append(self.nSamplesBetweenPeaks)
                # Increment peak counter
                self.nSymbols += 1 
                # Check if light long enough for dash
                if( self.nSamplesBetweenPeaks  >= self.nSamplesMinDashDuration ):
                    self.sequence += '-'
                    
                # Check if light long enough for dot
                elif( self.nSamplesBetweenPeaks  >= (self.nSamplesDotDuration - self.nSamplesErrorMargin ) and self.nSamplesBetweenPeaks  <= (self.nSamplesDotDuration + self.nSamplesErrorMargin ) ):
                    self.sequence += '.'
                    
                # Reset timer
                self.nSamplesBetweenPeaks = 0
        
        # If light on was detected
        if(self.posPeakFound == True):
            self.nSamplesBetweenPeaks += 1
            self.nSamplesLow = 0
            # If light was is on longer than dash
            if(self.nSamplesBetweenPeaks > self.nSamplesMaxDashDuration ):
                # False detection, reset detector flags & variables
                self.posPeakFound = False
                self.posPeakFlag = False
                self.negPeakFlag = False
                self.nSamplesBetweenPeaks = 0
        # If light on was not yet detected
        else:
            # Silence continues
            self.nSamplesLow += 1
        
        # Hold current sample for comparison
        self.previousSample = sample
        self.totalSampleCount += 1


"""
MorseCodeBinary tree object, initializes and populates a binary tree for morse code with methods to decode the whole sequence at once or by symbol.
"""
class MorseCodeBinaryTree(object):

    
    def __init__(self):
        # Define Root node
        self.rootNode = Node("*")
        self.traverseNode = self.rootNode

        # All characters in the morse code defined convinently for populating level by level of binary tree
        morseDictionary = "ETIANMSURWDKGOHVF*L*PJBXCYZQ**54*3***2**+****16=/*****7***8*90"

        # Current Node
        currentParentNode = self.rootNode
        # Node list
        nextNodesPlaceHolder = []

        # Populate binary tree
        # For each character in dictionary string
        for character in morseDictionary:
            # If there is no node object resulting from dot (to the left)  
            if( currentParentNode.dot == None ):
                # Insert node with value that is going to result from dot
                currentParentNode.dot = Node(character)
            # There is already an object to the left so take care of right side  
            else:
                # If there is no node object resulting from dash (to the right)  
                if (currentParentNode.dash == None):
                    # Insert node with value that is going to result from dash
                    currentParentNode.dash = Node(character)
                # Both children nodes have been assigned
                else:
                    # Append nodes to the list 
                    nextNodesPlaceHolder.append(currentParentNode.dot)
                    nextNodesPlaceHolder.append(currentParentNode.dash)
                    # Remove the first node object from the place holder to process next
                    # eseentially moving through the tree
                    currentParentNode = nextNodesPlaceHolder.pop(0)
                    # Create new node resulting from dot
                    currentParentNode.dot = Node(character)


    """
    Method which traverses morse code binary tree for the whole complete input string of dots and dashes
    and returns character for that sequnce.
    """
    def DecodeString(self, morseCodeSequence):

        # Start from root node
        currentNode = self.rootNode
        
        # For each character in the input sequence
        for character in morseCodeSequence:
            # If dot traverse to the left
            if( character == "." ):
                currentNode = currentNode.dot
            # Otherwise must be a dash, go right
            else:
                currentNode = currentNode.dash

        return currentNode.value


    """
    Method which traverses morse code binary tree based on the input and returns character for the sequnce if flag is provided.
    """
    def ProcessNode(self, inputChar, endFlag):

        # If dot traverse to the left
        if inputChar == ".":
            if( self.traverseNode.left == None):
                return '#'
            else:
                self.traverseNode = self.traverseNode.left
        # If dash traverse to the right
        elif (inputChar == "-"):
            if( self.traverseNode.right == None):
                return '#'
            else:
                self.traverseNode = self.traverseNode.right
        
        # If sequence of dots and dashes has ended return character
        if (endFlag == True):
            self.traverseNode = self.rootNode
            return self.traverseNode.value
            
        
"""
Binary node object
"""
class Node(object):
    # Contstructor
    def __init__(self, char):
        # Character corresponding to the sequence
        self.value = char
        # Child node objects
        self.dot = None
        self.dash = None
        
       
def unitTest():
    
    morseDecoder = MorseCodeDecoder()
    
    # Test whole string sequence for the alphabet 
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+=/"
    alphabetInMorse = [  ".-" , "-..." , "-.-." , "-.." , "." , "..-." , "--." , "...." , ".." , ".---" , "-.-" , ".-.." , "--" , "-." , "---" , ".--." , "--.-" , ".-." , "..." , "-" , "..-" , "...-" , ".--" , "-..-" , "-.--" , "--.." , "-----" , ".----" , "..---" , "...--" , "....-" , "....." , "-...." , "--..." , "---.." , "----." , ".-.-." , "-...-" , "-..-."]
    nCharacterInAlphabet = 39
    
    print("TESTING DECODER! - WHOLE SEQUENCE FOR CHARACTER")
    print("INPUT VALUES: " + alphabet )
    for x in range(nCharacterInAlphabet):
        decodedCharacter = morseDecoder.tree.DecodeString(alphabetInMorse[x])
        if( alphabet[x] == decodedCharacter):
            print(decodedCharacter)
        else:
            print("MORSE DECODER IS NOT OPERATING CORRECTLY!")
            print("EXPECTED CHARACTER:" + str(alphabet[x]) + " DECODED: " + str(decodedCharacter))
            return -1

        
    print("DECODER OPERATES CORRECTLY!")   
    return 0
        
if __name__ == "__main__":
    
    unitTest()