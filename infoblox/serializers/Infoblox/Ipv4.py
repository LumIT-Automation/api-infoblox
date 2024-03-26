from rest_framework import serializers


class InfobloxIpv4ExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxIpv4Serializer(serializers.Serializer):
    class InfobloxIpv4ExtattrsInnerSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["Name Server"] = InfobloxIpv4ExtattrsValueSerializer(required=False) # allows spaces in names.
            self.fields["Gateway"] = InfobloxIpv4ExtattrsValueSerializer(required=False)
            self.fields["Mask"] = InfobloxIpv4ExtattrsValueSerializer(required=False)
            self.fields["Reference"] = InfobloxIpv4ExtattrsValueSerializer(required=False, allow_null=True)

    class InfobloxIpv4OptionsSerializer(serializers.Serializer):
        name = serializers.CharField(max_length=255, required=False)
        num = serializers.IntegerField(required=True)
        use_options = serializers.BooleanField(required=False)
        value = serializers.CharField(max_length=255, required=False)
        vendor_class = serializers.CharField(max_length=64, required=False)

    class InfobloxIpv4NamesInnerSerializer(serializers.ListField):
        name = serializers.CharField(max_length=255)

    class InfobloxIpv4ObjectsInnerSerializer(serializers.ListField):
        objects = serializers.CharField(max_length=255)

    class InfobloxIpv4TypesInnerSerializer(serializers.ListField):
        types = serializers.CharField(max_length=255)

    class InfobloxIpv4UsageInnerSerializer(serializers.ListField):
        usage = serializers.CharField(max_length=255)

    asset_id = serializers.IntegerField(required=False)
    _ref = serializers.CharField(max_length=255, required=True)
    extattrs = InfobloxIpv4ExtattrsInnerSerializer(required=False)
    ip_address = serializers.IPAddressField(required=True)
    is_conflict = serializers.BooleanField(required=False)
    lease_state = serializers.CharField(max_length=15, allow_blank=True, allow_null=True, required=False)
    mac_address = serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=False, allow_blank=True)
    mac = serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=False, allow_blank=True)
    names = InfobloxIpv4NamesInnerSerializer(required=False)
    network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$', required=True)
    network_view = serializers.CharField(max_length=255, required=False)
    objects = InfobloxIpv4ObjectsInnerSerializer(required=False)
    status = serializers.CharField(max_length=255, required=True)
    types = InfobloxIpv4TypesInnerSerializer(required=False)
    usage = InfobloxIpv4UsageInnerSerializer(required=False)
    options = InfobloxIpv4OptionsSerializer(required=False, many=True)
