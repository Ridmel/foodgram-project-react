from rest_framework import mixins, viewsets


class ListRetrieveGenericViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    pass
