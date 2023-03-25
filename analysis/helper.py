import src.analysis as analysis
import src.cli as cli

def getLocation():
    inputStr = input("Places to be extracted (seperated by comma): ")
    return list(map(lambda x: x.strip(), inputStr.split(',')))

def main():
    while True:
        mode = input("What to help? extract (city) or (province) ")
        if mode == 'city':
            print('Extract data and cities from map')
            guangDong = cli.askForGeojosn()
            geoData = cli.getPoint()
            specificLocations = getLocation()
            citiesData, cities = analysis.get_cities_data(geoData, specificLocations, guangDong)
            cli.exportCsv(citiesData)
            cli.exportJson(cities)
            break
        elif mode == 'province':
            print('Extract data given map')
            guangDong = cli.askForGeojosn()
            geoData = cli.getPoint()
            guangDongData = analysis.extract_map_from_geojson(geoData, guangDong)
            cli.exportCsv(guangDongData)
            break
        else:
            print('Invalid input')

if __name__ == "__main__":
    main()