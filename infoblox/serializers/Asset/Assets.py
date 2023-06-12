from rest_framework import serializers


class InfobloxAssetsSerializer(serializers.Serializer):
    class InfobloxAssestItems(serializers.Serializer):
        id = serializers.IntegerField(required=True) # @todo: only valid data.
        address = serializers.CharField(max_length=64, required=False) # @todo: only valid data.
        fqdn = serializers.CharField(max_length=255, required=True) # @todo: only valid data.
        baseurl = serializers.CharField(max_length=255, required=True)
        tlsverify = serializers.IntegerField(required=True)
        datacenter = serializers.CharField(max_length=255, required=True)
        environment = serializers.CharField(max_length=255, required=True)
        position = serializers.CharField(max_length=255, required=False)

    items = InfobloxAssestItems(many=True)
