from rest_framework import serializers


class InfobloxIpv4sExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxIpv4sExtattrsInnerSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # A trick to allow spaces in names.
        self.fields["Name Server"] = InfobloxIpv4sExtattrsValueSerializer(required=False)

    Reference = InfobloxIpv4sExtattrsValueSerializer(required=False, allow_null=True)

class InfobloxIpv4sSerializer(serializers.Serializer):
    def __init__(self, reqType, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class InfobloxIpv4sInnerSerializer(serializers.Serializer):
            def __init__(self, reqType, *args, **kwargs):
                super().__init__(*args, **kwargs)

                # Build different serializer basing on reqType value.
                if reqType == "specified-ip":
                    self.fields["ipv4addr"] = serializers.IPAddressField(required=True)

                if reqType == "next-available":
                    self.fields["network"] = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$', required=True)
                    self.fields["object_type"] = serializers.CharField(max_length=255, required=False)

            mac = serializers.ListField(
                child=serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=True)
            )
            name = serializers.CharField(max_length=255, required=False)
            extattrs = InfobloxIpv4sExtattrsInnerSerializer(required=False, many=True)
            number = serializers.IntegerField(required=False)

        # Build son serializer dynamically, passing the plType parameter.
        self.fields["data"] = InfobloxIpv4sInnerSerializer(
            required=True,
            reqType=reqType
        )
