# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.abstract_client import AbstractClient
from tencentcloud.ims.v20201229 import models
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.ims.v20201229 import ims_client
from termcolor import colored
import json
import os
import base64
import time
import threading

class ImsClient(AbstractClient):
    _apiVersion = '2020-12-29'
    _endpoint = 'ims.tencentcloudapi.com'
    _service = 'ims'

    def CreateImageModerationAsyncTask(self, request):
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("CreateImageModerationAsyncTask", params, headers=headers)
            response = json.loads(body)
            model = models.CreateImageModerationAsyncTaskResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))

    def ImageModeration(self, request):
        try:
            params = request._serialize()
            headers = request.headers
            body = self.call("ImageModeration", params, headers=headers)
            response = json.loads(body)
            model = models.ImageModerationResponse()
            model._deserialize(response["Response"])
            return model
        except Exception as e:
            if isinstance(e, TencentCloudSDKException):
                raise
            else:
                raise TencentCloudSDKException(type(e).__name__, str(e))

def Image2Base64(image_path):
    with open(image_path, 'rb') as f:
        image = f.read()
    return base64.b64encode(image).decode('utf-8')

def checkAIGCImage(output_directory = "", pass_directory= "", fail_directory= "", preChecking = False):
    # current_directory = os.getcwd()
    output_directory_b = os.fsencode(output_directory)
    json_directory = fail_directory + r"\..\WebUI\public\log"
    # print(preChecking)
    
    while True:
        time.sleep(1)
        # send image to processing
        try:
            for file in os.listdir(output_directory_b):
                filename = os.fsdecode(file)
                # if filename in queued_file:
                #     print(filename, "Already queued")
                #     os.replace(os.path.join(input_directory.decode("utf-8"), filename), os.path.join(r"E:\GradioPython\finishedImage", filename))
                #     continue

                # output queue length when it update

                # print("queue empty")
                checkStatus = True
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', 'webp')): 
                    # move image from queue folder to input folder
                    file_path = os.path.join(output_directory, filename)
                    filename_pure, file_extension = os.path.splitext(filename)     
                    json_path = os.path.join(json_directory, filename_pure + ".json")
                    
                    
                    if preChecking:
                        progress={
                            "stage": "preCheck",
                            "queue_length": 1,
                            "progress": 0.2
                        }
                        # print("PreChecking Image json", filename, json_path)
                    else:
                        progress={
                            "stage": "AICheck",
                            "queue_length": 1,
                            "progress": 0.9
                        }
                        # print("AIChecking Image json", filename, json_path)
                        
                    with open(json_path, 'w') as file:
                        json.dump(progress, file)
                        print('update json file:', progress)
                        
                    print("Checking Image:", filename)
                    try:
                        # 初始化凭证
                        cred = credential.Credential(
                        os.environ.get("TENCENTCLOUD_SECRET_ID"),
                        os.environ.get("TENCENTCLOUD_SECRET_KEY"))

                        
                        # 配置HTTP选项
                        http_profile = HttpProfile()
                        http_profile.endpoint = "ims.tencentcloudapi.com"

                        # 配置客户端选项
                        client_profile = ClientProfile()
                        client_profile.httpProfile = http_profile

                        # 初始化客户端
                        client = ims_client.ImsClient(cred, "ap-guangzhou", client_profile)

                        # 构造请求
                        req = models.ImageModerationRequest()

                        # 设置请求参数
                        params = {
                            "BizType": "1799358210964983808",
                            "FileContent": Image2Base64(file_path)
                        }
                        req.from_json_string(json.dumps(params))

                        # 调用接口
                        resp = client.ImageModeration(req)
                        
                        # 打印响应
                        response_json = resp.to_json_string()
                        response_dict = json.loads(response_json)
                        
                        # print(response_json)
                        
                        if response_dict['Suggestion'] == 'Pass':
                            os.replace(os.path.join(output_directory, filename), os.path.join(pass_directory, filename))
                            print(colored('pass:','green'), filename)
                            if preChecking:
                                progress={
                                    "stage": "waitingComfyUI",
                                    "queue_length": 1,
                                    "progress": 0.4
                                }
                            else:
                                progress={
                                    "stage": "pass",
                                    "queue_length": 1,
                                    "progress": 1,
                                    "output_filename": filename
                                }
                        else:
                            os.replace(os.path.join(output_directory, filename), os.path.join(fail_directory, filename))
                            print(colored('fail:','red'), filename)
                            print(response_dict['Label'],response_dict['SubLabel'], response_dict['Score'])
                            print(response_dict)
                            progress={
                                "stage": "fail",
                                "queue_length": 1,
                                "progress": -1
                            }
                            
                        with open(json_path, 'w') as file:
                            json.dump(progress, file)
                            print('update json file:', progress)
                            
                    except TencentCloudSDKException as err:
                        print(err)
                        os.replace(os.path.join(output_directory, filename), os.path.join(fail_directory, filename))
                        print(colored('error:','red'), filename)
                        # print(response_dict['Label'],response_dict['SubLabel'], response_dict['Score'])
                        # print(response_dict)
                        progress={
                            "stage": "error",
                            "queue_length": 1,
                            "progress": -2
                        }
                            
                        with open(json_path, 'w') as file:
                            json.dump(progress, file)
                            print('update json file:', progress)
                        

                    # continue
                else:
                    print(filename, "Not an image file")
                    # continue

        except Exception as error:
            # handle the exception
            print("An exception occurred:", error)
            print("Check Error Occured")
            time.sleep(0.5)
            continue
    

if __name__ == "__main__":
    print("Checking Image...")
    current_directory = os.getcwd()

    preCheckThread = threading.Thread(target=checkAIGCImage, args=(current_directory + r"\..\preCheck", current_directory + r"\..\queue", current_directory + r"\..\fail", True))
    checkAIGCThread = threading.Thread(target=checkAIGCImage, args=(current_directory + r"\..\output", current_directory + r"\..\WebUI\public\pass", current_directory + r"\..\fail", False))
    preCheckThread.setDaemon(True)
    checkAIGCThread.setDaemon(True)
    preCheckThread.start()
    checkAIGCThread.start()

    while 1:
        pass
