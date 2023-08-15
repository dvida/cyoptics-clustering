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

from __future__ import print_function, absolute_import, division

import copy
import numpy as np
import matplotlib.pyplot as plt

### Define constants which tell what is the UNDEFINED value in the reachability plot

# -1 Value was used in cython as an undefined value, which is not satisfactory anymore, as the undefined value
# should be infinite
UNDEFINED = -1

# The new undefined value is the largest number possible by a signed 32-bit number
# NOTE: CHANGE THIS TO A HIGER VALUE IF YOU ARE USING EXTREMELY LARGE REACHABILITY DISTANCES (E.G. IF YOUR
# NORMAL REACHABILITY DISTANCES ARE ABOVE 10**8 - and don't forget to use more bits for numpy arrays!)
NEW_UNDEFINED = 2**31 - 1

###


class ReachabilityVector(object):
    """Init the vector between two points in the reachability diagram. """

    def __init__(self, rx, ry, w):

        """ Initilization function for the vector.
        
        Arguments:
            rx: [float] reachability of the first point
            ry: [float] reachability of the second point
            w: [float] distance between data points in the reachability plot

        Return:
            ReachabilityVector [object]

        """

        self.value = np.array((w, ry - rx))


    def abs(self):
        """ Returns the magnitude of a vector. """

        return np.sqrt(self.value.dot(self.value))



def inflectionIndex(reach_list, y, w):
    """ Calculates the inflection index of a certain point in the reachability diagram. 
    
    Arguments:
        reach_list: [ndarray] 1D numpy array containing reachability distance values of individual data points
        y: [int] index of the point for which the inflection index is calculated
        w: [float] distance between data points in the reachability plot

    Returns:
        [float] inflection index of the given point

    """

    # Get reachabilities of the previous, current and the next point
    x_r = reach_list[y - 1]
    y_r = reach_list[y]
    z_r = reach_list[y + 1]

    # Create vectors between with adjecent points
    prev_vect = ReachabilityVector(x_r, y_r, w)
    next_vect = ReachabilityVector(y_r, z_r, w)

    return (-w**2 + (x_r - y_r)*(z_r - y_r))/(prev_vect.abs()*next_vect.abs())



def gradientDeterminant(reach_list, y, w):
    """ Calculate the gradient determinant between two vectors. 
    
    Arguments:
        reach_list: [ndarray] 1D numpy array containing reachability distance values of individual data points
        y: [int] index of the point for which the gradient is calculated
        w: [float] distance between data points in the reachability plot

    Returns:
        [float] gradient determinant of the given point (see source paper for more information)

    """

    # Get reachabilities of the previous, current and the next point
    x_r = reach_list[y - 1]
    y_r = reach_list[y]
    z_r = reach_list[y + 1]

    return w*(y_r-x_r) - w*(z_r-y_r)



