from rest_framework import serializers


class InfobloxNetworkVlansSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=False)
    _ref = serializers.CharField(max_length=255, required=False)
    start_vlan_id = serializers.IntegerField(required=False)
    end_vlan_id = serializers.IntegerField(required=False)
    asset_id = serializers.IntegerField(required=False)


