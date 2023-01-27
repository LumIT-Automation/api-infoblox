from rest_framework import serializers

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer


class InfobloxNetworkContainersSerializer(serializers.Serializer):
    data = InfobloxNetworkSerializer(many=True, required=False)


class InfobloxNetworkContainerAddNetworkSerializer(serializers.Serializer):
    subnetMask = serializers.CharField(max_length=2, required=True)