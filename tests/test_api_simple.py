import requests

BASE_URL = "http://localhost:5000"

def test_api():
    print("🧪 Test des APIs...")
    
    # Test connexion
    try:
        response = requests.get(f"{BASE_URL}/test")
        print(f"✅ Serveur: {response.json()['message']}")
    except:
        print("❌ Serveur non accessible")
        return
    
    # Test patients
    response = requests.get(f"{BASE_URL}/api/patients")
    print(f"✅ Patients: {len(response.json())} trouvés")
    
    # Test médecins
    response = requests.get(f"{BASE_URL}/api/medecins")
    print(f"✅ Médecins: {len(response.json())} trouvés")
    
    # Test rendez-vous
    response = requests.get(f"{BASE_URL}/api/rendezvous")
    print(f"✅ Rendez-vous: {len(response.json())} trouvés")

if __name__ == "__main__":
    test_api()