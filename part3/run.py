from app import create_app
from app.services import facade

app = create_app()

def seed_data():
    with app.app_context():
        # 1. Création de l'utilisateur Admin
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

            guest = facade.create_user({
                "first_name": "Axel",
                "last_name": "Goré",
                "email": "axel.gore@holberton.com",
                "password": "swernslvl"
            })
            print("✅ User Axel crée.")

        # 2. Création sécurisée des Amenities
        print("🌱 Vérification des équipements...")
        
        # On récupère toutes les amenities existantes pour comparer les noms
        existing_amenities = facade.get_all_amenities()
        amenities_map = {a.name: a for a in existing_amenities}

        def get_or_create_amenity(name):
            if name in amenities_map:
                return amenities_map[name]
            print(f"  + Création de l'équipement : {name}")
            return facade.create_amenity({"name": name})

        wifi = get_or_create_amenity("WiFi")
        pool = get_or_create_amenity("Swimming Pool")
        ac = get_or_create_amenity("Air Conditioning")

        # 3. Création des Places de test
        existing_places = facade.get_all_places()
        if not existing_places:
            places_to_create = [
                {
                    "title": "Cozy Apartment",
                    "description": "A nice place in the heart of the city.",
                    "price": 50.0,
                    "latitude": 48.8566,
                    "longitude": 2.3522,
                    "owner_id": admin.id,
                    "amenities": [wifi.id]
                },
                {
                    "title": "Luxury Villa",
                    "description": "Perfect for summer vacations with a pool.",
                    "price": 150.0,
                    "latitude": 43.7102,
                    "longitude": 7.2620,
                    "owner_id": admin.id,
                    "amenities": [wifi.id, pool.id, ac.id]
                },
                {
                    "title": "Cheap Room",
                    "description": "Small but functional room for students.",
                    "price": 10.0,
                    "latitude": 45.7640,
                    "longitude": 4.8357,
                    "owner_id": admin.id,
                    "amenities": [ac.id]
                }
            ]

            for p_data in places_to_create:
                facade.create_place(p_data)
            
            print(f"✅ {len(places_to_create)} places créées.")
        else:
            print(f"ℹ️ {len(existing_places)} places déjà présentes.")

if __name__ == '__main__':
    seed_data()
    app.run(debug=True, port=5000)