from rest_framework import serializers


class InfobloxNetworkSerializer(serializers.Serializer):
    class InfobloxNetworkInnerExtattrsSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            class InfobloxNetworkInnerExtattrsValueAddressSerializer(serializers.Serializer):
                value = serializers.IPAddressField()

            class InfobloxNetworkInnerExtattrsValueStringSerializer(serializers.Serializer):
                value = serializers.CharField(max_length=255)

            self.fields["Real Network"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False) # allows spaces in names.
            self.fields["Gateway"] = InfobloxNetworkInnerExtattrsValueAddressSerializer(required=False)
            self.fields["Mask"] = InfobloxNetworkInnerExtattrsValueAddressSerializer(required=False)
            self.fields["Object Type"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)

    _ref = serializers.CharField(max_length=255)
    network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')
    network_container = serializers.CharField(max_length=255)
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

    items = InfobloxNetworkIpv4InnerSerializer(many=True, required=False)
