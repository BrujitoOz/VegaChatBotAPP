# VegaChatBotAPP

## ChatBot de Telegram
VegaChatBotAPP está diseñado para manejar preguntas y proporcionar respuestas utilizando datos personalizados de la empresa.

## Detalles de Implementación
### Primera Versión
La primera versión del chatbot utilizó la API de OpenAI con el modelo GPT-3.5, operando en un sistema de pago según el uso.

### Segunda Versión
La segunda versión aprovechó los modelos locales de Ollama, específicamente Zephyr. Para ejecutar el chatbot, Ollama debe estar instalado en un sistema con una CPU de alta calidad y preferiblemente una GPU. En esta versión, el chatbot fue entrenado con datos relacionados con una aplicación de ventas y puede ayudar a los usuarios a resolver problemas con la aplicación.

### En este caso el chatbot aprendio en base a data sobre un aplicativo de ventas, y es capaz de orientar al usuario a resolver inconvenientes con esta app:
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/264cce7e-6444-48b6-9a98-35b405ed3a16)
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/f10b7768-06ef-4e45-b44f-432f1e23c2e8)

## Detección de Objetos con Azure AI Vision
El proyecto integra un modelo de detección de objetos de Azure AI Vision para analizar la barra de estado en capturas de pantalla de los usuarios. Identifica elementos como el modo de ahorro de batería activado o las notificaciones secundarias, enviando los resultados al chatbot para una respuesta proactiva.
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/29102f64-c300-44c2-b89f-e742dfaa8864)

## Uso de OCR
El chatbot utiliza Reconocimiento Óptico de Caracteres (OCR) para extraer texto de imágenes, mejorando sus capacidades.
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/c5b19fd7-7808-4a19-974a-1192b5f33f70)
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/db06d176-b19d-4426-a145-f853c3e318fc)

## Docker
El proyecto incluye un Dockerfile para crear una imagen de Docker, que pesa aproximadamente 6.3GB. Al ejecutar el contenedor, es necesario configurar variables de entorno:
- `MODEL_TYPE`: Puede ser 'local' para usar el modelo Zephyr de Ollama o 'openai' para usar GPT-3.5 (este último requiere configurar OPENAI_API_KEY).
- `BOT_TOKEN`: El token del bot de Telegram.
- `OPENAI_API_KEY`: La clave de la API de OpenAI, que es necesaria para GPT-3.5 y opera en un sistema de pago según el uso.


