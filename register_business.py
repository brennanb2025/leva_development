from app import db
from app.input_sets.models import Business

def register_new_business():
    name = input("Business name: ")
    name = str(name)
    num_employees_max = input("Number of employees maximum: ")
    num_employees_max = int(num_employees_max)
    register_business_from_inputs(name=name,number_employees_maximum=num_employees_max)

def register_business_from_inputs(name, number_employees_maximum):
    b = Business(name=name, number_employees_maximum=number_employees_maximum, number_employees_currently_registered=0)
    db.session.add(b)
    db.session.commit()
    print("Success!")

if __name__ == '__main__':
    register_new_business()