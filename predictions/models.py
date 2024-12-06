from django.db import models

class PredictionResult(models.Model):
    image = models.ImageField(upload_to='media/analyzed_images/')
    predicted_class = models.CharField(max_length=100)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    diagnosis = models.TextField(default="No diagnosis available")  # Add default here
    treatment = models.TextField(default="No treatment available")

    def __str__(self):
        return f"{self.predicted_class} - {self.confidence:.2f}%"


