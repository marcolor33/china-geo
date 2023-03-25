
import pandas as pd

from datetime import datetime

from pathlib import Path

from pandas.io.json import json_normalize


import os
import asyncio
import traceback


from helper import init_api_key,batch_call_api


# global variable here

tencent_api_key_list = []
baidu_api_key_list = []



def post_process_repsonse(response,output,dc_data,api):


    if api == "baidu":


        dc_count = len(dc_data.index)
        result_list = response["result"]

        client_count = int(len(result_list) / dc_count)


        for x in range(client_count):

            json_obj = {}

            for i in range(dc_count):

                cluster_id = dc_data.loc[i,"cluster_id"]

                index = dc_count * x + i

                json_obj["dc_" + str(cluster_id) + "_distance"] = result_list[index]["distance"]["value"]
                # change into in hr
                json_obj["dc_" + str(cluster_id) + "duration"] = result_list[index]["duration"]["value"] / 3600


            output.append(json_obj)

    elif api == "tencent":

        result_list = response["result"]["rows"]

        dc_count = len(dc_data.index)

        client_count = int(len(result_list) / dc_count)

        for x in range(len(result_list)):


            json_obj = {}

            element_list = result_list[x]["elements"]

            for i in range(len(element_list)):

                cluster_id = dc_data.loc[i,"cluster_id"]

                json_obj["dc_" + str(cluster_id) + "_distance"] = element_list[i]["distance"]
                # change into in hr
                json_obj["dc_" + str(cluster_id) + "duration"] = element_list[i]["duration"] / 3600


            output.append(json_obj)

    return output



def compose_api_call_obj(start_index,matrix_max_size,client_data,dc_data,time_interval,api_key,api):
    print("start_index", start_index)


    temp_data = client_data.loc[start_index:start_index + matrix_max_size - 1]

    origin_list = []

    for index, row in temp_data.iterrows():
        origin_list.append(str(row['lat']) + "," + str(row['lng']))

    destination_list = []

    for index, row in dc_data.iterrows():
        destination_list.append(str(row['lat']) + "," + str(row['lng']))



    if api == "baidu":


        destinations = '|'.join(destination_list)

        origins = '|'.join(origin_list)

        api_call_obj = {

            "method": "get",
            "url": "https://api.map.baidu.com/routematrix/v2/driving",
            "data": {
                "output": "json",
                "origins" : origins,
                "destinations": destinations,
                "ak": api_key
            },

            "time_interval": time_interval,
        }


    elif api == "tencent":


        destinations = ';'.join(destination_list)

        origins = ';'.join(origin_list)

        api_call_obj = {

            "method": "get",
            "url": "https://apis.map.qq.com/ws/distance/v1/matrix",
            "data": {

                "mode" : "driving",
                "output": "json",
                "from" : origins,
                "to": destinations,
                "key": api_key
            },

            "time_interval": time_interval,
        }


    return api_call_obj





def generate_result(address_data,result_data,api):

    output_dir = "output"

    output_filename = os.path.join(output_dir,"drivingInfo_multi_output.csv")
    error_filename = os.path.join(output_dir,"drivingInfo_multi_error.csv")


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
def get_driving_info_multi(client_data_filename, dc_data_filename, api="tencent"):

    cache_filename = "cache/drivingInfo_multi_cache.csv"

    output = []

    cache_df = None

    print("starting getting data from API")
    # will get all lng lat from API, discarding the previous result stored in file

    cache_file = Path(cache_filename)

    start_index = 0



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

            api_key_list = init_api_key(api,"driving_multi")

            matrix_max_length = 200

            dc_count = len(dc_data.index)
            matrix_max_size = int(matrix_max_length / dc_count)


            call_limit = 80
            time_interval = 1 / call_limit


        else:

            api_key_list = init_api_key(api,"driving_multi")

            matrix_max_length = 50

            call_limit = 1

            dc_count = len(dc_data.index)
            matrix_max_size = int(matrix_max_length / dc_count)


            time_interval = 1 / call_limit

            time_interval = 5




        while start_index < count:

            task_list = []

            loop = asyncio.new_event_loop()

            for i, api_key in enumerate(api_key_list):

                print(api_key_list)


                api_call_obj_list = []

                for j in range(call_limit):


                    current_index = start_index + (matrix_max_size * call_limit * i) +  (matrix_max_size * j)


                    print("current_index")
                    print(current_index)

                    if current_index >= count:
                        print("outrange")
                        break

                    api_call_obj = compose_api_call_obj(current_index,matrix_max_size,client_data,dc_data,time_interval,api_key,api)

                    print("api_call_obj")
                    print(api_call_obj)

                    api_call_obj_list.append(api_call_obj)

                task = loop.create_task(batch_call_api(api_call_obj_list))

                task_list.append(task)


            loop.run_until_complete(asyncio.wait(task_list))

            for task in task_list:

                for result in task.result():

                    if result["response"]["status"] != 0 and api == "baidu":
                        raise Exception("This API Key has Error : " + str(result["data"]["ak"] + " message :" + result["response"]["message"]))




                    if result["response"]["status"] == 120:

                        print(result["response"]["message"])

                        raise Exception("This API Key has Error : " + str(result["data"]["key"] + " message :" + result["response"]["message"]  + "key " + result["data"]["ak"]))


                    response = result["response"]


                    output = post_process_repsonse(response,output,dc_data,api)

            start_index = start_index + (len(api_key_list) * call_limit * matrix_max_size)



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

        df = get_driving_info_multi(client_data_filename, dc_data_filename)


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
