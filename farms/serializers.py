from rest_framework import serializers
from .models import Farm

class FarmSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Farm
        fields = [
            "id",
            "owner",
            "name",
            "address",
            "city",
            "size",
            "latitude",
            "longitude",
        ]
        read_only_fields = ["id", "owner", "latitude", "longitude"]
