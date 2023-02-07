from rest_framework import serializers

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer


class InfobloxAssignNetworkSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    region = serializers.CharField(max_length=255, required=True)
    network_data = InfobloxNetworkSerializer(required=True)