def gradientClustering(reach_list, min_pts, t, w):
    """ Extracts clusters from the reachability diagram by using the gradient method. 
    
    Source paper: Brecheisen, S., Kriegel, H.P., Kroger, P. and Pfeifle, M., 2004, April. 
        Visually Mining through Cluster Hierarchies. In SDM (pp. 400-411).

    Arguments:
        reach_list: [ndarray] 1D numpy array containing reachability distance values of individual data points
        min_pts: [int] minimum number of points used for clustering
        t: [float] angle of minimum inflection index in the inflection point, values in the range 120-160 deg
            should work fine (see source paper for more information)
        w: [float] distance between data points in the reachability plot, this value influences the
            sensitivity of the gradient clustering procedure, a value of 0.025 should work fine

    Return:
        set_of_clusters: [list] a list of found clusters
            - note: individual cluster is just a list of point indices belonging to a specific cluster

    """

    # Replace all UNDEFINED values in the reach_list with infinites
    reach_list[reach_list == UNDEFINED] = NEW_UNDEFINED

    # Covert t from degrees to cosinus value
    t = np.cos(np.radians(t))

    # Input data size
    reach_list_size = len(reach_list)

    # Init the last endpoint
    last_endpoint = reach_list_size - 1

    # Init the empty working lists
    start_pts = []
    set_of_clusters = []
    curr_cluster = []

    # Add the first point to the start_pts
    start_pts.append(0)

    # Go through all the remaining points
    for i in range(1, reach_list_size - 1):

        # Check if the point is an inflection point
        if inflectionIndex(reach_list, i, w) > t:

            # Check if the next vector deviates to the right
            if gradientDeterminant(reach_list, i, w) > 0:

                # Check if the current cluster size is larger than the minimum number of points required
                if len(curr_cluster) >= min_pts:

                    # Add the cluster to a list of clusters
                    set_of_clusters.append(curr_cluster)

                # Reset the current cluster
                curr_cluster = []

                # Check if the list of start points is not empty
                if start_pts:

                    # Check if the last point in the start_pts has a smaller reachability distance than the 
                    # current point, if so, remove the last point
                    if reach_list[start_pts[-1]] <= reach_list[i]:
                        start_pts.pop()

                # Check if the list of start points is not empty
                if start_pts:

                    # While the last point in the start_pts has a smaller reachability distance than the current
                    # point, keep removing points from the end and add them to a list of clusters
                    while reach_list[start_pts[-1]] < reach_list[i]:
                        
                        temp_cluster = range(start_pts[-1], last_endpoint)

                        # Check if the temporary cluster size is larger than the minimum number of points required
                        if len(temp_cluster) >= min_pts:
                            set_of_clusters.append(temp_cluster)

                        # Remove the last start point from the list of start points
                        start_pts.pop()

                    # Lastly, add another cluster at the end, if it is not empty
                    temp_cluster = range(start_pts[-1], last_endpoint)
                    
                    if len(temp_cluster) >= min_pts:
                        
                        # Add a new cluster
                        set_of_clusters.append(range(start_pts[-1], last_endpoint))

                # If the current point is a starting point, add it to the list
                if reach_list[i+1] < reach_list[i]:
                    start_pts.append(i)



            # The next vector deviates to the left, marking an endpoint
            else:

                # If the current point is the endpoint and goes up, then take all points from the last start 
                # point to this one as a current cluster
                if reach_list[i+1] > reach_list[i]:

                    # Keep track of the lastest endpoint (add 1 for the python peculiarities, as otherwise the 
                    # last point would not be included in the list)
                    last_endpoint = i + 1


                    curr_cluster = range(start_pts[-1], last_endpoint)


    # Add clusters at the end of plot, while start points has any members
    while start_pts:
        
        # Take points from the last point in the start pooints to the last point
        curr_cluster = range(start_pts[-1], reach_list_size)


        if (reach_list[start_pts[-1]] > reach_list[-1]) and (len(curr_cluster) >= min_pts):
            set_of_clusters.append(curr_cluster)

        start_pts.pop()

    return set_of_clusters



def filterLargeClusters(clusters, input_size, cluster_fraction_thresh):
    """ Remove big clusters which have more points than a given fraction of total points in the input data. 

    Arguments:
        clusters: [list] a python list containing found clusters in the reachability diagram plot (optional)
            - note: individual cluster is just a list of point indices belonging to a specific cluster
        input_size: [int] total number of all data points used for clustering
        cluster_fraction_thresheld: [float] a number that defines the maximum ratio of the largest acceptable
            cluster size and the total number of all points used for clustering

    Return:
        filtered_clusters: [list] a list of clusters where the largle clusters were removed

    """

    filtered_clusters = []

    # Go through every cluster and check if it is too big
    for cluster in clusters:

        # If the cluster is small enough, add it to the list
        if len(cluster) < cluster_fraction_thresh*input_size and len(cluster) > 0:

            filtered_clusters.append(cluster)

    return filtered_clusters



