# 🛍️ eCommerce API

This is a fully functional eCommerce API built with **Django**, **Django REST Framework**, **Token Authentication**, and **Stripe** for payments. It provides endpoints for product listing, user registration, authentication, cart handling, and payment integration.

---

## 🚀 Features

- User registration & authentication (Token-based)
- Product listing & details
- Create, update, delete products (admin only)
- Add to cart / remove from cart
- Create Stripe payment intent
- DRF browsable API & Swagger docs

---

## 📦 Technologies Used

- Python 3.12+
- Django 5.1.6
- Django REST Framework
- drf-spectacular (Swagger Docs)
- Stripe API

---

## 🧰 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ecommerce-api.git
   cd ecommerce-api
   ```

2. **Create virtual environment**

   ```bash
   python -m venv env
   source env/bin/activate   # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Add Stripe API keys to `settings.py` or `.env`**

   ```env
   STRIPE_SECRET_KEY=sk_test_...
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   ```

5. **Apply migrations**

   ```bash
   python manage.py migrate
   ```

6. **Create superuser**

   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

---

## 📑 API Documentation

- **Swagger UI**: [http://127.0.0.1:8000/api/docs/](http://127.0.0.1:8000/api/docs/)
- **Schema**: [http://127.0.0.1:8000/api/schema/](http://127.0.0.1:8000/api/schema/)

---

## 🛒 Core Endpoints

### 🧍 Users

| Method | Endpoint           | Description              |
| ------ | ------------------ | ------------------------ |
| POST   | `/api/usercreate/` | Register user            |
| POST   | `/api/usertoken/`  | Login and get token      |
| GET    | `/api/user/`       | Get current user profile |

---

### 📦 Products

| Method | Endpoint                     | Description              |
| ------ | ---------------------------- | ------------------------ |
| GET    | `/api/products/`             | List all products        |
| GET    | `/api/products/<id>/`        | Retrieve product details |
| POST   | `/api/products/create/`      | Create a product (admin) |
| PUT    | `/api/products/<id>/update/` | Update a product (admin) |
| DELETE | `/api/products/<id>/delete/` | Delete a product (admin) |

---

### 🛍️ Cart

| Method | Endpoint            | Description              |
| ------ | ------------------- | ------------------------ |
| POST   | `/api/cart/add/`    | Add product to cart      |
| POST   | `/api/cart/remove/` | Remove product from cart |
| GET    | `/api/cart/`        | View user cart           |

---

### 💳 Payments

| Method | Endpoint                               | Description                 |
| ------ | -------------------------------------- | --------------------------- |
| POST   | `/api/products/create-payment-intent/` | Create Stripe PaymentIntent |

**Request Body:**

```json
{
  "amount": 5000 // amount in cents (e.g., $50.00)
}
```

**Response:**

```json
{
  "client_secret": "pi_12345_secret_..."
}
```

> 💡 Use this `client_secret` with Stripe.js or your frontend to complete the payment.

---

### 🛡️ Permissions

- `IsAuthenticated` — required for all user-specific endpoints (e.g., cart, wishlist, payments)
- `IsAdminUser` — required for product creation, update, and deletion

---

### 📂 Project Structure

```bash
ecommerce_api/
├── app/
│   ├── users/
│   ├── products/
│   ├── cart/
│   └── ...
├── manage.py
└── requirements.txt
```

---

### 🐞 Common Issues

#### 1. `TypeError: Response.__init__() got an unexpected keyword argument 'status'`

✅ **Fix**: Make sure you're using **DRF's Response**, not Django's HttpResponse.

```python
from rest_framework.response import Response
```

#### 2. `Authentication credentials were not provided.`

✅ **Fix**: Include the token in the headers for any protected route.

```http
Authorization: Token your-auth-token
```

---

### 📬 Contact

For questions, feature requests, or issues, feel free to open an issue or contact the maintainer.

---

### 📝 License

This project is licensed under the **MIT License**.
