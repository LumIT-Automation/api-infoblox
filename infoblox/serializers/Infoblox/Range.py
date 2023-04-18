from rest_framework import serializers


class InfobloxRangeSerializer(serializers.Serializer):
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
            self.fields["Country"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Reference"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["City"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Account ID"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Account Name"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)

    _ref = serializers.CharField(max_length=255, required=False)
    network = serializers.CharField(max_length=255, required=False)
    network_view = serializers.CharField(max_length=255, required=False)
    assetId = serializers.IntegerField(required=False)
    start_addr = serializers.IPAddressField(protocol='IPv4', required=False)
    end_addr = serializers.IPAddressField(protocol='IPv4', required=False)
    extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)
