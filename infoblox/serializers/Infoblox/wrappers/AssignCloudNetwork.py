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

                class InfobloxNetworkInnerExtattrsValueAccountIDSerializer(serializers.Serializer):
                    class IdStringRegexSerializer(serializers.RegexField):
                        def __init__(self, *args, **kwargs):
                            regex = '^[0-9]{12}$|^[0-9a-zA-Z]{8}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{4}-[0-9a-zA-Z]{12}$'
                            super().__init__(regex=regex, *args, **kwargs)

                    value = IdStringRegexSerializer(required=True)

                self.fields["Account ID"] = InfobloxNetworkInnerExtattrsValueAccountIDSerializer(required=True)
                self.fields["Reference"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=True)
                self.fields["Account Name"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=True)
                self.fields["Scope"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)


        network = InfobloxNetworkValueStringSerializer(required=True)
        subnetMaskCidr = serializers.IntegerField(required=False)
        extattrs = InfobloxNetworkInnerExtattrsSerializer(required=True)
        comment = serializers.CharField(max_length=255, allow_blank=True, required=False)


    provider = serializers.CharField(max_length=255, required=True)
    region = serializers.CharField(max_length=255, required=False, allow_blank=True)
    network_data = InfobloxAssignNetworkDataSerializer(required=True)
