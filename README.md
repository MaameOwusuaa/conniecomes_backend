# t4g-cohort5-final-project
# Conniecomes Beauty Salon API

A production-oriented REST API for **Conniecomes Beauty Salon**, built with **FastAPI**, **SQLAlchemy**, **MySQL**, guest shopping, and administrator JWT authentication.

The API supports guest shopping, orders, payments, and salon appointment bookings, with administrator-authenticated management endpoints.



## Table of Contents

* [Features](#features)
* [Technology Stack](#technology-stack)
* [Project Structure](#project-structure)
* [Requirements](#requirements)
* [Installation](#installation)
* [Environment Variables](#environment-variables)
* [Database Setup](#database-setup)
* [Alembic Migrations](#alembic-migrations)
* [Running the API](#running-the-api)
* [API Documentation](#api-documentation)
* [Authentication](#authentication)
* [API Endpoints](#api-endpoints)
* [Bookings](#bookings)
* [Orders](#orders)
* [Shopping Cart](#shopping-cart)
* [Frontend Integration](#frontend-integration)
* [Error Handling](#error-handling)
* [Testing](#testing)
* [Git](#git)
* [Future Improvements](#future-improvements)



# Features

The API provides:

* Guest shopping, checkout, and appointment booking
* Administrator JWT authentication
* Password hashing
* Current administrator information
* Product management
* Product categories
* Shopping cart management
* Order creation and retrieval
* Payment management
* Salon appointment booking
* Appointment updates and cancellation
* Customer contact messages delivered to the administrator dashboard
* Administrator-protected management data
* MySQL database persistence
* SQLAlchemy ORM
* Alembic database migrations
* Repository/service architecture
* Automatic API documentation through Swagger/OpenAPI
* Authentication-protected endpoints



# Technology Stack

## Backend

* Python
* FastAPI
* Uvicorn
* SQLAlchemy
* Pydantic
* Pydantic Settings
* Alembic

## Database

* MySQL
* MySQL Connector/Python

## Authentication & Security

* JWT
* Password hashing with bcrypt
* OAuth2-style bearer authentication

## Development Tools

* VS Code
* Postman
* Swagger/OpenAPI
* Git
* GitHub



# Project Structure

The application follows a layered architecture to keep responsibilities separated.


app/
│
├── core/
│   ├── config.py
│   ├── database.py
│   └── security.py
│
├── dependencies/
│   ├── auth_dependencies.py
│   └── user_dependencies.py
│
├── models/
│   ├── base.py
│   ├── user.py
│   ├── category.py
│   ├── product.py
│   ├── product_variant.py
│   ├── cart.py
│   ├── cart_item.py
│   ├── order.py
│   ├── order_items.py
│   ├── payment.py
│   └── booking.py
│
├── repositories/
│   ├── user_repository.py
│   ├── product_repository.py
│   ├── product_variant_repository.py
│   ├── cart_repository.py
│   ├── order_repository.py
│   ├── payment_repository.py
│   └── booking_repository.py
│
├── schemas/
│   ├── user.py
│   ├── token.py
│   ├── product.py
│   ├── category.py
│   ├── cart.py
│   ├── order.py
│   ├── payment.py
│   └── booking.py
│
├── services/
│   ├── user_service.py
│   ├── product_service.py
│   ├── cart_service.py
│   ├── order_service.py
│   ├── payment_service.py
│   └── booking_service.py
│
└── routers/
    ├── auth.py
    ├── users.py
    ├── products.py
    ├── categories.py
    ├── cart.py
    ├── orders.py
    ├── payments.py
    └── bookings.py


Other project files include:


alembic/
├── versions/
└── env.py

.env
.gitignore
alembic.ini
requirements.txt
main.py
README.md



# Requirements

Before running the API, make sure you have:

* Python 3.10+
* MySQL Server
* MySQL Connector/Python
* Git

A virtual environment is recommended.



# Installation

Clone the repository:


git clone <YOUR_GITHUB_REPOSITORY_URL>


Move into the project:


cd <PROJECT_DIRECTORY>


Create a virtual environment:


python -m venv owusuaa


Activate it on macOS/Linux:


source owusuaa/bin/activate


Install the dependencies:


pip install -r requirements.txt




# Environment Variables

Create a `.env` file in the project root.

Example:

env
DATABASE_URL=mysql+mysqlconnector://USERNAME:PASSWORD@localhost:3306/DATABASE_NAME

SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Booking status notifications (SMTP STARTTLS, usually port 587)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USERNAME=your-smtp-username
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM=appointments@example.com
SMTP_USE_TLS=true

# Twilio SMS
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_FROM_NUMBER=


Do **not** commit `.env` to GitHub.

The `.env` file should be included in `.gitignore`:

gitignore
.env


Booking status changes trigger an email and SMS to the contact details saved
with the booking. Configure both providers above to enable both channels. If
delivery fails or provider settings are incomplete, the status remains updated
and the admin dashboard reports which notification was not sent; details are
written to the backend log. Store real credentials only in the untracked
`.env` file or your deployment's secret manager.



# Database Setup

Create the MySQL database:

sql
CREATE DATABASE conniecomes_db;


The API uses SQLAlchemy to communicate with MySQL.

The database connection is configured through the application's settings rather than hard-coding credentials into the source code.

The connection follows this format:


mysql+mysqlconnector://USERNAME:PASSWORD@HOST:PORT/DATABASE


Example:


mysql+mysqlconnector://root:password@localhost:3306/conniecomes_db




# Alembic Migrations

Alembic is used to manage database schema changes.

After creating or modifying a SQLAlchemy model, create a migration:


alembic revision --autogenerate -m "description of change"


Review the generated migration before applying it.

Apply migrations:


alembic upgrade head


Check the current migration:


alembic current


View migration history:


alembic history


To downgrade one migration:


alembic downgrade -1


The database schema should be kept synchronized with the SQLAlchemy models through Alembic rather than manually modifying tables whenever possible.



# Running the API

Start the FastAPI development server with:


uvicorn app.main:app --reload --port 8000


The API will normally be available at:


http://127.0.0.1:8000




# API Documentation

FastAPI automatically provides interactive API documentation.

## Swagger UI


http://127.0.0.1:8000/docs


Swagger allows you to:

* View available endpoints
* Inspect request schemas
* Test endpoints
* Authenticate using a bearer token
* Inspect API responses
* Test protected routes

## ReDoc


http://127.0.0.1:8000/redoc




# Authentication

Only administrators use JWT bearer authentication. Customers can shop, check out, and book appointments without an account.

An administrator signs in:

http
POST /auth/admin/login


The admin dashboard uses the returned JWT for protected management requests.


A successful login returns:

json
{
    "access_token": "JWT_TOKEN",
    "token_type": "bearer"
}


The frontend stores the access token and sends it with protected requests:

http
Authorization: Bearer JWT_TOKEN


Protected management endpoints require an authenticated administrator.



# Authentication Endpoints

## Administrator Login

http
POST /auth/admin/login


Authenticates the administrator account.

Example request:

json
{
    "email": "admin@example.com",
    "password": "your-admin-password"
}


Successful response:

http
200 OK




## Administrator Login Response

http
POST /auth/admin/login


Authenticates the administrator.

Example request:

json
{
    "email": "admin@example.com",
    "password": "password123"
}


Successful response:

json
{
    "access_token": "JWT_TOKEN",
    "token_type": "bearer"
}




# User Endpoints

## Get Current User

http
GET /users/me


Requires authentication.

Header:

http
Authorization: Bearer JWT_TOKEN


Example response:

json
{
    "id": 1,
    "first_name": "Maame",
    "last_name": "Ofori",
    "email": "customer@example.com",
    "is_admin": false,
    "is_active": true,
    "created_at": "2026-08-18T10:00:00",
    "updated_at": "2026-08-18T10:00:00"
}


This endpoint is used by the customer dashboard to retrieve the currently authenticated customer's information.



# Product Endpoints

Product endpoints provide access to the salon's hair and beauty products.

Typical product operations include:


GET     /products
GET     /products/{product_id}
GET     /products/{product_id}/variants
POST    /products
PUT     /products/{product_id}
DELETE  /products/{product_id}
POST    /products/{product_id}/variants
GET     /products/{product_id}/variants/manage
PUT     /products/{product_id}/variants/{variant_id}
DELETE  /products/{product_id}/variants/{variant_id}


Products can contain information such as:

* Product name
* Description
* Price
* Stock quantity
* Image URL
* Category
* Color/length variants with separate images, prices and stock

Administrative operations should be protected from unauthorized customers.

Product synchronization and all product/category write endpoints require an
administrator bearer token. Product images uploaded through the admin dashboard
are stored under `backend/uploads/` and served from `/uploads/`.

Variant retrieval is public. Variant creation, editing, deletion and inventory
updates require administrator authorization. Cart items accept `variant_id` and
remain distinct by product/variant combination. Order items snapshot the selected
color, length and unit price.



# Category Endpoints

Categories organize products within the store.

Typical operations include:


GET     /categories
GET     /categories/{category_id}
POST    /categories
PUT     /categories/{category_id}
DELETE  /categories/{category_id}




# Shopping Cart

The shopping cart allows authenticated customers to add products before checkout.

Typical operations include:


GET     /cart
POST    /cart/items
PUT     /cart/items/{item_id}
DELETE  /cart/items/{item_id}


Cart data is associated with the authenticated user.

The cart response includes product information such as:

json
{
    "id": 1,
    "user_id": 1,
    "cart_items": []
}


Cart items contain:

* Product ID
* Quantity
* Product details
* Product price
* Stock quantity
* Product image



# Orders

Orders are associated with the authenticated customer.

## Create Order

http
POST /orders


The API creates an order for the current user's cart.

## Get Customer Orders

http
GET /orders


Returns the authenticated customer's orders.

Example response:


[
    {
        "id": 1,
        "user_id": 1,
        "total_amount": 450.00,
        "status": "pending",
        "order_items": [],
        "created_at": "2026-08-18T12:00:00",
        "updated_at": "2026-08-18T12:00:00"
    }
]


## Get One Order

GET /orders/{order_id}


Returns a specific order belonging to the authenticated customer.



# Bookings

The booking system allows authenticated customers to schedule salon appointments.

## Create Booking


POST /bookings


Example:


{
    "service": "Frontal Installation",
    "booking_date": "2026-08-28T10:00:00",
    "notes": "Please use a natural-looking finish."
}


The `booking_date` contains both the date and time.

The frontend can display them separately even though they are stored as one `datetime` value.



## Get Customer Bookings


GET /bookings


Returns bookings belonging to the currently authenticated customer.

Example response:

[
    {
        "id": 1,
        "user_id": 1,
        "service": "Frontal Installation",
        "booking_date": "2026-08-28T10:00:00",
        "notes": "Natural-looking finish.",
        "status": "pending",
        "created_at": "2026-08-18T12:00:00",
        "updated_at": "2026-08-18T12:00:00"
    }
]




## Get One Booking


GET /bookings/{booking_id}


Returns a specific booking belonging to the authenticated customer.



## Update Booking


PUT /bookings/{booking_id}


Example:


{
    "service": "Hair Braiding",
    "booking_date": "2026-08-29T14:00:00",
    "notes": "Medium knotless braids",
    "status": "confirmed"
}




## Delete Booking


DELETE /bookings/{booking_id}


Deletes a customer's booking.

Successful response:

204 No Content




# Payments

The payment system is designed to support customer checkout and payment processing.

Payment functionality can support:

* Order association
* Payment status
* Payment reference
* Payment method
* Payment verification

Supported payment methods may include:

* Card
* Mobile Money

Payment processing should be handled securely through the selected payment provider. Sensitive card information should never be stored directly in the application's database.



# Customer Dashboard

The frontend customer dashboard consumes several authenticated API endpoints.


                     Customer Dashboard
                             |
            +-+-+
            |                |                |
            ↓                ↓                ↓
       /users/me         /orders         /bookings
            |                |                |
        Profile           Orders         Appointments
            |                |                |
            +-+-+
                             |
                            /cart
                             |
                         Cart Items


The dashboard can therefore display:

* Customer name
* Customer email
* Number of orders
* Recent orders
* Upcoming appointments
* Appointment history
* Cart item count

A newly registered customer does **not** need an existing booking or order for the dashboard to appear. The dashboard loads the customer's available data and displays an appropriate empty state when no records exist.



# API Security

Protected endpoints require a valid JWT.

The API uses the authenticated user rather than accepting a customer ID directly from the frontend.

For example:


current_user: User = Depends(get_current_user)


This prevents customers from simply changing a `user_id` in a request to access another customer's information.

Customer-specific resources such as:

* Cart
* Orders
* Bookings
* Profile

are therefore associated with the authenticated account.



# Error Handling

The API uses appropriate HTTP status codes.

Common responses include:

| Status Meaning                                      
| `200`  | Request successful                           
| `201`  | Resource created                             
| `204`  | Resource deleted successfully                
| `400`  | Invalid request                              
| `401`  | Authentication required/invalid credentials  
| `404`  | Resource not found                           
| `409`  | Resource conflict, such as an existing email 
| `422`  | Validation error                             

FastAPI and Pydantic automatically validate request bodies and return validation errors when submitted data does not meet the schema requirements.



# Architecture

The project uses separation of concerns.

## Routers

Routers define HTTP endpoints and handle HTTP-specific concerns.


router → service → repository → database


## Services

Services contain business logic.

For example, the booking service handles booking creation and validation.

## Repositories

Repositories handle database operations through SQLAlchemy.

## Models

SQLAlchemy models represent database tables and relationships.

## Schemas

Pydantic schemas define:

* Request validation
* Response serialization
* API contracts

This structure makes the application easier to maintain, test, and extend.



# Database Relationships

The application uses SQLAlchemy relationships between entities.

Examples include:


User
 ├── Orders
 ├── Cart
 └── Bookings

Cart
 └── CartItems
       └── Product

Order
 ├── OrderItems
 └── Payment

Product
 └── Category


These relationships allow the API to associate customer activity with the correct database records.


# Frontend Integration

## Admin Dashboard

Open `pages/admin.html` while the frontend is served from an allowed CORS origin.
The dashboard requires a signed-in account whose database row has `is_admin = 1`.
Public registration always creates a non-admin account; promote a trusted account
directly through a secured database session rather than adding a public role-change
endpoint.

For a trusted account that has already been created, an authorized database
operator can grant access with:

```sql
UPDATE users SET is_admin = 1 WHERE email = 'admin@example.com';
```

Apply the latest database migration before starting the API. If the old
`owusuaa` environment points to a different machine, create a local environment:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
alembic upgrade head
python -m app.create_admin
uvicorn app.main:app --reload --port 8000
```

The bootstrap command prompts for the administrator password without echoing it
and stores only a salted password hash. The configured email defaults to
`otrish95@gmail.com`; change it only through the backend `ADMIN_EMAIL` environment
setting. Admin credentials cannot be created through public registration or
customer sign-in.

The migrations add the service catalog, optional product length, product variants,
variant images and nullable cart/order references. The dashboard uses these
administrator-only endpoints:

```text
POST   /admin/uploads
GET    /admin/bookings
PATCH  /admin/bookings/{booking_id}
GET    /admin/orders
PATCH  /admin/orders/{order_id}/delivery-status
DELETE /admin/transactions/cleared
GET    /admin/customers
GET    /admin/customers/{customer_id}
GET    /admin/contact-messages
GET    /admin/analytics?period=daily|weekly|monthly|quarterly|yearly
POST   /contact-messages
POST   /services
PUT    /services/{service_id}
DELETE /services/{service_id}
```

Revenue includes only payments confirmed as `successful` by the payment provider.
Paid orders include an administrator-editable delivery status: `pending`,
`preparing`, `out_for_delivery`, `delivered`, or `delivery_failed`. Applying the
latest migration adds this field to existing orders, defaulting them to
`pending`.
Contact messages submitted through the storefront are saved in the database and
shown in the administrator dashboard alongside bookings and successful product
purchases. Customer detail responses include linked orders, payment transactions,
sales, and bookings. Run `alembic upgrade head` to create the contact-message table.
Uploaded images are stored on the API server filesystem; production deployments
should use persistent storage or an object-storage service.

Products, variants, variant images, prices, and stock are served from MySQL through
the product API. The storefront does not keep a separate browser product catalog.

The frontend communicates with the API using HTTP requests.

Example:


const token = localStorage.getItem("access_token");

const response = await fetch(
    `${API_BASE_URL}/users/me`,
    {
        method: "GET",
        headers: {
            "Authorization": `Bearer ${token}`,
            "Content-Type": "application/json"
        }
    }
);


The admin frontend stores the JWT after successful administrator login and sends it with protected API requests.


# CORS

When the frontend and backend run on different origins during development, the API must allow the frontend origin through FastAPI's CORS middleware.

Example:


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


For production, replace development origins with the actual frontend domain instead of allowing arbitrary origins.



# Testing

The API can be tested using:

* Swagger UI
* Postman
* Automated tests

Swagger:


http://127.0.0.1:8000/docs


For protected endpoints:

1. Log in through `/auth/admin/login`.
2. Copy the returned `access_token`.
3. Authenticate in Swagger using the bearer token.
4. Test the protected endpoints.



# Git and Environment Security

Sensitive files should not be committed to GitHub.

The following should remain private:

.env
database passwords
SECRET_KEY
payment API keys
third-party API credentials


The `.gitignore` should include:


.env
__pycache__/
*.pyc
.venv/
owusuaa/


If `.env` was previously tracked by Git, remove it from tracking:


git rm --cached .env


Then commit the change:


git add .gitignore
git commit -m "Remove environment variables from Git tracking"


If secrets were exposed publicly, rotate those credentials.



# Development Workflow

A typical development workflow is:


1. Activate virtual environment
        ↓
2. Start MySQL
        ↓
3. Run Alembic migrations
        ↓
4. Start FastAPI
        ↓
5. Test endpoints with Swagger/Postman
        ↓
6. Connect frontend
        ↓
7. Test complete user flow


Start the server:


uvicorn main:app --reload

Run migrations:


alembic upgrade head




# Example Customer Flow

A typical customer journey is:

Register
   ↓
Login
   ↓
Receive JWT
   ↓
View Dashboard
   ↓
Browse Products
   ↓
Add Product to Cart
   ↓
Checkout
   ↓
Make Payment
   ↓
Order Created
   ↓
Inventory Updated
   ↓
View Order in Dashboard

For salon services:

Login
   ↓
View Dashboard
   ↓
Book Appointment
   ↓
POST /bookings
   ↓
Booking Saved to MySQL
   ↓
GET /bookings
   ↓
Appointment Appears on Dashboard


# Future Improvements

Potential future improvements include:

* Admin dashboard
* Product image uploads
* Inventory management interface
* Advanced appointment scheduling
* Appointment availability checking
* Email notifications
* SMS notifications
* Payment-provider webhook handling
* Order tracking
* Password reset
* Email verification
* Refresh tokens
* Rate limiting
* Automated test coverage
* Production deployment
* Docker containerization


# Project Status

The Conniecomes Beauty Salon API provides the backend foundation for the salon's e-commerce and appointment-booking platform.

The API currently includes authentication, users, products, categories, carts, orders, payments, and bookings, with MySQL persistence and Alembic-managed database migrations.
