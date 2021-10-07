from rest_framework import serializers


class InfobloxNetworkContainerExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxNetworkContainerExtattrsInnerSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A trick to allow spaces in names.
        self.fields["Real Network"] = InfobloxNetworkContainerExtattrsValueSerializer(required=False)

class InfobloxNetworkContainersSerializer(serializers.Serializer):
    class InfobloxNetworkContainersInnerSerializer(serializers.Serializer):
        _ref = serializers.CharField(max_length=255)
        network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')
        network_container = serializers.CharField(max_length=255)
        extattrs = InfobloxNetworkContainerExtattrsInnerSerializer(required=False)

    data = InfobloxNetworkContainersInnerSerializer(many=True, required=False)
