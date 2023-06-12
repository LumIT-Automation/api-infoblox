from rest_framework import serializers
from infoblox.serializers.Asset.Asset import InfobloxAssetSerializer


class InfobloxAssetsSerializer(serializers.Serializer):
    items = InfobloxAssetSerializer(many=True, required=False)
