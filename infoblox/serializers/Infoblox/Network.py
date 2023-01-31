from rest_framework import serializers


class InfobloxNetworkValueStringSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$|^next-available$'
        super().__init__(regex=regex, *args, **kwargs)


class InfobloxNetworkSerializer(serializers.Serializer):
    class InfobloxNetworkVlansSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True)
        name = serializers.CharField(max_length=255, required=False)
        vlan = serializers.CharField(max_length=255, required=False)

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
            self.fields["Name Server"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Object Type"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Region"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Color"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Country"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["CloudProviderRegion"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)

    _ref = serializers.CharField(max_length=255, required=False)
    network = InfobloxNetworkValueStringSerializer()
    network_container = serializers.CharField(max_length=255, required=False)
    network_view = serializers.CharField(max_length=255, required=False)
    vlans = InfobloxNetworkVlansSerializer(many=True, required=False)
    extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)
    comment = serializers.CharField(max_length=255, required=False)
