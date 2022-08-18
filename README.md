# Writing Heavy Metal Guitar Riffs With Python
#### Video Demo:  
[![Heavy Metal In Python](https://img.youtube.com/vi/EOAXEARPwSg/0.jpg)](https://www.youtube.com/watch?v=EOAXEARPwSg)
###### By: Kevin, Dec 2021

## Introduction

This python program uses random inputs, probabilities, and music theory to algorithmically write heavy metal guitar. Inputs can be tweaked and probabilities can be altered to customise the guitar parts. The program outputs a specified number of MIDI files, which can be imported into music software or used to learn the parts on a real guitar.

## Theory

[Markov Chain](https://en.wikipedia.org/wiki/Markov_chain)'s are the main concept used to implement music theory in this program. A Markov Chain is a matrix of probabilities which can be used to determine the likelihood of moving to another note, given what the current note is. Different Markov Chains are used for chords vs melodies, and both matrices represent my personal intuition about music theory.

For the musical scale, I used a composite scale with all of the notes from the natural and harmonic minor scale, as well as the flat second and flat fifth (the metal sounding notes). This means that looking up values can't be done using scale degrees, and must be done using additional lookup scales (keyHarmony3 and keyHarmony7).

Other theory utilised includes common increments for 2-note chords (most common in heavy metal), and most common timing for notes and rests. All of these inputs are fairly arbitrary, and again, they mostly just represent my personal intuition about music theory. Different choices for scales, harmonies, and Markov probabilities will lead to different sounding music.

## Important Inputs

Most of the randomisation inputs are treated as 0-10 ratings for likelihood, and normalised later. However, nothing actually limits these (other than negative values will likely lead to errors). In the base file, there is a random int generator for each of these values.

howMuchCrazy: How likely the next note or chord is to "disobey" music theory.
howManyChords: How many chords in the riff. All other chords are deleted from the chords Markov Chain before generating the riff.
highestNote: Up to 2 octaves above the root note. All higher notes are deleted from both Markov Chains.
howMuchPM: How much palm muting happens.
howMuchCHORDS: How often chords happen.
howMuchMELODY: How often single notes happen.
howMuchREST: How often rests happen.

repeats and songParts: Also important inputs, repeats and songParts (from Main()) determine how many MIDI files are outputted. By default, with 5 repeats and 3 songParts, the randomisation is completed 5 times, each time outputting 3 similar sounding riffs (same chords, style probabilities, and lengths). This gives a total of 15 MIDI tracks (by default).

## Interesting Stuff

I didn't tweak any of the Markov Chain matrices or transfer probability inputs, even though I expected to. Either my first instincts were good enough, or I could have gotten better results by tweaking these. This would be a large undertaking, and would be difficult to test without automated method for importing and writing drums for each part. This would also vary based on musical taste.

## Limitations

On my computer, it takes about 2 milliseconds to output a MIDI file. If it goes much faster than this, the timestamp in WriteMIDIFile() will need to be rounded less to avoid saving over files.

There are a few magic numbers and numbers that are arbitrarily parameterised. I could clarify or expand these parameters a bit, but at some point it changes from coding to artistic judgement. I don't think this is worth improving, but the current version could be considered sloppy in places.

This program won't arrange music, it can't write drums, bass, or vocals, and there is some work needed to get it sounding realistic once you've imported the MIDI into your music software. Otherwise, it works a lot better than I expected.

## Future Possibilities

It would be possible to combine similar riffs into longer variations. Many metal guitar riffs follow standard structures, for example AAAB or ABAC (for parts A, B, and C). This was originally part of my plan, but I have spent a lot of time on this, and wanted to get finished.

It would also be nice to get a matching bassline or kick drum pattern with each riff. These are easy enough to do by hand in most music software, so I don't think that is worth the extra code, clutter, or time to implement.

There are a few things that are impossible in this algorithm that happen in normal music, for example 16th notes that aren't muted (that would be an easy fix, but probabilities would need tweaking). It would be difficult to implement every possibility, but could be interesting to explore a few more ideas (maybe string bends).

## Conclusions

Python is a better guitar player than I thought it would be.
