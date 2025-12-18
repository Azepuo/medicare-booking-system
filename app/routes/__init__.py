"""
Enregistrement centralisé de TOUS les blueprints
"""
def register_blueprints(app):
    """
    Enregistre tous les blueprints de l'application
    """
    print("="*70)
    print("📦 ENREGISTREMENT DES BLUEPRINTS")
    print("="*70)
    
    # ✅ 1. Main routes
    try:
        from app.routes.main_routes import main
        app.register_blueprint(main)
        print("  ✓ main")
    except Exception as e:
        print(f"  ✗ main - Erreur: {e}")
    
    # ✅ 2. Auth routes
    try:
        from app.routes.authentification.authentification_routes import auth_bp
        app.register_blueprint(auth_bp)
        print("  ✓ auth_bp")
    except Exception as e:
        print(f"  ✗ auth_bp - Erreur: {e}")
    
    # ✅ 3. Patient routes (CRITIQUE !)
    try:
        from app.routes.patient.patient_routes import patient
        app.register_blueprint(patient)
        print("  ✓ patient ⭐ (IMPORTANT)")
    except Exception as e:
        print(f"  ✗ patient - ERREUR CRITIQUE: {e}")
        print("\n🔍 Détails de l'erreur :")
        import traceback
        traceback.print_exc()
        print("\n⚠️  Le blueprint patient N'A PAS été enregistré !")
        print("    Vérifiez app/routes/patient/patient_routes.py")
    
    print("="*70)
    print(f"✅ Blueprints enregistrés : {list(app.blueprints.keys())}")
    print("="*70)