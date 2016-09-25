# CyOPTICS clustering

## What is this?
So there is a very powerful [clustering](https://en.wikipedia.org/wiki/Cluster_analysis) algorithm called [OPTICS](https://en.wikipedia.org/wiki/OPTICS_algorithm) which I wanted to utilize for my project, but I just couldn't find a proper and fast enough Python implementation I could use. One week later, I completed my implementation and decided to share it with the world!

## Cool! How can I use it?

### Dependencies
First, you need to have the following installed to use this:
+ Python 2.7
+ numpy 1.11.0+
+ cython 0.24.0+ 
..+ If you are of Windows, you may have trouble installing it, use [this](https://github.com/cython/cython/wiki/CythonExtensionsOnWindows) tutorial. Modifying the find_vcvarsall() function and setting "compiler=msvc" worked for me.
..+ If you are on Linux, cython installs without a hitch. It's free and it works, what is more to be said?
+ matplotlib 1.5+
..+ This is just for data vizualization, if you just want raw data it is possible not to use matplotlib whatsoever.

That's it, there are no crazy dependencies! Yay!

### General layout



Fast OPTICS clustering in cython + gradient cluster extraction
