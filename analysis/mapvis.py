import src.visualize as visualize
import altair as alt
import sys
import src.cli as cli

def saveMap(vis):
    """Export altair or folium to HTML
    
    Arguments:
        vis {altair or folium} -- altair or folium object
    """
    outputName = input("Output file name: ")
    outputName = '%s.html' % outputName
    vis.save(outputName)
    print('Saved the file to %s' % outputName)

def getMap():
    map = cli.askForGeojosn()
    geo_data = alt.Data(values=map['features'])
    background = visualize.draw_map(geo_data)
    return background

def main():
    while True:
        mode = input("What to visualize? (map, point, cluster, heatmap) ")
        if mode == 'map':
            print('Visualize map only')
            background = getMap()
            saveMap(background)
            break
        elif mode == 'point':
            print('Visualize point')
            background = getMap()
            try:
                geoData = cli.getPoint()[['address', 'lat', 'lng']]
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            vis = visualize.draw_points(geoData, background)
            saveMap(vis)
            break
        elif mode == 'cluster':
            print('Visualize cluster')
            background = getMap()
            geoData = cli.getPoint()
            # if 'cluster_id' not in geoData.columns:
            #     sys.exit('Missing cluster column in the given csv file')
            try:
                geoData = geoData[['address', 'lat', 'lng', 'cluster_id']]
            except KeyError as e:
                sys.exit('Missing column(s): %s in the given csv file' % e.args[0])
            centersDf = cli.getCluster()
            vis = visualize.draw_cluster(geoData, centersDf, background)
            saveMap(vis)
            break
        elif mode == 'heatmap':
            print('Visualize heatmap')
            geoData = cli.getPoint()
            heatmap = visualize.draw_heatmap(geoData)
            saveMap(heatmap)
            break
        else:
            print('Invalid input')

if __name__ == "__main__":
    main()