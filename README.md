# Mondi - Warehouse Management System (WMS)

Mondi is a Warehouse Management System (WMS) built using the Django web framework. It provides an intuitive interface for managing different types of warehouses, tracking inventory items, updating stock levels, and organizing parts efficiently.

## Features

- **Warehouse Management:**
  - Create and manage different types of warehouses (e.g., 'parts' / Rezervni Delovi, and 'belts' / Kaiševi).
  - View all warehouses from a central dashboard.
- **Item Management:**
  - Add new items to specific warehouses with detailed attributes including Part ID/Barcode, Name, Position on Machine, Serial Number, Map Position, Supplier, Price, and Images.
  - Edit and delete existing items.
- **Inventory Control:**
  - Track current quantities and set minimum quantity thresholds for stock alarms.
  - Update stock levels (increase or decrease quantity) and record reasons for changes.
- **Search & Filtering:**
  - Search items within a warehouse by Part ID/Barcode, Name, or Serial Number to quickly find specific parts.
- **Dashboard & User Interface:**
  - Simple and interactive dashboard for an overview of all warehouses and their items.
  - Sidebar navigation to easily switch between different warehouses.

## Project Structure

- **`core/`**: The main Django application directory containing the business logic, models (`Warehouse`, `Item`), views, and URL routings for the WMS.
- **`mondi_wms/`**: The Django project configuration directory containing settings, main URL declarations, and WSGI/ASGI configurations.
- **`templates/`**: Directory containing HTML templates (`base.html`, `dashboard.html`, `warehouse_detail.html`) used to render the frontend views.
- **`media/`**: Directory for user-uploaded media files, such as images of the items stored in the warehouses.
- **`manage.py`**: A command-line utility that lets you interact with this Django project in various ways (e.g., running the development server, making migrations).
- **`db.sqlite3`**: The SQLite database file containing all the application data.
