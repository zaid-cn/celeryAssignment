from rest_framework import serializers
from .models import Tag, Image
from django.contrib.auth.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    def is_valid_for_insertion(self):
        return self.is_valid()

    def is_valid_for_retrieval(self):
        self.is_valid()
        errors = {}
        for key in self.errors:
            constraint_error_on_key = self.errors[key]
            non_unique_constraint_errors_on_key = []
            for error in constraint_error_on_key:
                if error.code != 'unique':
                    non_unique_constraint_errors_on_key.append(error)
            if len(non_unique_constraint_errors_on_key) != 0:
                errors[key] = non_unique_constraint_errors_on_key
        old_errors = self.errors
        # TODO make the assignment happen for proper error messages to be shown in the logs.
        # self.errors = errors.copy()
        # TODO: Above method is generic, make the below generic as well
        constraints_on_username = old_errors['username']
        if len(constraints_on_username) != 1:
            return False

        if constraints_on_username[0].code != 'unique':
            return False
        if len(old_errors) != 1:
            return False
        return True

    class Meta:
        model = User
        fields = '__all__'


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('name', 'place', 'uri', 'timestamp', 'user_id',)
