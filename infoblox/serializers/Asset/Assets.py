from rest_framework import serializers
from infoblox.serializers.Asset.Asset import InfobloxAssetSerializer


class InfobloxAssetsSerializer(serializers.Serializer):
    items = InfobloxAssetSerializer(idField=True, many=True, required=False)
