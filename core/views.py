from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Warehouse, Item

# Biblioteke za barkod (Proveri da li si uradio: pip install python-barcode pillow)
from barcode import Code128
from barcode.writer import ImageWriter
import io
import base64

def dashboard(request):
    """Prikaz glavne kontrolne table i kreiranje novih magacina."""
    if request.method == 'POST':
        w_name = request.POST.get('warehouseName')
        w_type = request.POST.get('warehouseType')
        if w_name:
            Warehouse.objects.create(name=w_name, warehouse_type=w_type)
            return redirect('dashboard')

    parts_warehouses = Warehouse.objects.filter(warehouse_type='parts')
    belts_warehouses = Warehouse.objects.filter(warehouse_type='belts')

    context = {
        'parts_warehouses': parts_warehouses,
        'belts_warehouses': belts_warehouses,
    }
    return render(request, 'dashboard.html', context)

def warehouse_detail(request, id):
    """Prikaz artikala u magacinu sa pretragom i dodavanjem."""
    magacin = get_object_or_404(Warehouse, id=id)
    query = request.GET.get('search')

    if request.method == 'POST':
        Item.objects.create(
            warehouse=magacin,
            part_id_barcode=request.POST.get('part_id_barcode'),
            name=request.POST.get('name'),
            position_on_machine=request.POST.get('position_on_machine'),
            serial_number=request.POST.get('serial_number'),
            map_position=request.POST.get('map_position'),
            quantity=request.POST.get('quantity', 0) or 0,
            min_quantity=request.POST.get('min_quantity', 1) or 1,
            supplier=request.POST.get('supplier'),
            price=request.POST.get('price', 0.00) or 0.00,
            image=request.FILES.get('image')
        )
        return redirect('warehouse_detail', id=id)

    artikli = magacin.items.all()
    if query:
        artikli = artikli.filter(
            Q(part_id_barcode__icontains=query) | 
            Q(name__icontains=query) |
            Q(serial_number__icontains=query)
        )
    
    parts_warehouses = Warehouse.objects.filter(warehouse_type='parts')
    belts_warehouses = Warehouse.objects.filter(warehouse_type='belts')

    context = {
        'magacin': magacin,
        'artikli': artikli,
        'parts_warehouses': parts_warehouses,
        'belts_warehouses': belts_warehouses,
        'query': query,
    }
    return render(request, 'warehouse_detail.html', context)

def delete_item(request, id):
    """Trajno brisanje artikla."""
    artikal = get_object_or_404(Item, id=id)
    magacin_id = artikal.warehouse.id
    artikal.delete()
    return redirect('warehouse_detail', id=magacin_id)

def edit_item(request, id):
    """Izmena podataka o artiklu preko Edit modala."""
    artikal = get_object_or_404(Item, id=id)
    if request.method == 'POST':
        artikal.part_id_barcode = request.POST.get('part_id_barcode')
        artikal.name = request.POST.get('name')
        artikal.position_on_machine = request.POST.get('position_on_machine')
        artikal.serial_number = request.POST.get('serial_number')
        artikal.map_position = request.POST.get('map_position')
        artikal.quantity = request.POST.get('quantity', 0) or 0
        artikal.min_quantity = request.POST.get('min_quantity', 1) or 1
        artikal.supplier = request.POST.get('supplier')
        artikal.price = request.POST.get('price', 0.00) or 0.00
        
        if request.FILES.get('image'):
            artikal.image = request.FILES.get('image')
            
        artikal.save()
        return redirect('warehouse_detail', id=artikal.warehouse.id)
    return redirect('dashboard')

def update_stock(request, id):
    """Brza promena stanja (Plus/Minus) sa razlogom."""
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        mode = request.POST.get('mode')
        amount = int(request.POST.get('amount', 0))
        reason = request.POST.get('reason')

        try:
            artikal = Item.objects.get(part_id_barcode=barcode, warehouse_id=id)
            if mode == 'plus':
                artikal.quantity += amount
            elif mode == 'minus':
                artikal.quantity -= amount
            
            artikal.last_change_reason = reason
            artikal.save()
        except Item.DoesNotExist:
            pass

    return redirect('warehouse_detail', id=id)

def print_cards(request):
    """Generisanje A4 stranice sa karticama i barkodovima za označene artikle."""
    item_ids = request.GET.getlist('items')
    artikli = Item.objects.filter(id__in=item_ids)
    
    cards_data = []
    for artikal in artikli:
        # Generisanje barkoda u memoriji
        buffer = io.BytesIO()
        # Code128 je standardni tip barkoda koji većina čitača podržava
        Code128(artikal.part_id_barcode, writer=ImageWriter()).write(buffer)
        barcode_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        cards_data.append({
            'artikal': artikal,
            'barcode_img': barcode_base64
        })
    
    return render(request, 'print_cards.html', {'cards': cards_data})