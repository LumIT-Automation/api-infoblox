from rest_framework import serializers

class InfobloxAssignCloudNetworkSerializer(serializers.Serializer):
    class InfobloxAssignNetworkDataSerializer(serializers.Serializer):
        class InfobloxNetworkValueStringSerializer(serializers.RegexField):
            def __init__(self, *args, **kwargs):
                regex = '^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$|^next-available$'
                super().__init__(regex=regex, *args, **kwargs)

        class InfobloxNetworkInnerExtattrsSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                class InfobloxNetworkInnerExtattrsValueStringSerializer(serializers.Serializer):
                    value = serializers.CharField(max_length=255)

                self.fields["Reference"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=True)
                self.fields["Account ID"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=True)
                self.fields["Account Name"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=True)

        network = InfobloxNetworkValueStringSerializer(required=True)
        extattrs = InfobloxNetworkInnerExtattrsSerializer(required=True)
        comment = serializers.CharField(max_length=255, allow_blank=True, required=True)

    provider = serializers.CharField(max_length=255, required=True)
    region = serializers.CharField(max_length=255, required=False, allow_blank=True)
    network_data = InfobloxAssignNetworkDataSerializer(required=True)
