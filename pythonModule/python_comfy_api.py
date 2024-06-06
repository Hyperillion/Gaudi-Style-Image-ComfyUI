# This script is released under the MIT License
# For full license text, see https://opensource.org/licenses/MIT
import json
from urllib import request, parse
import random
import os
import shutil
import time
import alicloudCheckSDK
import threading
from termcolor import colored

# ======================================================================
# This function sends a prompt workflow to the specified URL 
# (http://127.0.0.1:8188/prompt) and queues it on the ComfyUI server
# running at that address.
def queue_prompt(prompt_workflow):
    p = {"prompt": prompt_workflow}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)    
# ======================================================================

def checkImage(file_path = ""):
    access_key_id = os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
    access_key_secret = os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    # 接入区域和地址请根据实际情况修改。

    current_directory = os.getcwd()
    queue_directory = current_directory + r"\..\queue"
    input_directory = current_directory + r"\..\input"
    output_directory = current_directory + r"\..\output"
    pass_directory = current_directory + r"\..\pass"
    fail_directory = current_directory + r"\..\fail"

    output_directory_b = os.fsencode(output_directory)

    SensitivityThreshold = 20
    runningState = True
    # for every image in output folder...
    while runningState:
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
                    print("Checking Image:", filename)
                    response = alicloudCheckSDK.invoke_function(access_key_id, access_key_secret, 'green-cip.cn-shanghai.aliyuncs.com', file_path)
                    # 自动路由。
                    if response is not None:
                        if alicloudCheckSDK.UtilClient.equal_number(500,
                                                response.status_code) or (response.body is not None and 200 != response.body.code):
                            # 区域切换到cn-beijing。
                            response = alicloudCheckSDK.invoke_function(access_key_id, access_key_secret, 'green-cip.cn-beijing.aliyuncs.com', file_path)

                        if response.status_code == 200:
                            # 调用成功。
                            # 获取审核结果。
                            result = response.body
                            print('response success. result:{}'.format(result))
                            if result.code == 200:
                                for i in result.data.result:
                                    if i.label != 'nonLabel' and i.confidence >= 20:
                                        checkStatus = False
                                        break
                                if checkStatus:
                                    os.replace(os.path.join(output_directory, filename), os.path.join(pass_directory, filename))
                                    print(colored('pass:','green'), filename)
                                else:
                                    os.replace(os.path.join(output_directory, filename), os.path.join(fail_directory, filename))
                                    print(colored('fail:','red'), filename)
                            else:
                                continue
                        else:
                            print('response not success. status:{} ,result:{}'.format(response.status_code, response))

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


def getQueueRemaining():
    queue_url = "http://127.0.0.1:8188/prompt"
    queue_response = request.urlopen(queue_url)
    queue_json = json.loads(queue_response.read())
    queue_remaining = queue_json["exec_info"]["queue_remaining"]
    return queue_remaining


