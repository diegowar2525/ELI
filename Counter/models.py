from django.db import models

# Create your models here.


class Country(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Province(models.Model):
    country = models.ForeignKey(
        "Country", on_delete=models.CASCADE, null=True, blank=True
    )
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name}, {self.country.name}" if self.country else self.name


class Company(models.Model):
    province = models.ForeignKey(
        Province, on_delete=models.CASCADE, null=True, blank=True
    )
    ruc = models.CharField(max_length=11, unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class Report(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    file = models.FileField(upload_to="reportes/")
    upload_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Reporte {self.year} - {self.company.name}"


class TotalCount(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    year = models.PositiveIntegerField()
    word = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.word} ({self.quantity}) - {self.company.name} ({self.year})"

