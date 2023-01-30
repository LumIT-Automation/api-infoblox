from rest_framework import serializers


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
            self.fields["Object Type"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)

    _ref = serializers.CharField(max_length=255, required=False)
    #network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$') # @todo: restore this with OR "next-available".
    network = serializers.CharField(max_length=255, required=True)
    network_container = serializers.CharField(max_length=255, required=False)
    network_view = serializers.CharField(max_length=255, required=False)
    vlans = InfobloxNetworkVlansSerializer(many=True, required=False)
    extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)
    comment = serializers.CharField(max_length=255, required=False)
