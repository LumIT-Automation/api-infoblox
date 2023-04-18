from rest_framework import serializers

from infoblox.serializers.Infoblox.Range import InfobloxRangeSerializer


class InfobloxRangesSerializer(serializers.Serializer):
    data = InfobloxRangeSerializer(many=True, required=False)
