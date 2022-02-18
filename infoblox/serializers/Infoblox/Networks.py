from rest_framework import serializers

from infoblox.serializers.Infoblox.Network import InfobloxNetworkSerializer


class InfobloxNetworksSerializer(serializers.Serializer):
    data = InfobloxNetworkSerializer(many=True, required=False)
