
from drivingInfo_multi import main as drivingInfo_multi_main
from drivingInfo import main as drivingInfo_main
from latlng import main as latlng_main
import os, shutil


def clear_cache():

    folder = 'cache'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)
            raise e
    input("clear cache success")


def main():    # parse command line options

    print("1 : get latLng")
    print("2 : get driving info")
    print("3 : get driving info (multi)")
    print("4 : clear cache")

    option = int(input("please enter your option : "))


    if (option == 1):
        return latlng_main()

    elif (option == 2):
        return drivingInfo_main()

    elif (option == 3):
        return drivingInfo_multi_main()


    elif (option == 4):
        return clear_cache()


if __name__ == "__main__":
    main()
