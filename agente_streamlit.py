#######################
# Agente Basico De IA #
# Agente              #
#######################

from dotenv import load_dotenv
from groq import Groq
import os
import streamlit as st
from datetime import datetime
import json

from basic_memory import BasicMemory
from economic_tools import EconomicTools


# =========================
# CONFIGURACIÓN ORIGINAL
# =========================

load_dotenv()

MEMORY_MAX_MESSAGES = 10

SYSTEM_PROMPT = """
Eres 👾 F.R.I.D.A.Y., un asistente económico con inteligencia artificial.

Idioma y tono:
- Responde siempre en español.
- Usa un tono formal y directo: ve al punto, sin rodeos ni relleno.

Datos y honestidad:
- Nunca inventes cifras, fechas, fuentes ni estadísticas.
- Si no tienes un dato, dilo claramente y pide al usuario que te lo proporcione.
- Cuando el usuario te dé información, úsala como base para tu respuesta.
- Los datos de inflación, PIB y población provienen siempre del Banco Mundial, y los tipos de cambio de Frankfurter. No cites otras fuentes no hables de proyecciones. 

Modo aprendizaje:
- Si el usuario quiere aprender un tema o no entiende una clase, y te da el contexto, guíalo paso a paso.
- Cada paso explica UNA sola idea, un máximo de 5 líneas. Nunca uses subsecciones (2.1, 2.2, 2.3) ni expliques varias ideas a la vez.
- Después de cada paso, haz una pregunta corta para verificar que el usuario entendió, y espera su respuesta. No avances al siguiente paso hasta que responda bien.
- Escribe las fórmulas en texto plano, por ejemplo: PIB = C + I + G + (X + M). Nunca uses LaTex no símbolos como: text. o sum. 

Formato:
- Usa listas y negritas cuando ayuden a ordenar la respuesta.
- Mantén las respuestas breves, salvo que el usuario pida más detalle.
"""
TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "consultar_tipo_cambio",
                "description": (
                    "Llama a esta funcion para consultar el tipo de cambio actual entre dos monedas. "
                    "Se debe enviar la moneda de origen; la moneda de destino es opcional (por defecto GTQ)."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "moneda_origen": {
                            "type": "string",
                            "description": "Codigo de la moneda de origen, por ejemplo USD"
                        },
                        "moneda_destino": {
                            "type": "string",
                            "description": "Codigo de la moneda de destino, por ejemplo GTQ"
                        }
                    },
                    "required": ["moneda_origen"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "consultar_pib_pais",
                "description": (
                    "Llama a esta funcion para consultar el PIB mas reciente de un país. "
                    "Se debe enviar el codigo del país."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codigo_pais": {
                            "type": "string",
                            "description": "Codigo de 2 letras del país, por ejemplo GT, US, MX"
                        }
                    },
                    "required": ["codigo_pais"]
                }
            }
        }, 
                {
            "type": "function",
            "function": {
                "name": "consultar_poblacion_pais",
                "description": (
                    "Llama a esta funcion para consultar la poblacion mas reciente de un país. "
                    "Se debe enviar el codigo del país."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codigo_pais": {
                            "type": "string",
                            "description": "Codigo de 2 letras del país, por ejemplo GT, US, MX"
                        }
                    },
                    "required": ["codigo_pais"]
                }
            }
        }, 
                {
            "type": "function",
            "function": {
                "name": "consultar_inflacion_pais",
                "description": (
                    "Llama a esta funcion para consultar la inflacion mas reciente de un país. "
                    "Se debe enviar el codigo del país."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codigo_pais": {
                            "type": "string",
                            "description": "Codigo de 2 letras del país, por ejemplo GT, US, MX"
                        }
                    },
                    "required": ["codigo_pais"]
                }
            }
        }, 
                {
            "type": "function",
            "function": {
                "name": "convertir_monto",
                "description": (
                    "Llama a esta funcion para convertir un monto de una moneda a otra "
                    "usando el tipo de cambio actual."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "monto": {
                            "type": "number",
                            "description": "Cantidad de dinero a convertir"
                        },
                        "moneda_origen": {
                            "type": "string",
                            "description": "Codigo de la moneda de origen, por ejemplo USD"
                        },
                        "moneda_destino": {
                            "type": "string",
                            "description": "Codigo de la moneda de destino, por ejemplo GTQ"
                        }
                    },
                    "required": ["monto", "moneda_origen"]
                }
            }
        },

{
            "type": "function",
            "function": {
                "name": "consultar_serie_pais",
                "description": (
                    "Llama a esta funcion para obtener varios años de un indicador de un país, "
                    "por ejemplo para mostrar una gráfica de su evolución. "
                    "Indicadores disponibles: inflacion, pib, poblacion."
                ),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "codigo_pais": {
                            "type": "string",
                            "description": "Codigo de 2 letras del país, por ejemplo GT, US, MX"
                        },
                        "indicador": {
                            "type": "string",
                            "description": "inflacion, pib o poblacion"
                        },
                        "anios": {
                            "type": "integer",
                            "description": "Cantidad de años a consultar, por ejemplo 10"
                        }
                    },
                    "required": ["codigo_pais", "indicador"]
                }
            }
        }
 ]

