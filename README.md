# Django E-commerce

Django E-commerce is a full-fledged e-commerce platform built using the Django web framework. It provides a comprehensive set of features for building an online store, including product management, shopping cart, order processing, payment integration, and more.

## Getting Started

### Prerequisites

Before you can run the Django E-commerce application, you need to have the following software installed on your system:

- Python 3.x
- pip package manager

## Installation

1. Clone the repository:

	  git clone https://github.com/Himanshutomar31/django-ecommerce.git

2. Create a virtual environment and activate it:

		python -m venv env
		source env/bin/activate

3. Install the required packages:

		pip install -r requirements.txt
	
4. Run database migrations:

		python manage.py makemigrations
		python manage.py migrate
		
5. Configure SMTP settings for email notifications:

		In order to enable email notifications for order confirmations and password resets, 
		you need to configure the SMTP settings in your `settings.py` file.
		Here are the settings you need to configure:
		
		EMAIL_HOST = '' # Your email provider's SMTP server address
		EMAIL_PORT = 587 # Your email provider's SMTP server port
		EMAIL_HOST_USER = '' # Your email address
		EMAIL_HOST_PASSWORD = '' # Your email password or app-specific password
		EMAIL_USE_TLS = True # Use TLS encryption for SMTP connection

6. Start the development server:

		python manage.py runserver
		
		
You can now access the application at http://localhost:8000/ in your web browser.

## Features

Django E-commerce comes with the following features out of the box:

- Product management: Add, edit, and delete products with images, descriptions, prices, and categories.
- Shopping cart: Add and remove products to the cart, update quantities, and view the cart total.
- Checkout: Enter shipping and billing information, choose a payment method, and place orders.
- Order management: View and process orders from the admin dashboard. [Note: All the functionality has not been developed yet]
- User authentication: Register and log in users, and manage their profiles and addresses.
- Search: Search for products by keyword and category.

## Contributing

Contributions are welcome! If you have any suggestions or bug reports, please create an issue on the GitHub repository.






