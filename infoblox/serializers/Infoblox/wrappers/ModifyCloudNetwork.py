from rest_framework import serializers

class InfobloxModifyCloudNetworkSerializer(serializers.Serializer):
    class InfobloxModifyNetworkDataSerializer(serializers.Serializer):
        class InfobloxNetworkInnerExtattrsSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                class InfobloxNetworkInnerExtattrsValueStringSerializer(serializers.Serializer):
                    value = serializers.CharField(max_length=255)

                class InfobloxNetworkInnerExtattrsValueAccountIDSerializer(serializers.Serializer):
                    class IntegerStringRegexSerializer(serializers.RegexField):
                        def __init__(self, *args, **kwargs):
                            regex = '^[0-9]{12}$'
                            super().__init__(regex=regex, *args, **kwargs)

                    value = IntegerStringRegexSerializer(required=True)


                self.fields["Account ID"] = InfobloxNetworkInnerExtattrsValueAccountIDSerializer(required=True)
                self.fields["Reference"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)
                self.fields["Account Name"] = InfobloxNetworkInnerExtattrsValueStringSerializer(required=False)


        extattrs = InfobloxNetworkInnerExtattrsSerializer(required=False)
        comment = serializers.CharField(max_length=255, allow_blank=True, required=False)

    network_data = InfobloxModifyNetworkDataSerializer(required=True)
