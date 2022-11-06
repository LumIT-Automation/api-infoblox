from rest_framework import serializers

from infoblox.serializers.Permission.Role import RoleSerializer


class RolesSerializer(serializers.Serializer):
    items = RoleSerializer(many=True)
