from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Warehouse, Item
from barcode import Code128
from barcode.writer import ImageWriter
import io, base64

def dashboard(request):
    if request.method == 'POST':
        w_name = request.POST.get('warehouseName')
        w_type = request.POST.get('warehouseType')
        if w_name:
            Warehouse.objects.create(name=w_name, warehouse_type=w_type)
            return redirect('dashboard')
    
    return render(request, 'dashboard.html', {
        'parts_warehouses': Warehouse.objects.filter(warehouse_type='parts'),
        'belts_warehouses': Warehouse.objects.filter(warehouse_type='belts'),
    })

def warehouse_detail(request, id):
    magacin = get_object_or_404(Warehouse, id=id)
    query = request.GET.get('search')

    if request.method == 'POST':
        # Izvlačimo podatke iz forme
        barcode = request.POST.get('part_id_barcode')
        name = request.POST.get('name')
        purpose = request.POST.get('belt_purpose')
        dims = request.POST.get('dimensions')
        
        # AUTOMATIZACIJA: Ako je magacin za kaiševe i naziv je prazan
        if magacin.warehouse_type == 'belts' and not name and purpose:
            name = f"{purpose} ({dims if dims else ''})"

        Item.objects.create(
            warehouse=magacin,
            part_id_barcode=barcode,
            name=name,
            # Polja za kaiševe (Excel podaci)
            belt_purpose=purpose,
            belt_type=request.POST.get('belt_type'),
            thickness_teeth=request.POST.get('thickness_teeth'),
            dimensions=dims,
            open_closed=request.POST.get('open_closed'),
            position_on_machine=request.POST.get('position_on_machine'),
            # Zajednička polja
            unit_of_measure=request.POST.get('unit_of_measure', 'kom'),
            serial_number=request.POST.get('serial_number'),
            map_position=request.POST.get('map_position'),
            supplier=request.POST.get('supplier'),
            # Brojevi (Float zbog metraže)
            quantity=request.POST.get('quantity') or 0,
            min_quantity=request.POST.get('min_quantity') or 1,
            price=request.POST.get('price') or 0.00,
            image=request.FILES.get('image')
        )
        return redirect('warehouse_detail', id=id)
    

    artikli = magacin.items.all()
    if query:
        artikli = artikli.filter(
            Q(part_id_barcode__icontains=query) | 
            Q(name__icontains=query) |
            Q(serial_number__icontains=query) |
            Q(supplier__icontains=query) |
            Q(position_on_machine__icontains=query) | # Ovo je falilo za "Hvataljke"
            Q(belt_purpose__icontains=query) |
            Q(dimensions__icontains=query)
        )
    
    return render(request, 'warehouse_detail.html', {
        'magacin': magacin, 'artikli': artikli, 'query': query,
        'parts_warehouses': Warehouse.objects.filter(warehouse_type='parts'),
        'belts_warehouses': Warehouse.objects.filter(warehouse_type='belts'),
    })

def edit_item(request, id):
    artikal = get_object_or_404(Item, id=id)
    if request.method == 'POST':
        # Standardna polja
        artikal.part_id_barcode = request.POST.get('part_id_barcode')
        artikal.name = request.POST.get('name')
        artikal.position_on_machine = request.POST.get('position_on_machine')
        artikal.serial_number = request.POST.get('serial_number')
        artikal.map_position = request.POST.get('map_position')
        artikal.unit_of_measure = request.POST.get('unit_of_measure')
        artikal.supplier = request.POST.get('supplier')
        artikal.price = request.POST.get('price') or 0.00
        artikal.quantity = request.POST.get('quantity') or 0
        artikal.min_quantity = request.POST.get('min_quantity') or 1
        # Polja za kaiševe
        artikal.belt_purpose = request.POST.get('belt_purpose')
        artikal.belt_type = request.POST.get('belt_type')
        artikal.thickness_teeth = request.POST.get('thickness_teeth')
        artikal.dimensions = request.POST.get('dimensions')
        artikal.open_closed = request.POST.get('open_closed')

        if request.FILES.get('image'):
            artikal.image = request.FILES.get('image')
        artikal.save()
        return redirect('warehouse_detail', id=artikal.warehouse.id)
    
def delete_item(request, id):
    artikal = get_object_or_404(Item, id=id)
    m_id = artikal.warehouse.id
    artikal.delete()
    return redirect('warehouse_detail', id=m_id)

def update_stock(request, id):
    if request.method == 'POST':
        try:
            artikal = Item.objects.get(part_id_barcode=request.POST.get('barcode'), warehouse_id=id)
            amount = float(request.POST.get('amount', 0))
            if request.POST.get('mode') == 'plus': artikal.quantity += amount
            else: artikal.quantity -= amount
            artikal.last_change_reason = request.POST.get('reason')
            artikal.save()
        except Item.DoesNotExist: pass
    return redirect('warehouse_detail', id=id)

def print_cards(request):
    item_ids = request.GET.getlist('items')
    cards_data = []
    for artikal in Item.objects.filter(id__in=item_ids):
        buffer = io.BytesIO()
        Code128(artikal.part_id_barcode, writer=ImageWriter()).write(buffer)
        cards_data.append({'artikal': artikal, 'barcode_img': base64.b64encode(buffer.getvalue()).decode()})
    return render(request, 'print_cards.html', {'cards': cards_data})

def update_stock(request, id):
    """Brza promena stanja (Plus/Minus) - radi i za PCS i za Metre."""
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        mode = request.POST.get('mode')
        reason = request.POST.get('reason')
        
        # Koristimo float umesto int da bi radila metraža (npr. 0.5m)
        try:
            raw_amount = request.POST.get('amount', '0').replace(',', '.') # Menja zarez u tačku ako korisnik pogreši
            amount = float(raw_amount)
        except ValueError:
            amount = 0

        try:
            # Tražimo artikal po barkodu UNUTAR specifičnog magacina
            artikal = Item.objects.get(part_id_barcode=barcode, warehouse_id=id)
            
            if mode == 'plus':
                artikal.quantity += amount
            elif mode == 'minus':
                # Dozvoljavamo da ode u minus ako treba, ili dodaj proveru ovde
                artikal.quantity -= amount
            
            artikal.last_change_reason = reason
            artikal.save()
        except Item.DoesNotExist:
            # Ovde možeš dodati poruku: "Artikal sa tim barkodom nije u ovom magacinu"
            pass

    return redirect('warehouse_detail', id=id)