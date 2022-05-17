import base64

from rest_framework import serializers

from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        try:
            prefix, str_image = data.split(";base64,")
            file_format = prefix.split("/")[-1]
            byte_image = base64.b64decode(str_image)
            file_image = ContentFile(byte_image, name="img." + file_format)
        except Exception:
            return super().to_internal_value(data)
        else:
            return super().to_internal_value(file_image)
