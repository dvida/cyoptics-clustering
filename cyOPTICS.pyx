#!python
#cython: language_level=2, boundscheck=False, wraparound=False

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



# Sources used for implementation:
# - https://en.wikipedia.org/wiki/OPTICS_algorithm
# - https://gist.github.com/ryangomba/1724881



# Import cython libraries
cimport cython
import numpy as np
cimport numpy as np
from libc.math cimport sqrt

# Define cython numpy types
INT_TYPE = np.int32
ctypedef np.int32_t INT_TYPE_t

FLOAT_TYPE = np.float64
ctypedef np.float64_t FLOAT_TYPE_t


# Define constants
cdef int UNPROCESSED = 0
cdef int PROCESSED = 1
cdef int UNDEFINED = -1

# Point list column indices
cdef int PROCESSED_FLAG_IND = 0
cdef int REACHABILITY_DIST_IND = 1
cdef int CORE_DIST_IND = 2

# Total number not non-input data points, which are appended in the columns before the data
cdef int COLUMNS_TOTAL = 3



cdef float euclidianDistance(float x1, float y1, float x2, float y2):
    """ Calculate the Euclidian distance between two points. """

    return sqrt((x2 - x1)**2 + (y2 - y1)**2)



def getNeighbors(np.ndarray[FLOAT_TYPE_t, ndim=2] point_list, int i, float eps):
    """ Returns indices of all neighbors of a given point. Neighbouring points are within the distance eps. 
    
    Arguments:
        point_list: [ndarray] numpy 2D array which contains information about individual points
        i: [int] index of a point we are currently processing
        eps: [float] epsilon value, i.e. maximum distance to neighbors

    Return:
        indices: [ndarray] numpy 1D array containing indices of neighbors
        k: [int] number of returned neighbors

    """

    # Init used variables
    cdef int k = 0
    cdef int j

    # Init neighbor indices array, set them all to undefined
    cdef np.ndarray[INT_TYPE_t, ndim=1] indices = np.zeros(point_list.shape[0], dtype=INT_TYPE) + UNDEFINED
    
    # Go through all points and find neighbors
    for j in range(point_list.shape[0]):
        
        # Skip if on the input point
        if i == j:
            continue

        # Check if the current point is close enough
        if euclidianDistance(point_list[i, COLUMNS_TOTAL], point_list[i, COLUMNS_TOTAL+1], 
            point_list[j, COLUMNS_TOTAL], point_list[j, COLUMNS_TOTAL+1]) <= eps:

            # Add the point to the neighbors list
            indices[k] = j
            k += 1

    return indices, k



cdef float coreDistance(np.ndarray[FLOAT_TYPE_t, ndim=2] point_list, int i, 
    np.ndarray[INT_TYPE_t, ndim=1] neighbor_indices, int neighbors_count, float eps, int min_pts):
    """ Calculates the core distance, i.e. distance from the point to the Nth neighbor, in this case the 
    (min_pts-1)th neighbor. 

    Arguments:
        point_list: [ndarray] numpy 2D array which contains information about individual points
        i: [int] index of a point we are currently processing
        neighbor_indices: [ndarray] numpy 1D array containing indices of neighbors
        neighbors_count: [int] number of neighbors in the neighbors_indices list (the list is of fixed size, 
            so this is used to track the number of points inside)
        eps: [float] epsilon value, i.e. maximum distance to neighbors
        min_pts: [int] minimum number of points 

    Return:
        [float]: core distance
    """

    cdef np.ndarray[FLOAT_TYPE_t, ndim=1] referent_point = point_list[i]
    cdef int k

    # # Get the number of neighbors
    # cdef int neighbors_count = neighbor_indices.shape[0]

    # Init the neighbor distances array
    cdef np.ndarray[FLOAT_TYPE_t, ndim=1] neighbor_distances = np.zeros(neighbors_count, dtype=FLOAT_TYPE)

    # If the core distance was already calculated, return it
    if referent_point[CORE_DIST_IND] != UNDEFINED:
        return referent_point[CORE_DIST_IND]

    # Check if there are enough neighbors to proceed
    if neighbors_count >= min_pts-1:

        # Calculate the distance to each neighbor
        for k in range(neighbors_count):
            neighbor_distances[k] = euclidianDistance(referent_point[COLUMNS_TOTAL], 
                referent_point[COLUMNS_TOTAL+1], 
                point_list[neighbor_indices[k], COLUMNS_TOTAL], 
                point_list[neighbor_indices[k], COLUMNS_TOTAL+1])

        # Sort the neighbor distance list
        neighbor_distances = np.sort(neighbor_distances)

        # Take a next-to-last point from the min_pts
        return neighbor_distances[min_pts-2]

    # If there are not enough neighbors, the core distance remains undefined
    else:
        return UNDEFINED

        

