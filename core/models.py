# core/models.py
from django.db import models

class Warehouse(models.Model):
    TYPE_CHOICES = [
        ('parts', 'Rezervni Delovi'),
        ('belts', 'Kaiševi'),
    ]
    # Ime magacina (ujedno i ime mašine)
    name = models.CharField(max_length=100, unique=True)
    warehouse_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='parts')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Item(models.Model):
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, related_name='items')
    
    # Polja po tvojoj specifikaciji
    part_id_barcode = models.CharField(max_length=100) # ID i Barkod su ista stvar
    name = models.CharField(max_length=200) # Naziv dela
    position_on_machine = models.CharField(max_length=200) # Gde se nalazi na mašini
    serial_number = models.CharField(max_length=100, blank=True, null=True) # Serijski broj (opciono)
    map_position = models.CharField(max_length=100, blank=True, null=True) # Pozicija u mapama (npr. M-01)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) # Cena
    supplier = models.CharField(max_length=200, blank=True, null=True) # Dobavljač
    
    quantity = models.IntegerField(default=0) # Trenutno stanje na stanju
    min_quantity = models.IntegerField(default=1) # Minimalna kolicina za alarm
    
    image = models.ImageField(upload_to='items/', blank=True, null=True) # Slika dela

    last_change_reason = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.part_id_barcode})"