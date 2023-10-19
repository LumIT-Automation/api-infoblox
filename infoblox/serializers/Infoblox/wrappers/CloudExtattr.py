from rest_framework import serializers

class InfobloxCloudExtAttrSerializer(serializers.Serializer):
    class InfobloxCloudExtAttrInnerSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["Account ID"] = serializers.CharField(max_length=64, required=False)
            self.fields["Account Name"] = serializers.CharField(max_length=64, required=False)
            self.fields["Country"] = serializers.CharField(max_length=64, required=False)
            self.fields["Reference"] = serializers.CharField(max_length=64, required=False)

    data = InfobloxCloudExtAttrInnerSerializer(many=True, required=False)
