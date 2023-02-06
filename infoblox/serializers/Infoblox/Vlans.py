from rest_framework import serializers

from infoblox.serializers.Infoblox.Vlan import InfobloxVlanSerializer


class InfobloxVlansSerializer(serializers.Serializer):
    data = InfobloxVlanSerializer(many=True, required=False)
