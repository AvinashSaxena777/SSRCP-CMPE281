# SSRCP-CMPE281

## Environment Setup

1. Clone The Repo
2. Create virtual environment
3. Activate virtual environment
4. Install libraries
```
pip install -r requirements.txt
```
5. Run Django makemigrations
```
python manage.py makemigrations
```
6. Run Django migrate
```
python manage.py migrate
```
7. Add UserType record before creating a superuser, run this command in powershell
```
echo "from apps.home.models import UserType; UserType.objects.get_or_create(typeName='SUPER_ADMIN'); UserType.objects.get_or_create(typeName='ADMIN'); UserType.objects.get_or_create(typeName='STAFF')" | python manage.py shell
```
8. Create a superuser
```
python manage.py createsuperuser
```
9. Run application
```
python manage.py runserver
```
10. Login in application with your superuser credentials

## Carla Integration
1. Install Carla (version carla-0.9.15) in local or vm following installation instruction from Resources/Carla_Setup.pdf
2. If using vm, perform execute this ssh tunneling command
```
ssh -f -N -L 2000:localhost:2000 -L 2001:localhost:2001 userName@IPofVM
```
3. Open CarlaFastAPI in new window
4. For CarlaFastAPI, use python 3.7, as carla only supports python3.7
5. Create a virtual environment 
6. Install carla using CARLA whl file
```
pip install CarlaFastAPI\carla-0.9.15-cp37-cp37m-win_amd64.whl
```
7. Run Carla Fast API using
```
uvicorn main:app
```