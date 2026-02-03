from django.db import models
from django.contrib.auth.models import User
import json


class Dataset(models.Model):
    """Model to store uploaded datasets"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    upload_date = models.DateTimeField(auto_now_add=True)
    total_count = models.IntegerField()
    avg_flowrate = models.FloatField()
    avg_pressure = models.FloatField()
    avg_temperature = models.FloatField()
    type_distribution = models.TextField()  # JSON string
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.filename} - {self.upload_date}"
    
    def set_type_distribution(self, data):
        """Convert dict to JSON string"""
        self.type_distribution = json.dumps(data)
    
    def get_type_distribution(self):
        """Convert JSON string to dict"""
        return json.loads(self.type_distribution)


class Equipment(models.Model):
    """Model to store individual equipment records"""
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField()
    pressure = models.FloatField()
    temperature = models.FloatField()
    
    def __str__(self):
        return self.equipment_name