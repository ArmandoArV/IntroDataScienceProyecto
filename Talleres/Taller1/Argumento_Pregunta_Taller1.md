# Argumento: ¿Por qué analizar la desigualdad educativa y su correlación con la migración en la RM?

## Pregunta propuesta

> **¿Cómo varía la desigualdad educativa (ESCOLARIDAD) entre comunas de la Región Metropolitana, y existe correlación espacial con la concentración de población migrante?**

---

## 1. Relevancia social y de política pública

La Región Metropolitana concentra más de 7 millones de habitantes (según los microdatos censales con los que trabajamos: 7,112,808 registros). Dentro de este territorio coexisten **52 comunas** con realidades socioeconómicas profundamente distintas.

La educación es uno de los indicadores más robustos de desarrollo humano y movilidad social. Al mismo tiempo, Chile ha experimentado un crecimiento sostenido de la inmigración en la última década, concentrándose fuertemente en la RM. Entender **dónde** se acumula la desigualdad educativa y si esta se relaciona con la distribución espacial de la población migrante tiene implicaciones directas para:

- **Planificación de servicios públicos** (escuelas, programas de integración).
- **Focalización de políticas sociales** (subsidios, capacitación laboral).
- **Comprensión de dinámicas urbanas** (segregación residencial, gentrificación).

Esto conecta directamente con lo visto en **Clase 1** sobre cómo la ciencia de datos busca responder preguntas que impactan en el mundo real, y el ejemplo de **John Snow (1854)** que usó análisis espacial para entender la epidemia de cólera en Londres — nosotros haríamos algo análogo: usar la dimensión geográfica para revelar patrones ocultos.

---

## 2. Conexión con los conceptos de clase

### 2.1 Análisis Exploratorio de Datos (Clase 2)

La pregunta requiere aplicar directamente las herramientas de **EDA** presentadas en clase:

| Herramienta EDA | Aplicación en nuestra pregunta |
|---|---|
| **Histogramas** | Distribución de escolaridad por comuna (ya se usó `plt.hist` en el Taller con `P09`; aquí lo aplicamos a `ESCOLARIDAD`) |
| **Estadísticas de resumen** (media, mediana, desviación estándar) | Comparar escolaridad promedio entre comunas y detectar dispersión |
| **Diagramas de caja (boxplots)** | Visualizar la distribución de escolaridad por comuna, identificando outliers y asimetrías |
| **Gráficos de dispersión** | Relación entre % migrantes y escolaridad promedio por comuna |
| **Coeficiente de Pearson (ρ)** | Cuantificar la correlación entre concentración migrante y nivel educativo |

### 2.2 Distribuciones de probabilidad (Clase 2)

La escolaridad en distintas comunas probablemente siga distribuciones con formas muy diferentes:
- Comunas de altos ingresos → distribuciones concentradas en valores altos (poca varianza).
- Comunas con mayor diversidad socioeconómica → distribuciones bimodales o con alta dispersión.

Esto permite discutir conceptos de **función de densidad**, **varianza** y **comparación de distribuciones**.

### 2.3 Testeo de hipótesis (Clase 2)

Podemos formular una **hipótesis nula** concreta:

> **H₀**: No existe diferencia significativa en la escolaridad promedio entre comunas con alta y baja proporción de población migrante.

Y evaluarla usando:
- **Bootstrapping** para construir intervalos de confianza.
- **Testeo de permutaciones** (A/B testing) para evaluar si la diferencia observada es estadísticamente significativa.
- Cálculo de **valor p** para determinar si rechazamos H₀.

### 2.4 Ciencia de Datos Geográfica (Clase 1)

La dimensión **espacial** es lo que distingue esta pregunta de un análisis puramente tabular. Usando **GeoPandas** y el shapefile de zonas censales (ya cargado en el Taller), podemos:

- Generar **mapas coropléticos** de escolaridad promedio por zona censal.
- Generar **mapas coropléticos** de proporción de migrantes por zona.
- Comparar visualmente ambos mapas para detectar patrones de co-localización.

Esto conecta con la idea de **relaciones espaciales** de la Clase 1 y demuestra el valor de los datos geoespaciales.

---

## 3. Factibilidad con los datos disponibles

La pregunta es **completamente realizable** con el dataset `CensoRM.csv` que ya tenemos. Las variables clave son:

