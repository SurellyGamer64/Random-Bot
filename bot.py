# ==========================================
#   🎰 RULETA BOT - Python + discord.py
#   Por: Glitch / Gamer64
# ==========================================

import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import random
import os
from threading import Thread
from flask import Flask
from datetime import datetime

# ── CONFIG ──────────────────────────────────
TOKEN     = os.environ.get("TOKEN")
CLIENT_ID = os.environ.get("CLIENT_ID")

# ── FLASK (keep-alive) ───────────────────────
app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🎰 Ruleta Bot — Online</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                background: #0d0d0d;
                color: #eee;
                font-family: 'Segoe UI', sans-serif;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                min-height: 100vh;
                gap: 24px;
                overflow: hidden;
            }
            .glow {
                font-size: 3rem;
                font-weight: 900;
                letter-spacing: 4px;
                color: #ff6b00;
                text-shadow: 0 0 20px #ff6b00, 0 0 40px #ff3300;
                animation: pulse 2s ease-in-out infinite;
            }
            @keyframes pulse {
                0%, 100% { text-shadow: 0 0 20px #ff6b00, 0 0 40px #ff3300; }
                50%       { text-shadow: 0 0 40px #ff6b00, 0 0 80px #ff3300, 0 0 120px #ffaa00; }
            }
            .wheel {
                font-size: 5rem;
                animation: spin 3s linear infinite;
                display: inline-block;
            }
            @keyframes spin {
                from { transform: rotate(0deg); }
                to   { transform: rotate(360deg); }
            }
            .card {
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 16px;
                padding: 32px 48px;
                text-align: center;
                max-width: 420px;
                width: 90%;
                box-shadow: 0 0 40px rgba(255,107,0,0.15);
            }
            .status {
                display: inline-block;
                background: #00ff8820;
                border: 1px solid #00ff88;
                color: #00ff88;
                padding: 6px 18px;
                border-radius: 999px;
                font-size: 0.85rem;
                font-weight: 600;
                letter-spacing: 2px;
                text-transform: uppercase;
            }
            p { color: #888; font-size: 0.95rem; margin-top: 12px; }
            .numbers {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                justify-content: center;
                margin-top: 20px;
            }
            .num {
                background: #222;
                border: 1px solid #444;
                border-radius: 8px;
                width: 36px;
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 0.8rem;
                font-weight: 700;
                color: #aaa;
                transition: all 0.3s;
            }
            .num:hover { background: #ff6b00; color: #fff; border-color: #ff6b00; cursor: default; }
            .num.special { border-color: #ffd700; color: #ffd700; }
            footer { color: #444; font-size: 0.75rem; }
        </style>
    </head>
    <body>
        <div class="wheel">🎰</div>
        <div class="card">
            <div class="glow">RULETA BOT</div>
            <br>
            <span class="status">✅ Online</span>
            <p>Bot de Discord activo y funcionando.</p>
            <p>Usa <strong>/ruleta</strong> en tu servidor.</p>
            <div class="numbers">
                <div class="num">1</div><div class="num">2</div><div class="num">3</div>
                <div class="num">4</div><div class="num">5</div><div class="num">6</div>
                <div class="num special">7</div><div class="num">8</div><div class="num">9</div>
                <div class="num">10</div><div class="num">11</div><div class="num">12</div>
                <div class="num special">13</div><div class="num">14</div><div class="num">15</div>
                <div class="num">16</div><div class="num">17</div><div class="num">18</div>
                <div class="num">19</div><div class="num special">20</div>
            </div>
        </div>
        <footer>Glitch / Gamer64 — Ruleta Bot</footer>
    </body>
    </html>
    """

@app.route("/ping")
def ping():
    return "pong", 200

def run_flask():
    app.run(host="0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ── DATOS GLOBALES ───────────────────────────
# userId → {"wins": 0, "losses": 0, "total": 0, "last": None, "streak": 0}
user_stats: dict[str, dict] = {}
en_giro:    set[str]        = set()

NUMERO_LABELS = {
    1:  "1  — ☠️ Maldición",   2:  "2  — 😬 Bajo",
    3:  "3  — 🤞 Esperanza",    4:  "4  — 😐 Común",
    5:  "5  — 🌱 Creciendo",    6:  "6  — 😏 Clásico",
    7:  "7  — 🍀 Suerte",       8:  "8  — 🎱 Billar",
    9:  "9  — 🔱 Neptuno",      10: "10 — 💯 Perfecto",
    11: "11 — ⚡ Voltaje",      12: "12 — 🌙 Medianoche",
    13: "13 — 🖤 Trece Negro",  14: "14 — 💎 Diamante",
    15: "15 — 🔥 Fuego",        16: "16 — 🌊 Tsunami",
    17: "17 — 👑 Corona",       18: "18 — 🚀 Despegue",
    19: "19 — 🌟 Casi",         20: "20 — 💀 JACKPOT",
}

RULETA_FRAMES = [
    "🔴⚫🔴⚫🔴⚫🔴",
    "⚫🔴⚫🔴⚫🔴⚫",
    "🟡🔴⚫🔴⚫🔴🟡",
    "🔴🟡🔴⚫🔴🟡🔴",
    "⚫🔴🟡🔴🟡🔴⚫",
]

SPIN_LABELS = [
    "🟠 Iniciando...",
    "🟡 Acelerando...",
    "🟡 ¡A toda velocidad!",
    "🟢 Frenando...",
    "🔵 Casi...",
]

# ── HELPERS ──────────────────────────────────
def get_stats(user_id: str) -> dict:
    if user_id not in user_stats:
        user_stats[user_id] = {"wins": 0, "losses": 0, "total": 0, "last": None, "streak": 0}
    return user_stats[user_id]

def progress_bar(value: int, max_val: int = 20, size: int = 10) -> str:
    filled = round((value / max_val) * size)
    return "█" * filled + "░" * (size - filled)

def frame_ruleta(step: int) -> str:
    return RULETA_FRAMES[step % len(RULETA_FRAMES)]

# ── EMBEDS ───────────────────────────────────
def embed_espera(user: discord.User) -> discord.Embed:
    st = get_stats(str(user.id))
    streak_str = f"+{st['streak']}" if st["streak"] > 0 else str(st["streak"])
    last_str   = str(st["last"]) if st["last"] is not None else "—"
    embed = discord.Embed(
        title="🎰  RULETA  🎰",
        description=(
            f"> ¡Bienvenido/a, **{user.display_name}**!\n\n"
            "```\n"
            "  ┌─────────────────────────┐\n"
            "  │   1  ────────────  20   │\n"
            "  │      🔴 RULETA 🔴       │\n"
            "  │   ¿Dónde caerá hoy?     │\n"
            "  └─────────────────────────┘\n"
            "```\n"
            f"**📊 Tu historial:**\n"
            f"> 🎯 Partidas: `{st['total']}`  |  🏆 Racha: `{streak_str}`\n"
            f"> ✅ Aciertos ≥10: `{st['wins']}`  |  ❌ Debajo de 10: `{st['losses']}`\n"
            f"> 🔢 Último número: `{last_str}`"
        ),
        color=0xFF6B00,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text="¡Presiona GIRAR para empezar!")
    return embed

def embed_girando(frame_idx: int, step: int) -> discord.Embed:
    label = SPIN_LABELS[step] if step < len(SPIN_LABELS) else "⏳ Decidiendo..."
    bar   = progress_bar(step + 1, 5, 10)
    embed = discord.Embed(
        title="🎰  GIRANDO  🎰",
        description=(
            f"```\n"
            f"  {frame_ruleta(frame_idx)}\n\n"
            f"  [{bar}] {step+1}/5\n"
            "```\n"
            f"**{label}**\n\n"
            "_No cierres el chat... 👀_"
        ),
        color=0xFFD700,
    )
    embed.set_footer(text="Gira... gira... gira...")
    return embed

def embed_resultado(numero: int, user: discord.User) -> discord.Embed:
    st      = get_stats(str(user.id))
    is_high = numero >= 10
    jackpot  = numero == 20
    maldicion = numero == 1

    color = 0x00FF88 if is_high else 0xFF3333
    if jackpot:   color = 0xFFD700
    if maldicion: color = 0x111111

    bar    = progress_bar(numero, 20, 12)
    label  = NUMERO_LABELS.get(numero, str(numero))
    titulo = "🎰  RESULTADO  🎰"
    reaccion = ""

    if jackpot:
        titulo   = "💀  ¡JACKPOT — 20!  💀"
        reaccion = "> ⚡ **¡EL MÁXIMO ABSOLUTO! ¡LEGENDARIO!**"
    elif numero == 19:
        reaccion = "> 😤 ¡Tan cerca del 20!"
    elif numero == 7:
        reaccion = "> 🍀 ¡El número de la SUERTE!"
    elif maldicion:
        titulo   = "☠️  ¡LA MALDICIÓN — 1!  ☠️"
        reaccion = "> 💀 ¡El peor número posible!"
    elif is_high:
        reaccion = "> ✅ ¡Buen número!"
    else:
        reaccion = "> ❌ ¡Mala suerte!"

    streak_str = f"+{st['streak']}" if st["streak"] > 0 else str(st["streak"])

    embed = discord.Embed(
        title=titulo,
        description=(
            f"> 🎯 **{user.display_name}** sacó:\n\n"
            "```\n"
            f"         ┌──────────────┐\n"
            f"         │      {str(numero).zfill(2)}      │\n"
            f"         │  {label:<18}│\n"
            f"         └──────────────┘\n"
            "```\n"
            f"`[{bar}]` **{numero}/20**\n\n"
            f"{reaccion}\n\n"
            f"**📊 Stats actualizados:**\n"
            f"> 🏆 Racha actual: `{streak_str}`  |  🎮 Total: `{st['total']}`"
        ),
        color=color,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text="¡Presiona GIRAR DE NUEVO para otra vuelta!")
    return embed

def embed_duelo_result(retador: discord.User, retado: discord.User, n1: int, n2: int) -> discord.Embed:
    empate = n1 == n2
    ganador = retador if n1 > n2 else retado if n2 > n1 else None
    color  = 0xFFAA00 if empate else 0x00FF88
    bar1   = progress_bar(n1, 20, 8)
    bar2   = progress_bar(n2, 20, 8)

    r1 = retador.display_name[:14].ljust(14)
    r2 = retado.display_name[:14].ljust(14)

    resultado = (
        "> 🤝 **¡EMPATE PERFECTO!** ¡Imposible!"
        if empate
        else f"> 🏆 **¡{ganador.display_name} GANA EL DUELO!**"
    )

    embed = discord.Embed(
        title="⚔️  RESULTADO DEL DUELO  ⚔️",
        description=(
            "```\n"
            f"  {r1}: {str(n1).zfill(2)} — [{bar1}]\n"
            f"  {r2}: {str(n2).zfill(2)} — [{bar2}]\n"
            "```\n"
            f"{resultado}"
        ),
        color=color,
        timestamp=datetime.utcnow(),
    )
    return embed

def embed_top() -> discord.Embed:
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
    sorted_users = sorted(
        [(uid, s) for uid, s in user_stats.items() if s["total"] > 0],
        key=lambda x: x[1]["wins"],
        reverse=True,
    )[:5]

    if not sorted_users:
        desc = "_Nadie ha girado la ruleta todavía._"
    else:
        lines = []
        for i, (uid, s) in enumerate(sorted_users):
            streak = f"+{s['streak']}" if s["streak"] > 0 else str(s["streak"])
            lines.append(
                f"{medals[i]} <@{uid}> — ✅ `{s['wins']}` aciertos "
                f"en `{s['total']}` partidas (racha: `{streak}`)"
            )
        desc = "\n".join(lines)

    embed = discord.Embed(
        title="🏅  TOP RULETA  🏅",
        description=desc,
        color=0xFFD700,
        timestamp=datetime.utcnow(),
    )
    embed.set_footer(text="Acierto = número ≥ 10")
    return embed

# ── BOTONES ──────────────────────────────────
class BotonesInicio(discord.ui.View):
    def __init__(self, owner_id: str):
        super().__init__(timeout=300)
        self.owner_id = owner_id

    async def _check_owner(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.owner_id:
            await interaction.response.send_message(
                "⛔ ¡Esta ruleta no es tuya! Usa `/ruleta` para la tuya.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="🎰 GIRAR", style=discord.ButtonStyle.danger)
    async def girar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_owner(interaction): return
        if str(interaction.user.id) in en_giro:
            await interaction.response.send_message("⏳ ¡Ya estás girando! Espera...", ephemeral=True)
            return
        en_giro.add(str(interaction.user.id))
        await interaction.response.defer()
        await animar_giro(interaction, interaction.user, view_class="inicio")

    @discord.ui.button(label="📊 Mis Stats", style=discord.ButtonStyle.secondary)
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=embed_stats_user(interaction.user), ephemeral=True
        )

    @discord.ui.button(label="⚔️ Duelo", style=discord.ButtonStyle.primary)
    async def duelo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_owner(interaction): return
        if str(interaction.user.id) in en_giro:
            await interaction.response.send_message("⏳ ¡Estás girando! Termina primero.", ephemeral=True)
            return
        en_giro.add(str(interaction.user.id))
        await interaction.response.defer()
        numero = await animar_giro(interaction, interaction.user, view_class="duelo_post")
        await interaction.followup.send(
            f"⚔️ **{interaction.user.display_name}** sacó **{numero}**!\n"
            "Menciona a quien quieres retar con `/duelo @usuario`.",
            ephemeral=True,
        )


class BotonesResultado(discord.ui.View):
    def __init__(self, owner_id: str):
        super().__init__(timeout=300)
        self.owner_id = owner_id

    async def _check_owner(self, interaction: discord.Interaction) -> bool:
        if str(interaction.user.id) != self.owner_id:
            await interaction.response.send_message(
                "⛔ ¡Esta ruleta no es tuya!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="🔄 GIRAR DE NUEVO", style=discord.ButtonStyle.danger)
    async def girar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_owner(interaction): return
        if str(interaction.user.id) in en_giro:
            await interaction.response.send_message("⏳ ¡Ya estás girando!", ephemeral=True)
            return
        en_giro.add(str(interaction.user.id))
        await interaction.response.defer()
        await animar_giro(interaction, interaction.user, view_class="resultado")

    @discord.ui.button(label="📊 Stats", style=discord.ButtonStyle.secondary)
    async def stats(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            embed=embed_stats_user(interaction.user), ephemeral=True
        )

    @discord.ui.button(label="⚔️ Duelo", style=discord.ButtonStyle.primary)
    async def duelo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self._check_owner(interaction): return
        if str(interaction.user.id) in en_giro:
            await interaction.response.send_message("⏳ ¡Estás girando!", ephemeral=True)
            return
        en_giro.add(str(interaction.user.id))
        await interaction.response.defer()
        numero = await animar_giro(interaction, interaction.user, view_class="duelo_post")
        await interaction.followup.send(
            f"⚔️ **{interaction.user.display_name}** sacó **{numero}**!\n"
            "Menciona a quien quieres retar con `/duelo @usuario`.",
            ephemeral=True,
        )

    @discord.ui.button(label="🏅 Top", style=discord.ButtonStyle.success)
    async def top(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(embed=embed_top(), ephemeral=True)


class BotonAceptarDuelo(discord.ui.View):
    def __init__(self, retador: discord.User, retado: discord.User, n_retador: int):
        super().__init__(timeout=120)
        self.retador   = retador
        self.retado    = retado
        self.n_retador = n_retador

    @discord.ui.button(label="⚔️ ¡Aceptar Duelo!", style=discord.ButtonStyle.danger)
    async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.retado.id):
            await interaction.response.send_message("⛔ ¡Este duelo no es contigo!", ephemeral=True)
            return
        if str(interaction.user.id) in en_giro:
            await interaction.response.send_message("⏳ ¡Estás girando!", ephemeral=True)
            return
        en_giro.add(str(interaction.user.id))
        await interaction.response.defer()
        n2 = await animar_giro(interaction, interaction.user, view_class="resultado")
        await interaction.followup.send(
            embed=embed_duelo_result(self.retador, interaction.user, self.n_retador, n2)
        )
        self.stop()

    @discord.ui.button(label="🏳️ Rechazar", style=discord.ButtonStyle.secondary)
    async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != str(self.retado.id):
            await interaction.response.send_message("⛔ Solo el retado puede rechazar.", ephemeral=True)
            return
        embed = discord.Embed(
            title="🏳️ Duelo Rechazado",
            description=f"> **{interaction.user.display_name}** rechazó el duelo.",
            color=0x888888,
        )
        await interaction.response.edit_message(embed=embed, view=None)
        self.stop()

# ── ANIMACIÓN ────────────────────────────────
async def animar_giro(
    interaction: discord.Interaction,
    user: discord.User,
    view_class: str = "resultado",
) -> int:
    uid = str(user.id)
    delays = [0.4, 0.65, 0.9, 1.2, 1.65]

    for step in range(5):
        frame_idx = step + random.randint(0, 9)
        await interaction.edit_original_response(
            embed=embed_girando(frame_idx, step),
            view=None,
        )
        await asyncio.sleep(delays[step])

    numero = random.randint(1, 20)

    # Actualizar stats
    st = get_stats(uid)
    st["total"] += 1
    st["last"]   = numero
    if numero >= 10:
        st["wins"]   += 1
        st["streak"]  = st["streak"] + 1 if st["streak"] >= 0 else 1
    else:
        st["losses"] += 1
        st["streak"]  = st["streak"] - 1 if st["streak"] <= 0 else -1

    en_giro.discard(uid)

    # Elegir qué view mostrar
    if view_class == "inicio":
        view = BotonesInicio(uid)
    elif view_class == "duelo_post":
        view = BotonesResultado(uid)
    else:
        view = BotonesResultado(uid)

    await interaction.edit_original_response(
        embed=embed_resultado(numero, user),
        view=view,
    )
    return numero

# ── EMBED STATS ──────────────────────────────
def embed_stats_user(user: discord.User) -> discord.Embed:
    st = get_stats(str(user.id))
    streak_str = f"+{st['streak']}" if st["streak"] > 0 else str(st["streak"])
    tasa = f"{round(st['wins'] / st['total'] * 100)}%" if st["total"] > 0 else "—"
    embed = discord.Embed(
        title=f"📊 Stats de {user.display_name}",
        description=(
            f"> 🎮 Partidas totales: **{st['total']}**\n"
            f"> ✅ Aciertos (≥10):   **{st['wins']}**\n"
            f"> ❌ Fallos (<10):      **{st['losses']}**\n"
            f"> 🏆 Racha actual:      **{streak_str}**\n"
            f"> 🔢 Último número:     **{st['last'] or '—'}**\n"
            f"> 📈 Tasa de aciertos:  **{tasa}**"
        ),
        color=0x5865F2,
        timestamp=datetime.utcnow(),
    )
    embed.set_thumbnail(url=user.display_avatar.url)
    return embed

# ── BOT SETUP ────────────────────────────────
intents = discord.Intents.default()
bot     = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅  Bot listo como {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"⚙️   {len(synced)} slash commands sincronizados.")
    except Exception as e:
        print(f"❌  Error sincronizando comandos: {e}")

# ── SLASH COMMANDS ────────────────────────────
@bot.tree.command(name="ruleta", description="🎰 Abre la ruleta interactiva (1-20)")
async def ruleta(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=embed_espera(interaction.user),
        view=BotonesInicio(str(interaction.user.id)),
    )

@bot.tree.command(name="top", description="🏅 Ver el top de la ruleta")
async def top(interaction: discord.Interaction):
    await interaction.response.send_message(embed=embed_top())

@bot.tree.command(name="mis-stats", description="📊 Ver tus estadísticas de la ruleta")
async def mis_stats(interaction: discord.Interaction):
    await interaction.response.send_message(
        embed=embed_stats_user(interaction.user), ephemeral=True
    )

@bot.tree.command(name="duelo", description="⚔️ Reta a otro usuario con la ruleta")
@app_commands.describe(usuario="El jugador al que quieres retar")
async def duelo_cmd(interaction: discord.Interaction, usuario: discord.Member):
    if usuario.id == interaction.user.id:
        await interaction.response.send_message("⛔ ¡No puedes retarte a ti mismo!", ephemeral=True)
        return
    if usuario.bot:
        await interaction.response.send_message("⛔ ¡No puedes retar a un bot!", ephemeral=True)
        return
    if str(interaction.user.id) in en_giro:
        await interaction.response.send_message("⏳ ¡Estás girando! Termina primero.", ephemeral=True)
        return

    en_giro.add(str(interaction.user.id))
    await interaction.response.defer()

    # Giro del retador
    for step in range(5):
        frame_idx = step + random.randint(0, 9)
        await interaction.edit_original_response(
            embed=embed_girando(frame_idx, step), view=None
        )
        await asyncio.sleep([0.4, 0.65, 0.9, 1.2, 1.65][step])

    n_retador = random.randint(1, 20)
    st = get_stats(str(interaction.user.id))
    st["total"] += 1
    st["last"]   = n_retador
    if n_retador >= 10:
        st["wins"]  += 1
        st["streak"] = st["streak"] + 1 if st["streak"] >= 0 else 1
    else:
        st["losses"] += 1
        st["streak"]  = st["streak"] - 1 if st["streak"] <= 0 else -1

    en_giro.discard(str(interaction.user.id))

    bar = progress_bar(n_retador, 20, 8)
    r1  = interaction.user.display_name[:14].ljust(14)
    r2  = usuario.display_name[:14].ljust(14)

    embed = discord.Embed(
        title="⚔️  DUELO DE RULETA  ⚔️",
        description=(
            f"> **{interaction.user.display_name}** reta a **{usuario.display_name}**\n\n"
            "```\n"
            f"  {r1}: {str(n_retador).zfill(2)} — [{bar}]\n"
            f"  {r2}: ?? — [????????]\n"
            "```\n"
            f"**🎯 {usuario.display_name}** debe aceptar el duelo!\n"
            "_El ganador es quien saque el número más alto._"
        ),
        color=0xAA00FF,
    )
    embed.set_footer(text="¡Acepta el duelo!")

    await interaction.edit_original_response(
        embed=embed,
        view=BotonAceptarDuelo(interaction.user, usuario, n_retador),
    )

# ── MAIN ─────────────────────────────────────
if __name__ == "__main__":
    if not TOKEN:
        print("❌  Falta la variable de entorno TOKEN")
        exit(1)

    keep_alive()        # Inicia Flask en hilo separado
    bot.run(TOKEN)
