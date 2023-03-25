
import pandas as pd
import os
from datetime import datetime

from pathlib import Path


from helper import init_api_key,batch_call_api

from pandas.io.json import json_normalize

import traceback
import asyncio


def post_process_repsonse(response,output,api):


    if api == "baidu":

        json_obj = {

            "duration" : response["result"]["routes"][0]["duration"] / 3600,
            "distance": response["result"]["routes"][0]["distance"]
        }


    elif api == "tencent":

        json_obj = {

            "duration" : response["result"]["routes"][0]["duration"] / 60,
            "distance": response["result"]["routes"][0]["distance"]
        }


    output.append(json_obj)


    return output


def compose_api_call_obj(current_index,client_data,dc_data,time_interval,api_key,api):


    destination = str(client_data.loc[current_index, 'lat']) + "," +  str(client_data.loc[current_index, 'lng'])

    cluster_id = int(client_data.loc[current_index, 'cluster_id'])



    origin = str(dc_data.loc[cluster_id, 'lat']) + "," + str(dc_data.loc[cluster_id, 'lng'])

    # print("origin : " + origin)
    # print("destination : " + destination)

    if api == "tencent":

        api_call_obj = {

            "method": "get",
            "url": "https://apis.map.qq.com/ws/direction/v1/driving/",
            "data": {

                "from": origin,
                "to": destination,
                "key": api_key
            },

            "time_interval": time_interval
        }

    else:

        api_call_obj = {

            "method": "get",
            "url": "http://api.map.baidu.com/directionlite/v1/driving",
            "data": {
                "output": "json",

                "origin": origin,
                "destination": destination,
                "ak": api_key
            },

            "time_interval": time_interval
        }

    return api_call_obj




def generate_result(address_data,result_data,api):



    output_dir = "output"

    output_filename = os.path.join(output_dir,"drivingInfo_output.csv")
    error_filename = os.path.join(output_dir,"drivingInfo_error.csv")


    # combine address data and api result
    full_df = pd.concat([address_data, result_data], axis=1)


    print(full_df.head())
    # handle in the baidu way
    if api == "baidu":

        output_df = full_df
        # error_df = full_df



    elif api == "tencent":

        output_df = full_df
        # error_df = full_df





    output_df.to_csv(output_filename, index=False, encoding='utf_8_sig')
    # error_df.to_csv(error_filename, index=False, encoding='utf_8_sig')




# return a df with all lat lng
def get_driving_info(client_data_filename, dc_data_filename, api="tencent"):

    cache_filename = "cache/drivingInfo_cache.csv"

    output = []

    cache_df = None

    print("starting getting data from API")
    # will get all lng lat from API, discarding the previous result stored in file

    cache_file = Path(cache_filename)

    start_index = 0

    # read from xlsx

    input_dir = "input"


    client_data_filename = os.path.join(input_dir,client_data_filename)

    client_data_file = Path(client_data_filename)

    if not client_data_file.is_file():
        raise Exception("client_data_file not found")



    dc_data_filename = os.path.join(input_dir, dc_data_filename)

    dc_data_file = Path(dc_data_filename)

    if not dc_data_file.is_file():
        raise Exception("dc_data_file not found")



    client_data = pd.read_csv(client_data_filename)
    dc_data = pd.read_csv(dc_data_filename)


    # check if there is a cache file
    if cache_file.is_file():

        print("cache file found")
        cache_df = pd.read_csv(cache_filename)

        # find the index where to resume
        start_index = len(cache_df.index)

        if start_index == len(client_data.index):

            generate_result(client_data,cache_df,api)

            return cache_df

    try:

        count = len(client_data.index)


        if api == "tencent":
            api_key_list = init_api_key(api)
            call_limit = 5
            time_interval = 1 / call_limit

        else:

            api_key_list = init_api_key(api)

            call_limit = 20
            time_interval = 1 / call_limit





        while start_index < count:

            task_list = []

            loop = asyncio.new_event_loop()

            for i, api_key in enumerate(api_key_list):


                api_call_obj_list = []

                for j in range(call_limit):


                    current_index = start_index + call_limit * i + j

                    if current_index >= count:
                        print("outrange")
                        break


                    api_call_obj = compose_api_call_obj(current_index,client_data,dc_data,time_interval,api_key,api)

                    api_call_obj_list.append(api_call_obj)

                task = loop.create_task(batch_call_api(api_call_obj_list))

                task_list.append(task)


            loop.run_until_complete(asyncio.wait(task_list))

            for task in task_list:

                for result in task.result():


                    if result["response"]["status"] == 120:

                        print(result["response"]["message"])

                        raise Exception("This API Key has Error : " + str(result["data"]["key"] + " message :" + result["response"]["message"] ))



                    response = result["response"]

                    output = post_process_repsonse(response,output,api)



                    start_index = start_index + 1

            loop.close()

    # if something's wrong, save df into cache
    except Exception as e:

        print("somethings is wrong,save data in cache")

        if len(output) > 0:

            df = json_normalize(output)

            if cache_df is not None:
                df = cache_df.append(df,ignore_index=True)

            df.to_csv(cache_filename, index=False,encoding='utf_8_sig')

        raise e


    # normally return df
    df = json_normalize(output)

    if cache_df is not None:
        df = cache_df.append(df,ignore_index=True)

    generate_result(client_data,df,api)



    return df



def main():
    # parse command line options

    try:


        client_data_filename = input("client_data (default : kmeans.csv): ")


        if not client_data_filename:
            print("using default")
            client_data_filename = "kmeans.csv"



        dc_data_filename = input("dc_data (default: cluster.csv):")

        if not dc_data_filename:
            dc_data_filename = "cluster.csv"


        print("setting is confirmed, proceeding")
        start_time = datetime.now()


        df = get_driving_info(client_data_filename,dc_data_filename)


        endtime = datetime.now()

        print(str(endtime - start_time))



    except Exception as e:


        traceback.print_exc()
        print("some exception encountered, now quiting")


    finally:

        input('data generation whole process completed, press enter to leave. . . ')
        return


if __name__ == "__main__":
    main()
