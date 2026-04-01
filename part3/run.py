from app import create_app
from app.services import facade

app = create_app()

def seed_data():
    with app.app_context():
        # 1. Création de l'utilisateur Admin (si pas déjà fait)
        admin_email = "admin@hbnb.com"
        admin = facade.get_user_by_email(admin_email)
        if not admin:
            admin = facade.create_user({
                "first_name": "Admin",
                "last_name": "HBnB",
                "email": admin_email,
                "password": "password123",
                "is_admin": True
            })
            print("✅ User Admin créé.")

        # 2. Création de quelques Places de test
        # On vérifie si la liste est vide pour ne pas dupliquer à chaque reboot
        existing_places = facade.get_all_places()
        if not existing_places:
            places_to_create = [
                {
                    "title": "Cozy Apartment",
                    "description": "A nice place in the heart of the city.",
                    "price": 10.0,
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "owner_id": admin.id
                },
                {
                    "title": "Luxury Villa",
                    "description": "Perfect for summer vacations with a pool.",
                    "price": 50.0,
                    "latitude": 43.7102,
                    "longitude": 7.2620,
                    "owner_id": admin.id
                },
                {
                    "title": "Cheap Room",
                    "description": "Small but functional room for students.",
                    "price": 100.0,
                    "latitude": 45.7640,
                    "longitude": 4.8357,
                    "owner_id": admin.id
                }
            ]

            for p_data in places_to_create:
                facade.create_place(p_data)
            
            print(f"✅ {len(places_to_create)} places créées en mémoire.")
        else:
            print(f"ℹ️ {len(existing_places)} places déjà présentes.")

if __name__ == '__main__':
    seed_data()
    app.run(debug=True, port=5000)