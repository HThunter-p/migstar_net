# migstar_net

## Local setup

From the repository root, create and activate a virtual environment, then install
the project dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create the local environment file and generate a Django secret key:

```powershell
Copy-Item migstarn_net\.env.example migstarn_net\.env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set the generated value as `SECRET_KEY` in `migstarn_net\.env` and add any
payment-gateway credentials needed for your environment. Do not commit `.env`.

Run database migrations and start the development server:

```powershell
python migstarn_net\manage.py migrate
python migstarn_net\manage.py runserver
```
