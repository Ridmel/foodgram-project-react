from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import UserSerializer

User = get_user_model()


class UserViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def perform_create(self, serializer):
        password = serializer.validated_data.pop("password")
        hash_password = make_password(password)
        serializer.save(password=hash_password)

    def get_permissions(self):
        if self.action == "list" or self.action == "create":
            self.permission_classes = (permissions.AllowAny,)
        else:
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    @action(detail=False)
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(instance=user)
        return Response(serializer.data)
