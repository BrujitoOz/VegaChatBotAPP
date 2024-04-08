from llama_index.llms.ollama import Ollama
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
import openai
from llama_index.core import (
    PromptTemplate, 
    Settings, 
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core.memory import ChatMemoryBuffer
import telebot, onnxruntime, requests, pytesseract, os, re, cv2, time
import numpy as np
from PIL import Image
import platform
from dotenv import load_dotenv
load_dotenv()
model_type = os.getenv("MODEL_TYPE")

if os.getenv("OPENAI_API_KEY"):
    openai.api_key = os.getenv("OPENAI_API_KEY")

if model_type == "local":
    llm = Ollama(model="zephyr", request_timeout=8000.0)
    Settings.llm = llm

elif model_type == "openai":
    llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
    Settings.llm = llm
    
else:
    raise ValueError("La variable de entorno MODEL_TYPE debe ser 'local' o 'openai'.")

Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
Settings.llm = llm
Settings.num_output = 512
Settings.context_window = 3900

try:
    storage_context = StorageContext.from_defaults(persist_dir="./storage/vmaps")
    index = load_index_from_storage(storage_context)
    index_loaded = True
except:
    index_loaded = False

if not index_loaded:
    documents = SimpleDirectoryReader(input_dir = './data/vmaps').load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir="./storage/vmaps")


QA_PROMPT_TMPL = (
    "Eres un asistente chatbot que atiende preguntas y consultas de nuestros clientes "
    "sobre el aplicativo VMaps, ellos te avisaran de sus problemas y con la información de contexto "
    "que tienes les daras soluciones. "
    "La información de contexto se encuentra a continuación.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Dada la información de contexto y no conocimiento previo, "
    "responde la pregunta. También recibiras textos de imagenes gracias a un OCR "
    "el cual puede fallar y darte un texto incomprensible o con errores tipograficos, avisa al usuario si el texto es de mala calidad.\n" 
    "Si la pregunta no está en el contexto o te preguntan algo que no tiene nada que ver con el contexto "
    "informa al usuario que no puedes responder la pregunta - NO INVENTES UNA RESPUESTA.\n "
    "Sé breve con tus respuestas y siempre respondes en español.\n"
    "Pregunta: {query_str}\n"
)
QA_PROMPT = PromptTemplate(QA_PROMPT_TMPL)

memory = ChatMemoryBuffer.from_defaults(token_limit=1500)
chat_engine = index.as_chat_engine(chat_mode="context", 
                                   memory=memory,
                                   streaming=True, 
                                   text_qa_template=QA_PROMPT)


BOT_TOKEN = os.getenv("BOT_TOKEN")
MODEL_PATH = './AzureOD_SystemBar.onnx'
STATUS_BAR_HEIGHT = 55
CONFIDENCE_THRESHOLD = 0.20

if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

START_TIME = time.time()

# Iniciar
bot = telebot.TeleBot(BOT_TOKEN)
print("Bot initialized successfully.")

bot.set_webhook()
session = onnxruntime.InferenceSession(MODEL_PATH, providers=['AzureExecutionProvider', 'CPUExecutionProvider'])

# Preprocesamos la imagen con el fin de mejorar la captura del texto del OCR
def increase_contrast(image):
  image = image.resize((720, 1600))
  image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
  image_gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)

  clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
  contrast_image = clahe.apply(image_gray)
  _, binarized_image = cv2.threshold(contrast_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

  return Image.fromarray(binarized_image)

# Limpiar el texto para evitar caracteres raros como simbolos dolar, porcentaje, etc
def clean_text(text):
  cleaned_text = re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]', '', text)
  cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
  lines = cleaned_text.split('\n')
  lines = [line for line in lines if line.strip()]
  cleaned_text = '\n'.join(lines)

  return cleaned_text

def extract_text_from_image(image_path):
  image = Image.open(image_path)
  image = increase_contrast(image)
  text = pytesseract.image_to_string(image, lang="spa", config='--psm 6')
  text = clean_text(text)
  return text