def update(np.ndarray[FLOAT_TYPE_t, ndim=2] point_list, int i, 
    np.ndarray[INT_TYPE_t, ndim=1] neighbor_indices, int neighbors_count, 
    np.ndarray[INT_TYPE_t, ndim=1] seeds, int seed_count):
    """ Update the seeds' reachability distance if a smaller value is found. 
    
    Arguments:
        point_list: [ndarray] numpy 2D array which contains information about individual points
        i: [int] index of a point we are currently processing
        neighbor_indices: [ndarray] numpy 1D array containing indices of neighbors
        neighbors_count: [int] number of neighbors in the neighbors_indices array (the array is of fixed size, 
            so this is used to track the number of points inside)
        seeds: [ndarray] numpy 1D array containing indices of seeds 
        seed_count: [int] number of seeds in the seeds array (the array is of fixed size, so this is used to 
            track the number of points inside)

    Return:
        point_list: [ndarray] updated point_list
        seeds: [ndarray] updated seed indices
        seed_count: [int] updated seeds array
    """

    cdef int k
    cdef float new_reach
    cdef np.ndarray[FLOAT_TYPE_t, ndim=1] neighbor = np.zeros(point_list.shape[1], dtype=FLOAT_TYPE)

    # Go through all neighbors
    for k in range(neighbors_count):

        neighbor = point_list[neighbor_indices[k]]

        # Check if the neighbor is not processed
        if neighbor[PROCESSED_FLAG_IND] == UNPROCESSED:

            # Find a new reachability distance, it is a max between the core distance in the distance between
            # the point and the neighbor
            new_reach = max(point_list[i, CORE_DIST_IND], euclidianDistance(point_list[i,COLUMNS_TOTAL], 
                point_list[i,COLUMNS_TOTAL+1], neighbor[COLUMNS_TOTAL], neighbor[COLUMNS_TOTAL+1]))

            # If the reachability distance was not previously defined, set it to the new calculated value
            if neighbor[REACHABILITY_DIST_IND] == UNDEFINED:
                point_list[neighbor_indices[k], REACHABILITY_DIST_IND] = new_reach

                # Add a new seed
                seeds[seed_count] = neighbor_indices[k]
                seed_count += 1

            # If the newly calculated reachability is smaller, set it as the new reachability distance
            elif new_reach < neighbor[REACHABILITY_DIST_IND]:
                
                # Set the new reachability distance
                point_list[neighbor_indices[k], REACHABILITY_DIST_IND] = new_reach


    return point_list, seeds, seed_count



cdef int getUnprocessed(np.ndarray[FLOAT_TYPE_t, ndim=2] point_list):
    """ Returns the index of the next unprocessed point. 

    Arguments:
        point_list: [ndarray] numpy 2D array which contains information about individual points

    Return:
        [int]: index of the next unprocessed point
    """

    cdef int i

    for i in range(point_list.shape[0]):

        # Choose an unprocessed point
        if point_list[i, PROCESSED_FLAG_IND] == UNPROCESSED:
            return i

    # If there is nothing to process, return UNDEFINED
    return UNDEFINED



