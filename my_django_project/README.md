# My Django Project

This is a Django project for managing "vigencia_plan" data related to companies. The project includes functionalities for displaying, editing, and managing plans.

## Project Structure

```
my_django_project
├── my_app
│   ├── migrations
│   ├── static
│   ├── templates
│   │   ├── empresas
│   │   │   ├── vigencia_planes.html
│   │   │   └── editar_vigencia_plan.html
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── my_django_project
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
└── README.md
```

## Features

- **Manage Companies and Plans**: Users can view and manage the vigencia_plan data associated with different companies.
- **Edit Functionality**: Users can edit existing vigencia_plan entries through a dedicated form.
- **Form Validation**: The application includes form validation to ensure data integrity.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd my_django_project
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Apply migrations:
   ```
   python manage.py migrate
   ```

4. Run the development server:
   ```
   python manage.py runserver
   ```

5. Access the application at `http://127.0.0.1:8000/`.

## Usage

- Navigate to the "Empresas Vigentes" section to view the list of companies and their plans.
- Click the "Edit" button next to a plan to modify its details.
- Fill out the form and submit to save changes.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for details.