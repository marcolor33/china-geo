import src.analysis as analysis
import pandas as pd
import numpy as np
import sys
import src.cli as cli

def getDBSCANInput():
    km = int(input("Radius of a neighborhood: "))
    num_of_pts = int(input("Minimun points in a cluster: "))
    return km, num_of_pts

def getKmeansInput():
    n_clusters = int(input("Number of cluster: "))
    max_iter = int(input("Maximun iteration: "))
    n_init = int(input("Run how many times k-means: "))
    while True:
        isFixed = input("Any fixed clusters? (yes, no): ")
        if isFixed == 'yes':
            clusterDf = cli.getPoint('cluster centroid')
            try:
                fixCluster = clusterDf[['lat', 'lng']].values
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            break
        elif isFixed == 'no':
            fixCluster = None
            break
        else:
            print('Invalid input')
    return n_clusters, max_iter, n_init, fixCluster

def getHierarchicalInput():
    n_clusters = int(input("Number of cluster: "))
    return n_clusters

def getSubClusteringInput():
    clusterDf = cli.getPoint('clsuter centroid')
    try:
        cluster_pos = clusterDf[['lat', 'lng']].values
    except KeyError as e:
        sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
    avg_size = int(input("Estimated average points in a cluster: "))
    return cluster_pos, avg_size

def exportResult(data, cluster_pos):
    cli.exportCsv(data, 'data point')
    centerDf = pd.DataFrame(cluster_pos, columns=['lat', 'lng']).reset_index().rename(columns={'index': 'cluster_id'})
    cli.exportCsv(centerDf, 'cluster centroid')

def main():
    while True:
        mode = input("Which clustering method to be used? (kmeans, dbscan, hierarchical, subclustering) ")
        if mode == 'kmeans':
            geoData = cli.getPoint('data point')
            try:
                coords = geoData[['lat', 'lng']].values
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            n_clusters, max_iter, n_init, fixCluster = getKmeansInput()
            labels, cluster_pos = analysis.k_means(coords, n_clusters=n_clusters, max_iter=max_iter, n_init=n_init, fixCluster=fixCluster)
            geoData['cluster_id'] = labels
            exportResult(geoData, cluster_pos)
            break
        elif mode == 'dbscan':
            geoData = cli.getPoint('data point')
            try:
                coords = geoData[['lat', 'lng']].values
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            km, num_of_pts = getDBSCANInput()
            labels, cluster_pos = analysis.dbscan(coords, km=km, num_of_pts=num_of_pts)
            geoData['cluster_id'] = labels
            exportResult(geoData, cluster_pos)
            break
        elif mode == 'hierarchical':
            geoData = cli.getPoint('data point')
            try:
                coords = geoData[['lat', 'lng']].values
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            n_clusters = getHierarchicalInput()
            labels, cluster_pos = analysis.aggClustering(coords, n_clusters=n_clusters)
            geoData['cluster_id'] = labels
            exportResult(geoData, cluster_pos)
            break
        elif mode == 'subclustering':
            geoData = cli.getPoint('data point')
            try:
                geoData = geoData[['address', 'lat', 'lng', 'cluster_id']]
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            cluster_pos, avg_size = getSubClusteringInput()
            labels, cluster_pos = analysis.subClustering(geoData, cluster_pos, method=analysis.k_means, avg_size=avg_size)
            geoData['cluster_id'] = labels
            exportResult(geoData, cluster_pos)
            break
        else:
            print('Invalid input')

if __name__ == "__main__":
    main()