def runCyOPTICS(np.ndarray[FLOAT_TYPE_t, ndim=2] input_list, float eps, int min_pts):
    """ Runs the OPTICS algorithm on the given data.
        
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

    cdef int i, neighbor
    cdef int input_list_size = input_list.shape[0]

    # Add the processed flag, reachability distance and core distance columns in the points list
    cdef np.ndarray[FLOAT_TYPE_t, ndim=2] point_list = np.hstack((np.zeros(shape=(input_list_size, 
        COLUMNS_TOTAL)), input_list))

    # Set all points as unprocessed
    point_list[:,PROCESSED_FLAG_IND] = UNPROCESSED

    # Set the reachability and core distance to -1 (value for undefined)
    point_list[:,REACHABILITY_DIST_IND] = UNDEFINED
    point_list[:,CORE_DIST_IND] = UNDEFINED

    # Init the ordered list
    cdef np.ndarray[INT_TYPE_t, ndim=1] ordered_list = np.zeros(input_list_size, dtype=INT_TYPE)
    cdef int ordered_count = 0

    # Init the seeds list
    cdef np.ndarray[INT_TYPE_t, ndim=1] seeds = np.zeros(input_list_size*2, dtype=INT_TYPE)
    cdef int seed_count = 0

    # Init neighbor indices
    cdef np.ndarray[INT_TYPE_t, ndim=1] neighbor_indices = np.zeros(input_list_size, dtype=INT_TYPE)
    cdef int neighbors_count = 0

    # Set the unprocessed counter
    cdef int unprocessed_count = input_list_size

    # Repeat while there are unprocessed points
    while unprocessed_count:

        # Get the index of the unprocessed point
        i = getUnprocessed(point_list)

        # Get the neighboring points
        neighbor_indices, neighbors_count = getNeighbors(point_list, i, eps)

        # Mark the point as processed and add to ordered list
        point_list[i, PROCESSED_FLAG_IND] = PROCESSED
        ordered_list[ordered_count] = i
        ordered_count += 1
        unprocessed_count -= 1

        # Get the core distance
        point_list[i, CORE_DIST_IND] = coreDistance(point_list, i, neighbor_indices, neighbors_count, 
            eps, min_pts)


        # If the core distance is not undefined
        if point_list[i, CORE_DIST_IND] != UNDEFINED:

            # Reset the seed list
            seeds[:] = UNDEFINED
            seed_count = 0

            # Update reachability distance for each unprocessed neighbor
            point_list, seeds, seed_count = update(point_list, i, neighbor_indices, neighbors_count, seeds, 
                seed_count)

            # Go through seeds while there are any
            while seeds[0] != UNDEFINED:

                ### Sort seeds by reachability

                # Set the last seeds to UNDEFINED
                seeds[seed_count:] = UNDEFINED

                # Find all seeds that have values and sort them
                seeds_sort_indices = seeds[point_list[seeds[seeds > UNDEFINED]][:,REACHABILITY_DIST_IND].argsort()]
                seeds[:seed_count] = seeds_sort_indices

                ###
                

                # Take the first point in seeds as the neighbor
                neighbor = seeds[0]

                # Mark the neighbor as processed and add to the ordered list
                point_list[neighbor, PROCESSED_FLAG_IND] = PROCESSED
                ordered_list[ordered_count] = neighbor
                ordered_count += 1
                unprocessed_count -= 1


                # Remove the taken neighbor from the seed list and shift all seeds after one index down
                seeds[0 : input_list_size-2] = seeds[1 : input_list_size-1]

                # Set the last element to UNDEFINED
                seeds[input_list_size-1] = UNDEFINED

                # Decrement the seed count
                seed_count -= 1


                # Find neighbors of the chosen neighbor
                neighbor_indices_mark, neighbors_count_mark = getNeighbors(point_list, neighbor, eps)

                # Update the core distance for the neighbor
                point_list[neighbor, CORE_DIST_IND] = coreDistance(point_list, neighbor, 
                    neighbor_indices_mark, neighbors_count_mark, eps, min_pts)

                # If the neighbor as a core distance
                if point_list[neighbor, CORE_DIST_IND] != UNDEFINED:

                    # Update the reachability distance of each entry in neighbor_indices_mark
                    point_list, seeds, seed_count = update(point_list, neighbor, neighbor_indices_mark, 
                        neighbors_count_mark, seeds, seed_count)


    return point_list[ordered_list[:ordered_count]]




