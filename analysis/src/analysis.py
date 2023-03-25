from sklearn.cluster import KMeans, DBSCAN, AgglomerativeClustering
from sklearn.mixture import BayesianGaussianMixture
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from functools import reduce
from shapely.geometry import shape, Point
import math

OUTPUT_DIR = 'output/'
JSON_DIR = 'json/'
DATA_DIR = 'data/'
HTML_DIR = 'html/'

# Helper functions
def centeroidnp(arr):
    """Get the centeroid of an array of coordinates
    
    Arguments:
        arr {list} -- List of coordinates
    
    Returns:
        list -- List of the centeroid in the format of [x, y]
    """
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return [sum_x/length, sum_y/length]

def extract_map_from_geojson(data, geojson):
    """Extract the data with coordinate information within the given map geojson
    
    Arguments:
        data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
        geojson {dict} -- Geojson of the map
    
    Returns:
        pandas.DataFrame -- Remaining data inside the map given
    """
    polygons = []
    for place in geojson['features']:
        polygons.append(shape(place['geometry']))
    isInside = []
    for _, row in data.iterrows():
        isInside.append(reduce(lambda x, y: x or y, [polygon.contains(Point(row['lng'], row['lat'])) for polygon in polygons], False))
    return data[isInside]

def get_cities_data(geoData, specificLocations, guangDong):
    """Extract the data inside specific locations
    
    Arguments:
        geoData {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
        specificLocations {list} -- List of string of specific locations
        guangDong {dict} -- Geojson of the map
    
    Returns:
        tuple -- Tuple of extracted data and cities map data
    """
    cities = {'features': [feature for feature in guangDong['features'] if feature['properties']['name'] in specificLocations]}
    citiesData = extract_map_from_geojson(geoData, cities)
    return citiesData, cities

def exportResult(geoData, cluster_pos, resultFileName='kmeans.csv', clusterFileName='cluster.csv'):
    """Export result into 2 files which are result and cluster coordinates
    
    Arguments:
        geoData {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
        cluster_pos {list} -- List of [x, y] coordinates
    
    Keyword Arguments:
        resultFileName {str} -- Filename of the result file (default: {'kmeans.csv'})
        clusterFileName {str} -- Filename for cluster coordinates file (default: {'cluster.csv'})
    """
    geoData.to_csv(OUTPUT_DIR + resultFileName, encoding='utf_8_sig')
    pd.DataFrame(cluster_pos, columns=['lat', 'lng']).reset_index().rename(columns={'index': 'cluster_id'}).to_csv(OUTPUT_DIR + 'cluster.csv', index=False)
    
def outputHeatmap(data, filename='heatmap.csv'):
    """Export heatmap data for web usage
    
    Arguments:
        data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
    
    Keyword Arguments:
        filename {str} -- Filename of the result file (default: {'heatmap.csv'})
    """
    outputCSV = data[['lat', 'lng']].reset_index().drop(columns='index')
    outputCSV['weight'] = np.ones(len(outputCSV.index))
    outputCSV.to_csv(OUTPUT_DIR + filename)

########################## Clustering method ################################
# Kmean
def k_means(coords, n_clusters=None, n_init=100, max_iter=2000, tol=0.0001, plot=False, custom=False, fixCluster=None):
    """Custom K-means function
    
    Arguments:
        coords {List} -- List of [x, y] coordinates
    
    Keyword Arguments:
        n_clusters {integer} -- Number of clusters to be generated (default: {None})
        n_init {int} -- Number of times running K-Means with different initialization (default: {100})
        max_iter {int} -- Number of times iteration in one K-Means (default: {2000})
        tol {float} -- Minimun number for tolerance (Related to covergence of K-Means) (default: {0.0001})
        plot {bool} -- Plot the result (default: {False})
        custom {bool} -- Using custom K-Means (DECRAPTED) (default: {False})
        fixCluster {List} -- List of [x, y] coordinates of fixed cluster (default: {None})
    
    Returns:
        tuple -- Labels array and cluster centroid array
    """
    if n_clusters is None:
        print('Not specific n_clusters')
        return None, None
    kmeans = KMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter)
    # if custom:
    #     kmeans = MyKMeans(n_clusters=n_clusters, n_init=n_init, max_iter=max_iter)
    if fixCluster is not None:
        numFixCluster = len(fixCluster)
        all_kmeans = []
        for _ in range(n_init):
            init = coords[np.random.choice(len(coords), n_clusters - numFixCluster, replace=False)]
            init = np.append(fixCluster, init, axis=0)
            error = 0
            for _ in range(max_iter):
                kmeans = KMeans(n_clusters=n_clusters, n_init=1, max_iter=1, init=init)
                kmeans.fit(coords)
                init = kmeans.cluster_centers_
                init[:numFixCluster] = fixCluster
                if np.abs(kmeans.inertia_ - error) < tol:
                    break
                error = kmeans.inertia_
            all_kmeans.append(kmeans)
        best_keams = None
        best_error = float('inf')
        for k in all_kmeans:
            if k.inertia_ < best_error:
                best_keams = k
                best_error = k.inertia_
        kmeans = best_keams

    kmeans.fit(coords)
    
    if fixCluster is not None:
        original = kmeans.cluster_centers_[:numFixCluster]
        error = np.linalg.norm(original - fixCluster, axis=1)
        kmeans.cluster_centers_[:numFixCluster] = fixCluster
        print('Error: ' + np.array2string(error, precision=4, separator=','))
    
    if plot:
        plt.figure(num=None, figsize=(8, 6), dpi=80, facecolor='w', edgecolor='k')
        plt.scatter(coords[:, 1], coords[:, 0], c=kmeans.predict(coords), s=5, cmap='viridis')
        plt.show()
    labels = kmeans.predict(coords)
    return labels, kmeans.cluster_centers_

