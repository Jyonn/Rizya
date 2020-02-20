""" 180228 Adel Liu

七牛上传政策
"""
import json

from Base.common import HOST
from Rizya.settings import MAX_IMAGE_SIZE, MAX_VIDEO_SIZE

CALLBACK = '%s/v1/3-party/qiniu/image' % HOST

IMAGE_POLICY = dict(
    insertOnly=1,
    callbackBodyType='application/json',
    fsizeMin=1,
    fsizeLimit=MAX_IMAGE_SIZE,
    mimeLimit='image/png;image/jpeg;image/heic',
    callbackUrl=CALLBACK,
)

IMAGE_BODY = dict(
    key="$(key)",
    mime_type="$(mimeType)",
    color_average="$(imageAve)",
    image_info="$(imageInfo)"
)


class Policy:
    @staticmethod
    def customize(**kwargs):
        kwargs.update(IMAGE_BODY)
        policy = dict(
            callbackBody=json.dumps(kwargs, ensure_ascii=False)
        )
        policy.update(IMAGE_POLICY)
        print('policy')
        print(policy)
        return policy
