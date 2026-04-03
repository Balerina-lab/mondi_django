from django.db import models

class Warehouse(models.Model):
    name = models.CharField(max_length=100)
    warehouse_type = models.CharField(max_length=20, choices=[('parts', 'Parts'), ('belts', 'Belts')])
    def __str__(self): return self.name

class Item(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items')
    part_id_barcode = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200, blank=True, null=True) # Može biti prazno
    
    # Jedinice mere
    unit_of_measure = models.CharField(max_length=10, default='kom') # kom, m, l...

    # Specifična polja za kaiševe
    position_on_machine = models.CharField(max_length=200, blank=True, null=True)
    belt_purpose = models.CharField(max_length=200, blank=True, null=True)
    belt_type = models.CharField(max_length=100, blank=True, null=True)
    thickness_teeth = models.CharField(max_length=100, blank=True, null=True)
    dimensions = models.CharField(max_length=100, blank=True, null=True)
    open_closed = models.CharField(max_length=50, blank=True, null=True)

    # Standardna polja
    serial_number = models.CharField(max_length=100, blank=True, null=True)
    map_position = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.FloatField(default=0) # Float jer kaiš može biti npr. 1.5 metara
    min_quantity = models.FloatField(default=1)
    supplier = models.CharField(max_length=200, blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    image = models.ImageField(upload_to='items/', blank=True, null=True)
    last_change_reason = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self): return f"{self.part_id_barcode} - {self.name or self.belt_purpose}"