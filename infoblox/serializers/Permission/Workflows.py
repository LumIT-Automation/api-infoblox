from rest_framework import serializers

from infoblox.serializers.Permission.Workflow import WorkflowSerializer


class WorkflowsSerializer(serializers.Serializer):
    items = WorkflowSerializer(many=True)
