# Poultry Sync Assessment - Multi-Tenant Ordering System

A Django-based multi-tenant application where each company manages its own orders and products. This system implements soft-deletion, role-based access control, and comprehensive order management with real-time stock tracking.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
  - [Local Installation](#local-installation)
  - [Docker Installation](#docker-installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [User Roles](#user-roles)
  - [API Endpoints](#api-endpoints)
  - [Web Interface](#web-interface)
- [File Structure & Logic](#file-structure--logic)
- [Database Models](#database-models)
- [Business Logic](#business-logic)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

This is a multi-tenant ordering system built with Django REST Framework that allows multiple companies to manage their products and orders independently. Each company has its own isolated data, and users are assigned roles (Admin, Operator, Viewer) with different permission levels.

### Key Concepts

- **Multi-Tenancy**: Each company has completely isolated data
- **Role-Based Access Control**: Three user roles with different permissions
- **Soft Deletion**: Products are marked as inactive instead of being deleted
- **Order Management**: Orders start as pending and can be updated to success/failed
- **Stock Management**: Automatic stock deduction when orders are fulfilled

## ✨ Features

### Core Features
- ✅ Multi-tenant architecture with company-based data isolation
- ✅ Role-based access control (Admin, Operator, Viewer)
- ✅ Product management (CRUD operations)
- ✅ Order management with status tracking
- ✅ Stock management with automatic deduction
- ✅ Soft deletion for products
- ✅ Order confirmation email logging
- ✅ CSV export for orders
- ✅ Real-time product and order tracking
- ✅ Beautiful, responsive web interface

### User Role Permissions

| Feature | Admin | Operator | Viewer |
|---------|-------|----------|--------|
| Add Product | ✅ | ✅ | ✅ |
| Edit Product | ✅ | ✅ | ❌ |
| Delete Product | ✅ | ✅ | ❌ |
| Create Order | ✅ | ❌ | ❌ |
| Edit Today's Orders | ✅ | ✅ | ❌ |
| Edit Other Orders | ✅ | ❌ | ❌ |
| View Orders | ✅ | ✅ | ✅ |
| Export Orders | ✅ | ✅ | ❌ |

## 🛠 Technology Stack

- **Backend Framework**: Django 4.2.7
- **API Framework**: Django REST Framework 3.16.1
- **Database**: SQLite (development) / MySQL (production ready)
- **Authentication**: Token Authentication & Session Authentication
- **Frontend**: Bootstrap 5, Vanilla JavaScript
- **API Documentation**: drf-spectacular (Swagger/OpenAPI)
- **Python Version**: 3.11+

## 📁 Project Structure

```
Poultry-Sync-Assessment/
│
├── api/                          # Main application directory
│   ├── __init__.py              # Package initialization
│   ├── models.py                # Database models (Company, User, Product, Order)
│   ├── views.py                 # API views and business logic
│   ├── serializers.py           # DRF serializers for API
│   ├── urls.py                  # URL routing for API endpoints
│   ├── admin.py                 # Django admin configuration
│   ├── signals.py               # Django signals (if any)
│   ├── apps.py                  # App configuration
│   ├── tests.py                 # Unit tests
│   ├── migrations/              # Database migrations
│   │   ├── 0001_initial.py
│   │   └── 0002_update_user_roles_and_company.py
│   └── templates/
│       └── index.html           # Main web interface template
│
├── Poultry_Sync_Assessment/     # Django project settings
│   ├── __init__.py
│   ├── settings.py              # Django settings and configuration
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI configuration
│   └── asgi.py                  # ASGI configuration
│
├── logs/                        # Application logs
│   └── order_confirmations.log  # Order confirmation emails (simulated)
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── .dockerignore                # Docker ignore file
├── db.sqlite3                   # SQLite database (development)
└── README.md                    # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Docker (optional, for containerized deployment)

### Local Installation

#### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Poultry-Sync-Assessment
```

#### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv env
env\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv env
source env/bin/activate
```

#### Step 3: Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Step 4: Run Migrations

```bash
python manage.py migrate
```

#### Step 5: Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user. Note: You'll need to create a Company first in the admin panel, then assign it to the user.

#### Step 6: Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000`

### Docker Installation

#### Option 1: Using Docker Compose (Recommended)

**Step 1: Start Services**
```bash
docker-compose up -d
```

**Step 2: Run Migrations**
```bash
docker-compose exec web python manage.py migrate
```

**Step 3: Create Superuser**
```bash
docker-compose exec web python manage.py createsuperuser
```

**Step 4: Access Application**
Open your browser and navigate to `http://localhost:8000`

**Step 5: Stop Services**
```bash
docker-compose down
```

#### Option 2: Using Dockerfile Directly

**Step 1: Build Docker Image**
```bash
docker build -t poultry-sync .
```

**Step 2: Run Container**
```bash
docker run -d -p 8000:8000 --name poultry-sync poultry-sync
```

**Step 3: Access Application**
Open your browser and navigate to `http://localhost:8000`

**Step 4: Create Superuser (Inside Container)**
```bash
docker exec -it poultry-sync python manage.py createsuperuser
```

## ⚙️ Configuration

### Environment Variables

For production, create a `.env` file:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=mysql://user:password@localhost/dbname
```

### Database Configuration

The default configuration uses SQLite. For production, update `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```

## 📖 Usage

### User Roles

#### Admin
- Full access to all features
- Can create, edit, and delete products
- Can create and edit any order
- Can export orders
- Can manage product status (activate/deactivate)

#### Operator
- Can add, edit, and delete products
- Can edit orders created today (regardless of creator)
- Cannot create new orders
- Can export orders
- Cannot activate/deactivate products (only admins)

#### Viewer
- Can only view products and orders
- Cannot create, edit, or delete anything
- Read-only access

### API Endpoints

#### Authentication
- `POST /api/auth/token/` - Get authentication token
- `POST /api/login/` - User login
- `POST /api/logout/` - User logout

#### Products
- `GET /api/products/` - List active products (company-scoped)
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Retrieve product details
- `PATCH /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Soft-delete product
- `DELETE /api/products/bulk-delete/?ids=id1&ids=id2` - Bulk soft-delete

#### Orders
- `GET /api/orders/` - List orders (company-scoped)
- `POST /api/orders/` - Create order(s) (admin only)
  - Supports single order: `{"product": "uuid", "quantity": 10}`
  - Supports multiple orders: `[{"product": "uuid", "quantity": 10}, ...]`
- `GET /api/orders/{id}/` - Retrieve order details
- `PATCH /api/orders/{id}/` - Update order
- `GET /api/orders/export/` - Export orders as CSV

### Web Interface

#### Main Page (`/`)
- Product creation form
- Products table with actions
- Orders table with export functionality
- Real-time updates

#### Features:
- **Product Management**: Create, edit, delete products
- **Order Management**: Create orders (admin), edit orders, view order history
- **Status Tracking**: Visual status indicators for products and orders
- **Export**: Download orders as CSV file
- **Filtering**: Toggle to show/hide inactive products

## 📄 File Structure & Logic

### `api/models.py`

Contains all database models:

#### `Company`
- **Purpose**: Represents a tenant/company
- **Fields**: `id` (UUID), `name`, `created_at`
- **Logic**: Each user belongs to exactly one company

#### `CustomUser` (extends AbstractUser)
- **Purpose**: Custom user model with company and role
- **Fields**: `company` (ForeignKey), `role` (admin/operator/viewer)
- **Properties**: `is_admin`, `is_operator`, `is_viewer`
- **Logic**: Users must belong to a company. Role determines permissions.

#### `Product`
- **Purpose**: Represents a product in inventory
- **Fields**: 
  - `id` (UUID), `name`, `price`, `stock`
  - `is_active` (for soft deletion)
  - `company` (ForeignKey), `created_by` (ForeignKey)
  - `created_at` (immutable), `last_updated_at`
- **Methods**:
  - `soft_delete()`: Marks product as inactive
  - `can_be_ordered(quantity)`: Checks if product can be ordered

#### `Order`
- **Purpose**: Represents an order
- **Fields**:
  - `id` (UUID), `company`, `product`, `quantity`
  - `status` (pending/success/failed)
  - `created_by`, `created_at` (immutable)
  - `shipped_at` (set when status = success)
- **Methods**:
  - `can_user_edit(user)`: Checks if user can edit order
    - Admin: Can edit any order
    - Operator: Can edit orders created today
  - `validate_stock()`: Validates stock availability

### `api/views.py`

Contains all view logic and API endpoints:

#### Key Functions:

**`_log_order_confirmation(order)`**
- Logs order confirmation to `logs/order_confirmations.log`
- Simulates email sending with order details

**`index(request)`**
- Renders main web interface
- Handles product creation via POST
- Returns products and orders for user's company

#### ViewSets:

**`ProductViewSet`**
- Handles product CRUD operations
- `get_queryset()`: Returns active products for list, all products for other actions
- `perform_destroy()`: Soft-deletes product (sets is_active=False)
- `bulk_delete()`: Bulk soft-delete action
- Permissions: All company members can create, admins/operators can edit/delete

**`OrderViewSet`**
- Handles order CRUD operations
- `create()`: Only admins can create orders
  - Validates product is active
  - Checks stock availability
  - Creates order with PENDING status
- `update()`: 
  - Admins can edit any order
  - Operators can edit orders created today
  - When status changes to SUCCESS:
    - Deducts stock
    - Sets shipped_at
    - Logs confirmation email
- `export()`: Exports orders as CSV

#### API Views:

**`create_product(request)`**
- Creates a new product
- All authenticated users can create products

**`create_order(request)`**
- Creates a new order
- Only admins can create orders
- Validates stock and product status

**`toggle_product_active(request, pk)`**
- Toggles product active status
- Only admins can use this

### `api/serializers.py`

DRF serializers for API serialization/deserialization:

#### `UserSerializer`
- Serializes user data
- Includes company name as read-only field

#### `ProductSerializer`
- Serializes product data
- Fields: id, name, price, stock, is_active, created_at
- `created_at` is read-only

#### `OrderSerializer`
- Serializes order data
- Includes product name as read-only field
- `validate()`: 
  - For creation: Validates admin can create, product is active, stock available
  - For update: Validates product belongs to company
- `update()`: Handles status change to SUCCESS
  - Deducts stock when status becomes SUCCESS
  - Sets shipped_at timestamp

### `api/urls.py`

URL routing configuration:

- Registers ViewSets with DRF router
- Defines custom endpoints:
  - `/api/orders/export/` - Order export
  - `/api/products/bulk-delete/` - Bulk product deletion
  - `/api/products/{pk}/delete/` - Single product deletion
  - `/api/products/create/` - Product creation
  - `/api/orders/create/` - Order creation

### `api/admin.py`

Django admin configuration:

#### `ProductAdmin`
- List display: name, price, stock, company, created_by, is_active
- Filters: company, is_active
- Bulk action: Mark selected products as inactive
- Data isolation: Users only see their company's products

#### `OrderAdmin`
- List display: id, product, company, quantity, status, created_at, created_by
- Filters: company, status
- Action: Export orders as CSV
- Data isolation: Users only see their company's orders

#### `CompanyAdmin`
- List display: name, created_at
- Data isolation: Non-superusers only see their own company

#### `CustomUserAdmin`
- Extends Django's UserAdmin
- Adds company and role fields
- Data isolation: Users only see their company's users

### `api/templates/index.html`

Main web interface template:

#### Structure:
1. **Navigation Bar**: User info, logout
2. **Product Creation Form**: Add new products
3. **Products Table**: 
   - Shows all products (with toggle for inactive)
   - Actions: Order (admin), Edit (admin/operator), Delete (admin/operator)
4. **Orders Table**:
   - Shows all orders for company
   - Actions: Edit (admin/operator), Export CSV (admin/operator)

#### Modals:
- **Order Modal**: Create new orders
- **Edit Product Modal**: Edit product details
- **Delete Product Modal**: Confirm product deletion
- **Edit Order Modal**: Edit order details

#### JavaScript Functions:
- Form submissions with AJAX
- Modal handling
- Alert notifications
- Real-time validation

### `Poultry_Sync_Assessment/settings.py`

Django project settings:

#### Key Configurations:

**INSTALLED_APPS**
- Django core apps
- `rest_framework` - API framework
- `rest_framework.authtoken` - Token authentication
- `drf_spectacular` - API documentation
- `api` - Main application

**AUTH_USER_MODEL**
- Set to `api.CustomUser` for custom user model

**REST_FRAMEWORK**
- Authentication: Token & Session
- Permissions: IsAuthenticated by default
- Pagination: PageNumberPagination (10 per page)
- Schema: drf-spectacular for OpenAPI

**DATABASES**
- Default: SQLite (development)
- Can be changed to PostgreSQL for production

## 🔄 Business Logic

### Order Lifecycle

1. **Creation** (Admin only)
   - Order created with status: PENDING
   - Stock is checked but NOT deducted
   - Product must be active

2. **Update to SUCCESS**
   - Stock is deducted from product
   - `shipped_at` timestamp is set
   - Confirmation email is logged to file

3. **Update to FAILED**
   - Order marked as failed
   - No stock deduction
   - No email sent

### Product Soft Deletion

- Products are never hard-deleted
- `is_active` flag is set to `False`
- Inactive products:
  - Don't appear in API list endpoint
  - Can still be viewed in web interface (with toggle)
  - Cannot be ordered
  - Can be reactivated by admins

### Data Isolation

- All queries are filtered by `company`
- Users can only see their company's data
- API endpoints automatically scope to user's company
- Admin interface filters by company

### Stock Management

- Stock is checked when order is created
- Stock is deducted when order status changes to SUCCESS
- If stock is insufficient, order cannot be created
- Stock cannot go negative

## 🧪 Testing

### Run Tests

```bash
python manage.py test
```

### Test Specific App

```bash
python manage.py test api
```

### Create Test Data

You can use Django admin or create a management command to populate test data.

## 🚢 Deployment

### Production Checklist

1. **Security Settings**
   - Set `DEBUG = False`
   - Update `SECRET_KEY` (use environment variable)
   - Configure `ALLOWED_HOSTS`
   - Enable HTTPS
   - Set secure cookie flags

2. **Database**
   - Use PostgreSQL instead of SQLite
   - Set up database backups
   - Configure connection pooling

3. **Static Files**
   - Run `python manage.py collectstatic`
   - Configure static file serving (Nginx, AWS S3, etc.)

4. **WSGI Server**
   - Use Gunicorn or uWSGI
   - Configure reverse proxy (Nginx)

5. **Environment Variables**
   - Store sensitive data in environment variables
   - Use `.env` file or secrets management

### Example Production Settings

```python
DEBUG = False
ALLOWED_HOSTS = ['yourdomain.com']
SECRET_KEY = os.environ.get('SECRET_KEY')
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        # ... production database config
    }
}
```

## 🐛 Troubleshooting

### Common Issues

#### Issue: Migration errors
**Solution**: 
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Issue: Cannot delete inactive products
**Solution**: Ensure the product exists in your company and you have admin/operator permissions.

#### Issue: Orders not showing
**Solution**: Check that orders belong to your company and you're logged in.

#### Issue: Permission denied errors
**Solution**: Verify your user role and company assignment in Django admin.

#### Issue: CSRF token errors
**Solution**: Ensure CSRF token is included in forms and API requests.

### Debug Mode

For development, ensure `DEBUG = True` in `settings.py` to see detailed error messages.

## 📝 License

This project is part of an assessment and is provided as-is.

## 👥 Support

For issues or questions, please refer to the project documentation or contact the development team.

---

**Built with ❤️ using Django and Django REST Framework**

