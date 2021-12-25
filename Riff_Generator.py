from midiutil.MidiFile import MIDIFile  
# https://github.com/MarkCWirt/MIDIUtil
# https://midiutil.readthedocs.io/en/latest/
import numpy as np
import pandas as pd
from datetime import datetime

pd.set_option('precision',3)

######################### settings ########################

# initial settings
time = 0            # GLOBAL TIME VARIABLE!!!!! In beats (1/4 notes), needs to reinitialise every run when looping
tempo = 140
djent = 1/4         # smallest increment of notes, quarter quarter note = 1/16 note
key = 33            # ROOT NOTE IN MIDI (7-string drop-A tuning is 33 (55 Hz), low E standard guitar is 40 (~82.4 Hz))
downPick = 110      # down picking velocity / volume (out of 127, per MIDI standard)
upPick = 90         # up picking velocity / volume
chordPick = 120     # chord picking velocity / volume

# at riffLengthMin = 4, will be between 1 and 4 bars per riff part (4 times that for entire repeat)
# these 3 lengths are arbitrary but common, but powers of 2 are common in music
# 3 values may be chosen without the formula for medium and long riffs
riffLengthMin = 4                         # careful: this is 1 bar is 4 beats and 16 16th notes
riffLengthMed = riffLengthMin * 2
riffLengthMax = riffLengthMed * 2         

# create a MIDI object using midiutil.MidiFile
channel = 0     # midi channel
track = 0       # the main track
# the track for palmmuting, 0 if on same track, 1 for separate track
# CreateMIDIFile() will adjust  if PMtrack is set to 0
# annotations are added if MIDI is sent to notation software, denoted "PM" (see functions section below)
PMtrack = 1

def CreateMIDIFile():
    global mf
    global time
    time = 0                # start at the beginning
    mf = MIDIFile(1 + PMtrack)      # only 1 track unless PMtrack is used
    mf.addTempo(track, time, tempo)
    mf.addTempo(PMtrack, time, tempo)   # not needed for format 1 midi (default)
    # mf.addTrackName(track, time, "Sample Track") # use if you need to name the track

######################## INPUTS TO RANDOMISE ########################
# inputs that are used in the riff generation function, ranges are typically
# change the high and low range to change the output style
# typically ratings out of 10 (to be normalised later), but are not actually restricted to 10
# try extreme values at your own risk (also, negative values probably break stuff)

def RandomiseInputs():
    global howMuchCrazy
    global howManyChords
    global highestNote
    global howMuchPM
    global howMuchCHORDS
    global howMuchMELODY
    global howMuchREST
    howMuchCrazy = np.random.randint(0,2)           # how likly the pattern is to not follow the flowchart
    howManyChords = np.random.randint(2,8)          # how many chords in chord progression transfer matrix
    highestNote = np.random.choice([12,13,14,15,17,18,19,20,22,23,24])      # highest note available (note must be in keyScale below)
    howMuchPM = np.random.randint(3,9)              # int out of 10, a priority (not actually restricted to 10)
    howMuchCHORDS = np.random.randint(3,9)          # int out of 10, a priority
    howMuchMELODY = np.random.randint(3,9)          # int out of 10, a priority
    howMuchREST = np.random.randint(0,4)            # int out of 10, a priority

######################## chord harmonies ########################

# harmonies used to determine chords (fixed ratios don't work because they may go off key)
# these scales are the natural minor, plus a flat 2nd, flat 5th, and sharp 7th (the metal notes)
# scales have 2 full octaves (plus an extra root)
keyHarmony7 = [7,8,10,10,12,13,14,15,17,18,19,20,22,22,24,25,26,27,29,30,31]   # 5th of the scale (7 notes apprx above)
keyHarmony3 = [3,5,5,7,8,10,10,12,14,14,15,17,17,19,20,22,22,24,26,26,27]      # 3rd from above scale (3 or 4 notes above)
keyScale = [0,1,2,3,5,6,7,8,10,11,12,13,14,15,17,18,19,20,22,23,24]  

