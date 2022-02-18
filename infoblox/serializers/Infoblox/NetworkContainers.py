from rest_framework import serializers

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer


class InfobloxNetworkContainersSerializer(serializers.Serializer):
    data = InfobloxNetworkSerializer(many=True, required=False)
