from django.db import models
from django.db.models import JSONField

# Create your models here.


class Province(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}"


class Company(models.Model):
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, blank=True
    )
    ruc = models.CharField(max_length=11, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.ruc}"


class Report(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to="reportes/")
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.year} - {self.name}"


class TotalCount(models.Model):
    year = models.PositiveIntegerField()
    word = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.word} - {self.quantity}"


class TotalCountReport(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('report', 'word')
    
    def __str__(self):
        return f"{self.word} - {self.quantity}"