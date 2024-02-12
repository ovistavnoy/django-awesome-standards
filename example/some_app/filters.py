from django.contrib.auth import get_user_model

from django_filters import FilterSet, filters

__all__ = ('SomeFilterSet', )

User = get_user_model()


class SomeFilterSet(FilterSet):
    is_active = filters.ChoiceFilter(
        choices=(
            (True, 'One'),
            (False, 'Two'),
        )
    )

    class Meta:
        model = User
        fields = []
