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
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18817087/a0d3114e-8325-11e6-8e96-0533e54398bc.png>
</p>

How many individual clusters can you identify?

I will help you out by marking the individual generated clusters:
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18817088/a0d4becc-8325-11e6-89aa-188d0c2a989e.png>
</p>

As you can see, the generated clusters are quite complex. In the upper left corner we have one large disperse cluster with a smaller, more concentrated in its centre. And at the bottom of that cluster there is another disperse cluster, albeit a smaller one.
In the upper right corner there is one lone concentrated cluster which we will use as a control cluster. The algorithm should always nicely identify that one.
Finally, at the bottom we have one larger disperse cluster with 2 smaller ones inside.
These input points should pose any clustering algorithm a huge challenge!

#### Metrics funtion
One of the most important part of each clustering algortihm is its metrics funtion. A metrics function is basically a way by which you can get a quantifiable measure of similarity between two data points. In the case of points on a 2D plane, I used the good old Euclidean distance. This was implemented as a function in the Cython script, and the reason for it is that it has to run fast, as it is the funtion with the largest number of calls.

If you are implementing you own metrics function, please be aware that it is probably the largest contributor to the runtime of this script. If you take a look the the source code, you will see that the Euclidean distance function does not use any of the Python magic, thus it is directy translated to C (which makes it run fast). When optimizing you code, use `cython -a cyOPTICS.pyx` to see if your metrics function needs optimization. If you run that command on the original cyOPTICS.pyx, and open the generated HTML file, you will see that all lines in the Euclidian distance funtion are white, meaning they are not using any of the Python magic.


#### Building the reachability plot
OPTICS does not generate an output list of clusters right away. First, you need to build something called a "reachability plot". This plot basically shows you the results of the OPTICS ordering - it orders points by their mutual distance. To build this plot you need to give the algotihm 2 input parameters: **min_points** and **elipson**. I will give you a general description of there 2 parameters, but I recommend that you look into the original [(Ankerst et al. 1999) paper](http://fogo.dbs.ifi.lmu.de/Publikationen/Papers/OPTICS.pdf) for a more detailed explanation.

* **min_pts** defines how many neighbouring points a certain point must have to be a core point, and also defines the minimum size of an individual cluster.
* **epsilon** defines the maximum similarity distance between the points - i.e. the algorithm will "grow" an individual cluster if the next point is within this distance. The value of epsilon doesn't have to be defined, you can just put a large number if you are unsure what to use, but the algorithm will run longer in that case. If you do however have a notion which value to use, it will help to reduce the runtime significanty as the algorithm will not check every point again each other.

Now let's see how the reachability diagram looks like for our input data and input parameters:

* **min_points = 40**
* **epsilon = 5.0**.
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18817085/8ebe1580-8325-11e6-860f-da8b54e07278.png>
</p>

Clusters in reachability plots are manifested as valleys in the plot. The deepness of the valleys (i.e. the reachability distance between the points) indicates the density of the clusters. Deeper valleys mean denser clusters, and vice versa. 

What can we tell about our clusters from this plot? You can notice that I have marked individual clusters with letters A-G. How did I know that those are really our clusters? Or to be more exact, how did I know that A and E are also clusters?

Let's take a look at the plot. One obvious thing is that there are 2 large spikes on the plot, at points 195 and 277. These points mark the beginning of new clusters. Think about it this way - if the points are ordered by their mutual distance, then if you have a large spike in the plot that means the point at the spike is very distant from the previous point. If the spike is followed by a valley, then you certainly know that it is a new cluster!