kHarm7 = pd.DataFrame(keyHarmony7)
kHarm3 = pd.DataFrame(keyHarmony3)
kScale = pd.DataFrame(keyScale)

######################## generate the main transfer function ########################

# Markov Chain / transfer function probability weightings (to be normalises later)
# these numbers are somewhat arbitrary, the chord is most likely to stay, so stay should be high
# p = 0 is offset by howMuchCrazy
# with p = 0, the unlikely transfers (P = p) are just as likley as the out of bounds transfers (P = 0)

stay = 100          # STAY prob to stay on one note
h = 20              # high probability transfers
m = 5               # medium probability transfers
p = 0               # probability of all other transfers

# the below fuction creates a MARKOV CHAIN representing my intuition about music theory
# I'm calling these Markov Chians "transfer function" but that's probably a misnomer, but whatever, it makes sense to me
# what is the probability, given the current note, of the next note
# better chord progressions and note intervals are more likely
# it should end up sounding better than a random walk

def TransferFunction():
    global tf

    # this is cut and paste from Excel, easier to draw harmony shapes in Excel
    tfDATA = {
    '0': [stay,h,m,m,m,h,m,m,h,h,h,m,m,m,m,m,m,m,m,m,m],
    '1': [m,stay,p,m,p,m,p,p,p,p,p,h,0,0,0,0,0,0,0,0,0],
    '2': [p,p,stay,m,h,p,p,p,p,p,p,p,h,0,0,0,0,0,0,0,0],
    '3': [m,m,h,stay,p,m,h,h,m,p,m,m,m,h,0,0,0,0,0,0,0],
    '5': [m,p,p,p,stay,p,p,m,p,p,p,p,p,p,h,0,0,0,0,0,0],
    '6': [m,p,p,p,p,stay,p,p,p,p,p,p,p,p,p,h,0,0,0,0,0],
    '7': [m,p,p,m,p,m,stay,h,p,p,p,p,p,m,p,m,h,0,0,0,0],
    '8': [m,p,p,m,p,p,m,stay,m,p,h,p,p,m,p,p,m,h,0,0,0],
    '10': [m,p,p,h,h,p,m,m,stay,p,h,p,p,m,m,p,m,m,h,0,0],
    '11': [m,p,p,p,p,p,p,p,p,stay,p,p,p,p,p,p,p,p,p,h,0],
    '12': [m,p,p,p,p,m,p,p,p,h,stay,h,h,h,h,h,h,h,h,h,h],
    '13': [0,p,p,p,p,p,p,p,p,p,p,stay,p,m,p,m,p,p,p,p,p],
    '14': [0,0,p,p,p,p,p,p,p,p,p,p,stay,m,m,p,p,p,p,p,p],
    '15': [0,0,0,p,p,p,p,p,p,p,p,m,m,stay,p,m,m,m,m,p,m],
    '17': [0,0,0,0,p,p,p,p,p,p,p,p,p,p,stay,p,p,m,p,p,p],
    '18': [0,0,0,0,0,p,p,p,p,p,p,p,p,p,p,stay,p,p,p,p,p],
    '19': [0,0,0,0,0,0,p,p,p,p,p,p,p,m,p,m,stay,m,p,p,p],
    '20': [0,0,0,0,0,0,0,p,p,p,p,p,p,m,p,p,m,stay,m,p,m],
    '22': [0,0,0,0,0,0,0,0,p,p,p,p,p,m,m,p,m,m,stay,p,m],
    '23': [0,0,0,0,0,0,0,0,0,p,p,p,p,p,p,p,p,p,p,stay,p],
    '24': [0,0,0,0,0,0,0,0,0,0,p,p,p,p,p,m,p,p,p,m,stay]}

    tf1 = pd.DataFrame(data = tfDATA,
    columns = ['0', '1', '2', '3', '5', '6', '7', '8', '10', '11', '12', '13', '14', '15', '17', '18', '19', '20', '22', '23', '24'],
    index = ['0', '1', '2', '3', '5', '6', '7', '8', '10', '11', '12', '13', '14', '15', '17', '18', '19', '20', '22', '23', '24'])
    # print(tf1) # looks good, rows and columns get swapped, but that is correct
    # Note: rows/indices should sum to zero, handled later in calculation

    # delete rows and columns above highest note
    tf2 = tf1.loc['0':str(highestNote),'0':str(highestNote)]
    # add crazy
    tf3 = tf2 + howMuchCrazy
    # normalise probabilities in tf, rows/index must sum to 1.0
    tf = (tf3.T / tf3.sum(axis=1)).T
    # don't know why I couldn't get this to work without transposing using axis=0, but this works, so I kept it

    ######################## MAIN TRANSFER FUNCTION ########################
    # print(tf)

