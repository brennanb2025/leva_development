from app import app, application

if __name__ == '__main__': #on flask run include: -p 8000 after to run it on port 8000.
    application.run()
    print("main = running")