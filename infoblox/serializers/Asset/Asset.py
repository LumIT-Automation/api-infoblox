from rest_framework import serializers


class InfobloxAssetSerializer(serializers.Serializer):
    def __init__(self, idField: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if idField:
            self.fields["id"] = serializers.IntegerField(required=False)
    address = serializers.CharField(max_length=64, required=False, allow_blank=True) # @todo: only valid data.
    fqdn = serializers.CharField(max_length=255, required=True, allow_blank=True) # @todo: only valid data.
    baseurl = serializers.CharField(max_length=255, required=True) # @todo: only valid data.
    tlsverify = serializers.IntegerField(required=True)
    datacenter = serializers.CharField(max_length=255, required=True, allow_blank=True)
    environment = serializers.CharField(max_length=255, required=True)
    position = serializers.CharField(max_length=255, required=False, allow_blank=True)
    username = serializers.CharField(max_length=64, required=False)
    password = serializers.CharField(max_length=64, required=False)
