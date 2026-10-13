# Proyecto: gestión de torneo de videojuegos

- Stack: Python, Django, SQLite, Bootstrap 5, Chart.js
- Apps: accounts, games, stats
- Modelos: User (role admin/jugador), Game, Registration (user, game, level amateur/normal/expert, points)
- Torneo por puntos: clasificación por juego y general (suma de puntos)
- Clasificación calculada a partir de los partidos: 3 pts victoria, 1 empate, 0 derrota
- Nombres de variables, clases y funciones en inglés
- Textos de la interfaz, verbose_name, mensajes y plantillas en español
- Usar class-based views y mixins para los permisos
- Los secretos se gestionan con python-decouple, nunca en el código
- Tests: archivos test_*.py en cada app (TestCase), helpers en config/testing.py
- Ejecutar: python manage.py test; cobertura: coverage run manage.py test
- Linter: ruff check . (configuración en ruff.toml)