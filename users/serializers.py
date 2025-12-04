from rest_framework.serializers import CharField, ModelSerializer

from users.models import User

class UserCreateSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")


class UserListSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "avatar")


class UserDetailSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "avatar", "tg_chat_id")


class UserUpdateSerializer(ModelSerializer):
    password = CharField(style={"input_type": "password"})

    class Meta:
        model = User
        fields = ("email", "password", "avatar", "tg_chat_id")

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.set_password(validated_data.get("password", instance.password))
        instance.avatar = validated_data.get("avatar", instance.avatar)
        instance.tg_chat_id = validated_data.get("tg_chat_id", instance.tg_chat_id)
        instance.save()
        return instance
