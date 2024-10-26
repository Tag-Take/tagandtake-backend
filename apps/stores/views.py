from django.db import transaction
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from apps.stores.utils import generate_pin
from apps.stores.permissions import IsStoreUser, IsStoreWithValidPIN
from apps.stores.models import (
    StoreProfile,
    StoreItemCategory,
    StoreItemCondition,
    StoreNotificationPreferences,
)
from apps.stores.serializers import (
    StoreProfileSerializer,
    StoreItemCategorySerializer,
    StoreItemConditionSerializer,
    StoreItemConditionUpdateSerializer,
    StoreNotificationPreferencesSerializer,
    StoreItemCategoryBulkSerializer,
    StoreProfileImageSerializer,
)
from apps.notifications.emails.services.email_senders import StoreEmailSender
from apps.common.constants import STORE_ID, STORE, PROFILE_PHOTO_URL


class StoreProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsStoreUser, IsStoreWithValidPIN]
    serializer_class = StoreProfileSerializer

    def get_object(self):
        return self.request.user.store


class GenerateNewPinView(generics.UpdateAPIView):
    permission_classes = [IsAuthenticated, IsStoreUser]
    queryset = StoreProfile.objects.all()

    def get_object(self):
        return self.request.user.store

    def update(self, request, *args, **kwargs):
        profile = self.get_object()
        profile.pin = generate_pin()
        profile.save()

        StoreEmailSender(profile).send_reset_pin_email()

        return Response(
            {"message": "New PIN generated and sent to your email."},
            status=status.HTTP_200_OK,
        )


class PublicStoreItemCategoriesView(generics.ListAPIView):
    serializer_class = StoreItemCategorySerializer

    def get_queryset(self):
        store_id = self.kwargs.get(STORE_ID)
        return StoreItemCategory.objects.filter(store_id=store_id)


class PublicStoreItemConditionsView(generics.ListAPIView):
    serializer_class = StoreItemConditionSerializer

    def get_queryset(self):
        store_id = self.kwargs.get(STORE_ID)
        return StoreItemCondition.objects.filter(store_id=store_id)


class StoreOwnerCategoriesView(generics.ListCreateAPIView):
    serializer_class = StoreItemCategoryBulkSerializer
    permission_classes = [IsAuthenticated, IsStoreWithValidPIN]

    def get_queryset(self):
        return StoreItemCategory.objects.filter(store=self.request.user.store)

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store = self.request.user.store

        serializer.context[STORE] = store

        with transaction.atomic():
            StoreItemCategory.objects.filter(store=store).delete()
            created_store_item_categories = serializer.save()

        response_serializer = StoreItemCategorySerializer(
            created_store_item_categories, many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        response_serializer = StoreItemCategorySerializer(page, many=True)
        return self.get_paginated_response(response_serializer.data)


class StoreOwnerConditionsView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated, IsStoreWithValidPIN]
    serializer_class = StoreItemConditionUpdateSerializer

    def get_queryset(self):
        return StoreItemCondition.objects.filter(store=self.request.user.store)

    def perform_create(self, serializer):
        serializer.save(store=self.request.user.store)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        store = self.request.user.store

        serializer.context[STORE] = store

        with transaction.atomic():
            StoreItemCondition.objects.filter(store=store).delete()
            created_store_item_categories = serializer.save()

        response_serializer = StoreItemConditionSerializer(
            created_store_item_categories, many=True
        )
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        response_serializer = StoreItemConditionSerializer(page, many=True)
        return self.get_paginated_response(response_serializer.data)


class StoreNotificationPreferencesView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsStoreWithValidPIN]
    serializer_class = StoreNotificationPreferencesSerializer

    def get_object(self):
        return StoreNotificationPreferences.objects.get(store__user=self.request.user)


class StoreProfileImageView(generics.CreateAPIView, generics.DestroyAPIView):
    permission_classes = [IsAuthenticated, IsStoreWithValidPIN]
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    serializer_class = StoreProfileImageSerializer

    def get_object(self):
        return self.request.user.store

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(store=self.get_object())

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data={})
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(serializer)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, serializer):
        serializer.save()
