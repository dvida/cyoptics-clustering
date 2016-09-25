# CyOPTICS clustering

## What is this?
So there is a very powerful [clustering](https://en.wikipedia.org/wiki/Cluster_analysis) algorithm called [OPTICS](https://en.wikipedia.org/wiki/OPTICS_algorithm) which I wanted to utilize for my project, but I just couldn't find a proper and fast enough Python implementation I could use. One week later, I completed my implementation and decided to share it with the world!

## Cool! How can I use it?

### Dependencies
First, you need to have the following installed to use this:
1. Python 2.7
2. numpy 1.11.0+
3. cython 0.24.0+ 
..* If you are of Windows, you may have trouble installing it, use [this](https://github.com/cython/cython/wiki/CythonExtensionsOnWindows) tutorial. Modifying the find_vcvarsall() function and setting "compiler=msvc" worked for me.
..* If you are on Linux, cython installs without a hitch. It's free and it works, what is more to be said?
4. matplotlib 1.5+
..* This is just for data vizualization, if you just want raw data it is possible not to use matplotlib whatsoever.

That's it, there are no crazy dependencies! Yay!

### Usage
Generally, OPTICS works in 2 stages. You can read more about it [HERE](https://en.wikipedia.org/wiki/OPTICS_algorithm). First, you build a reachability plot, then you extract clusters from that plot. A bit unusual for a clustering algorithm, I know, but it seems to work.

I will provide you with a step-by-step guide how to use the whole thing.

#### Inpout data and the metrics function

First, we need to talk about our input data. For demonstration purposes, I have used plain old points in 2 dimensions. The points are organized in [Gaussian point sources](http://pypr.sourceforge.net/mog.html). There are several point sources with different standard deviations (i.e. "spreads"). Here is the image of our input data.


#### Building the reachability plot. 
OPTICS does not generate an output list of clusters right away. First, you need too build something called a "reachability plot." This plot basically tells you
You give it the input data and 2 input parameters: **min_points** and **elipson**. 
..* **min_pts** defines how many neighbouring points a certain paoint must have to be a core point



Fast OPTICS clustering in cython + gradient cluster extraction
