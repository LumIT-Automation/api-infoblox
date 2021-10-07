from rest_framework import serializers


class InfobloxNetworkContainerSerializer(serializers.Serializer):
    class InfobloxNetworkContainerInnerSerializer(serializers.Serializer):
        _ref = serializers.CharField(max_length=255)
        network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$')

    data = InfobloxNetworkContainerInnerSerializer(many=True, required=False)
