from rest_framework import serializers

from user.models import User


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['question1', 'question2', 'question3']
        