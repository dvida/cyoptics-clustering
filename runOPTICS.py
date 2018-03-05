# MIT License

# Copyright (c) 2016 Denis Vida

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import print_function, division, absolute_import

import numpy as np

# Cython init
import pyximport
pyximport.install(setup_args={'include_dirs':[np.get_include()]})
from cyOPTICS import runCyOPTICS


def runOPTICS(input_list, eps, min_pts):
    """ A wrapper funtion for the OPTICS clustering Cython implementation.
    Arguments:
        input_list: [ndarray] 2D numpy array containing the input data (1 datum per row)
        eps: [float] epsilon parameter - maximum distance between points
        min_pts: [int] minimum points in the cluster

    Return:
        point_list: [ndarray] 2D numpy array containing information about every processed point, the columns
            of the array are:
            - processed: 0 for not processed, 1 for processed - upon returning, processed values of all 
                entries should be 1
            - reachability distance: -1 for first points in the cluster, positive for all others
            - core distance: -1 for noise, positive otherwise (the notion of noise can change with regard to 
                the different input values eps and min_pts)
            - input data points (the input data colums are appended to the right)
    """

    return runCyOPTICS(input_list, eps, min_pts)



def sampleGaussian(x, y, std_x, std_y, n_samples):
    """ Draw samples from a 2D Gaussian distribution with the given input parameters. """

    mean = [x, y]
    cov = [[std_x, 0], [0, std_y]]  # diagonal covariance
    return np.random.multivariate_normal(mean, cov, n_samples)


def plotPoints(points, clusters=[], title=''):

    # Plot all points
    plt.scatter(points[:,0], points[:,1], c='k', linewidth=0.2, edgecolor='w', facecolor=None)

    # Plot clusters, if any
    if clusters:

        # Generate a list of colors for each cluster and randomize their order (so close clusters would have
        # significcantly different color)
        colors = cm.inferno(np.linspace(0.3, 1, len(clusters)))
        color_order = random.sample(range(len(colors)), len(colors))

        # Plot the clusters in 2D
        for color, cluster in zip(colors[color_order], clusters):
            plt.scatter(ordered_list[cluster][:,3], ordered_list[cluster][:,4], c=color, linewidth=0.2, 
                edgecolor='w')

    # Set the title
    plt.title(title)

    # Turn on the grid, set color to grey
    plt.gca().grid(color='0.5')

    # Set background color to black
    plt.gca().set_axis_bgcolor('black')

    # Set the ratio to the window size 1:1
    plt.gca().set_aspect('equal')
    plt.tight_layout()

    plt.show()




if __name__ == '__main__':

    import matplotlib.pyplot as plt
    import matplotlib.cm as cm
    import time
    import random

    from GradientClustering import gradientClustering, plotClusteringReachability, filterLargeClusters, \
        mergeSimilarClusters


    ### Set OPTICS parameters
    # See this paper for more information:
    # http://fogo.dbs.ifi.lmu.de/Publikationen/Papers/OPTICS.pdf

    min_points = 40
    epsilon = 5.0

    ###
    
    ### Gradient clustering parameters
    # See this paper for more details about there parameters (section 3.2)
    # http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.215.3924&rep=rep1&type=pdf

    t = 150 # deg

    # Width between the data in the reachability diagram
    w = 0.025

    ###

    ### Cluster postprocessing parameters

    # Value which determines the size of the largest cluster, i.e. if the value is 0.5, all clusters larger 
    # than 50% of the number of the total input points will be rejected (max. value of 1.0)
    max_points_ratio = 0.5

    # Value which determines how similar clusters are to be merged, i.e. if 0.7 then 2 clusters must share at
    # least 70% common points to be merged (max. value of 1.0)
    cluster_similarity_threshold = 0.7

    ###


    ### Generate input data as Gaussian point sources

    np.random.seed(1)

    # Range of points per cluster
    points_per_cluster_range = [50, 100]

    input_data = np.empty((0, 2))

    input_data = np.r_[input_data, sampleGaussian(-5, 6, 2.3, 2.3, 
        np.random.randint(*points_per_cluster_range))]

    input_data = np.r_[input_data, sampleGaussian(-5, 6, 0.05, 0.05, 
        np.random.randint(*points_per_cluster_range))]

    input_data = np.r_[input_data, sampleGaussian(-5, 2, 0.4, 0.4, 
        np.random.randint(*points_per_cluster_range))]

    input_data = np.r_[input_data, sampleGaussian(8, 5, 0.3, 0.3, 
        np.random.randint(*points_per_cluster_range))]

    input_data = np.r_[input_data, sampleGaussian(4, -1, 0.1, 0.1, 
        np.random.randint(*points_per_cluster_range))]

    input_data = np.r_[input_data, sampleGaussian(1, -2, 0.2, 0.2, 
        np.random.randint(*points_per_cluster_range))]

    input_data = np.r_[input_data, sampleGaussian(3, -2, 2.0, 2.0, 
        np.random.randint(*points_per_cluster_range))]

    ### 

    print('Input data size', len(input_data))

    # Plot input data
    plotPoints(input_data, title='Input data')


    t1 = time.clock()

    # Run OPTICS ordering
    ordered_list = runOPTICS(input_data, epsilon, min_points)

    print('Total time for processing', time.clock() - t1, 's')

    print('Ordered list')
    print('Point index [Processed, reachability dist, code dist, input data ... ]')
    for j, entry in enumerate(ordered_list):
        print(j, entry)

    print(ordered_list[:,1])

    # Plot the reachability diagram
    plotClusteringReachability(ordered_list[:,1])


    # Do the gradient clustering
    clusters = gradientClustering(ordered_list[:,1], min_points, t, w)


    # Remove very large clusters
    filtered_clusters = filterLargeClusters(clusters, len(ordered_list), max_points_ratio)


    print('TOTAL BEFORE MERGING', len(filtered_clusters))

    # Plot the results, reachability diagram
    plotClusteringReachability(ordered_list[:,1], filtered_clusters)

    
    # Merge similar clusters by looking at the ratio of their intersection and their total number
    filtered_clusters = mergeSimilarClusters(filtered_clusters, cluster_similarity_threshold)

    print('TOTAL POINTS', len(ordered_list[:,1]))
    print('CLUSTERS')
    for cluster in filtered_clusters:

        members = ordered_list[cluster][:,3:]
        
        x_mean = np.mean(members[:,0])
        x_std = np.std(members[:,0])

        y_mean = np.mean(members[:,1])
        y_std = np.std(members[:,1])


        print('------------------------------------------')
        
        print('Size, X mean +/- stddev, Y mean +/- stddev')
        print(len(cluster), x_mean, x_std, y_mean, y_std)
        print('Members:')
        print(members)

    # Plot the results, reachability diagram
    plotClusteringReachability(ordered_list[:,1], filtered_clusters)

    # Plot the final results
    plotPoints(input_data, filtered_clusters, title='Final results')

    