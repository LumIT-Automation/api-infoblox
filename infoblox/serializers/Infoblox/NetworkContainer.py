from rest_framework import serializers


class InfobloxNetworkContainerExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxNetworkContainerExtattrsValueAddressSerializer(serializers.Serializer):
    value = serializers.IPAddressField()

class InfobloxNetworkContainerExtattrsInnerSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["Real Network"] = InfobloxNetworkContainerExtattrsValueSerializer(required=False) # allows spaces in names.
        self.fields["Object Type"] = InfobloxNetworkContainerExtattrsValueSerializer(required=False)
        self.fields["Gateway"] = InfobloxNetworkContainerExtattrsValueAddressSerializer(required=False)
        self.fields["Mask"] = InfobloxNetworkContainerExtattrsValueAddressSerializer(required=False)

class InfobloxNetworkContainerSerializer(serializers.Serializer):
    _ref = serializers.CharField(max_length=255)
    network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')
    network_container = serializers.CharField(max_length=255)
    extattrs = InfobloxNetworkContainerExtattrsInnerSerializer(required=False)



class InfobloxNetworkContainerNetworksSerializer(serializers.Serializer):
    class InfobloxNetworkContainerInnerNetworksSerializer(serializers.Serializer):
        _ref = serializers.CharField(max_length=255)
        network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')

    items = InfobloxNetworkContainerInnerNetworksSerializer(many=True, required=False)
