from rest_framework import serializers

class TaskSerializer(serializers.Serializer):
    
    id = serializers.IntegerField(required=False)
    title = serializers.CharField(max_length=255)
    due_date = serializers.DateField(allow_null=True, required=False)
    estimated_hours = serializers.FloatField(default=0, min_value=0)
    importance = serializers.IntegerField(default=5, min_value=1, max_value=10)
    dependencies = serializers.ListField(
        child=serializers.IntegerField(),
        default=list,
        required=False
    )
    
    def validate_estimated_hours(self, value):
        if value < 0:
            raise serializers.ValidationError("Estimated hours cannot be negative")
        return value
    
    def validate_importance(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError("Importance must be between 1 and 10")
        return value


class AnalyzedTaskSerializer(TaskSerializer):
    
    priority_score = serializers.FloatField(read_only=True)
    explanation = serializers.CharField(read_only=True)