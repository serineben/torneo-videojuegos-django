# Proyecto: gestión de torneo de videojuegos

- Stack: Python, Django, SQLite, Bootstrap 5, Chart.js
- Apps: accounts, tournaments, matches, stats
- Modelo User personalizado (AbstractUser) con campo role (admin / jugador)
- Clasificación calculada a partir de los partidos: 3 pts victoria, 1 empate, 0 derrota
- Nombres de variables, clases y funciones en inglés
- Textos de la interfaz, verbose_name, mensajes y plantillas en español
- Usar class-based views y mixins para los permisos
- Los secretos se gestionan con python-decouple, nunca en el código