######################## generate the melody transfer function ########################
# similarly, but for the melody / lead functions (single notes)

def MelodyTransferFunction():
    global mtf

    # this is cut and paste from Excel, easier to draw harmony shapes in Excel
    mtfDATA = {
    '0': [h,h,m,m,m,h,m,m,h,h,h,h,m,m,m,m,m,m,m,m,m],
    '1': [m,h,m,m,m,m,m,m,m,m,m,h,0,0,0,0,0,0,0,0,0],
    '2': [p,p,h,m,h,p,p,p,p,p,p,p,h,0,m,0,0,0,0,0,0],
    '3': [h,m,h,h,p,m,h,h,m,p,h,m,h,h,0,0,m,m,0,0,m],
    '5': [m,h,h,p,h,p,p,m,h,p,m,h,h,p,h,0,0,0,m,0,0],
    '6': [m,m,m,m,m,h,m,m,m,h,m,m,m,m,m,h,0,0,0,m,0],
    '7': [h,p,p,h,h,m,h,h,p,p,h,p,p,h,h,m,h,m,0,0,m],
    '8': [m,h,p,m,p,p,m,h,m,p,m,h,p,m,p,p,m,h,0,0,0],
    '10': [m,p,h,h,m,p,m,m,h,p,m,p,h,h,m,p,m,m,h,0,0],
    '11': [m,p,p,p,h,p,p,p,p,h,p,p,p,p,p,p,p,p,p,h,0],
    '12': [h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h,h],
    '13': [0,h,m,m,m,h,m,m,p,m,m,h,m,m,m,m,m,m,m,m,m],
    '14': [0,0,h,p,p,p,h,p,h,h,p,p,h,m,h,p,p,p,p,p,p],
    '15': [0,0,0,h,p,p,p,h,m,p,h,m,h,h,p,m,h,h,m,p,h],
    '17': [0,0,0,0,h,p,p,p,h,p,m,h,h,p,h,p,p,m,h,p,p],
    '18': [0,0,0,0,0,h,m,m,m,h,m,m,m,m,m,h,m,m,m,h,m],
    '19': [0,0,0,0,0,0,h,p,m,p,h,p,p,h,h,m,h,h,p,p,h],
    '20': [0,0,0,0,0,0,0,h,p,p,p,p,p,m,p,p,m,h,m,p,m],
    '22': [0,0,0,0,0,0,0,0,h,p,p,p,p,m,m,p,m,m,h,p,m],
    '23': [0,0,0,0,0,0,0,0,0,h,p,p,p,p,p,p,p,p,p,h,p],
    '24': [0,0,0,0,0,0,0,0,0,0,h,p,p,p,p,m,p,p,p,m,h]}

    mtf1 = pd.DataFrame(data = mtfDATA,
    columns = ['0', '1', '2', '3', '5', '6', '7', '8', '10', '11', '12', '13', '14', '15', '17', '18', '19', '20', '22', '23', '24'],
    index = ['0', '1', '2', '3', '5', '6', '7', '8', '10', '11', '12', '13', '14', '15', '17', '18', '19', '20', '22', '23', '24'])

    # delete rows and columns above highest note
    mtf2 = mtf1.loc['0':str(highestNote),'0':str(highestNote)]
    # add crazy
    mtf3 = mtf2 + howMuchCrazy
    # normalise probabilities 
    mtf = (mtf3.T / mtf3.sum(axis=1)).T

    ######################## melody transfer function ########################
    # print(mtf)

