# 🎰 Ruleta Bot — Discord

Bot de Discord interactivo con ruleta del 1 al 20. Hecho por **Glitch / Gamer64**.

---

## ✨ Características

| Feature | Descripción |
|---------|-------------|
| 🎰 `/ruleta` | Abre la ruleta con animación en tiempo real |
| 🔄 Botón GIRAR | Animación de 5 pasos con aceleración/frenado |
| 📊 Botón Stats | Tus estadísticas privadas (ephemeral) |
| ⚔️ Botón Duelo | Inicia un duelo con otro usuario |
| 🏅 `/top` | Leaderboard del servidor |
| 📊 `/mis-stats` | Ver tus stats completos |

---

## 🛠️ Setup

### 1. Clonar / Instalar dependencias

```bash
npm install
```

### 2. Crear el bot en Discord

1. Ir a https://discord.com/developers/applications
2. **New Application** → ponle nombre
3. Ve a **Bot** → habilita **Message Content Intent** (no es requerido pero recomendado)
4. Copia el **TOKEN**
5. Ve a **OAuth2** → copia el **Application ID** (CLIENT_ID)
6. Para invitar al bot: **OAuth2 → URL Generator** → scopes: `bot`, `applications.commands` → permisos: `Send Messages`, `Embed Links`, `Use Slash Commands`

### 3. Ejecutar

```bash
TOKEN=tu_token_aqui CLIENT_ID=tu_client_id_aqui node index.js
```

O con un archivo `.env` (instala `dotenv`):

```
TOKEN=tu_token
CLIENT_ID=tu_client_id
```

---

## 🎮 Cómo jugar

1. Escribe `/ruleta` en cualquier canal
2. Presiona **🎰 GIRAR** — la ruleta anima en tiempo real
3. Obtienes un número del 1 al 20 con su "título"
4. **≥ 10** = acierto ✅ | **< 10** = fallo ❌
5. Acumula racha y aparece en el `/top`

### Duelo
1. Presiona ⚔️ Duelo en tu mensaje de ruleta
2. Giras primero — se muestra tu número
3. El otro jugador acepta y gira
4. El número más alto gana!

---

## 🔢 Números especiales

- **1** ☠️ — La Maldición
- **7** 🍀 — El número de la suerte
- **13** 🖤 — Trece Negro
- **20** 💀 — JACKPOT legendario

---

## 📁 Estructura

```
ruleta-bot/
├── index.js       ← Todo el bot
├── package.json
└── README.md
```

---

## 🚀 Deploy en Render / Railway

El bot no necesita HTTP ni base de datos (usa RAM). Para mantenerlo vivo en Render:
- Build Command: `npm install`
- Start Command: `node index.js`
- Agrega `TOKEN` y `CLIENT_ID` como Environment Variables

> **Nota:** Los stats se resetean al reiniciar. Para persistencia, guárdalos en un `db.json` como en Androide PVP 😉

---

*Creado con ❤️ usando discord.js v14*
