class MovieLoader:
    # ... остальной код ...
    
    def load_movies_to_db(self, 
                         js_file_path: str = None, 
                         created_by_user_id: int = None,  # Делаем необязательным
                         skip_existing: bool = True) -> dict:
        """
        Загружает фильмы из JS файла в базу данных
        """
        try:
            movies_data = self.extract_movies_from_js(js_file_path)
            loaded_count = 0
            skipped_count = 0
            errors = []
            
            for movie_data in movies_data:
                # Добавляем ID пользователя только если он указан
                if created_by_user_id:
                    movie_data['created_by'] = created_by_user_id
                else:
                    # Удаляем поле, если оно есть в исходных данных
                    movie_data.pop('created_by', None)
                
                # Проверяем, существует ли уже фильм с таким названием
                if skip_existing:
                    existing = self.repository.get_movie_by_title(movie_data['title'])
                    if existing:
                        skipped_count += 1
                        continue
                
                try:
                    self.repository.create_movie(movie_data)
                    loaded_count += 1
                except Exception as e:
                    errors.append(f"Ошибка при добавлении фильма '{movie_data.get('title')}': {str(e)}")
            
            return {
                "total_in_file": len(movies_data),
                "loaded": loaded_count,
                "skipped": skipped_count,
                "errors": errors
            }
            
        except Exception as e:
            return {"error": str(e)}