# CyOPTICS clustering

## What is this?
So there is a very powerful [clustering](https://en.wikipedia.org/wiki/Cluster_analysis) algorithm called [OPTICS](https://en.wikipedia.org/wiki/OPTICS_algorithm) which I wanted to utilize for my project, but I just couldn't find a proper and fast enough Python implementation I could use. One week later, I completed my implementation and decided to share it with the world!

## Cool! How can I use it?

### Dependencies
First, you need to have the following installed to use this:

1. Python 2.7
2. numpy 1.11.0+
3. cython 0.24.0+ 
  * If you are of Windows, you may have trouble installing it, use [this](https://github.com/cython/cython/wiki/CythonExtensionsOnWindows) tutorial. Modifying the find_vcvarsall() function and setting "compiler=msvc" worked for me.
  * If you are on Linux, cython installs without a hitch. It's free and it works, what is more to be said?
4. matplotlib 1.5+
  * This is just for data vizualization, if you just want raw data it is possible not to use matplotlib whatsoever.

That's it, there are no crazy dependencies! Yay!

### Usage
**For the impatient:** If you want to dive into the code ASAP and don't want to read the whole page, download the repository and run the runOPTICS script. You will be presented with a few graphs and a final result. It you want to know what those actually mean, keep reading...

Generally, OPTICS works in 2 stages. You can read more about it [HERE](https://en.wikipedia.org/wiki/OPTICS_algorithm). First, you build a reachability plot, then you extract clusters from that plot. A bit unusual for a clustering algorithm, I know, but it seems to work.

I will provide you with a step-by-step guide how to use the whole thing.

#### Input data

First, we need to talk about our input data. For demonstration purposes, I have used plain old points in 2 dimensions. The points are organized in [Gaussian point sources](http://pypr.sourceforge.net/mog.html). There are several point sources with different standard deviations (i.e. "spreads"). Here is the image of our input data.
![1_input_data](https://cloud.githubusercontent.com/assets/7250465/18816738/50212e3c-831d-11e6-9357-6b76f5f81833.png)

How many individual clusters can you identify?

I will help you out by marking the individual generated clusters:
![1_input_data_marked](https://cloud.githubusercontent.com/assets/7250465/18816739/502127a2-831d-11e6-95dc-1cbbc2924fe5.png)

As you can see, the generated clusters are quite complex. In the upper left corner we have one large disperse cluster with a smaller, more concentrated in its centre. And at the bottom of that cluster there is another disperse cluster, albeit a smaller one.
In the upper right corner there is one lone concentrated cluster which we will use as a control cluster. The algorithm should always nicely identify that one.
Finally, at the bottom we have one larger disperse cluster with 2 smaller ones inside.
These input points should pose any clustering algorithm a huge challenge!

#### Metrics funtion
One of the most important part of each clustering algortihm is its metrics funtion. A metrics function is basically a way by which you can get a quantifiable measure of similarity between two data points. In the case of points on a 2D plane, I used the good old Euclidean distance. This was implemented has a function in the Cython script, and the reason for it is that it has to run fast, as it is the funtion with the largest number of calls.

If you are implementing you own metrics function, please be aware that it is probably the largest contributor to the runtime or your software. If you take a look the the source code, you will see that the Euclidean distance function does not use any of the Python magic, thus it is directy translated to C (which makes it run fast). When optimizing you code, use `cython -a cyOPTICS.pyx` to see if your metrics function needs optimization. If you run that command on the original cyOPTICS.pyx, and open the generated HTML file, you will see that all lines in the Euclidian distance funtion are white, meaning they are not using any of the Python magic.


#### Building the reachability plot
OPTICS does not generate an output list of clusters right away. First, you need to build something called a "reachability plot". This plot basically shows you the results of the OPTICS ordering - it orders points by their mutual distance. To build this plot you need to give the algotihm 2 input parameters: **min_points** and **elipson**. I will give you a general description of there 2 parameters, but I recommend that you look into the original [(Ankerst et al. 1999) paper](http://fogo.dbs.ifi.lmu.de/Publikationen/Papers/OPTICS.pdf) for a more detailed explanation.
* **min_pts** defines how many neighbouring points a certain point must have to be a core point, and also defines the minimum size of an individual cluster.
* **epsilon** defines the maximum similarity distance between the points - i.e. the algorithm will "grow" an individual cluster if the next point is within this distance

The function 
