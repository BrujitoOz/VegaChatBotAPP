# Telegram-ChatBot
## Telegram ChatBot: diseñado para responder preguntas y respuestas con data personalizada empresarial
### Como se hizo?
#### Para darle al modelo la información de la empresa, se uso Retrieval-augmented generation (RAG)

### Primera versión
#### Se hizo usando el API de OpenAI para usar el modelo GPT-3.5, es decir que se usa un sistema de pago pay-as-you-go

### Segunda versión
#### Se hizo usando los modelos locales de Ollama, en este caso Zephyr. Se necesita tener instalado Ollama y que la PC que uses tenga un buen CPU y preferiblemente también GPU.

### En este caso el chatbot aprendio en base a data sobre un aplicativo de ventas, y es capaz de orientar al usuario a resolver inconvenientes con esta app:
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/264cce7e-6444-48b6-9a98-35b405ed3a16)
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/f10b7768-06ef-4e45-b44f-432f1e23c2e8)

### Uso de Modelo de Detección de Objetos con Azure AI Vision
#### Este proyecto integra un modelo de detección de objetos de Azure AI Vision para analizar la barra de estado en capturas de pantalla de usuarios. Detecta elementos como ahorro de batería activado o notificaciones secundarias, enviando los resultados al chatbot para una respuesta proactiva:
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/29102f64-c300-44c2-b89f-e742dfaa8864)

### Con uso de OCR, este chatbot puede leer el texto extraido de las imagenes:
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/c5b19fd7-7808-4a19-974a-1192b5f33f70)
![image](https://github.com/BrujitoOz/VegaChatBotAPP/assets/54969025/db06d176-b19d-4426-a145-f853c3e318fc)

# Docker
## El proyecto incluye un archivo Dockerfile para crear la imagen docker que pesará aproximadamente 6.3GB.
### Al correr el contenedor, es necesario configurar variables de entorno.
#### MODEL_TYPE: puede ser 'local' para usar el modelo Zephyr de Ollama o 'openai' para usar GPT-3.5 (este último hace que configurar OPENAI_API_KEY sea obligatorio) 
#### BOT_TOKEN: el token del chatbot creado en telegram.
#### OPENAI_API_KEY: este token se obtiene desde la plataforma de OpenAI, usa el sistema de pago pay-as-you-go.


