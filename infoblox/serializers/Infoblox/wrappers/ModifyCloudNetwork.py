from rest_framework import serializers

class InfobloxModifyCloudNetworkSerializer(serializers.Serializer):
    class InfobloxModifyNetworkDataSerializer(serializers.Serializer):
        class InfobloxNetworkValueStringSerializer(serializers.RegexField):
            def __init__(self, *args, **kwargs):
                regex = '^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$|^next-available$'
                super().__init__(regex=regex, *args, **kwargs)

        class InfobloxNetworkInnerExtattrsSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                class InfobloxNetworkInnerExtattrsValueStringSerializer(serializers.Serializer):
                    value = serializers.CharField(max_length=255)

                self.fields["Reference"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
                self.fields["Account ID"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
                self.fields["Account Name"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)

        extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)
        comment = serializers.CharField(max_length=255, allow_blank=True, required=False)


    #provider = serializers.CharField(max_length=255, required=False)
    #region = serializers.CharField(max_length=255, required=False, allow_blank=True)
    network_data = InfobloxModifyNetworkDataSerializer(required=True)
