from rest_framework import serializers


class InfobloxTriggerSerializer(serializers.Serializer):
    class InfobloxTriggerConditionSerializer(serializers.Serializer):
        src_asset_id = serializers.IntegerField(required=True)
        condition = serializers.CharField(max_length=255, required=True)

    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=255, required=True)
    dst_asset_id = serializers.IntegerField(required=True)
    action = serializers.CharField(max_length=255, required=True)
    enabled = serializers.IntegerField(required=True)
    conditions = InfobloxTriggerConditionSerializer(many=True, required=False)
