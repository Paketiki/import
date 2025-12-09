# check_imports.py
try:
    from app.models.users import User
    print("✅ User imported")
    
    from app.models.roles import Role
    print("✅ Role imported")
    
    from app.models.movies import Movie
    print("✅ Movie imported")
    
    from app.models.movie_picks import Pick
    print("✅ Pick imported")
    
    from app.models.reviews import Review
    print("✅ Review imported")
    
    from app.models.movie_picks import MoviePick
    print("✅ MoviePick imported")
    
    print("\n🎉 Все импорты работают!")
    
except ImportError as e:
    print(f"\n❌ Ошибка импорта: {e}")
    import traceback
    traceback.print_exc()