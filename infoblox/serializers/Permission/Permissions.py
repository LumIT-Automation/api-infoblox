from rest_framework import serializers

from infoblox.serializers.Permission.Permission import PermissionSerializer


class PermissionsSerializer(serializers.Serializer):
    items = PermissionSerializer(many=True)