def callComfyUI():
    # read workflow api data from file and convert it into dictionary 
    # assign to var prompt_workflow
    runningState = True

    prompt_workflow = json.load(open('gaudiWorkflow.json'))

    current_directory = os.getcwd()
    queue_directory = current_directory + r"\..\queue"
    input_directory = current_directory + r"\..\input"
    output_directory = current_directory + r"\..\output"
    queue_directory_b = os.fsencode(queue_directory)
    input_directory_b = os.fsencode(input_directory)
    # create a list of queue
    queued_file = []
    waiting_file = []

    

    # # give some easy-to-remember names to the nodes
    # chkpoint_loader_node = prompt_workflow["4"]
    # prompt_pos_node = prompt_workflow["6"]
    # empty_latent_img_node = prompt_workflow["5"]
    canny_ksampler_node = prompt_workflow["3"]
    depth_ksampler_node = prompt_workflow["26"]
    # lora_node = prompt_workflow["11"]
    save_image_node = prompt_workflow["39"]
    load_image_node = prompt_workflow["18"]

    # # load the checkpoint. 
    # chkpoint_loader_node["inputs"]["ckpt_name"] = "realisticVisionV60B1_v60B1VAE.safetensors"

    # # set image dimensions and batch size in EmptyLatentImage node
    # empty_latent_img_node["inputs"]["width"] = 1024
    # empty_latent_img_node["inputs"]["height"] = 1024
    # # each prompt will produce a batch of 4 images
    # empty_latent_img_node["inputs"]["batch_size"] = 4

    # initialize parameters
    waiting_status = False
    queue_remaining = -1
    dot_num = 0
    # for every prompt in prompt_list...
    while runningState:
        # send image to processing
        try:
            for file in os.listdir(queue_directory_b):
                filename = os.fsdecode(file)
                # if filename in queued_file:
                #     print(filename, "Already queued")
                #     os.replace(os.path.join(input_directory.decode("utf-8"), filename), os.path.join(r"E:\GradioPython\finishedImage", filename))
                #     continue

                # output queue length when it update

                # print("queue empty")

                if filename.lower().endswith(('.png', '.jpg', '.jpeg', 'webp')): 
                    # print("\n")
                    # move image from queue folder to input folder
                    # shutil.copyfile(os.path.join(queue_directory, filename), os.path.join(input_directory, filename))
                    os.replace(os.path.join(queue_directory, filename), os.path.join(input_directory, filename))

                    load_image_node["inputs"]["image"] = os.path.join(input_directory, filename)
                    # set the text prompt for positive CLIPTextEncode node
                    #   prompt_pos_node["inputs"]["text"] = prompt

                    # set a random seed in KSampler node 
                    canny_ksampler_node["inputs"]["seed"] = random.randint(1, 18446744073709551614)
                    depth_ksampler_node["inputs"]["seed"] = random.randint(1, 18446744073709551614)
                    # canny_ksampler_node["inputs"]["seed"] = 1
                    # depth_ksampler_node["inputs"]["seed"] = 1

                    # set filename prefix to be the same as prompt
                    # (truncate to first 100 chars if necessary)
                    fileprefix = filename
                    if len(fileprefix) > 100:
                        fileprefix = fileprefix[:100]

                    save_image_node["inputs"]["filename_prefix"] = "%time" + fileprefix
                    save_image_node["inputs"]["path"] = output_directory

                    # everything set, add entire workflow to queue.
                    queue_prompt(prompt_workflow)

                    # add the filename to the list of queued files
                    queued_file.append(filename)
                    # print the prompt that was queued
                    if prev_queue_remaining == 0:
                        print("")
                    print("Queued:", os.path.join(queue_directory, filename))

                    # task_counter += 1
                    # os.remove(os.path.join(queue_directory, filename))

                    #waiting for process
                    # time.sleep(2)
                    # continue
                else:
                    print(filename, "Not an image file")
                    # continue

        except Exception as error:
            # handle the exception
            print("An exception occurred:", error)
            print("Generate Error Occured")
            time.sleep(0.5)
            continue

        # get queue size in ComfyUI
        prev_queue_remaining = queue_remaining
        queue_remaining = getQueueRemaining()

        # print queue size when it updates
        if prev_queue_remaining != queue_remaining:
            print("Queue Size:",queue_remaining)

        # print waiting signal when queue is empty
        if (queue_remaining == 0):
            waitingMsg = "waiting for images." + "."  * (dot_num % 3) + " " * ((dot_num+2) % 3)
            print("\r\r{}".format(waitingMsg), end='')
            dot_num += 1

        time.sleep(0.2)


def print1test():
    while 1:
        print(1)

if __name__ == "__main__":
    generateThread = threading.Thread(target=callComfyUI)
    checkThread = threading.Thread(target=checkImage)
    generateThread.setDaemon(True)
    checkThread.setDaemon(True)
    generateThread.start()
    checkThread.start()

    while 1:
        pass
        