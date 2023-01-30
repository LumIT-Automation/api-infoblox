from rest_framework import serializers

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer


class InfobloxNetworkContainersSerializer(serializers.Serializer):
    data = InfobloxNetworkSerializer(many=True, required=False)


class InfobloxNetworkContainerAddNetworkSerializer(serializers.Serializer):
    subnet_mask_cidr = serializers.IntegerField(required=True)
    network_data = InfobloxNetworkSerializer(required=False)