######################## CHORDS ########################
# this function limits the number of chords in the scale
# it starts on the root note (the root chord is always included)
# and follows the transfer function through n = howManyChords

def ChordsTransferFunction():
    global ct
    global chordsInKey
    chordsInKey = []
    chordsInKey.append(tf.iloc[0].index[0])  # always include tonic in chords
    chordsInKey
    newChord = '0'   # initialise newChord

    while len(chordsInKey) < howManyChords:
        newChord = np.random.choice(tf.iloc[tf.index.get_loc(newChord)].index, p = tf.iloc[tf.index.get_loc(newChord)])
        if newChord not in chordsInKey:
            chordsInKey.append(newChord)
        
    chordsInKey  # chords to be used in the chord transfer function

    # delete all other chords and re-normalise as a new dataframe
    chordTransitions = tf.loc[chordsInKey,chordsInKey]
    ct = (chordTransitions.T / chordTransitions.sum(axis=1)).T   # re-normalise

######################## CHORD PROGRESSION TRANSFER FUNCTION ########################
# print(ct)   # order doesn't matter

######################## FUNCTIONS ########################
# here are all of the musical building blocks used in the riff generation engine

def Harmony(note,interval):
    harmony = note + interval
    if interval == 3:
        harmony = int(kHarm3.iloc[int(kScale.loc[kScale.isin([note]).any(axis=1)].index[0])][0])
    elif interval == 7:
        harmony = int(kHarm7.iloc[int(kScale.loc[kScale.isin([note]).any(axis=1)].index[0])][0])
    return harmony

def Chord(note,interval,length):   # length in beats
    global time                 # so time is never explicit
    pitch = key + note
    pitch2 = key + Harmony(note,interval)
    volume = chordPick
    mf.addNote(track, channel, pitch, time, length, volume)
    mf.addNote(track, channel, pitch2, time, length, volume)
    time += length
    
def Note(note,length):
    global time                 # so time is never explicit
    pitch = key+note
    volume = chordPick
    mf.addNote(track, channel, pitch, time, length, volume)
    time += length
    
def Rest(length):
    global time
    time += length
    
def DownPM(note):
    global time                 # so time is never explicit
    pitch = key+note            # randomise whether this used note or not
    mf.addNote(PMtrack, channel, pitch, time, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 2/4, djent, downPick, annotation="PM")
    time += 1
    
def UpDown(note):
    global time                 # so time is never explicit
    pitch = key+note            # randomise whether this used note or not
    mf.addNote(PMtrack, channel, pitch, time, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 1/4, djent, upPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 2/4, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 3/4, djent, upPick, annotation="PM")
    time += 1

def Gallop(note):
    global time                 # so time is never explicit
    pitch = key+note            # randomise whether this used note or not
    mf.addNote(PMtrack, channel, pitch, time, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 2/4, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 3/4, djent, upPick, annotation="PM")
    time += 1

def RevGallop(note):
    global time                 # so time is never explicit
    pitch = key+note            # randomise whether this used note or not
    mf.addNote(PMtrack, channel, pitch, time, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 1/4, djent, upPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 2/4, djent, downPick, annotation="PM")
    time += 1
    
############ if you would prefer a specific PM pattern, you could modify this function (change odds to 0 or 1) ############
def PalmMute(note):
    if np.random.random() < 0.25:
        Gallop(note)
    elif np.random.random() < 0.25:
        RevGallop(note)
    elif np.random.random() < 0.25:
        UpDown(note)
    else:
        DownPM(note)
        
def UpDownSHORT(note):
    global time                 # so time is never explicit
    pitch = key+note            # randomise whether this used note or not
    mf.addNote(PMtrack, channel, pitch, time, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch, time + 1/4, djent, upPick, annotation="PM")
    time += 1/2
    
