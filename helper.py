
import os
import pandas as pd
import requests
import asyncio

async def batch_call_api(api_call_obj_list):

    result_list = []

    for api_call_obj in api_call_obj_list:


        loop = asyncio.get_event_loop()

        task = loop.create_task(call_api(api_call_obj))

        result = await task
        result_list.append(result)

    return result_list


async def async_request(method,url,data):

        print("calling. . .")

        if method == "post":
            response = requests.post(url, data)
        else:
            response = requests.get(url, data)

        return response.json()


async def call_api(api_call_obj):

        time_interval = api_call_obj["time_interval"]
        method = api_call_obj["method"]
        url = api_call_obj["url"]
        data = api_call_obj["data"]


        loop = asyncio.get_event_loop()
        task = loop.create_task(async_request(method,url,data))

        temp_result = await asyncio.wait((task,asyncio.sleep(time_interval)))


        response = task.result()

        api_call_obj["response"] = response
        # api_call_obj["response_status"] = response.status_code

        return api_call_obj



def init_api_key(api="baidu",mode="normal"):


    try:

        api_key_list = []


        apikey_dir = "apikey"

        if api == "tencent" :

            api_key_filename = os.path.join(apikey_dir, "apikey_tencent.csv")

        elif api == "baidu":

            if mode == "driving_multi":
                api_key_filename = os.path.join(apikey_dir, "apikey_driving_multi_baidu.csv")

            else:
                api_key_filename = os.path.join(apikey_dir, "apikey_baidu.csv")

        df = pd.read_csv(api_key_filename)

        for index, row in df.iterrows():
            key = row["key"]
            api_key_list.append(key)


        return api_key_list

    except Exception as e:

        print("cannot init API key")

        raise e


