from rest_framework import serializers

from infoblox.serializers.Trigger.Trigger import InfobloxTriggerSerializer


class InfobloxTriggersSerializer(serializers.Serializer):
    items = InfobloxTriggerSerializer(many=True)