# Función para recortar la imagen y obtener solo la barra de estado
def crop_status_bar(image_path):
  image = Image.open(image_path)
  ancho_deseado = 720
  factor_escalado = ancho_deseado / image.width
  nuevo_alto = int(image.height * factor_escalado)
  image = image.resize((ancho_deseado, nuevo_alto))
  cropped_image = image.crop((0, 0, ancho_deseado, STATUS_BAR_HEIGHT))

  return cropped_image

# Obtener la lista de categorias de imagenes detectados
def process_image(image_path, mensaje):
  text = extract_text_from_image(image_path)

  imagen_recortada = crop_status_bar(image_path)
  imagen_recortada = imagen_recortada.resize((320, 320))
  imagen_recortada = np.array(imagen_recortada).astype('float32')
  imagen_recortada = np.transpose(imagen_recortada, (2, 0, 1))
  imagen_recortada = np.expand_dims(imagen_recortada, axis=0)

  input_name = session.get_inputs()[0].name
  predictions = session.run(None, {input_name: imagen_recortada})
  predicted_tags = predictions[1][0]
  confidence_scores = predictions[2][0]

  tag_map = {
    0: 'Actualizacion sistema pendiente detectada.',
    1: 'Ahorro de batería activado detectado.',
    2: 'Bluetooth detectado',
    3: 'Aplicaciones secundarias detectadas.'
  }
  detected_tags = []
  for i, etiqueta_id in enumerate(predicted_tags):
      confidence = confidence_scores[i]
      if confidence >= CONFIDENCE_THRESHOLD:
          etiqueta = tag_map.get(etiqueta_id)
          if etiqueta:
              detected_tags.append(etiqueta)

  detected_tags = list(set(detected_tags))
  return detected_tags if detected_tags else None, text


@bot.message_handler(content_types=['text', 'photo'])
def handle_messages(mensaje):
    message_time = mensaje.date

    if message_time < START_TIME:
        return

    if mensaje.content_type == 'text':
        handle_message(mensaje)

    elif mensaje.content_type == 'photo':
        handle_photo(mensaje)


@bot.message_handler(content_types=['text'])
def handle_message(mensaje):
  print("Handling text message...")
  texto = mensaje.text
  print("Mensaje recibido: ", texto)
  response = chat_engine.chat(texto)
  print("Respuesta: ", response)
  bot.send_message(mensaje.chat.id, response)

@bot.message_handler(content_types=['photo'])
def handle_photo(mensaje):
  print("Handling photo message...")
  chat_id = mensaje.chat.id

  file_info = bot.get_file(mensaje.photo[-1].file_id)
  print("file info: ", file_info)
  
  file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file_info.file_path}"
  status = requests.get(file_url)
  print("status: ", status)
  
  with open("temp_image.jpg", "wb") as image_file:
    image_file.write(status.content)

  detected_tags, text_img = process_image("temp_image.jpg", mensaje)
  print("tags detectados en la imagen: ", detected_tags)
  print("texto en la imagen: ", text_img)
  
  if detected_tags and text_img:
    text_joined = '. '.join(detected_tags)
    print("texto unido: ", text_joined)
    
    if mensaje.caption:
      response = chat_engine.chat(text_joined + ". Texto en la imagen: " + text_img + ". " + mensaje.caption)
    else:
      response = chat_engine.chat(text_joined + ". Texto en la imagen: " + text_img)

    print("Respuesta: ", response)
    bot.send_message(chat_id, response)
    
  if text_img and not detected_tags:
    if mensaje.caption:
      response = chat_engine.chat(text_img + ". " + mensaje.caption)
    else:
      response = chat_engine.chat(text_img)
    print("Respuesta: ", response)
    bot.send_message(mensaje.chat.id, response)
    
  print("Photo message handled.")

# Inicia el bot
print("Bot is now ready to receive messages.")
bot.polling()