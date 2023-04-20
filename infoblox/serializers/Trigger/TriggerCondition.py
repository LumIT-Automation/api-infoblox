from rest_framework import serializers


class InfobloxTriggerConditionSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    src_asset_id = serializers.IntegerField(required=True)
    condition = serializers.CharField(max_length=255, required=True)