| Variable | Descripción | Uso |
|---|---|---|
| `ESCOLARIDAD` | Años de escolaridad (0–22) | Variable dependiente principal |
| `P10` | Lugar de nacimiento (misma comuna, otra comuna, otro país) | Identificar migrantes internacionales |
| `P10PAIS` / `P10PAIS_GRUPO` | País de nacimiento | Clasificar origen migratorio |
| `P12` | Residencia habitual | Confirmar residencia actual |
| `P12A_LLEGADA` | Año de llegada al país | Temporalidad migratoria |
| `COMUNA` | Código de comuna | Agrupación geográfica |
| `P08` | Sexo | Control demográfico |
| `P09` | Edad | Control demográfico |

No se requieren datos externos: todo está en el censo.

---

## 4. Métodos propuestos (paso a paso)

### Paso 1: Preparación de datos
```python
# Filtrar población relevante (ej: mayores de 25 años, para escolaridad completa)
censo_adultos = censo[censo['P09'] >= 25]

# Crear variable binaria de migrante internacional
censo_adultos['MIGRANTE'] = (censo['P10'] == 4).astype(int)  # nacido en otro país
```

### Paso 2: Estadísticas descriptivas por comuna
```python
# Escolaridad promedio y % migrantes por comuna
stats_comuna = censo_adultos.groupby('COMUNA').agg(
    escolaridad_media=('ESCOLARIDAD', 'mean'),
    escolaridad_std=('ESCOLARIDAD', 'std'),
    pct_migrante=('MIGRANTE', 'mean'),
    poblacion=('PERSONAN', 'count')
)
```

### Paso 3: Análisis de correlación
```python
# Coeficiente de Pearson (Clase 2)
from scipy.stats import pearsonr
r, p_value = pearsonr(stats_comuna['escolaridad_media'], stats_comuna['pct_migrante'])

# Scatter plot
plt.scatter(stats_comuna['pct_migrante'], stats_comuna['escolaridad_media'])
plt.xlabel('% Población Migrante')
plt.ylabel('Escolaridad Promedio (años)')
```

### Paso 4: Visualización espacial
```python
# Merge con GeoDataFrame y generar mapa coroplético (como en el Taller)
zonas_censales = zonas_censales.merge(stats_zona, on='ID_ZONA_U')
zonas_censales.plot(column='escolaridad_media', legend=True, cmap='RdYlGn')
```

### Paso 5: Testeo de hipótesis (opcional, avanzado)
```python
# Bootstrap para intervalo de confianza de la correlación
bootstrap_corrs = []
for _ in range(10000):
    sample = stats_comuna.sample(frac=1, replace=True)
    r_boot, _ = pearsonr(sample['escolaridad_media'], sample['pct_migrante'])
    bootstrap_corrs.append(r_boot)
ci = np.percentile(bootstrap_corrs, [2.5, 97.5])
```

---

## 5. ¿Por qué esta pregunta es más atractiva que otras alternativas?

| Criterio | Esta pregunta | Alternativa simple (ej: solo distribución etaria) |
|---|---|---|
| **Variables involucradas** | Múltiples (escolaridad, migración, geografía, edad) | Una sola (edad) |
| **Métodos demostrados** | EDA + correlación + mapas + hipótesis | Solo histograma |
| **Relevancia social** | Alta (desigualdad, migración, política pública) | Moderada |
| **Complejidad adecuada** | Suficiente para demostrar competencias sin ser inabordable | Demasiado básica |
| **Visualización** | Scatter + boxplots + mapas coropléticos | Un solo gráfico |
| **Conexión con Clase 1 y 2** | Usa conceptos de ambas clases | Solo herramientas básicas |

---

## 6. Conclusión

Esta pregunta es atractiva porque:

1. **Es socialmente relevante**: aborda desigualdad educativa y migración, dos temas centrales en Chile.
2. **Integra múltiples conceptos del curso**: EDA, correlación de Pearson, distribuciones, bootstrapping, testeo de hipótesis, y análisis geoespacial.
3. **Es factible**: todos los datos necesarios ya están en el dataset del Taller.
4. **Permite visualizaciones impactantes**: mapas coropléticos que revelan segregación espacial.
5. **Conecta con el espíritu de la ciencia de datos** (Clase 1): extraer información significativa de los datos para responder preguntas que importan.

> *"Es la ciencia de extraer información significativa de los datos"* — Definición de Ciencia de Datos, Clase 1.
