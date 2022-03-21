from rest_framework import serializers


class HistorySerializer(serializers.Serializer):
    class HistoryInnerSerializer(serializers.Serializer):
        class HistoryItemsSerializer(serializers.Serializer):
            id = serializers.IntegerField(required=True)
            username = serializers.CharField(max_length=255, required=True)
            action = serializers.CharField(max_length=2048, required=True)
            asset_id = serializers.IntegerField(required=True)
            type = serializers.CharField(max_length=255, required=True)
            status = serializers.CharField(max_length=255, required=True)
            date = serializers.CharField(max_length=255, required=True)

            address = serializers.IPAddressField(required=True, allow_blank=True)
            network = serializers.RegexField(regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$', required=True, allow_blank=True)
            mask = serializers.CharField(max_length=255, required=False, allow_blank=True)
            gateway = serializers.CharField(max_length=255, required=False, allow_blank=True)

        items = HistoryItemsSerializer(many=True)

    data = HistoryInnerSerializer(required=True)