# DBSCAN
def dbscan(coords, n_clusters=None, km=50, num_of_pts=100, plot=False):
    """Custom DBSCAN
    
    Arguments:
        coords {List} -- List of [x, y] coordinates
    
    Keyword Arguments:
        n_clusters {integer} -- Does NOT matter for DBSCAN (default: {None})
        km {int} -- Maximun distance bewteen points inside a cluster (default: {50})
        num_of_pts {int} -- Minimun points inside a cluster (default: {100})
        plot {bool} -- Plot the result (default: {False})

    Returns:
        tuple -- Labels array and cluster centroid array
    """
    kms_per_radian = 6371.0088
    epsilon = km / kms_per_radian
    db = DBSCAN(eps=epsilon, min_samples=num_of_pts, algorithm='ball_tree', metric='haversine').fit(np.radians(coords))
    # core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    # core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise_ = list(labels).count(-1)

    print('Estimated number of clusters: %d' % n_clusters_)
    print('Estimated number of noise points: %d' % n_noise_)
    
    unique_labels = set(labels)
    cluster_pos = []
    for k in unique_labels:
        if k == -1:
            continue
        class_member_mask = (labels == k)
        xy = coords[class_member_mask]
        cluster_pos.append(centeroidnp(xy))

    if plot:
        # Black removed and is used for noise instead.
        cmap = plt.cm.get_cmap("Spectral")
        colors = [cmap(each)
                  for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            if k == -1:
                # Black used for noise.
                col = [0, 0, 0, 1]
            class_member_mask = (labels == k)
            xy = coords[class_member_mask]
            plt.plot(xy[:, 1], xy[:, 0], 'o', color=tuple(col), markersize=3)

        plt.title('Estimated number of clusters: %d' % n_clusters_)
        plt.show()
    return labels, cluster_pos

# Hierarchical clustering
def aggClustering(coords, n_clusters=None, plot=False):
    """Custom Hierarchical clustering
    
    Arguments:
        coords {List} -- List of [x, y] coordinates
    
    Keyword Arguments:
        n_clusters {integer} -- Number of clusters to be generated (default: {None})
        plot {bool} -- Plot the result (default: {False})
    
    Returns:
        tuple -- Labels array and cluster centroid array
    """
    if n_clusters is None:
        print('Not specific n_clusters')
        return None, None
    agg = AgglomerativeClustering(n_clusters = 15)
    agg.fit(coords)
    labels = agg.labels_

    # Number of clusters in labels, ignoring noise if present.
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

    print('Estimated number of clusters: %d' % n_clusters_)
    
    unique_labels = set(labels)
    cluster_pos = []
    for k in unique_labels:
        if k == -1:
            continue
        class_member_mask = (labels == k)
        xy = coords[class_member_mask]
        cluster_pos.append(centeroidnp(xy))
    
    if plot:
        cmap = plt.cm.get_cmap("Spectral")
        colors = [cmap(each)
                  for each in np.linspace(0, 1, len(unique_labels))]
        for k, col in zip(unique_labels, colors):
            class_member_mask = (labels == k)

            xy = coords[class_member_mask]
            plt.plot(xy[:, 1], xy[:, 0], 'o', color=tuple(col), markersize=3)

        plt.title('Estimated number of clusters: %d' % n_clusters_)
        plt.show()
    return labels, cluster_pos

# Subclustering
def subClustering(geoData, cluster_pos, method=k_means, avg_size=50000):
    """Phase 2 clustering
    
    Arguments:
        geoData {pandas.DataFrame} -- DataFrame containing coordinate information and cluster label, i.e. lat and lng
        cluster_pos {List} -- List of cluster centroid [x, y] coordinates
    
    Keyword Arguments:
        method {function} -- Type of clustering used in subclustering (default: {k_means})
        avg_size {int} -- Target size of points inside a cluster (default: {50000})
    
    Returns:
        tuple -- Labels array and cluster centroid array
    """
    clusterSize = geoData.groupby('cluster_id').size().reset_index(name='count')
    index = clusterSize['cluster_id'].values
    # Remove old clusters
    index = np.delete(index, clusterSize[clusterSize['count'] > avg_size]['cluster_id'].index)
    cluster_pos = np.delete(cluster_pos, clusterSize[clusterSize['count'] > avg_size]['cluster_id'], axis=0)
    for id in clusterSize[clusterSize['count'] > avg_size]['cluster_id']:
        if len(index) == 0:
            new_cluster = len(clusterSize['cluster_id'].values)
        else:
            new_cluster = index[-1] + 1
        print(id)
    #     print(clusterSize['count'][id])
        target = geoData[geoData['cluster_id'] == id]
        local_cluster_size = math.ceil(clusterSize['count'][id] / avg_size)
        cluster_coords = target[['lat', 'lng']].values
        local_labels, local_clusters_pos = method(cluster_coords, n_clusters=local_cluster_size, plot=False)
        local_labels = np.array(list(map(lambda d: d + new_cluster, local_labels)))
        geoData.loc[geoData.cluster == id, 'cluster_id'] = local_labels
        local_counts = pd.Series(local_labels).groupby(local_labels).size()
        print(local_counts)
        index = np.append(index, local_counts.index.values)
        cluster_pos = np.append(cluster_pos, local_clusters_pos, axis=0)
    # Update cluster id
    index_map = {id: i for i, id in enumerate(index)}
    print(index_map)
    # geoData['cluster_id'].unique()
    return geoData['cluster_id'].map(lambda d: index_map.get(d, -1)), cluster_pos