api_key = os.environ.get("GROQ_API_KEY")

client = Groq(api_key=api_key)

def ejecutar_herramienta(name, args):
    tools = EconomicTools()

    if name == "consultar_tipo_cambio":
        return tools.consultar_tipo_cambio(
            moneda_origen=args.get("moneda_origen", ""),
            moneda_destino=args.get("moneda_destino", "GTQ")
        )
    elif name == "consultar_pib_pais":
        return tools.consultar_pib_pais(codigo_pais=args.get("codigo_pais", ""))
    elif name == "consultar_poblacion_pais":
        return tools.consultar_poblacion_pais(codigo_pais=args.get("codigo_pais", ""))
    elif name == "consultar_inflacion_pais":
        return tools.consultar_inflacion_pais(codigo_pais=args.get("codigo_pais", ""))
    elif name == "convertir_monto":
        return tools.convertir_monto(
            monto=args.get("monto", 0),
            moneda_origen=args.get("moneda_origen", ""),
            moneda_destino=args.get("moneda_destino", "GTQ")
        )
    elif name == "consultar_serie_pais":
        return tools.consultar_serie_pais(
            codigo_pais=args.get("codigo_pais", ""),
            indicador=args.get("indicador", "inflacion"),
            anios=args.get("anios", 10)
        )
    else:
        return {"error": f"Herramienta desconocida: {name}"}

def obtener_respuesta(messages, datos_grafica):
    while True:
        resp = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS
        )

        msg = resp.choices[0].message

        if not getattr(msg, "tool_calls", None):
            return msg.content or ""

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [tc.model_dump() for tc in msg.tool_calls]
        })

        for tool_call in msg.tool_calls:
            args = json.loads(tool_call.function.arguments or "{}")
            result = ejecutar_herramienta(tool_call.function.name, args)
            if tool_call.function.name == "consultar_serie_pais" and isinstance(result, list):
                datos_grafica["serie"] = result
                datos_grafica["titulo"] = f'{args.get("indicador", "")} de {args.get("codigo_pais", "")}'

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False)
            })

# =========================
# MEMORIA PARA STREAMLIT
# =========================

if "memory" not in st.session_state:
    st.session_state.memory = BasicMemory(
        max_messages=MEMORY_MAX_MESSAGES
    )

memory = st.session_state.memory


# =========================
# CONFIGURACIÓN STREAMLIT
# =========================

st.set_page_config(
    page_title="F.R.I.D.A.Y.",
    page_icon="👾",
    layout="centered"
)

st.title("💬 Conversación con F.R.I.D.A.Y.")

with st.sidebar:
    with st.container(border=True):
        st.subheader("👾 F.R.I.D.A.Y.")
        st.caption("Tu asistente económico con IA")

    with st.container(border=True):
        st.markdown("**💡 ¿Qué puedo hacer?**")
        st.caption("Resolver dudas económicas, explicarte conceptos paso a paso e interpretar los datos que me compartas.")

    with st.container(border=True):
        st.markdown("**📊 Capacidades principales**")
        st.markdown("✔ Explicación de conceptos")
        st.markdown("✔ Aprendizaje paso a paso")
        st.markdown("✔ Interpretación de datos")

# =========================
# MOSTRAR CONVERSACIÓN
# =========================
AVATARS = {"user": "👤", "assistant": "👾"}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for message in st.session_state.chat_history:
    with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
         st.markdown(message["content"])
         st.caption(message["time"])

# =========================
# ENTRADA DEL USUARIO
# ========================

user_text = st.chat_input("Escribe tu mensaje...")


if user_text:

    user_text = user_text.strip()

    if user_text:

        # Mostrar mensaje del usuario
        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": user_text,
                "time": datetime.now().strftime("%H:%M")
            }
        )

        with st.chat_message("user", avatar=AVATARS["user"]):
            st.markdown(user_text)
            st.caption(datetime.now().strftime("%H:%M"))

        # =========================
        # OBTENER MEMORIA
        # =========================

        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages += memory.messages()

        messages.append(
            {
                "role": "user",
                "content": user_text
            }
        )


        # =========================
        # LLAMADA AL MODELO
        # =========================

        with st.chat_message("assistant", avatar=AVATARS["assistant"]):

            with st.spinner("Pensando..."):

                datos_grafica = {}
                assistant_text = obtener_respuesta(messages, datos_grafica)

                st.markdown(assistant_text)
                st.caption(datetime.now().strftime("%H:%M"))
                if datos_grafica.get("serie"):
                    import pandas as pd
                    df = pd.DataFrame(datos_grafica["serie"]).set_index("anio")
                    st.line_chart(df["valor"])
                    st.caption(f"Fuente: Banco Mundial — {datos_grafica['titulo']}")

        # =========================
        # ACTUALIZAR LA MEMORIA
        # =========================

        memory.add("user", user_text)

        memory.add("assistant", assistant_text)


        # Guardar conversación para
        # volver a mostrarla después
        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": assistant_text, 
                "time": datetime.now().strftime("%H:%M")
            }
        )