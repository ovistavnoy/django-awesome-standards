************************
django-awesome-standards
************************

Package provides backend implementation of specification in docs represented by Alex Tkachenko:

- https://gitlab.com/preusx/development-documentation-draft

----

===========
Instalation
===========

.. code-block:: bash

    pip install djangorestframework-camel-case
    pip install drf_orjson_renderer
    pip install git+https://gitlab.com/kastielspb/django-awesome-standards.git#egg=django-awesome-standards

.. code-block:: python

    # apps/settings/default.py
    ...

    INSTALLED_APPS = PROJECT_APPS + [
        ...
        'rest_framework',
        'standards',
        ...
    ]

    ...

    REST_FRAMEWORK = {
        'DEFAULT_METADATA_CLASS': 'standards.drf.metadata.FieldsetMetadata',
        'DEFAULT_PARSER_CLASSES': (
            'standards.drf.parsers.CamelCaseORJSONParser',
            'djangorestframework_camel_case.parser.CamelCaseFormParser',
            'djangorestframework_camel_case.parser.CamelCaseMultiPartParser',
        ),
        'DEFAULT_RENDERER_CLASSES': (
            'standards.drf.renderers.CamelCaseORJSONRenderer',
            'djangorestframework_camel_case.render.CamelCaseBrowsableAPIRenderer',
        ),
        'EXCEPTION_HANDLER': 'standards.drf.handlers.exception_handler',
    }

----

Currently implemented:
======================

1. common.quering.API
---------------------

1.1. Response
`````````````

.. code-block:: json

    {
        "code": 200,
        "data": {
            "item": {}
        }
    }

or

.. code-block:: json

    {
        "code": 200,
        "data": {
            "items": []
        }
    }

Realization module:
...................

.. code-block:: python

    standards.drf.views.RetrieveAPIView
    standards.drf.views.ListAPIView


1.2. Paginated response
```````````````````````

Response:
.........

.. code-block:: json

    {
        "code": 200,
        "data": {
            "items": [],
            "pagination": {
            "limit": 20,
            "offset": 0,
            "total": 43095
            }
        }
    }

Realization module:
...................

.. code-block:: python

    standards.drf.pagination.limitoffset_pagination
    standards.drf.pagination.pagenumber_pagination

----

2. common.quering.Entity
------------------------
2.1. Entity
```````````

Response:
.........

.. code-block:: json

    {
        "id": "entity-identifier-that-is-unique-inside-one-type",
        "caption": "Verbose representation of the entity object",
        "type": "EntityObjectModel",
        "props": {
            "propertyName": "Property value"
        }
    }

Realization module:
...................

.. code-block:: python

    standards.drf.serializers.EntityModelSerializer

----

3. common.quering.Request
-------------------------
3.1. Request
````````````

Response:
.........

.. code-block:: json

    {
        "singular": {
            "id": 10, "title": "some"
        },
        "multiple": [
            {"id": 10, "title": "some"},
            {"title": "another"},
            {"id": 11, "_delete": true}
        ]
    }

Realization module:
...................

.. code-block:: python

    standards.drf.serializers.NestedListSerializer

Example:
........

.. code-block:: python

    from django.db import transaction

    class SomeNestedSerializer(ModelSerializer):
        _delete = serializers.BooleanField(required=False, write_only=True)

        class Meta:
            extra_kwargs = {'id': {'read_only': False, 'required': False}}
            fields = ('id', '_delete', ...)
            list_serializer_class = NestedListSerializer

    class SomeParentSerializer(ModelSerializer):
        some_field = SomeNestedSerializer(many=True)

        def update(self, instance, data):
            some_field_data = data.pop('some_field', [])
            with transaction.atomic():
                self.instance = super().update(instance, data)

                self.fields['some_field'].update(
                    self.instance.some_field.all(),
                    [
                        {'some_related': self.instance, **dict(item)}
                        for item in some_field_data
                    ]
                )

4. common.quering.Response
--------------------------
4.1. RequestError
`````````````````

Response:
.........

.. code-block:: json

    {
        "code": 400,
        "message": "Some basic message, like: 'Bad request'.",
        "errors": [{
            "message": "Form is invalid",
            "domain": "request",
            "reason": "form_value_invalid",
            "state": {
                "fieldName": [
                    {
                        "reason": "invalid_format",
                        "message": "Field name has an invalid format"
                    }
                ]
            }
        }]
    }

