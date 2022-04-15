run:
	python manage.py runserver 0.0.0.0:8000
migrate:
	python manage.py makemigrations
	python manage.py migrate
lint:
	isort ./ && flake8 ./
packages:
	pip install -r ./requirements/dev.txt
superuser:
	python manage.py createsuperuser
files:
	python manage.py collectstatic --no-input