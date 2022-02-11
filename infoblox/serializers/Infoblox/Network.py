from rest_framework import serializers
from infoblox.helpers.Log import Log


class InfobloxNetworkInnerExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxNetworkSerializer(serializers.Serializer):
    class InfobloxNetworkInnerExtattrsSerializer(serializers.Serializer):
        class InfobloxNetworkInnerExtattrsValueSerializer(serializers.Serializer):
            value = serializers.IPAddressField()

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            # A trick to allow spaces in names.
            self.fields["Object Type"] = InfobloxNetworkInnerExtattrsValueSerializer(required=False)

        Gateway = InfobloxNetworkInnerExtattrsValueSerializer(required=False)
        Mask = InfobloxNetworkInnerExtattrsValueSerializer(required=False)

    _ref = serializers.CharField(max_length=255)
    network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')
    network_container = serializers.CharField(max_length=255, required=False)
    network_view = serializers.CharField(max_length=255)
    extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)



class InfobloxNetworkIpv4Serializer(serializers.Serializer):
    class InfobloxNetworkIpv4InnerSerializer(serializers.Serializer):
        class InfobloxNetworkIpv4NamesInnerSerializer(serializers.ListField):
            name = serializers.CharField(max_length=255)

        class InfobloxNetworkIpv4ObjectsInnerSerializer(serializers.ListField):
            objects = serializers.CharField(max_length=255)

        class InfobloxNetworkIpv4TypesInnerSerializer(serializers.ListField):
            types = serializers.CharField(max_length=255)

        class InfobloxNetworkIpv4UsageInnerSerializer(serializers.ListField):
            usage = serializers.CharField(max_length=255)

        _ref = serializers.CharField(max_length=255)
        ip_address = serializers.IPAddressField()
        mac_address = serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=False, allow_blank=True)
        names = InfobloxNetworkIpv4NamesInnerSerializer(required=False)
        network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')
        network_view = serializers.CharField(max_length=255)
        objects = InfobloxNetworkIpv4ObjectsInnerSerializer(required=False)
        status = serializers.CharField(max_length=255)
        types = InfobloxNetworkIpv4TypesInnerSerializer(required=False)
        usage = InfobloxNetworkIpv4UsageInnerSerializer(required=False)

    data = InfobloxNetworkIpv4InnerSerializer(many=True, required=False)
