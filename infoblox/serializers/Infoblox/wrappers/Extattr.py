from rest_framework import serializers

class InfobloxExtAttrSerializer(serializers.Serializer):
    class InfobloxExtAttrInnerSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["Account ID"] = serializers.CharField(max_length=64, required=False)
            self.fields["Account Name"] = serializers.CharField(max_length=64, required=False)
            self.fields["Country"] = serializers.CharField(max_length=64, required=False)

    data = InfobloxExtAttrInnerSerializer(many=True, required=False)
