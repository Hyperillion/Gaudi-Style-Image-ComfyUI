from alibabacloud_green20220302.client import Client
from alibabacloud_green20220302 import models
from alibabacloud_tea_openapi.models import Config
from alibabacloud_tea_util.client import Client as UtilClient
from alibabacloud_tea_util import models as util_models
import json
import uuid
import oss2
import time
import os

# 服务是否部署在vpc上
is_vpc = False
# 文件上传token endpoint->token
token_dict = dict()
# 上传文件客户端
bucket = None


# 创建请求客户端
def create_client(access_key_id, access_key_secret, endpoint):
    config = Config(
        access_key_id=access_key_id,
        access_key_secret=access_key_secret,
        # 设置http代理。
        # http_proxy='http://10.10.xx.xx:xxxx',
        # 设置https代理。
        # https_proxy='https://10.10.xx.xx:xxxx',
        # 接入区域和地址请根据实际情况修改。
        endpoint=endpoint
    )
    return Client(config)


# 创建文件上传客户端
def create_oss_bucket(is_vpc, upload_token):
    global token_dict
    global bucket
    auth = oss2.StsAuth(upload_token.access_key_id, upload_token.access_key_secret, upload_token.security_token)

    if (is_vpc):
        end_point = upload_token.oss_internal_end_point
    else:
        end_point = upload_token.oss_internet_end_point
    # 注意：此处实例化的bucket请尽可能重复使用，避免重复建立连接，提升检测性能。
    bucket = oss2.Bucket(auth, end_point, upload_token.bucket_name)

# 上传文件
def upload_file(file_name, upload_token):
    create_oss_bucket(is_vpc, upload_token)
    object_name = upload_token.file_name_prefix + str(uuid.uuid1()) + '.' + file_name.split('.')[-1]
    bucket.put_object_from_file(object_name, file_name)
    return object_name


def invoke_function(access_key_id, access_key_secret, endpoint, file_path):
    # 注意：此处实例化的client请尽可能重复使用，避免重复建立连接，提升检测性能。
    client = create_client(access_key_id, access_key_secret, endpoint)
    # 创建RuntimeObject实例并设置运行参数。
    runtime = util_models.RuntimeOptions()

    # 本地文件的完整路径，例如D:\localPath\exampleFile.png
    # file_path = r"C:\Users\Public\Gaudi\ComfyUI\ComfyUI_windows_portable\ComfyUI\Gaudi-Style-Image-ComfyUI\output\asdiugvalurhg123125.jpg"

    # 获取文件上传token
    upload_token = token_dict.setdefault(endpoint, None)
    if (upload_token == None) or int(upload_token.expiration) <= int(time.time()):
        response = client.describe_upload_token()
        upload_token = response.body.data
        token_dict[endpoint] = upload_token
    # 上传文件
    object_name = upload_file(file_path, upload_token)

    # 检测参数构造。
    service_parameters = {
        # 待检测文件所在bucket名称。
        'ossBucketName': upload_token.bucket_name,
        # 待检测文件。
        'ossObjectName': object_name,
        # 数据唯一标识
        'dataId': str(uuid.uuid1())
    }

    image_moderation_request = models.ImageModerationRequest(
        # 图片检测service：内容安全控制台图片增强版规则配置的serviceCode，示例：baselineCheck
      	# 支持service请参考：https://help.aliyun.com/document_detail/467826.html?0#p-23b-o19-gff
        service='aigcCheck',
        service_parameters=json.dumps(service_parameters)
    )

    try:
        return client.image_moderation_with_options(image_moderation_request, runtime)
    except Exception as err:
        print(err)


if __name__ == '__main__':
    # 阿里云账号AccessKey拥有所有API的访问权限，建议您使用RAM用户进行API访问或日常运维。
    # 强烈建议不要把AccessKey ID和AccessKey Secret保存到工程代码里，否则可能导致AccessKey泄露，威胁您账号下所有资源的安全。
    # 常见获取环境变量方式：
    # 获取RAM用户AccessKey ID：os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
    # 获取RAM用户AccessKey Secret：os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    access_key_id = os.environ['ALIBABA_CLOUD_ACCESS_KEY_ID']
    access_key_secret = os.environ['ALIBABA_CLOUD_ACCESS_KEY_SECRET']
    file_path = r"C:\Users\Public\Gaudi\ComfyUI\ComfyUI_windows_portable\ComfyUI\Gaudi-Style-Image-ComfyUI\output\ea421ef5c4014cefba2ee021c9003545.webp"
    # 接入区域和地址请根据实际情况修改。
    response = invoke_function(access_key_id, access_key_secret, 'green-cip.cn-shanghai.aliyuncs.com', file_path)
    # 自动路由。
    if response is not None:
        if UtilClient.equal_number(500,
                                   response.status_code) or (response.body is not None and 200 != response.body.code):
            # 区域切换到cn-beijing。
            response = invoke_function(access_key_id, access_key_secret, 'green-cip.cn-beijing.aliyuncs.com', file_path)

        if response.status_code == 200:
            # 调用成功。
            # 获取审核结果。
            result = response.body
            print('response success. result:{}'.format(result))
            if result.code == 200:
                print(type(result.data.result))                
                for i in result.data.result:
                    if i.label != 'nonLabel' and i.confidence >= 20:
                        print('fail')
                        
                    else:
                        print('pass')
        else:
            print('response not success. status:{} ,result:{}'.format(response.status_code, response))