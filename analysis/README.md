# Map Project Documentation
## File structure
```
.
├── analysis.ipynb                  --> A jupyter notebook for interactive
├── cluster.py                      --> Python file for clustering
├── mapvis.py                       --> Python file for visualization
├── helper.py                       --> Python file contains some helper functions
├── data                            --> Folder containing data files
├── json                            --> Folder containing json files (propably map geojson)
│   ├── china.geo.json              --> China map
│   └── guangdong.json              --> Specific Guang Dong map
├── output                          --> Folder containing output files
│   └── html                        --> Folder containing output HTML files (usually the interactive visualization website)
├── README.md
├── requirements.txt                --> File for pip installation
└── src                             --> Source files
    ├── analysis.py                 --> Functions for analysis
    ├── cli.py                      --> Functions for CLI usage (i.e. I/O functions)
    └── visualize.py                --> Functions for visualization
```
## Functionality (Python files in ```src``` folder)
### Analysis (```analysis.py```)
- Helper functions
    ```
    def centeroidnp(arr):
        """Get the centeroid of an array of coordinates
        
        Arguments:
            arr {list} -- List of coordinates
        
        Returns:
            list -- List of the centeroid in the format of [x, y]
        """
    ```
    ```
    def extract_map_from_geojson(data, geojson):
        """Extract the data with coordinate information within the given map geojson
        
        Arguments:
            data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
            geojson {dict} -- Geojson of the map
        
        Returns:
            pandas.DataFrame -- Remaining data inside the map given
        """
    ```
    ```
    def get_cities_data(geoData, specificLocations, guangDong):
        """Extract the data inside specific locations
        
        Arguments:
            geoData {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
            specificLocations {list} -- List of string of specific locations
            guangDong {dict} -- Geojson of the map
        
        Returns:
            tuple -- Tuple of extracted data and cities map data
        """
    ```
    ```
    def exportResult(geoData, cluster_pos, resultFileName='kmeans.csv', clusterFileName='cluster.csv'):
        """Export result into 2 files which are result and cluster coordinates
        
        Arguments:
            geoData {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
            cluster_pos {list} -- List of [x, y] coordinates
        
        Keyword Arguments:
            resultFileName {str} -- Filename of the result file (default: {'kmeans.csv'})
            clusterFileName {str} -- Filename for cluster coordinates file (default: {'cluster.csv'})
        """
    ```
    ```
    def outputHeatmap(data, filename='heatmap.csv'):
        """Export heatmap data for web usage
        
        Arguments:
            data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
        
        Keyword Arguments:
            filename {str} -- Filename of the result file (default: {'heatmap.csv'})
        """
    ```
- Clustering methods
    ```
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
    ```
    ```
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
    ```
    ```
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
    ```
    ```
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
    ```
### Visualization
- Map visualization (```visualize.py```)
    ```
    def draw_map(data_geo):
        """Draw map
        
        Arguments:
            data_geo {pandas.DataFrame} -- DataFrame of map geojson
        
        Returns:
            altair -- Map visualization generate by altair
        """
    ```
    ```
    def draw_points(data, background):
        """Draw points
        
        Arguments:
            data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
            background {altair} -- Map visualization generate by altair
        
        Returns:
            altair -- Map visualization generate by altair
        """
    ```
    ```
    def draw_cluster(data, centersDf, background):
        """Draw cluster and points
        
        Arguments:
            data {pandas.DataFrame} -- DataFrame containing coordinate information, i.e. lat and lng
            centersDf {pandas.DataFrame} -- DataFrame containing cluster centroid coordinate information, i.e. lat and lng
            background {altair} -- Map visualization generate by altair
        
        Returns:
            altair -- Map visualization generate by altair
        """
    ```
## Installation
### Environment
- Python version: >= 3.6
- OS: Linux 16.04
### How to install
Run ```pip install -r requirements.txt```.

## How to use
### Python
- To run clustering, run ```python clustering.py```.
- To generate map visualizationm, run ```python mapvis.py```.
- To run helper functions (extract data from province and city), run ```python helper.py```.
### Jupyter Notebook
- Run ```jupyter notebook```.
- Go into ```analysis.ipynb```.
    - For the notebook only (not for JupyterLab) run the following command once per session:
        ```
        alt.renderers.enable('notebook')
        alt.data_transformers.enable('default', max_rows=None)
        ```