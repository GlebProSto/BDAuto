import sqlite3

class CarDatabase:
    def __init__(self):
        self.db_path = r"C:\Users\Admin\Desktop\БД\Автомобили"
        self.con = None
        self.cursor = None
    
    def connect(self):
        try:
            
            self.con = sqlite3.connect(self.db_path)
            self.cursor = self.con.cursor()
            self.cursor.execute("PRAGMA foreign_keys = ON")
            print(f"Подключение к БД: {self.db_path}")
            return True
        except sqlite3.Error as e:
            print(f"Ошибка подключения: {e}")
            return False

    def check_exit(self, input_text):
        return str(input_text).strip().lower() in ['0', 'exit', 'выход', 'меню', 'back', 'назад']

    def safe_input(self, prompt):
        user_input = input(prompt)
        if self.check_exit(user_input):
            return None
        return user_input
    def safe_int_input(self, prompt):
        while True:
            user_input = self.safe_input(prompt)
            if user_input is None:
                return None
            try:
                return int(user_input)
            except ValueError:
                print("Ошибка: введите целое число!")

    def show_statistics(self):
        try:
            print("\nСТАТИСТИКА ПО БАЗЕ ДАННЫХ:")
            
            self.cursor.execute("SELECT COUNT(*) FROM cars")
            total_cars = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM brands")
            total_brands = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM models")
            total_models = self.cursor.fetchone()[0]
            
            print(f"Всего автомобилей: {total_cars}")
            print(f"Всего брендов: {total_brands}")
            print(f"Всего моделей: {total_models}")
            
            if total_cars > 0:
                self.cursor.execute("""
                    SELECT 
                        MIN(horsepower) as min_hp,
                        MAX(horsepower) as max_hp,
                        AVG(horsepower) as avg_hp,
                        MIN(weight) as min_weight,
                        MAX(weight) as max_weight,
                        AVG(weight) as avg_weight
                    FROM cars
                """)
                stats = self.cursor.fetchone()
                
                print(f"\nСтатистика автомобилей:")
                print(f"Мощность: {stats[0]} - {stats[2]:.1f} - {stats[1]} л.с. (мин-сред-макс)")
                print(f"Вес: {stats[3]} - {stats[5]:.1f} - {stats[4]} кг (мин-сред-макс)")
            
            self.cursor.execute("SELECT COUNT(*) FROM brands WHERE isActive = 1")
            active_brands = self.cursor.fetchone()[0]
            print(f"Активных брендов: {active_brands}/{total_brands}")
            
        except sqlite3.Error as e:
            print(f"Ошибка статистики: {e}")

    def edit_data(self):
        print("\nРЕДАКТИРОВАНИЕ ДАННЫХ")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        tables = ["countries", "brands", "models", "body_types", "engine_types", "drivetrains", "cars"]
        
        try:
            print("\nДоступные таблицы для редактирования:")
            for i, table in enumerate(tables, 1):
                print(f"{i} - {table}")
            
            table_choice = self.safe_input("\nВведите номер таблицы для редактирования: ")
            if table_choice is None:
                return
            if not table_choice.isdigit() or not (1 <= int(table_choice) <= len(tables)):
                print("Ошибка: введите корректный номер таблицы!")
                return
            
            table_name = tables[int(table_choice) - 1]
            
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            print(f"\nСодержимое таблицы {table_name}:")
            self.get_table_data(table_name)
            
            pk_column = columns[0][1]
            
            record_id = self.safe_input(f"\nВведите номер записи для редактирования ({pk_column}): ")
            if record_id is None:
                return
            
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE {pk_column} = ?", (record_id,))
            record = self.cursor.fetchone()
            
            if not record:
                print("Запись не найдена!")
                return
            
            print(f"\nТекущие данные записи:")
            for i, col in enumerate(columns):
                print(f"{i+1}. {col[1]}: {record[i]}")
            
            print("\nВыберите поле для редактирования:")
            for i, col in enumerate(columns, 1):
                print(f"{i} - {col[1]}")
            
            field_choice = self.safe_input("Введите номер поля: ")
            if field_choice is None:
                return
            if not field_choice.isdigit() or not (1 <= int(field_choice) <= len(columns)):
                print("Ошибка: введите корректный номер поля!")
                return
            
            selected_column = columns[int(field_choice) - 1][1]
            column_type = columns[int(field_choice) - 1][2].upper()
            
            new_value = self.safe_input(f"Введите новое значение для '{selected_column}': ")
            if new_value is None:
                return
            
            if "INT" in column_type:
                try:
                    new_value = int(new_value) if new_value else None
                except ValueError:
                    print("Ошибка: должно быть целое число!")
                    return
            elif "BOOLEAN" in column_type or selected_column == "isActive":
                new_value = 1 if new_value.lower() in ['1', 'true', 'да', 'yes'] else 0
            
            update_query = f"UPDATE {table_name} SET {selected_column} = ? WHERE {pk_column} = ?"
            self.cursor.execute(update_query, (new_value, record_id))
            
            if self.cursor.rowcount > 0:
                self.con.commit()
                print("Данные успешно обновлены!")
                
                print("\nОбновленные данные:")
                self.cursor.execute(f"SELECT * FROM {table_name} WHERE {pk_column} = ?", (record_id,))
                updated_record = self.cursor.fetchone()
                for i, col in enumerate(columns):
                    print(f"{col[1]}: {updated_record[i]}")
            else:
                print("Ошибка при обновлении данных!")
                
        except ValueError:
            print("Ошибка ввода числового значения!")
        except sqlite3.Error as e:
            error_msg = str(e)
            if "UNIQUE constraint failed" in error_msg:
                print("Ошибка: запись с такими данными уже существует!")
            elif "FOREIGN KEY constraint failed" in error_msg:
                print("Ошибка: указан несуществующий номер связанной записи!")
            else:
                print(f"Ошибка базы данных: {e}")

    def sort_cars(self):
        print("\nСОРТИРОВКА АВТОМОБИЛЕЙ")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        print("1 - По мощности (возрастание)")
        print("2 - По мощности (убывание)")
        print("3 - По весу (возрастание)")
        print("4 - По весу (убывание)")
        
        try:
            choice = self.safe_input("Введите номер варианта сортировки: ")
            if choice is None:
                return
            
            if choice == "1":
                order = "horsepower ASC"
            elif choice == "2":
                order = "horsepower DESC"
            elif choice == "3":
                order = "weight ASC"
            elif choice == "4":
                order = "weight DESC"
            else:
                print("Ошибка: введите число от 1 до 4!")
                return
            
            query = f"""
                SELECT c.vin, c.horsepower, c.weight, 
                       m.name as model, b.name as brand
                FROM cars c
                JOIN models m ON c.model_id = m.model_id
                JOIN brands b ON m.brand_id = b.brand_id
                ORDER BY {order}
            """
            
            self.cursor.execute(query)
            cars = self.cursor.fetchall()
            
            print(f"\nАвтомобили (отсортировано):")
            print("VIN | Мощность | Вес | Модель | Бренд")
            print("-" * 60)
            
            for car in cars:
                print(f"{car[0]} | {car[1]} л.с. | {car[2]} кг | {car[3]} | {car[4]}")
                
        except sqlite3.Error as e:
            print(f"Ошибка сортировки: {e}")

    def get_table_data(self, table_name):
        try:
            self.cursor.execute(f"SELECT * FROM {table_name}")
            data = self.cursor.fetchall()
            
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [col[1] for col in self.cursor.fetchall()]
            
            print(f"\nТаблица {table_name}:")
            print(" | ".join(columns))
            print("-" * 80)
            
            for row in data:
                print(" | ".join(str(item) if item is not None else "NULL" for item in row))
            
            return data
        except sqlite3.Error as e:
            print(f"Ошибка получения данных: {e}")
            return []

    def add_new_country(self):
        print("\nДОБАВЛЕНИЕ НОВОЙ СТРАНЫ")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        name = self.safe_input("Введите название новой страны: ")
        if name is None:
            return None
        
        try:
            self.cursor.execute("INSERT INTO countries (name) VALUES (?)", (name,))
            self.con.commit()
            print(f"Страна '{name}' успешно добавлена!")
            
            self.cursor.execute("SELECT country_id FROM countries WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                print("Ошибка: страна с таким названием уже существует!")
            else:
                print(f"Ошибка при добавлении страны: {e}")
            return None

    def add_new_brand(self):
        print("\nДОБАВЛЕНИЕ НОВОГО БРЕНДА")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        print("Доступные страны:")
        self.cursor.execute("SELECT country_id, name FROM countries")
        countries = self.cursor.fetchall()
        for row in countries:
            print(f"{row[0]} - {row[1]}")
        print("0 - Добавить новую страну")
        
        name = self.safe_input("Введите название бренда: ")
        if name is None:
            return None
        
        yearFounded = self.safe_int_input("Введите год основания: ")
        if yearFounded is None:
            return None
        
        isActive_input = self.safe_input("Активен (1-да, 0-нет): ")
        if isActive_input is None:
            return None
        isActive = 1 if isActive_input in ['1', 'true', 'да', 'yes'] else 0
        
        country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
        if country_choice is None:
            return None
        
        if country_choice == "0":
            country_id = self.add_new_country()
            if country_id is None:
                return None
        else:
            country_id = int(country_choice)
        
        try:
            self.cursor.execute(
                "INSERT INTO brands (name, yearFounded, isActive, country_id) VALUES (?, ?, ?, ?)", 
                (name, yearFounded, isActive, country_id)
            )
            self.con.commit()
            print(f"Бренд '{name}' успешно добавлен!")
            
            self.cursor.execute("SELECT brand_id FROM brands WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                print("Ошибка: бренд с таким названием уже существует!")
            else:
                print(f"Ошибка при добавлении бренда: {e}")
            return None

    def add_new_model(self):
        print("\nДОБАВЛЕНИЕ НОВОЙ МОДЕЛИ")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        print("Доступные бренды:")
        self.cursor.execute("SELECT brand_id, name FROM brands")
        brands = self.cursor.fetchall()
        for row in brands:
            print(f"{row[0]} - {row[1]}")
        print("0 - Добавить новый бренд")
        
        brand_choice = self.safe_input("Введите номер бренда (или 0 для добавления нового): ")
        if brand_choice is None:
            return None
        
        if brand_choice == "0":
            brand_id = self.add_new_brand()
            if brand_id is None:
                return None
        else:
            brand_id = int(brand_choice)
        
        print("\nДоступные страны:")
        self.cursor.execute("SELECT country_id, name FROM countries")
        countries = self.cursor.fetchall()
        for row in countries:
            print(f"{row[0]} - {row[1]}")
        print("0 - Добавить новую страну")
        
        name = self.safe_input("Введите название модели: ")
        if name is None:
            return None
        
        yearFounded = self.safe_int_input("Введите год начала производства: ")
        if yearFounded is None:
            return None
        
        generation = self.safe_input("Введите поколение: ")
        if generation is None:
            return None
        
        country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
        if country_choice is None:
            return None
        
        if country_choice == "0":
            country_id = self.add_new_country()
            if country_id is None:
                return None
        else:
            country_id = int(country_choice)
        
        yearDiscontinued_input = self.safe_input("Введите год снятия с производства (или Enter если нет): ")
        if yearDiscontinued_input is None:
            return None
        yearDiscontinued = int(yearDiscontinued_input) if yearDiscontinued_input else None
        
        try:
            self.cursor.execute(
                "INSERT INTO models (name, yearFounded, yearDiscontinued, generation, brand_id, country_id) VALUES (?, ?, ?, ?, ?, ?)", 
                (name, yearFounded, yearDiscontinued, generation, brand_id, country_id)
            )
            self.con.commit()
            print(f"Модель '{name}' успешно добавлена!")
            
            self.cursor.execute("SELECT model_id FROM models WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                print("Ошибка: модель с таким названием уже существует!")
            else:
                print(f"Ошибка при добавлении модели: {e}")
            return None

    def add_new_body_type(self):
        print("\nДОБАВЛЕНИЕ НОВОГО ТИПА КУЗОВА")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        name = self.safe_input("Введите тип кузова: ")
        if name is None:
            return None
        
        description = self.safe_input("Введите описание: ")
        if description is None:
            return None
        
        door_count = self.safe_int_input("Введите количество дверей: ")
        if door_count is None:
            return None
        
        try:
            self.cursor.execute(
                "INSERT INTO body_types (name, description, door_count) VALUES (?, ?, ?)", 
                (name, description, door_count)
            )
            self.con.commit()
            print(f"Тип кузова '{name}' успешно добавлен!")
            
            self.cursor.execute("SELECT body_type_id FROM body_types WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                print("Ошибка: тип кузова с таким названием уже существует!")
            else:
                print(f"Ошибка при добавлении типа кузова: {e}")
            return None

    def add_new_engine_type(self):
        print("\nДОБАВЛЕНИЕ НОВОГО ТИПА ДВИГАТЕЛЯ")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        print("Доступные страны:")
        self.cursor.execute("SELECT country_id, name FROM countries")
        countries = self.cursor.fetchall()
        for row in countries:
            print(f"{row[0]} - {row[1]}")
        print("0 - Добавить новую страну")
        
        name = self.safe_input("Введите тип двигателя: ")
        if name is None:
            return None
        
        description = self.safe_input("Введите описание: ")
        if description is None:
            return None
        
        country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
        if country_choice is None:
            return None
        
        if country_choice == "0":
            country_id = self.add_new_country()
            if country_id is None:
                return None
        else:
            country_id = int(country_choice)
        
        try:
            self.cursor.execute(
                "INSERT INTO engine_types (name, description, country_id) VALUES (?, ?, ?)", 
                (name, description, country_id)
            )
            self.con.commit()
            print(f"Тип двигателя '{name}' успешно добавлен!")
            
            self.cursor.execute("SELECT engine_type_id FROM engine_types WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                print("Ошибка: тип двигателя с таким названием уже существует!")
            else:
                print(f"Ошибка при добавлении типа двигателя: {e}")
            return None

    def add_new_drivetrain(self):
        print("\nДОБАВЛЕНИЕ НОВОГО ТИПА ПРИВОДА")
        print("Введите '0' в любой момент для возврата в главное меню")
        
        print("Доступные страны:")
        self.cursor.execute("SELECT country_id, name FROM countries")
        countries = self.cursor.fetchall()
        for row in countries:
            print(f"{row[0]} - {row[1]}")
        print("0 - Добавить новую страну")
        
        name = self.safe_input("Введите тип привода: ")
        if name is None:
            return None
        
        description = self.safe_input("Введите описание: ")
        if description is None:
            return None
        
        country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
        if country_choice is None:
            return None
        
        if country_choice == "0":
            country_id = self.add_new_country()
            if country_id is None:
                return None
        else:
            country_id = int(country_choice)
        
        try:
            self.cursor.execute(
                "INSERT INTO drivetrains (name, description, country_id) VALUES (?, ?, ?)", 
                (name, description, country_id)
            )
            self.con.commit()
            print(f"Тип привода '{name}' успешно добавлен!")
            
            self.cursor.execute("SELECT drivetrain_id FROM drivetrains WHERE name = ?", (name,))
            return self.cursor.fetchone()[0]
        except sqlite3.Error as e:
            if "UNIQUE constraint failed" in str(e):
                print("Ошибка: тип привода с таким названием уже существует!")
            else:
                print(f"Ошибка при добавлении типа привода: {e}")
            return None

    def add_data_to_table(self, table_name):
        try:
            print(f"\nДОБАВЛЕНИЕ ДАННЫХ В ТАБЛИЦУ: {table_name}")
            print("Введите '0' в любой момент для возврата в главное меню")
            
            if table_name == "countries":
                name = self.safe_input("Введите название страны: ")
                if name is None:
                    return False
                self.cursor.execute("INSERT INTO countries (name) VALUES (?)", (name,))
                
            elif table_name == "brands":
                print("\nДоступные страны:")
                self.cursor.execute("SELECT country_id, name FROM countries")
                countries = self.cursor.fetchall()
                for row in countries:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новую страну")
                
                name = self.safe_input("Введите название бренда: ")
                if name is None:
                    return False
                
                yearFounded = self.safe_int_input("Введите год основания: ")
                if yearFounded is None:
                    return False
                
                isActive_input = self.safe_input("Активен (1-да, 0-нет): ")
                if isActive_input is None:
                    return False
                isActive = 1 if isActive_input in ['1', 'true', 'да', 'yes'] else 0
                
                country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
                if country_choice is None:
                    return False
                
                if country_choice == "0":
                    country_id = self.add_new_country()
                    if country_id is None:
                        return False
                else:
                    country_id = int(country_choice)
                
                self.cursor.execute(
                    "INSERT INTO brands (name, yearFounded, isActive, country_id) VALUES (?, ?, ?, ?)", 
                    (name, yearFounded, isActive, country_id)
                )
                
            elif table_name == "models":
                print("\nДоступные бренды:")
                self.cursor.execute("SELECT brand_id, name FROM brands")
                brands = self.cursor.fetchall()
                for row in brands:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новый бренд")
                
                brand_choice = self.safe_input("Введите номер бренда (или 0 для добавления нового): ")
                if brand_choice is None:
                    return False
                
                if brand_choice == "0":
                    brand_id = self.add_new_brand()
                    if brand_id is None:
                        return False
                else:
                    brand_id = int(brand_choice)
                
                print("\nДоступные страны:")
                self.cursor.execute("SELECT country_id, name FROM countries")
                countries = self.cursor.fetchall()
                for row in countries:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новую страну")
                
                name = self.safe_input("Введите название модели: ")
                if name is None:
                    return False
                
                yearFounded = self.safe_int_input("Введите год начала производства: ")
                if yearFounded is None:
                    return False
                
                generation = self.safe_input("Введите поколение: ")
                if generation is None:
                    return False
                
                country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
                if country_choice is None:
                    return False
                
                if country_choice == "0":
                    country_id = self.add_new_country()
                    if country_id is None:
                        return False
                else:
                    country_id = int(country_choice)
                
                yearDiscontinued_input = self.safe_input("Введите год снятия с производства (или Enter если нет): ")
                if yearDiscontinued_input is None:
                    return False
                yearDiscontinued = int(yearDiscontinued_input) if yearDiscontinued_input else None
                
                self.cursor.execute(
                    "INSERT INTO models (name, yearFounded, yearDiscontinued, generation, brand_id, country_id) VALUES (?, ?, ?, ?, ?, ?)", 
                    (name, yearFounded, yearDiscontinued, generation, brand_id, country_id)
                )
                
            elif table_name == "body_types":
                name = self.safe_input("Введите тип кузова: ")
                if name is None:
                    return False
                
                description = self.safe_input("Введите описание: ")
                if description is None:
                    return False
                
                door_count = self.safe_int_input("Введите количество дверей: ")
                if door_count is None:
                    return False
                
                self.cursor.execute(
                    "INSERT INTO body_types (name, description, door_count) VALUES (?, ?, ?)", 
                    (name, description, door_count)
                )
                
            elif table_name == "engine_types":
                print("\nДоступные страны:")
                self.cursor.execute("SELECT country_id, name FROM countries")
                countries = self.cursor.fetchall()
                for row in countries:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новую страну")
                
                name = self.safe_input("Введите тип двигателя: ")
                if name is None:
                    return False
                
                description = self.safe_input("Введите описание: ")
                if description is None:
                    return False
                
                country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
                if country_choice is None:
                    return False
                
                if country_choice == "0":
                    country_id = self.add_new_country()
                    if country_id is None:
                        return False
                else:
                    country_id = int(country_choice)
                
                self.cursor.execute(
                    "INSERT INTO engine_types (name, description, country_id) VALUES (?, ?, ?)", 
                    (name, description, country_id)
                )
                
            elif table_name == "drivetrains":
                print("\nДоступные страны:")
                self.cursor.execute("SELECT country_id, name FROM countries")
                countries = self.cursor.fetchall()
                for row in countries:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новую страну")
                
                name = self.safe_input("Введите тип привода: ")
                if name is None:
                    return False
                
                description = self.safe_input("Введите описание: ")
                if description is None:
                    return False
                
                country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
                if country_choice is None:
                    return False
                
                if country_choice == "0":
                    country_id = self.add_new_country()
                    if country_id is None:
                        return False
                else:
                    country_id = int(country_choice)
                
                self.cursor.execute(
                    "INSERT INTO drivetrains (name, description, country_id) VALUES (?, ?, ?)", 
                    (name, description, country_id)
                )
                
            elif table_name == "cars":
                print("\nДоступные модели:")
                self.cursor.execute("SELECT model_id, name FROM models")
                models = self.cursor.fetchall()
                for row in models:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новую модель")
                
                model_choice = self.safe_input("Введите номер модели (или 0 для добавления новой): ")
                if model_choice is None:
                    return False
                
                if model_choice == "0":
                    model_id = self.add_new_model()
                    if model_id is None:
                        return False
                else:
                    model_id = int(model_choice)
                
                print("\nДоступные типы кузова:")
                self.cursor.execute("SELECT body_type_id, name FROM body_types")
                body_types = self.cursor.fetchall()
                for row in body_types:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новый тип кузова")
                
                body_choice = self.safe_input("Введите номер типа кузова (или 0 для добавления нового): ")
                if body_choice is None:
                    return False
                
                if body_choice == "0":
                    body_type_id = self.add_new_body_type()
                    if body_type_id is None:
                        return False
                else:
                    body_type_id = int(body_choice)
                
                print("\nДоступные типы двигателей:")
                self.cursor.execute("SELECT engine_type_id, name FROM engine_types")
                engines = self.cursor.fetchall()
                for row in engines:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новый тип двигателя")
                
                engine_choice = self.safe_input("Введите номер типа двигателя (или 0 для добавления нового): ")
                if engine_choice is None:
                    return False
                
                if engine_choice == "0":
                    engine_type_id = self.add_new_engine_type()
                    if engine_type_id is None:
                        return False
                else:
                    engine_type_id = int(engine_choice)
                
                print("\nДоступные типы привода:")
                self.cursor.execute("SELECT drivetrain_id, name FROM drivetrains")
                drivetrains = self.cursor.fetchall()
                for row in drivetrains:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новый тип привода")
                
                drivetrain_choice = self.safe_input("Введите номер типа привода (или 0 для добавления нового): ")
                if drivetrain_choice is None:
                    return False
                
                if drivetrain_choice == "0":
                    drivetrain_id = self.add_new_drivetrain()
                    if drivetrain_id is None:
                        return False
                else:
                    drivetrain_id = int(drivetrain_choice)
                
                print("\nДоступные страны:")
                self.cursor.execute("SELECT country_id, name FROM countries")
                countries = self.cursor.fetchall()
                for row in countries:
                    print(f"{row[0]} - {row[1]}")
                print("0 - Добавить новую страну")
                
                vin = self.safe_input("Введите VIN: ")
                if vin is None:
                    return False
                
                horsepower = self.safe_int_input("Введите мощность (л.с.): ")
                if horsepower is None:
                    return False
                
                weight = self.safe_int_input("Введите вес (кг): ")
                if weight is None:
                    return False
                
                country_choice = self.safe_input("Введите номер страны (или 0 для добавления новой): ")
                if country_choice is None:
                    return False
                
                if country_choice == "0":
                    country_id = self.add_new_country()
                    if country_id is None:
                        return False
                else:
                    country_id = int(country_choice)

                self.cursor.execute(
                    "INSERT INTO cars (vin, horsepower, weight, model_id, body_type_id, engine_type_id, drivetrain_id, country_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                    (vin, horsepower, weight, model_id, body_type_id, engine_type_id, drivetrain_id, country_id)
                )
            
            self.con.commit()
            print(f"Данные добавлены в таблицу {table_name}!")
            return True
            
        except sqlite3.Error as e:
            error_msg = str(e)
            if "UNIQUE constraint failed" in error_msg:
                if "countries.name" in error_msg:
                    print("Ошибка: страна с таким названием уже существует!")
                elif "brands.name" in error_msg:
                    print("Ошибка: бренд с таким названием уже существует!")
                elif "models.name" in error_msg:
                    print("Ошибка: модель с таким названием уже существует!")
                elif "cars.vin" in error_msg:
                    print("Ошибка: автомобиль с таким VIN уже существует!")
                else:
                    print("Ошибка: запись с такими данными уже существует!")
            elif "FOREIGN KEY constraint failed" in error_msg:
                print("Ошибка: указан несуществующий номер связанной записи!")
            elif "NOT NULL constraint failed" in error_msg:
                print("Ошибка: обязательные поля не могут быть пустыми!")
            else:
                print(f"Ошибка базы данных: {e}")
            return False

def main():
    db = CarDatabase()
    
    if not db.connect():
        return
    
    tables = ["countries", "brands", "models", "body_types", "engine_types", "drivetrains", "cars"]
    
    while True:
        print("\n" + "="*50)
        print("АВТОМОБИЛЬНАЯ БАЗА ДАННЫХ")
        print("="*50)
        print("1 - Просмотр таблиц")
        print("2 - Добавление данных")
        print("3 - Редактирование данных")
        print("4 - Статистика")
        print("5 - Сортировка автомобилей")
        print("0 - Выход")
        print("\nВведите '0' в любой момент для возврата в главное меню")
        
        choice = input("\nВведите номер действия: ")
        
        if choice == "1":
            print("\nДоступные таблицы:")
            for i, table in enumerate(tables, 1):
                print(f"{i} - {table}")
            
            table_choice = input("Введите номер таблицы для просмотра: ")
            if db.check_exit(table_choice):
                continue
            if table_choice.isdigit() and 1 <= int(table_choice) <= len(tables):
                db.get_table_data(tables[int(table_choice)-1])
            else:
                print("Ошибка: введите корректный номер таблицы!")
        
        elif choice == "2":
            print("\nДоступные таблицы:")
            for i, table in enumerate(tables, 1):
                print(f"{i} - {table}")
            
            table_choice = input("Введите номер таблицы для добавления данных: ")
            if db.check_exit(table_choice):
                continue
            if table_choice.isdigit() and 1 <= int(table_choice) <= len(tables):
                db.add_data_to_table(tables[int(table_choice)-1])
            else:
                print("Ошибка: введите корректный номер таблицы!")
        
        elif choice == "3":
            db.edit_data()
        
        elif choice == "4":
            db.show_statistics()
        
        elif choice == "5":
            db.sort_cars()
        
        elif choice == "0":
            print("До свидания!")
            break
        
        else:
            print("Ошибка: введите число от 0 до 5!")

if __name__ == "__main__":
    main()