def mergeSimilarClusters(clusters, similarity_threshold):
    """ Merge clusters which have a minimum ratio of shared points compared to the other clusters.
    
    Arguments:
        clusters: [list] a python list containing found clusters in the reachability diagram plot (optional)
            - note: individual cluster is just a list of point indices belonging to a specific cluster
        similarity_threshold: [float] a minimum ratio between the intersection of two clusters and the 
            members of the larger cluster

    Return:
        clusters: [list] a list of merged clusters

    """

    # Sort clusters by ascending size 
    clusters = list(reversed(sorted(clusters, key=len)))

    # Init the filtering lists
    previous_iteration_clusters = clusters
    merged_clusters = []

    # Run the filtering until the final list of merged clusters does not change
    while len(previous_iteration_clusters) != len(merged_clusters):

        # Sort clusters by ascending size 
        clusters = list(reversed(sorted(clusters, key=len)))

        # Init the list of clusters to skip
        skip_list = []

        # Deep copy the results of previous interations into the variable that holds info about clusters from
        # the previous iteration
        previous_iteration_clusters = copy.deepcopy(merged_clusters)

        merged_clusters = []

        
        # Merge similar clusters by looking at the ratio of their intersection and their total number
        for i, cluster1 in enumerate(clusters):

            # Skip if the cluster was already processed
            if i in skip_list:
                continue

            found_similar = False
            for j, cluster2 in enumerate(clusters):

                # Skip if the same cluster and all previous up until cluster1
                if j <= i:
                    continue

                # Skip if already processed
                if j in skip_list:
                    continue

                # Find the number of common points between clusters
                intersect_points = len(set(cluster1).intersection(cluster2))

                # Find the bigger cluster
                if len(cluster1) > len(cluster2):
                    bigger_size = len(cluster1)
                else:
                    bigger_size = len(cluster2)


                # Check for the intersection ratio, i.e. the ratio of common points and the point number of
                # the bigger cluster
                if (intersect_points >= similarity_threshold*bigger_size):

                    # Merge two clusters into one
                    new_merged_cluster = sorted(list(set(set(cluster1) | set(cluster2))))

                    # Put the merged cluster to the list of merged clusters
                    merged_clusters.append(new_merged_cluster)

                    # Put the index of the removed cluster to the list of those clusters to be skipped
                    skip_list.append(j)

                    # Mark that a similar cluster has been found
                    found_similar = True

                    break

            # If the current cluster was not merged to any other, out it back to the list of all clusters
            if not found_similar:
                merged_clusters.append(cluster1)

        # Copy the resulting list to the list of final clusters
        clusters = copy.deepcopy(merged_clusters)


    # Sort clusters by descending size
    clusters = list(reversed(sorted(clusters, key=len)))

    return clusters



def plotClusteringReachability(reach_list, clusters=[]):
    """ Plot the reachability diagram and the detected clusters (clusters are optional). 
    
    Arguments:
        reach_list: [ndarray] 1D numpy array containing reachability distance values of individual data points
        clusters: [list] a python list containing found clusters in the reachability diagram plot (optional)
            - note: individual cluster is just a list of point indices belonging to a specific cluster

    Return:
        None

    """

    # Replace all UNDEFINED values in the reach_list with infinites
    reach_list[reach_list == UNDEFINED] = NEW_UNDEFINED

    NUM_COLORS = len(clusters) + 1

    # Renerate a range of colors
    cm = plt.get_cmap('gist_rainbow')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_prop_cycle(color=[cm(1.*i/NUM_COLORS) for i in range(NUM_COLORS)])  

    # Plot the reachability plot
    ax.plot(range(len(reach_list)), reach_list)

    # Sort the clusters by size
    clusters = sorted(clusters, key=len, reverse=True)

    # Plot the clusters by their reachability
    for i, cluster in enumerate(clusters):

        # Get the vertical value of the plot as the first non-undefined reachability distance
        for k in reversed(range(len(cluster))):
            vertical_reach = reach_list[cluster[k]]
            if vertical_reach < NEW_UNDEFINED:
                break

        vertical_values = np.zeros(len(cluster)) + vertical_reach

        # Plot cluster lines on top of one another, smaller ones on the top, with line thicknesses
        # correspoding to the size of the cluster
        ax.plot(cluster, vertical_values, linewidth=np.log10(len(cluster))/2, zorder=i)

    # Set the axis limits
    plt.xlim((0, len(reach_list)-1))
    plt.ylim((0, np.max(reach_list[reach_list < NEW_UNDEFINED])*1.1))

    # Set the titles
    if clusters:
        plt.title('OPTICS results (Reachability diagram) - ' + str(len(clusters)) + ' clusters found')
    else:
        plt.title('OPTICS results (Reachability diagram)')

    # Set axis labels
    plt.xlabel('Point indices')
    plt.ylabel('Reachability distance')
    plt.tight_layout()

    plt.show()
    plt.clf()
    plt.close()

