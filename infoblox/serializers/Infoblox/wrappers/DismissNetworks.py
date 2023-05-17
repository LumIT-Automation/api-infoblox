from rest_framework import serializers

class InfobloxDismissCloudNetworkStringSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])$'
        super().__init__(regex=regex, *args, **kwargs)


class InfobloxDismissCloudNetworkSerializer(serializers.Serializer):
    class InfobloxNetworkInnerExtattrsSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            class InfobloxNetworkInnerExtattrsValueStringSerializer(serializers.Serializer):
                value = serializers.CharField(max_length=255)

            self.fields["Region"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Account ID"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
            self.fields["Account Name"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)

    network = InfobloxDismissCloudNetworkStringSerializer(required=False)
    extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)


class InfobloxDismissNetworksSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    network_data = InfobloxDismissCloudNetworkSerializer(required=True)