def PMChordSHORT(note,interval):   # length in beats
    global time                 # so time is never explicit
    pitch = key + note
    pitch2 = key + Harmony(note,interval)
    mf.addNote(PMtrack, channel, pitch, time, djent, downPick, annotation="PM")
    mf.addNote(PMtrack, channel, pitch2, time, djent, downPick, annotation="PM")
    time += 1/2
        
def PalmMuteSHORT(note,interval):
    if np.random.random() < 0.5:
        UpDownSHORT(note)
    else:
        PMChordSHORT(note,interval)

######################## RIFF GENERATING ENGINE ########################

############ if you want a specific length, you could modify this function or sett all the attributes equal above ############
def RiffLengthRandom():
    global riffLength
    if np.random.random() < 1/3:
        riffLength = riffLengthMin
    elif np.random.random() < 1/2:
        riffLength = riffLengthMed   
    else:
        riffLength = riffLengthMax

def RiffGenerator():
    # inputs and initialisation

    currentChord = '0'
    palmMuteNote = '0'
    currentNoteLength = 1/2
    currentNote = '0'

    howMuch = howMuchPM + howMuchCHORDS + howMuchMELODY + howMuchREST
    pm = howMuchPM / howMuch
    ch = howMuchCHORDS / howMuch
    ml = howMuchMELODY / howMuch
    rs = howMuchREST / howMuch

    # when doing something, more likely to keep doing that
    # stickinessFactor = 2
    pmCURRENT = 1
    chCURRENT = 1
    mlCURRENT = 1

    # internal probabilites of variation within sections of the while loop
    # to modify these, you'll need to spend time looking at the loop in detail
    # there is probably a better way to parameterise these, but this worked well enough
    pPM = 0.5   # PM internal probability
    pCH = 0.2   # Chords internal probability
    pN = 0.3    # Melody / note internal probability

######################## CALCULATION ########################
# complicated nested whiles and ifs that follow my musical intuition about how to make a metal guitar riff
# there is a stickiness factor at the end of each section, the odds are more likely that will happen again
# the stickiness was a variable, but now it's a magic number because different values seem to work better for different sections
# again, I could probably parameterise this better, but it is what it is

    global riffLength
    global time
    while time < riffLength:
        # markov chain to change chord
        currentChord = np.random.choice(ct.iloc[ct.index.get_loc(currentChord)].index, p = ct.iloc[ct.index.get_loc(currentChord)])
        currentInterval = 7
        time = int(time * 2) / 2                  # correct rounding errors in time, only 1/8 notes
        
        # palm muting
        if np.random.random() < pm * pmCURRENT:
            if np.random.random() > pPM:
                palmMuteNote = currentChord
            else:
                palmMuteNote = '0'
            if time % 1 != 0:                      # should only be 1/2 or 1 unless rounding errors
                PalmMuteSHORT(int(palmMuteNote),currentInterval)
            else:
                PalmMute(int(palmMuteNote))
            pmCURRENT = 2
            chCURRENT = 1
            mlCURRENT = 1
            
        # chords
        elif np.random.random() < ch * chCURRENT:
            #chord length
            if np.random.random() < pCH:
                currentNoteLength = 1/2
            elif np.random.random() < pCH:
                currentNoteLength = 3/2
            elif np.random.random() < pCH / 2:          # less chance of long chord
                currentNoteLength = 2
            else:
                currentNoteLength = 1
            # check how long is left, and correct to avoid overruns
            if currentNoteLength > riffLength - time:
                currentNoteLength = riffLength - time
            
            # change the chord interval randomly (mostly 5ths (7), but some 3rds)
            if np.random.random() < pCH:
                currentInterval = 3
            else:
                currentInterval = 7
                        
            if np.random.random() < pCH:             # PM chords
                PMChordSHORT(int(currentChord),currentInterval)
                if currentNoteLength >= 1:          # max of 2 PM chords in a row even with a longer chord, maybe fix this logic
                    PMChordSHORT(int(currentChord),currentInterval)
                    time += currentNoteLength - 1
                else:
                    time += currentNoteLength - 1/2
            else:
                Chord(int(currentChord),currentInterval,currentNoteLength)
            pmCURRENT = 1
            chCURRENT = 2
            mlCURRENT = 1
            
        # melody
        elif np.random.random() < ml * mlCURRENT:
            if np.random.random() < pN:                   # might not change to chord not
                currentNote = currentChord
                
            if np.random.random() < pN:                   # might change the length of the notes
                currentNoteLength *= 2
            elif np.random.random() < pN * 2:
                currentNoteLength /= 2
            
            if currentNoteLength > 2:                     # make sure note lengths are not stupid
                currentNoteLength = 1
            elif currentNoteLength < 1/2:
                currentNoteLength = 1
                
            # check how long is left, and correct to avoid overruns
            if currentNoteLength > riffLength - time:
                currentNoteLength = riffLength - time
            
            # lookup notes from markov chain
            currentNote = np.random.choice(mtf.iloc[mtf.index.get_loc(currentNote)].index, p = mtf.iloc[mtf.index.get_loc(currentNote)])
            Note(int(currentNote),currentNoteLength)
            pmCURRENT = 1
            chCURRENT = 1
            mlCURRENT = 4    # more likely to keep playing notes
            
        # rest
        elif np.random.random() < rs:
            if np.random.random() < 0.5:
                Rest(1/2)
            else:
                Rest(1)
            pmCURRENT = 1
            chCURRENT = 1
            mlCURRENT = 1

