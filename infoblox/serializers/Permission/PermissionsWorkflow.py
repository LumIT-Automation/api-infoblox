from rest_framework import serializers

from infoblox.serializers.Permission.PermissionWorkflow import PermissionWorkflowSerializer


class PermissionsWorkflowSerializer(serializers.Serializer):
    items = PermissionWorkflowSerializer(many=True)
