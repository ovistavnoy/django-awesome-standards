from collections import OrderedDict

from rest_framework import serializers

__all__ = (
    'StandardSerializerMixin',
    'EntitySerializerMixin',
    'Serializer',
    'ModelSerializer',
    'EntityModelSerializer',
    'NestedListSerializer',
)


class StandardSerializerMixin:
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')


class Serializer(StandardSerializerMixin, serializers.Serializer):
    pass


class ModelSerializer(StandardSerializerMixin, serializers.ModelSerializer):
    pass


class EntitySerializerMixin:

    def to_representation(self, instance):
        return OrderedDict([
            ("id", instance.id),
            ("caption", str(instance)),
            ("type", instance.__class__.__name__),
            ("props", super().to_representation(instance)),
        ])


class EntityModelSerializer(EntitySerializerMixin, ModelSerializer):
    pass


class NestedListSerializer(serializers.ListSerializer):
    """
    Usage example:

    class SomeNestedSerializer(serializers.ModelSerializer):
        ...
        _delete = serializers.BooleanField(required=False, write_only=True)

        class Meta:
            ...
            extra_kwargs = {
                'id': {'read_only': False, 'required': False}
            }
            fields = ('id', '_delete', ...)
            list_serializer_class = NestedListSerializer
            ...


    class SomeParentSerializer(serializers.ModelSerializer):
        ...
        some_field = SomeNestedSerializer(many=True)

        def update(self, instance, data):
            some_field_data = data.pop('some_field', [])
            self.instance = super().update(instance, data)

            self.fields["some_field"].update(
                self.instance.some_field.all(),
                [
                    {'some_related': self.instance, **dict(item)}
                    for item in some_field_data
                ]
            )
            ...
    """

    delete_key = '_delete'

    def update(self, objects, data):
        obj_map = {obj.id: obj for obj in objects}

        result = []
        # Perform creations and updates.
        for item in data:
            pk = item.pop('id', None)
            to_delete = item.pop(self.delete_key, False)
            obj = obj_map.get(pk)

            if obj:
                if to_delete:
                    obj.delete()
                else:
                    result.append(self.child.update(obj, item))
            elif not to_delete:
                result.append(self.child.create(item))
        return result
