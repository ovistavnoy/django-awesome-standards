from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.exceptions import Throttled, UnsupportedMediaType
from rest_framework import serializers

from standards.drf.serializers import Serializer, ModelSerializer

__all__ = ('SomeSerializer', 'UserSerializer')

User = get_user_model()


class UserSerializer(ModelSerializer):
    update_url = serializers.SerializerMethodField()

    class Meta:
        fields = ('id', 'first_name', 'last_name', 'email', 'update_url')
        model = User

    def get_update_url(self, obj):
        return reverse('user_update', args=[obj.id])


class SomeNestedSerializer(Serializer):
    title = serializers.CharField()

    class Meta:
        fields = ('title', )


class SomeSerializer(Serializer):
    name = serializers.CharField()
    phone = serializers.CharField()
    choice = serializers.ChoiceField(
        choices=(
            (1, 'Choice 1'),
            (2, 'Choice 2'),
        )
    )
    nested_obj = SomeNestedSerializer()

    class Meta:
        fields = ('name', 'phone', 'choice', 'nested_obj')

    def validate(self, data):
        raise serializers.ValidationError('Some error1')
        raise serializers.ValidationError('Some error2')
        # raise Throttled(6)
        raise UnsupportedMediaType(
            self.context.get('request').content_type
        )

    def create(self, data):
        return data
