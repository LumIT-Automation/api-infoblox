from rest_framework import serializers

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer


class InfobloxNetworkContainersSerializer(serializers.Serializer):
    data = InfobloxNetworkSerializer(many=True, required=False)


class InfobloxNetworkContainerAddNetworkSerializer(serializers.Serializer):
    class InfobloxNetworkContainerAddNetworkInnerSerializer(serializers.Serializer):
        subnet_mask = serializers.CharField(max_length=2, required=True)

    next_available = InfobloxNetworkContainerAddNetworkInnerSerializer(required=True)
