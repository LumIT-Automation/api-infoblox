from rest_framework import serializers

class InfobloxDismissCloudNetworkStringSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])$'
        super().__init__(regex=regex, *args, **kwargs)


class InfobloxDismissCloudNetworkSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class IntegerStringRegexSerializer(serializers.RegexField):
            def __init__(self, *args, **kwargs):
                regex = '^[0-9]{12}$'
                super().__init__(regex=regex, *args, **kwargs)


        self.fields["Account ID"] = IntegerStringRegexSerializer(required=True)
        self.fields["Account Name"] = serializers.CharField(max_length=64, required=False)

    network = InfobloxDismissCloudNetworkStringSerializer(required=False)
    Region = serializers.CharField(max_length=64, required=False)


class InfobloxDismissNetworksSerializer(serializers.Serializer):
    provider = serializers.CharField(max_length=255, required=True)
    network_data = InfobloxDismissCloudNetworkSerializer(required=True)