######################## OUTPUT ########################

def WriteMIDIFile():
    # function that names and saves midi files
    # attributes to identify file uniquely
    filename = ""
    bars = riffLength / 4     # check how long the riff is
    chordz = ""
    for i in chordsInKey:
        chordz += i
        chordz += "_"
    now = datetime.now()
    ############## IF YOU'RE NOT GETTING ALL OF YOUR FILES, ROUND THIS LESS VVVVV ##############
    timestamp = now.strftime("%Y%m%d_%H%M%S.") + str(int(int(now.strftime("%f"))/1000))
    filename = ("b" + str(int(bars)) 
                # + "cz" + str(howMuchCrazy) 
                # + "h" + str(highestNote) 
                # + "pm" + str(howMuchPM) 
                # + "ch" + str(howMuchCHORDS) 
                # + "m" + str(howMuchMELODY) 
                # + "r" + str(howMuchREST) 
                # + "t" + str(tempo) 
                + "_" + chordz
                + timestamp
                + ".mid")

    with open(filename, 'wb') as out:
        mf.writeFile(out)

def Main():
    # this runs through the functions in order to produce a metal guitar riff and save a midi file in your working directory
    # if you want to run it multiple times, choose repeats > 1
    # songParts is the number of riffs that are generated using the same random attributes (chords, ratios), making them more consisten
    # songParts of 2 or 3 can be combined into complicated riffs, often riffs follow AAAB structure or similar
    # choosing riffs with similar initialisation values with make them more consistent

    repeats = 5             # run the entire riff generator multiple times, each time iterating over all songParts
    songParts = 3           # 2 or 3 for AAAB ABAC etc song structure, using same chords (more coherent) / more for full song
    for i in range(repeats):
        CreateMIDIFile() 
        RandomiseInputs()
        TransferFunction()
        MelodyTransferFunction()
        ChordsTransferFunction()
        RiffLengthRandom()
        ############## IF YOU'RE NOT GETTING ALL OF YOUR FILES, ROUND TIMESTAMP LESS ##############
        ############## see above in WriteMIDIFile() function definition ##############
        for j in range(songParts):
            if j > 0:
                CreateMIDIFile() 
            RiffGenerator()
            WriteMIDIFile()

# run the main function       
if __name__ == "__main__":
    Main()