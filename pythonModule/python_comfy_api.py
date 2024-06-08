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
from PIL import Image
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

def getQueueRemaining():
    queue_url = "http://127.0.0.1:8188/prompt"
    queue_response = request.urlopen(queue_url)
    queue_json = json.loads(queue_response.read())
    queue_remaining = queue_json["exec_info"]["queue_remaining"]
    return queue_remaining


# def crop_center(image_path, output_path):
#     # Open an image file
#     with Image.open(image_path) as img:
#         # Get dimensions
#         width, height = img.size

#         # Determine the size of the square
#         new_size = min(width, height)

#         # Calculate the coordinates for cropping
#         left = (width - new_size) / 2
#         top = (height - new_size) / 2
#         right = (width + new_size) / 2
#         bottom = (height + new_size) / 2

#         # Crop the center of the image
#         img_cropped = img.crop((left, top, right, bottom))

#         # Save the cropped image
#         img_cropped.save(output_path)

def callComfyUI():
    # read workflow api data from file and convert it into dictionary 
    # assign to var prompt_workflow
    runningState = True

    prompt_workflow = json.load(open('gaudiSavePrev.json'))

    current_directory = os.getcwd()
    queue_directory = current_directory + r"\..\queue"
    input_directory = current_directory + r"\..\input"
    prev_directory = current_directory + r"\..\WebUI\public\prev"
    output_directory = current_directory + r"\..\output"
    json_directory = current_directory + r"\..\WebUI\public\log"
    queue_directory_b = os.fsencode(queue_directory)
    input_directory_b = os.fsencode(input_directory)
    # create a list of queue
    queued_file = []
    waiting_file = []

    

    # # give some easy-to-remember names to the nodes
    # chkpoint_loader_node = prompt_workflow["4"]
    prompt_pos_node = prompt_workflow["6"]
    # empty_latent_img_node = prompt_workflow["5"]
    canny_ksampler_node = prompt_workflow["3"]
    depth_ksampler_node = prompt_workflow["26"]
    # lora_node = prompt_workflow["11"]
    load_image_node = prompt_workflow["18"]
    save_image_node = prompt_workflow["39"]
    save_prev_image_node = prompt_workflow["40"]
    # filename_load_node = prompt_workflow["43"]

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

                    os.rename(os.path.join(queue_directory, filename), os.path.join(queue_directory, filename.lower()))
                    filename = filename.lower()
                    filename_pure, extension = os.path.splitext(filename)
                    if filename.endswith('.jpg'):
                        os.rename(os.path.join(queue_directory, filename), os.path.join(queue_directory, filename.replace('.jpg', '.jpeg')))
                        filename = filename.replace('.jpg', '.jpeg')
                        extension = '.jpeg'
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


                    prompt_pos_node["inputs"]["text"] = "Antonio Gaudi's architecture, sunny, bright, nature curves, colorful mosaic, RAW photo, subject, 8k uhd, dslr, soft lighting, high quality, film grain, Fujifilm XT3"
                    # set filename prefix to be the same as prompt
                    # (truncate to first 100 chars if necessary)
                    fileprefix = filename
                    if len(fileprefix) > 100:
                        fileprefix = fileprefix[:100]


                    save_image_node["inputs"]["filename"] = filename_pure
                    save_image_node["inputs"]["path"] = output_directory
                    save_image_node["inputs"]["extension"] = extension[1:]

                    save_prev_image_node["inputs"]["filename"] = filename_pure
                    save_prev_image_node["inputs"]["path"] = prev_directory
                    save_prev_image_node["inputs"]["extension"] = extension[1:]

                    # everything set, add entire workflow to queue.
                    queue_prompt(prompt_workflow)

                    # add the filename to the list of queued files
                    queued_file.append(filename)
                    # print the prompt that was queued
                    if prev_queue_remaining == 0:
                        print("")
                    print("Queued:", os.path.join(queue_directory, filename))
                    
                    progress={
                        "stage": "sendToComfyUI", 
                        "progress": 0.4
                        }
                    
                    json_path = os.path.join(json_directory, filename_pure + ".json")
                    with open(json_path, 'w') as file:
                        json.dump(progress, file)
                        print('update json file:', progress)
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

        time.sleep(3)


def print1test():
    while 1:
        print(1)

if __name__ == "__main__":
    callComfyUI()
    # generateThread = threading.Thread(target=callComfyUI)
    # checkThread = threading.Thread(target=checkAIGCImage)
    # generateThread.setDaemon(True)
    # checkThread.setDaemon(True)
    # generateThread.start()
    # checkThread.start()

    # while 1:
    #     pass
        