
import pandas as pd

from datetime import datetime

from pathlib import Path

from pandas.io.json import json_normalize


import asyncio
from helper import init_api_key,batch_call_api
import os
import traceback



# global variable here


def post_process_repsonse(response,output,api):


    json_obj = {

        "lat" : response["result"]["location"]["lat"],
        "lng": response["result"]["location"]["lng"],
    }

    if api == "baidu":

        json_obj["precise"] = response["result"]["precise"]

    elif api == "tencent":

        json_obj["status"] = response["result"]["status"]




    output.append(json_obj)


    return output



def generate_result(address_data,result_data,api):

    output_dir = "output"

    output_filename = os.path.join(output_dir,"latlng_output.csv")
    error_filename = os.path.join(output_dir,"latlng_error.csv")


    # combine address data and api result
    full_df = pd.concat([address_data, result_data], axis=1)

    # print(full_df.head())
    # handle in the baidu way

    if api == "baidu":

        output_df = full_df.loc[full_df['precise'] == 1]
        error_df = full_df.loc[full_df['precise'] == 0]


    elif api == "tencent":


        output_df = full_df.loc[full_df['status'] == 0]
        error_df = full_df.loc[full_df['status'] != 0]

    output_df.to_csv(output_filename, index=False, encoding='utf_8_sig')
    error_df.to_csv(error_filename, index=False, encoding='utf_8_sig')



# return a df with all lat lng
def get_all_latlng(address_data_filename,api="tencent"):

    cache_filename = "cache/latlng_cache.csv"


    output = []

    cache_df = None



    print("starting getting data from API")
    # will get all lng lat from API, discarding the previous result stored in file

    cache_file = Path(cache_filename)

    start_index = 0

    # read from xlsx


    input_dir = "input"

    address_data_filename = os.path.join(input_dir, address_data_filename)

    address_data_file = Path(address_data_filename)

    if not address_data_file.is_file():
        raise Exception("address file not found")


    address_data = pd.read_excel(address_data_filename)


    # check if there is a cache file
    if cache_file.is_file():

        print("cache file found")
        cache_df = pd.read_csv(cache_filename)

        # find the index where to resume
        start_index = len(cache_df.index)

        if start_index == len(address_data.index):
            generate_result(address_data, cache_df, api)
            return cache_df

    try:

        count = len(address_data.index)
        # count = 20

        if api == "tencent":
            api_key_list = init_api_key(api)
            call_limit = 5
            time_interval = 1 / call_limit

        else:

            api_key_list = init_api_key(api)
            call_limit = 100
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

                    address_string = address_data.loc[current_index, 'address']

                    if api == "tencent":

                        api_call_obj = {

                            "method": "get",
                            "url": "https://apis.map.qq.com/ws/geocoder/v1/",
                            "data": {
                                "address": address_string,
                                "key": api_key
                            },

                            "time_interval": time_interval
                        }

                    else:

                        api_call_obj = {

                            "method": "get",
                            "url": "http://api.map.baidu.com/geocoder/v2/",
                            "data": {
                                "output" : "json",
                                "address": address_string,
                                "ak": api_key
                            },

                            "time_interval": time_interval
                        }



                    api_call_obj_list.append(api_call_obj)

                task = loop.create_task(batch_call_api(api_call_obj_list))

                task_list.append(task)


            loop.run_until_complete(asyncio.wait(task_list))

            for task in task_list:

                for result in task.result():

                    response = result["response"]


                    if response["status"] == 120:

                        print(result["response"]["message"])

                        raise Exception("This API Key has Error : " + str(result["data"]["key"] + " message :" + result["response"]["message"] ))


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


    generate_result(address_data,df,api)




    return df



def main():
    # parse command line options

    try:


        address_data_filename = input("addres filename (default : data.xlsx):")

        if not address_data_filename:
            address_data_filename = "data.xlsx"


        df = get_all_latlng(address_data_filename,"baidu")

    except Exception as e:


        traceback.print_exc()
        print("some exception encountered, now quiting")


    finally:

        input('data generation whole process completed, press enter to leave. . . ')
        return


if __name__ == "__main__":
    main()
