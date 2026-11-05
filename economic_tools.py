#######################
# Agente Economico    #
# Herramientas        #
#######################

# Importacion para hacer peticiones a APIs
import requests

class EconomicTools:

    def __init__(self):
        pass

    # Herramienta para consultar el tipo de cambio con Frankfurter API
    def consultar_tipo_cambio(self, moneda_origen: str = "", moneda_destino: str = "GTQ"):
        print(f"Herramienta consultar_tipo_cambio llamada con {moneda_origen} -> {moneda_destino}")

        if not moneda_origen:
            return "Error: Se requiere la moneda de origen para consultar el tipo de cambio."

        url = (
            f"https://api.frankfurter.dev/v2/rates"
            f"?base={moneda_origen}&quotes={moneda_destino}"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data[0]
        except Exception as e:
            print(f"Error al consultar_tipo_cambio: {moneda_origen} -> {moneda_destino}. Error: {e}")
            return f"ERROR: No se pudo obtener el tipo de cambio de {moneda_origen} a {moneda_destino}"

    # Herramienta para consultar el PIB de un país con la API del Banco Mundial
    def consultar_pib_pais(self, codigo_pais: str = ""):
        print(f"Herramienta consultar_pib_pais llamada con {codigo_pais}")

        if not codigo_pais:
            return "Error: Se requiere el código del país para consultar el PIB."

        url = (
            f"https://api.worldbank.org/v2/country/{codigo_pais}"
            f"/indicator/NY.GDP.MKTP.CD?format=json"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            dato_mas_reciente = data[1][0]
            return dato_mas_reciente
        except Exception as e:
            print(f"Error al consultar_pib_pais: {codigo_pais}. Error: {e}")
            return f"ERROR: No se pudo obtener el PIB para el país {codigo_pais}"


    # Herramienta para consultar la población de un país con la API del Banco Mundial
    def consultar_poblacion_pais(self, codigo_pais: str = ""):
        print(f"Herramienta consultar_poblacion_pais llamada con {codigo_pais}")

        if not codigo_pais:
            return "Error: Se requiere el código del país para consultar la población."

        url = (
            f"https://api.worldbank.org/v2/country/{codigo_pais}"
            f"/indicator/SP.POP.TOTL?format=json"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            dato_mas_reciente = data[1][0]
            return dato_mas_reciente
        except Exception as e:
            print(f"Error al consultar_poblacion_pais: {codigo_pais}. Error: {e}")
            return f"ERROR: No se pudo obtener la población para el país {codigo_pais}"


    # Herramienta para consultar la inflación de un país con la API del Banco Mundial
    def consultar_inflacion_pais(self, codigo_pais: str = ""):
        print(f"Herramienta consultar_inflacion_pais llamada con {codigo_pais}")

        if not codigo_pais:
            return "Error: Se requiere el código del país para consultar la inflación."

        url = (
            f"https://api.worldbank.org/v2/country/{codigo_pais}"
            f"/indicator/FP.CPI.TOTL.ZG?format=json"
        )

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()
            dato_mas_reciente = data[1][0]
            return dato_mas_reciente
        except Exception as e:
            print(f"Error al consultar_inflacion_pais: {codigo_pais}. Error: {e}")
            return f"ERROR: No se pudo obtener la inflación para el país {codigo_pais}"

    # Herramienta para convertir un monto entre dos monedas
    def convertir_monto(self, monto: float = 0, moneda_origen: str = "", moneda_destino: str = "GTQ"):
        print(f"Herramienta convertir_monto llamada con {monto} {moneda_origen} -> {moneda_destino}")

        if not monto or not moneda_origen:
            return "Error: Se requiere el monto y la moneda de origen para hacer la conversion."

        tipo_cambio = self.consultar_tipo_cambio(moneda_origen, moneda_destino)

        if isinstance(tipo_cambio, str):
            return tipo_cambio

        tasa = tipo_cambio.get("rate")
        resultado = monto * tasa

        return {
            "monto_original": monto,
            "moneda_origen": moneda_origen,
            "moneda_destino": moneda_destino,
            "tasa": tasa,
            "monto_convertido": round(resultado, 2)
            }
                # Herramienta para consultar varios años de un indicador del Banco Mundial
    def consultar_serie_pais(self, codigo_pais: str = "", indicador: str = "inflacion", anios: int = 10):
        print(f"Herramienta consultar_serie_pais llamada con {codigo_pais}, {indicador}, {anios}")

        indicadores = {
            "inflacion": "FP.CPI.TOTL.ZG",
            "pib": "NY.GDP.MKTP.CD",
            "poblacion": "SP.POP.TOTL"
        }

        if not codigo_pais:
            return "Error: Se requiere el código del país."

        if indicador not in indicadores:
            return "Error: El indicador debe ser inflacion, pib o poblacion."

        url = (
            f"https://api.worldbank.org/v2/country/{codigo_pais}"
            f"/indicator/{indicadores[indicador]}?format=json&per_page={anios}"
        )

        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            data = response.json()
            serie = []
            for punto in data[1]:
                if punto["value"] is not None:
                    serie.append({"anio": punto["date"], "valor": punto["value"]})
            serie.reverse()
            return serie
        except Exception as e:
            print(f"Error al consultar_serie_pais: {codigo_pais}. Error: {e}")
            return f"ERROR: No se pudo obtener la serie de {indicador} para {codigo_pais}"