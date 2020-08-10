# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 12:45:37 2020

VAD pipeline

@author: Ben GUtteridge
"""

'''
Take path to wav file and desired destination folder. Choose VAD aggressiveness,
target loudness value for normalisation, and produce processed files with 
speech removed

'''

import librosa
import numpy as np
import os
from os.path import join
import soundfile as sf
import pyloudnorm as pyln
from webrtc_vad import VAD
from webrtc_utils import speech_stripper


def VAD_pipeline(root, file, destination, agg=0, sr=8000, LU =-35, norm_only=False):
    '''

    Parameters
    ----------
    root : string
        Input directory.
    file : string
        Input file name.
    destination : string
        Output directory (uses same name for output file as input).
    agg : int, optional
        Aggressiveness of VAD. The default is 0, i.e. less aggressive about removing noise, false positives preferred to false negatives.
    sr : int, optional
        Sampling frequency in Hz. The default is 8kHz.
    LU : int or float, optional
        Target output file loudness. The default is -35, approximately the same loudness of much of our mosquito recordings.
        
    Returns
    -------
    None. Output files are written to destination folder.

    '''
    path = join(root, file)
    data, sr = librosa.load(path, sr=8000)
    meter = pyln.Meter(sr) # create BS.1770 meter
    loudness = meter.integrated_loudness(data) # measure loudness
    print('\n%s\nLength = %.2fs\nLoudness = %.2fdB' % (file, data.shape[0]/sr, loudness))
    loudness_normalized_audio = pyln.normalize.loudness(data,loudness, LU)
    sf.write(join(destination,file), loudness_normalized_audio, sr, 
             subtype='PCM_16') 
    timestamps = VAD(join(destination,file), agg, chunks=False)
    stripped_t, _ = speech_stripper(loudness_normalized_audio, timestamps, sr)
    
    if norm_only == True:
        print('New loudness = %.2fdB' % LU)
        return 0
    
    if stripped_t.shape[0]/sr > 1:  # Must be >1s of non-speech
        sf.write(join(destination,file), stripped_t, sr, subtype='PCM_16')
        print('New length = %.2fs\nNew loudness = %.2fdB' % \
              (stripped_t.shape[0]/sr, LU))
    else:
        print('File not processed, entirely speech detected')
        os.remove(join(destination, file))
    

def main():
    root = r'D:\Big Files\Humbug OneDrive\Experiments\REPORT\noise_experiments\test\input'
    destination = root[:-5] + 'output'
    LU = -35            # similar to most of our moz test files
    for file in os.listdir(root):
        if file.endswith('.wav'):
            VAD_pipeline(root, file, destination, LU=LU)
            
if __name__ == '__main__':
    main()