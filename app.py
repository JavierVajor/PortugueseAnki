import streamlit as st
from openai import OpenAI
import base64
from PIL import Image
import io
from pdf2image import convert_from_bytes

st.set_page_config(page_title="Profesor de Portugués Anki", page_icon="🇵🇹")

st.title("🇵🇹 Generador de Tarjetas Anki")
st.write("Sube una foto o la primera página de un PDF con tus marcas.")

# Barra lateral
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Prompt del "Profesor Experto"
SYSTEM_PROMPT = """Actúa como un experto profesor de Portugués de Portugal con más de 20 años de experiencia. 
Tu misión es crear un mazo de Anki exhaustivo a partir del material proporcionado.

INSTRUCCIONES DE PROCESAMIENTO:
1. Prioridad Absoluta a Marcas Visuales: Identifica CADA UNA de las palabras o frases subrayadas o resaltadas. Es obligatorio crear una tarjeta por cada elemento marcado.
2. Tratamiento de Verbos: Si ves tablas de conjugación, crea tarjetas con la conjugación completa en Presente de Indicativo.
3. Lógica de Preguntas: De Español a Portugués con frase de contexto obligatoria.
4. Enfoque Contrastivo: Énfasis en falsos amigos y reglas de transformación (Z -> Ç, etc.).
5. Formato: Una sola línea por tarjeta. Separador ';'. Usa <b> y <i>. No incluyas notas adicionales."""

def get_image_from_file(uploaded_file):
    # Leemos los bytes una sola vez
    file_bytes = uploaded_file.read()
    
    if uploaded_file.type == "application/pdf":
        try:
            # Convertimos solo la primera página
            images = convert_from_bytes(file_bytes, first_page=1, last_page=1)
            return images[0]
        except Exception as e:
            st.error(f"Error al procesar PDF: {e}")
            return None
    else:
        return Image.open(io.BytesIO(file_bytes))

if api_key:
    client = OpenAI(api_key=api_key)
    uploaded_file = st.file_uploader("Sube imagen o PDF...", type=["jpg", "jpeg", "png", "pdf"])

    if uploaded_file:
        image = get_image_from_file(uploaded_file)
        
        if image:
            # Mostrar miniatura para confirmar
            st.image(image, caption='Documento detectado', use_container_width=True)
            
            if st.button("Generar Tarjetas"):
                with st.spinner("Analizando marcas y traduciendo..."):
                    # Preparar imagen para la API
                    buffered = io.BytesIO()
                    image.save(buffered, format="JPEG")
                    base64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    
                    try:
                        response = client.chat.completions.create(
                            model="gpt-4o",
                            messages=[
                                {
                                    "role": "user",
                                    "content": [
                                        {"type": "text", "text": SYSTEM_PROMPT},
                                        {
                                            "type": "image_url",
                                            "image_url": {
                                                "url": f"data:image/jpeg;base64,{base64_image}"
                                            },
                                        },
                                    ],
                                }
                            ],
                            max_tokens=2500,
                        )
                        
                        cards = response.choices[0].message.content
                        st.success("¡Mazo generado!")
                        st.text_area("Copia esto en un .txt para Anki:", cards, height=300)
                        
                        st.download_button(
                            label="Descargar archivo Anki",
                            data=cards,
                            file_name="estudio_portugues.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"Error en la IA: {e}")
else:
    st.info("Introduce tu API Key en la izquierda para activar el sistema.")
