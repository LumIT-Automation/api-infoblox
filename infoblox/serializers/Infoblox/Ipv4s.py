from rest_framework import serializers

from infoblox.serializers.Infoblox.Ipv4 import InfobloxIpv4Serializer


class InfobloxIpv4sExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxIpv4sExtattrsValueAddressSerializer(serializers.Serializer):
    value = serializers.IPAddressField()

class InfobloxIpv4sExtattrsInnerSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["Name Server"] = InfobloxIpv4sExtattrsValueSerializer(required=False) # allows spaces in names.
        self.fields["Gateway"] = InfobloxIpv4sExtattrsValueAddressSerializer(required=False)
        self.fields["Mask"] = InfobloxIpv4sExtattrsValueAddressSerializer(required=False)
        self.fields["Reference"] = InfobloxIpv4sExtattrsValueSerializer(required=False)

class InfobloxIpv4OptionsSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=False)
    num = serializers.IntegerField(required=True)
    use_options = serializers.BooleanField(required=False)
    value = serializers.CharField(max_length=255, required=False)
    vendor_class = serializers.CharField(max_length=64, required=False)

class InfobloxIpv4sSerializer(serializers.Serializer):
    def __init__(self, reqType, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class InfobloxIpv4sInnerSerializer(serializers.Serializer):
            def __init__(self, reqType, *args, **kwargs):
                super().__init__(*args, **kwargs)

                # Build different serializer basing on reqType value.
                if reqType == "post.specified-ip":
                    self.fields["ipv4addr"] = serializers.IPAddressField(required=True)
                    self.fields["mac"] = serializers.ListField(
                        child=serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=True)
                    )
                    self.fields["name"] = serializers.CharField(max_length=255, required=False)
                    self.fields["extattrs"] = InfobloxIpv4sExtattrsInnerSerializer(required=False, many=True)
                    self.fields["number"] = serializers.IntegerField(required=False)
                    self.fields["options"] = InfobloxIpv4OptionsSerializer(required=False, many=True)

                elif reqType == "post.next-available":
                    self.fields["network"] = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$', required=True)
                    self.fields["range_first_ip"] = serializers.IPAddressField(protocol='IPv4', required=False)
                    self.fields["range_last_ip"] = serializers.IPAddressField(protocol='IPv4', required=False)
                    self.fields["object_type"] = serializers.CharField(max_length=255, required=False)
                    self.fields["mac"] = serializers.ListField(
                        child=serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=True)
                    )
                    self.fields["name"] = serializers.CharField(max_length=255, required=False)
                    self.fields["extattrs"] = InfobloxIpv4sExtattrsInnerSerializer(required=False, many=True)
                    self.fields["number"] = serializers.IntegerField(required=False)
                    self.fields["options"] = InfobloxIpv4OptionsSerializer(required=False, many=True)

                elif reqType == "get":
                    self.fields["items"] = InfobloxIpv4Serializer(many=True, required=False)

        # Build son serializer dynamically, passing the plType parameter.
        self.fields["data"] = InfobloxIpv4sInnerSerializer(
            required=True,
            reqType=reqType
        )
