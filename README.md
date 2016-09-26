# CyOPTICS clustering

# What is this?
So there is a very powerful [clustering](https://en.wikipedia.org/wiki/Cluster_analysis) algorithm called [OPTICS](https://en.wikipedia.org/wiki/OPTICS_algorithm) which I wanted to utilize for my project, but I just couldn't find a proper and fast enough Python implementation I could use. One week later, I completed my implementation and decided to share it with the world!

# Cool! How can I use it?

## Dependencies
First, you need to have the following installed to use this:

1. Python 2.7
2. numpy 1.11.0+
3. cython 0.24.0+ 
  * If you are of Windows, you may have trouble installing it, use [this](https://github.com/cython/cython/wiki/CythonExtensionsOnWindows) tutorial. Modifying the find_vcvarsall() function and setting "compiler=msvc" worked for me.
  * If you are on Linux, cython installs without a hitch. It's free and it works, what more say?
4. matplotlib 1.5+
  * This is just for data vizualization, if you just want raw data it is possible not to use matplotlib whatsoever.

That's it, there are no crazy dependencies! Yay!

## Usage
**For the impatient:** If you want to dive into the code ASAP and don't want to read the whole page, download the repository and run the **runOPTICS.py** script. You will be presented with a few graphs and a final result. It you want to know what those actually are, keep reading...

Generally, OPTICS works in 2 stages. First, you build a reachability plot, then you extract clusters from that plot. A bit unusual for a clustering algorithm, I know, but it seems to work.  You can read more about OPTICS in general [HERE](https://en.wikipedia.org/wiki/OPTICS_algorithm).

I will provide you with a step-by-step guide how to use the whole thing.

### Input data

First, we need to talk about our input data. For demonstration purposes, I have used plain old points in 2 dimensions. The points are organized in [Gaussian point sources](http://pypr.sourceforge.net/mog.html). There are several point sources with different standard deviations (i.e. "spreads"). The image of our input data is given in Figure 1.
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18817087/a0d3114e-8325-11e6-8e96-0533e54398bc.png>
<br>
Figure 1. Input data points
</p>

How many individual clusters can you identify?

I will help you out by marking the individual clusters that were generated:
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18817088/a0d4becc-8325-11e6-89aa-188d0c2a989e.png>
<br>
Figure 2. Input ddata points with marked clusters
</p>

As you can see, the generated clusters are quite complex. In the upper left corner we have one large disperse cluster with a smaller, more concentrated in its centre. And at the bottom of that cluster there is another disperse cluster, albeit a smaller one.
In the upper right corner there is one lone concentrated cluster which we will use as a control cluster. The algorithm should always nicely identify that one.
Finally, at the bottom we have one larger disperse cluster with 2 smaller ones inside.
These input points should pose any clustering algorithm a huge challenge! (Just try to properly detect those with DBSCAN, I dare you!)

### Metric funtion
One of the most important part of each clustering algortihm is its metric funtion. A metric function is basically a way by which you can get a quantifiable measure of similarity between two data points. In the case of points on a 2D plane, I used the good old Euclidean distance:
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18819088/42877ce2-8357-11e6-89d7-2698a1bd5b6d.gif>
</p>
This was implemented as a function in the Cython script, and the reason for it is that it has to run fast, as it is the funtion with the largest number of calls.

If you are implementing you own metric function, please be aware that it is probably the largest contributor to the runtime of this script. If you take a look at the source code, you will see that the Euclidean distance function does not use any of the Python magic, thus it is directy translated to C (which makes it run fast). When optimizing you code, use `cython -a cyOPTICS.pyx` to see if your metric function needs optimization. If you run that command on the original cyOPTICS.pyx, and open the generated HTML file, you will see that all lines in the Euclidian distance funtion are white, meaning they are not using any Python functions, just pure C.


### Building the reachability plot
OPTICS does not generate an output list of clusters right away. First, you need to build something called a **"reachability plot"**. This plot basically shows you the results of the OPTICS ordering - it orders points by their mutual distance. To build this plot you need to give the algotihm 2 input parameters: **min_points** and **elipson**. I will give you a general description of there 2 parameters, but I recommend that you look into the original [(Ankerst et al. 1999) paper](http://fogo.dbs.ifi.lmu.de/Publikationen/Papers/OPTICS.pdf) for a more detailed explanation.

* **min_points** defines how many neighbouring points a certain point must have to be a core point, and also defines the minimum size of an individual cluster.
* **epsilon** defines the maximum similarity distance between the points - i.e. the algorithm will "grow" an individual cluster if the next point is within this distance. The value of epsilon doesn't have to be defined, you can just put a large number if you are unsure what to use, but the algorithm will run longer in that case. If you do however have a notion which value to use, it will help to reduce the runtime significanty as the algorithm will not check every point again each other.

To obtain the reachability plot, the function **runOPTICS** from the runOPTICS.py file is called, which actually wraps the original Cython function runCyOPTICS from the cyOPTICS.pyx file for you convenience, so you don't have to worry about Cython stuff at all. Now let's see how the reachability plot looks like for our input data and input parameters:

* **min_points = 40**
* **epsilon = 5.0**
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18817085/8ebe1580-8325-11e6-860f-da8b54e07278.png>
<br>
Figure 3. The resulting reachability diagram with marked clusters
</p>

Clusters in reachability plots are manifested as **valleys** in the plot. The **deepness** of the valleys (i.e. the reachability distance between the points) indicates the **density** of the clusters. **Deeper valleys mean denser clusters**, and vice versa. 

What can we tell about our clusters from this plot? You can notice that I have marked individual clusters with letters A-G. How did I know that those are really our clusters? Or to be more exact, how did I know that A and E are also clusters?

Let's take a look at the plot. One obvious thing is that there are **2 large spikes** on the plot, at **points 195 and 277**. These points mark the beginning of new clusters. Think about it this way - if the points are ordered by their mutual distance, then if you have a large spike in the plot that means the point at the spike is very distant from the previous point. If the spike is followed by a valley, then you certainly know that it is a cluster!

Now let's start analyzing the plot from left to right:

* First we can see that there are two valleys between points 0 and 195. The first valley (B) is higher than the second one (C), meaning that is has a higher dispersion of points (i.e. the individual distance between points are higher). The two valleys are separated by a small spike with the reachability distance of only ~1.5. Furthermore, it can be noticed that the valley C does not have a sharp ending, but it climbes slowly up. These are evidence for claiming that they are in fact a part of a larger, more disperse cluster. When we look more carefully, the points of cluster C are actually those from 65 to 125 (as they are of approximately the same reachability distance), while the rest of points to 195 are a part of that disperse background cluster.
* As for the cluster D, it is surrounded by high spikes in reachability distances. This is the evidence that this is in fact that lone and dense cluster on the right side of Figure 2.
* Finally, we have a similar situation as we had before, 2 clusters (F and G) inside one disperse cluster (E).

"*OK, OK, enough with this reachability plot business already*", I can hear some of you say, "*we want real clusters, not some mind-boggling valleys!*".

### Extracting clusters from reachability plots
As it was demonstrated in the previous section, the whole business of cluster identification is reduced from the original problem in N dimensions (in our case N = 2, but you could have data of more dimensions) to a 1D problem of detecting valleys in the reachability plot. This means it doesn't really matter what your initial data or the problem is, being it a simple 2D clustering or some crazy clustering in 11 dimensions, in the end it all boils down to the same thing.

Although it may *sound* easy, the problem of robustly detecting valleys is far from it. I have first tried to implement the original method of cluster extraction from [(Ankerst et al. 1999)](http://fogo.dbs.ifi.lmu.de/Publikationen/Papers/OPTICS.pdf) without much success. I just couldn't crack the algorithm, the original [Java impementation](https://github.com/anupambagchi/elki/blob/master/src/main/java/de/lmu/ifi/dbs/elki/algorithm/clustering/OPTICSXi.java) is not very well documented. The description in the paper is just too high-level to be usable.

Just as I was starting to think I will have to pull the plug on the project, I found the [(Brecheisen et al., 2004)](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.215.3924&rep=rep1&type=pdf) paper describing a new gradient method of cluster extraction. I gave it a go and it seems to be working! I will not describe the method in detail, you can read the original paper (section 3.2), or follow this [LINK](https://github.com/atidjani/IoSL_Clustering/wiki/Gradient-Clustering) for more details. In short, the method detects gradients in the data by finding inflection points in the reachability plot. In essence, this means that it detects areas which begin and end with a certain steepness, which you can define. 


Take a look at Figure 3. It can easily be noticed that all clusters start with steep lines going down and end with steep lines going up. Areas in between are more or less flat. If you detect all steep areas and pair them with each other, in between them you should have real clusters. And that is in short the main idea of this algorithm. Figure 4 illustrates the method.

<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18818893/5f06b576-8353-11e6-8601-6a598b13227e.png>
<br>
Figure 4. Gradent method illustration
</p>

The gradient clustering method takes 2 parameters, **t** and **w**. Parameter **t** determines the threshold of steepness you are interested in. The steepness at each point is determied by pairing the previous and the current point, and the current and the subsequent point in two lines. Then the angle between the two is determined. If t = 150°, then the points with gradients <150° and >210° will be taken as steep points. As a general rule of thumb, if you encrease the **t** value, you will get more clusters detected and vice versa. The **w** parameter sets the width between points in the reachability plot. This value directy influences the **t** value as with the width between the points the angle between them also changes. During my testing, I have always used **w = 0.025**, and **t** in the **120-160** range.

The gradient clustering is run by invoking the **gradientClustering** function from the GradientClustering.py file. When we run the gradient clustering with parameters **w = 0.025** and **t = 150** we get the result shown in figure 5. Each cluster is represented by a horizontal line with has its beginning at the first and its end at the last point of the cluster.
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18819103/969cd5ca-8357-11e6-9726-27bb2d0855d2.png>
<br>
Figure 5. Results of gradient cluster identification
</p>
"*Well hot damn, that's a lotta clusters rite 'ere, a bit too much for my likin'.*" - I know, the algorithm detected 59 of them, which is a bit too much. But if we take a closer look, we can notice that the algorithm actually properly detected all clusters, but some it detected several times. What it actually did is it detected the cluster *too* well, every single sudden change in the plot was detected, but for the most part, the clusters in individual valleys are quite similar to each other by their size and the points they contain. Well if only we could somehow merge those ones which are similar...

### Postprocessing - Filtering and merging similar clusters
#### Removing large clusters
One short thing before merging the clusters. When I experimented with various settings of the algorithm, I have found that it sometimes produces very large clusters, often 50% larger than the total number of input points. Thus there is one extra step where you can remove all clusters larger then a certain percentage of the total number of points. You can modify the **max_points_ratio** variable to you liking, or leave it at 0.5. The algorithm calls the **filterLargeClusters** function from the GradientClustering.py file and removes all clusters which contain at least 50% (i.e. 0.5) of the total number of input points. This filter actually puts an upper limit on the size of individual clusters, meaning that you can actually define the range of cluster sizes you are interesed in. If you don't want to use this feature, just set **max_points_ratio = 1.0**.

#### Merging similar clusters
The algorithm for merging clusters is quite simple in fact, it just looks at the intersection between every cluster, and merges the two clusters if they share at least some predefined fraction of points. This is done iteratively until no more clusters can be merged. At every iteration, the clusters are sorted so at the beginning of every iteration smaller clusters have a higher probability of being merged. If this was not done, then middle-sized clusters would have merged to larger ones, 'escaping' the smaller ones and you end up with a bunch of small and large clusters. Sorting the clusters by size at each iteration results in a distribution of middle to large sized clusters. 

If you look at the figure 5, you can notice that smaller clusters are below larger ones (that is because of the way I decided to plot them, the vertical component of each line is determined by the final reachability distance of a cluster). I like to think of this algorithm in an illustrative way: smaller clusters are reaching up and clinging to the cluster above them. If they have a lot in common, they merge and become one. Simple! And they say that opposites attract, hmph...

You can control the fraction of points which the clusters must share to be merged by changing the **cluster_similarity_threshold** variable. I keep it at 0.7, meaning that that have to have at least 70% points in common to be merged. The function **mergeSimilarClusters** from the GradientClustering.py file is called and the clusters are merged. You can see the results in figure 6.
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18819376/cd6340d4-835d-11e6-87d9-13d5693537ad.png>
<br>
Figure 6. Results of cluster merging
</p>

"*Hey, that's more like it!*" - Wait for a few moments and we well see how the clusters actually look on the 2D plot. But judging from the previous figure, it seems that all were properly detected. But wait, the figure says 8 clusters, didn't we have only 7?

### Final results
<p align="center">
<img src=https://cloud.githubusercontent.com/assets/7250465/18819421/c3d73cd6-835e-11e6-806b-3d0fa8dfee9d.png>
<br>
Figure 7. Final clustering results
</p>
Figure 7 shows our final results. Different clusters are represented in different colors. But what is the deal with that one extra cluster, which one is the extra one? 

What actually hapened is the algorithm connected points in those clusters on the upper left hand side and decided that they are similar, so it concluded that there is one big cluster, in which there are 2 smaller ones, and one of the smaller ones has an even smaller one inside. But here is the twist, the **extra one is actually our A cluster**! It turnes out that there are actually 2 clusters in place of the C cluster (compare figures 3 and 6), on the upper left hand side of the 2D plot: the disperse one on the top, and the small dense one in the middle of it. The cluster A is a cluster of all points on the upper left hand size, which in reality we did not generate. If you notice that when I assigned letters to individual clusters on the reachability diagram, I did not talk about which cluster is which. In fact when I produced the graphs I didn't think about it, but now it is obvious that I had made a mistake (which I will intentinally leave in this tutorial). This only shows that not everyone is infallible even when it comes to simple feature detection on reachability diagrams. In this case it was a simple 2D plot where we could notice our mistake, but if you had the data of higher dimension which you cannot easily visualize, how would you know that you made a mistake in manually choosing clusters on the reachability plot? Fortunately the algorithim gave us all solutions and what is most important it recognized the area of higher density which we would have easily missed.

### Final remarks
Feel free to fiddle with the input parameters to see how the whole thing works. You will notice that the result are in fact dependant on the input parameters, but this just says that you need to *know thy data* and choose proper parameters on some form of reasoning. Of you could calibrate the parameters on some known data until you get what you want, then apply it to other data.

I hope you will enjoy using this software as least as I have enjoyed making it!

# Citing and use for academic papers
If you find this work interesting, feel free to use it! I would ask you to reference this GitHub page until I publish a proper paper on application of this method.

