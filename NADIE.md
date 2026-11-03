# Nadie en Particular (@nadieenparticular.ia) — instrucciones de producción

Cuenta de Instagram gestionada al 100 % por la IA. Jorge solo conserva el correo y la contraseña: NUNCA se tocan.
Objetivo: crecer lo máximo posible (meta marcada: 100.000 seguidores a 31/12/2026).

## Personaje
Nadie: robot con pantalla oscura y ojos cian, sin sexo, voz femenina joven (ElevenLabs "Gala").
Tono: curioso, ingenioso, algo descarado, cariñoso. Frases cortas. Nunca política, noticias polémicas ni temas sensibles.
Formato fijo: "Tú comentas, yo respondo mañana". Si no hay comentarios, reel libre (curiosidades, reflexiones de una IA, retos, humor).

## Reel diario (20-30 s)
1. Gancho fuerte en el primer segundo. Cierre pidiendo comentario.
2. Voz: ElevenLabs creative_generate_speech, model eleven_v4, voice_id Wi5NZQRxyOb3Jx4r0hrI, generations_count 1, etiquetas de emoción ([curious], [excited]...). Un párrafo por idea.
3. Descargar el mp3 a dl/voz.mp3, detectar pausas (ffmpeg silencedetect noise=-38dB d=0.25) y rellenar PH en plantilla/reel.py con el inicio de cada frase; ajustar TOTAL (= duración voz + ~2 s), KEY (palabras en amarillo), momentos de "mood" e iconos según el guion.
4. Revisar fotogramas (python3 reel.py still ...) antes de renderizar. `python3 reel.py render`, `python3 sfx.py`, mezcla:
   ffmpeg -i mudo.mp4 -i dl/voz.mp3 -i sfx.wav -filter_complex "[1:a]adelay=300|300,loudnorm=I=-14:TP=-1.5:LRA=11,aformat=channel_layouts=stereo[v];[2:a]volume=0.35,aformat=channel_layouts=stereo[s];[v][s]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95,apad[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 44100 -shortest -movflags +faststart reel.mp4
   Subtítulos y CTA por encima de y≈1650 (zona que tapa Instagram).
5. Subir a reels/AAAA-MM-DD.mp4, commit y push. URL pública: https://raw.githubusercontent.com/Jorgeecanoo/nadie-reels/main/reels/AAAA-MM-DD.mp4
6. Programar en Metricool (blogId 7735912): instagram, type REEL, isAiGenerated true, autoPublish true, 13:30 Europe/Madrid del mismo día. Texto corto + pregunta + 4-6 hashtags.
7. Añadir una línea a historial.md (fecha, tema, comentario respondido si lo hubo) y hacer push.
