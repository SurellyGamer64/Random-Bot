// ==========================================
//   🎰 RULETA BOT - Bot de Discord Interactivo
//   Por: Glitch / Gamer64
// ==========================================

const { Client, GatewayIntentBits, SlashCommandBuilder, EmbedBuilder,
        ActionRowBuilder, ButtonBuilder, ButtonStyle, REST, Routes,
        ModalBuilder, TextInputBuilder, TextInputStyle } = require('discord.js');

// ── CONFIG ──────────────────────────────────
const TOKEN   = process.env.TOKEN;
const CLIENT_ID = process.env.CLIENT_ID;

// ── ESTADO GLOBAL ────────────────────────────
const stats       = new Map(); // userId → { wins, losses, total, lastNumber, streak }
const duelos      = new Map(); // messageId → { retador, retado, numero }
const enGiro      = new Set(); // userId → girando en este momento

const client = new Client({
  intents: [GatewayIntentBits.Guilds]
});

// ── HELPERS ──────────────────────────────────

function getUserStats(userId) {
  if (!stats.has(userId)) {
    stats.set(userId, { wins: 0, losses: 0, total: 0, lastNumber: null, streak: 0 });
  }
  return stats.get(userId);
}

function randomNum(min = 1, max = 20) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

// Los famosos "números de la suerte" que suenan cool
const NUMERO_LABELS = {
  1:  '1  — ☠️ Maldición',   2:  '2  — 😬 Bajo',
  3:  '3  — 🤞 Esperanza',    4:  '4  — 😐 Común',
  5:  '5  — 🌱 Creciendo',    6:  '6  — 😏 Clásico',
  7:  '7  — 🍀 Suerte',       8:  '8  — 🎱 Billar',
  9:  '9  — 🔱 Neptuno',      10: '10 — 💯 Perfecto',
  11: '11 — ⚡ Voltaje',      12: '12 — 🌙 Medianoche',
  13: '13 — 🖤 Trece Negro',  14: '14 — 💎 Diamante',
  15: '15 — 🔥 Fuego',        16: '16 — 🌊 Tsunami',
  17: '17 — 👑 Corona',       18: '18 — 🚀 Despegue',
  19: '19 — 🌟 Casi',         20: '20 — 💀 JACKPOT',
};

const RULETA_FRAMES = [
  '🔴⚫🔴⚫🔴⚫🔴',
  '⚫🔴⚫🔴⚫🔴⚫',
  '🟡🔴⚫🔴⚫🔴🟡',
  '🔴🟡🔴⚫🔴🟡🔴',
  '⚫🔴🟡🔴🟡🔴⚫',
];

function frameRuleta(step) {
  return RULETA_FRAMES[step % RULETA_FRAMES.length];
}

// Genera una barra de progreso visual
function progressBar(value, max = 20, size = 10) {
  const filled = Math.round((value / max) * size);
  return '█'.repeat(filled) + '░'.repeat(size - filled);
}

// ── EMBEDS ────────────────────────────────────

function embedEspera(user) {
  const st = getUserStats(user.id);
  return new EmbedBuilder()
    .setColor(0xFF6B00)
    .setTitle('🎰  RULETA  🎰')
    .setDescription([
      `> ¡Bienvenido/a, **${user.displayName}**!`,
      '',
      '```',
      '  ┌─────────────────────────┐',
      '  │   1  ────────────  20   │',
      '  │      🔴 RULETA 🔴       │',
      '  │   ¿Dónde caerá hoy?     │',
      '  └─────────────────────────┘',
      '```',
      `**📊 Tu historial:**`,
      `> 🎯 Partidas: \`${st.total}\`  |  🏆 Racha: \`${st.streak}\``,
      `> ✅ Aciertos ≥10: \`${st.wins}\`  |  ❌ Debajo de 10: \`${st.losses}\``,
      `> 🔢 Último número: \`${st.lastNumber ?? '—'}\``,
    ].join('\n'))
    .setFooter({ text: '¡Presiona GIRAR para empezar!' })
    .setTimestamp();
}

function embedGirando(frame, step) {
  const labels = ['🟠 Iniciando...', '🟡 Acelerando...', '🟡 A toda velocidad!', '🟢 Frenando...', '🔵 Casi...'];
  return new EmbedBuilder()
    .setColor(0xFFD700)
    .setTitle('🎰  GIRANDO  🎰')
    .setDescription([
      '```ansi',
      `\u001b[1;33m  ${frameRuleta(frame)} \u001b[0m`,
      '',
      `  ${progressBar(step + 1, 5)} ${step + 1}/5`,
      '```',
      `**${labels[step] ?? '⏳ Decidiendo...'}**`,
      '',
      '_No cierres el chat... 👀_',
    ].join('\n'))
    .setFooter({ text: 'Gira... gira... gira...' });
}

function embedResultado(numero, user) {
  const st = getUserStats(user.id);
  const isHigh = numero >= 10;
  const jackpot = numero === 20;
  const maldicion = numero === 1;

  let color = isHigh ? 0x00FF88 : 0xFF3333;
  if (jackpot) color = 0xFFD700;
  if (maldicion) color = 0x111111;

  const bar = progressBar(numero, 20, 12);

  let titulo = '🎰  RESULTADO  🎰';
  let reaccion = '';
  if (jackpot)   { titulo = '💀  ¡JACKPOT — 20!  💀'; reaccion = '> ⚡ **¡EL MÁXIMO ABSOLUTO! ¡LEGENDARIO!**'; }
  else if (numero === 19) reaccion = '> 😤 ¡Tan cerca del 20!';
  else if (numero === 7)  reaccion = '> 🍀 ¡El número de la SUERTE!';
  else if (maldicion)    { titulo = '☠️  ¡LA MALDICIÓN — 1!  ☠️'; reaccion = '> 💀 ¡El peor número posible!'; }
  else if (isHigh) reaccion = '> ✅ ¡Buen número!';
  else             reaccion = '> ❌ ¡Mala suerte!';

  return new EmbedBuilder()
    .setColor(color)
    .setTitle(titulo)
    .setDescription([
      `> 🎯 **${user.displayName}** sacó:`,
      '',
      '```',
      `         ┌──────────────┐`,
      `         │      ${numero.toString().padStart(2,'0')}      │`,
      `         │  ${NUMERO_LABELS[numero] ?? numero}  │`,
      `         └──────────────┘`,
      '```',
      `\`[${bar}]\` **${numero}/20**`,
      '',
      reaccion,
      '',
      `**📊 Stats actualizados:**`,
      `> 🏆 Racha actual: \`${st.streak}\`  |  🎮 Total: \`${st.total}\``,
    ].join('\n'))
    .setFooter({ text: '¡Presiona GIRAR DE NUEVO para otra vuelta!' })
    .setTimestamp();
}

function embedDuelo(retador, retado, numeroRetador) {
  return new EmbedBuilder()
    .setColor(0xAA00FF)
    .setTitle('⚔️  DUELO DE RULETA  ⚔️')
    .setDescription([
      `> **${retador.displayName}** reta a **${retado.displayName}**`,
      '',
      '```',
      `  ${retador.displayName}: ${numeroRetador.toString().padStart(2,'0')} — ${progressBar(numeroRetador, 20, 8)}`,
      `  ${retado.displayName}:  ?? — ¿¿¿¿¿¿¿¿??`,
      '```',
      `**🎯 ${retado.displayName}** debe girar su ruleta!`,
      '_El ganador es quien saque el número más alto._',
    ].join('\n'))
    .setFooter({ text: '¡Acepta el duelo!' });
}

function embedDueloResult(retador, retado, n1, n2) {
  const ganador = n1 > n2 ? retador : n2 > n1 ? retado : null;
  const empate  = n1 === n2;
  const color   = empate ? 0xFFAA00 : 0x00FF88;

  return new EmbedBuilder()
    .setColor(color)
    .setTitle('⚔️  RESULTADO DEL DUELO  ⚔️')
    .setDescription([
      '```',
      `  ${retador.displayName.padEnd(16)}: ${n1.toString().padStart(2,'0')} — ${progressBar(n1, 20, 8)}`,
      `  ${retado.displayName.padEnd(16)}: ${n2.toString().padStart(2,'0')} — ${progressBar(n2, 20, 8)}`,
      '```',
      empate
        ? '> 🤝 **¡EMPATE PERFECTO!** ¡Imposible!'
        : `> 🏆 **¡${ganador.displayName} GANA EL DUELO!**`,
    ].join('\n'))
    .setTimestamp();
}

// ── BOTONES ──────────────────────────────────

function botonesInicio(userId) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`girar_${userId}`)
      .setLabel('🎰 GIRAR')
      .setStyle(ButtonStyle.Danger),
    new ButtonBuilder()
      .setCustomId(`stats_${userId}`)
      .setLabel('📊 Mis Stats')
      .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setCustomId(`duelo_${userId}`)
      .setLabel('⚔️ Duelo')
      .setStyle(ButtonStyle.Primary),
  );
}

function botonesResultado(userId) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`girar_${userId}`)
      .setLabel('🔄 GIRAR DE NUEVO')
      .setStyle(ButtonStyle.Danger),
    new ButtonBuilder()
      .setCustomId(`stats_${userId}`)
      .setLabel('📊 Stats')
      .setStyle(ButtonStyle.Secondary),
    new ButtonBuilder()
      .setCustomId(`duelo_${userId}`)
      .setLabel('⚔️ Duelo')
      .setStyle(ButtonStyle.Primary),
    new ButtonBuilder()
      .setCustomId(`top_${userId}`)
      .setLabel('🏅 Top')
      .setStyle(ButtonStyle.Success),
  );
}

function botonAceptarDuelo(retadorId, retadoId, numeroRetador) {
  return new ActionRowBuilder().addComponents(
    new ButtonBuilder()
      .setCustomId(`aceptar_duelo_${retadorId}_${retadoId}_${numeroRetador}`)
      .setLabel('⚔️ ¡Aceptar Duelo!')
      .setStyle(ButtonStyle.Danger),
    new ButtonBuilder()
      .setCustomId(`rechazar_duelo_${retadoId}`)
      .setLabel('🏳️ Rechazar')
      .setStyle(ButtonStyle.Secondary),
  );
}

// ── ANIMACIÓN DE GIRO ──────────────────────────

async function animarGiro(interaction, userId) {
  const user = interaction.user;

  // Frames de animación
  for (let i = 0; i < 5; i++) {
    await interaction.editReply({
      embeds: [embedGirando(i + Math.floor(Math.random() * 10), i)],
      components: [],
    });
    // Delay que va frenando progresivamente
    await new Promise(r => setTimeout(r, 400 + i * 250));
  }

  // Número final
  const numero = randomNum(1, 20);

  // Actualiza stats
  const st = getUserStats(userId);
  st.total++;
  st.lastNumber = numero;
  if (numero >= 10) {
    st.wins++;
    st.streak = st.streak >= 0 ? st.streak + 1 : 1;
  } else {
    st.losses++;
    st.streak = st.streak <= 0 ? st.streak - 1 : -1;
  }

  enGiro.delete(userId);

  await interaction.editReply({
    embeds: [embedResultado(numero, user)],
    components: [botonesResultado(userId)],
  });

  return numero;
}

// ── TOP / LEADERBOARD ─────────────────────────

function embedTop() {
  const sorted = [...stats.entries()]
    .filter(([, s]) => s.total > 0)
    .sort((a, b) => b[1].wins - a[1].wins)
    .slice(0, 5);

  const medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'];
  const rows = sorted.length === 0
    ? ['_Nadie ha girado la ruleta todavía._']
    : sorted.map(([id, s], i) => `${medals[i]} <@${id}> — ✅ \`${s.wins}\` aciertos en \`${s.total}\` partidas (racha: \`${s.streak > 0 ? '+' : ''}${s.streak}\`)`);

  return new EmbedBuilder()
    .setColor(0xFFD700)
    .setTitle('🏅  TOP RULETA  🏅')
    .setDescription(rows.join('\n'))
    .setFooter({ text: 'Acierto = número ≥ 10' })
    .setTimestamp();
}

// ── REGISTRO DE COMANDOS ──────────────────────

async function registrarComandos() {
  const commands = [
    new SlashCommandBuilder()
      .setName('ruleta')
      .setDescription('🎰 Abre la ruleta interactiva (1-20)'),
    new SlashCommandBuilder()
      .setName('top')
      .setDescription('🏅 Ver el top de la ruleta'),
    new SlashCommandBuilder()
      .setName('mis-stats')
      .setDescription('📊 Ver tus estadísticas de la ruleta'),
  ].map(c => c.toJSON());

  const rest = new REST({ version: '10' }).setToken(TOKEN);
  try {
    console.log('⚙️  Registrando slash commands...');
    await rest.put(Routes.applicationCommands(CLIENT_ID), { body: commands });
    console.log('✅  Slash commands registrados!');
  } catch (err) {
    console.error('❌ Error registrando comandos:', err);
  }
}

// ── EVENTOS ───────────────────────────────────

client.once('ready', async () => {
  console.log(`✅  Bot listo como ${client.user.tag}`);
  await registrarComandos();
});

client.on('interactionCreate', async (interaction) => {

  // ── SLASH COMMANDS ──
  if (interaction.isChatInputCommand()) {
    const { commandName, user } = interaction;

    if (commandName === 'ruleta') {
      await interaction.reply({
        embeds: [embedEspera(user)],
        components: [botonesInicio(user.id)],
      });
    }

    if (commandName === 'top') {
      await interaction.reply({ embeds: [embedTop()], ephemeral: false });
    }

    if (commandName === 'mis-stats') {
      const st = getUserStats(user.id);
      const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle(`📊 Stats de ${user.displayName}`)
        .setThumbnail(user.displayAvatarURL())
        .setDescription([
          `> 🎮 Partidas totales: **${st.total}**`,
          `> ✅ Aciertos (≥10):   **${st.wins}**`,
          `> ❌ Fallos (<10):      **${st.losses}**`,
          `> 🏆 Racha actual:      **${st.streak > 0 ? '+' : ''}${st.streak}**`,
          `> 🔢 Último número:     **${st.lastNumber ?? '—'}**`,
          '',
          st.total > 0 ? `> 📈 Tasa de aciertos: **${Math.round(st.wins / st.total * 100)}%**` : '',
        ].join('\n'))
        .setTimestamp();
      await interaction.reply({ embeds: [embed], ephemeral: true });
    }
    return;
  }

  // ── BOTONES ──
  if (interaction.isButton()) {
    const { customId, user } = interaction;

    // -- GIRAR --
    if (customId.startsWith('girar_')) {
      const ownerId = customId.split('_')[1];
      if (user.id !== ownerId) {
        return interaction.reply({ content: '⛔ ¡Esta ruleta no es tuya! Usa `/ruleta` para la tuya.', ephemeral: true });
      }
      if (enGiro.has(user.id)) {
        return interaction.reply({ content: '⏳ ¡Ya estás girando! Espera...', ephemeral: true });
      }
      enGiro.add(user.id);
      await interaction.deferUpdate();
      await animarGiro(interaction, user.id);
      return;
    }

    // -- STATS --
    if (customId.startsWith('stats_')) {
      const st = getUserStats(user.id);
      const embed = new EmbedBuilder()
        .setColor(0x5865F2)
        .setTitle(`📊 Stats de ${user.displayName}`)
        .setThumbnail(user.displayAvatarURL())
        .setDescription([
          `> 🎮 Partidas: **${st.total}**  |  🏆 Racha: **${st.streak > 0 ? '+' : ''}${st.streak}**`,
          `> ✅ Aciertos: **${st.wins}**  |  ❌ Fallos: **${st.losses}**`,
          `> 🔢 Último: **${st.lastNumber ?? '—'}**`,
          st.total > 0 ? `> 📈 Tasa: **${Math.round(st.wins / st.total * 100)}%**` : '',
        ].join('\n'))
        .setTimestamp();
      return interaction.reply({ embeds: [embed], ephemeral: true });
    }

    // -- TOP --
    if (customId.startsWith('top_')) {
      return interaction.reply({ embeds: [embedTop()], ephemeral: true });
    }

    // -- DUELO --
    if (customId.startsWith('duelo_') && !customId.includes('aceptar') && !customId.includes('rechazar')) {
      const ownerId = customId.split('_')[1];
      if (user.id !== ownerId) {
        return interaction.reply({ content: '⛔ ¡No puedes retar con la ruleta de otro!', ephemeral: true });
      }
      if (enGiro.has(user.id)) {
        return interaction.reply({ content: '⏳ ¡Estás girando! Termina primero.', ephemeral: true });
      }

      // Primer giro del retador
      enGiro.add(user.id);
      await interaction.deferUpdate();
      const numeroRetador = await animarGiro(interaction, user.id);

      // Ahora pide a quién retar
      await interaction.followUp({
        content: `⚔️ **${user.displayName}** sacó **${numeroRetador}**! Para retar a alguien, menciona a un usuario: \`/ruleta\` y usa el botón ⚔️ Duelo en el mismo mensaje, o responde aquí mencionándolo con @usuario.`,
        components: [],
        ephemeral: true,
      });
      return;
    }

    // -- ACEPTAR DUELO --
    if (customId.startsWith('aceptar_duelo_')) {
      const parts = customId.split('_');
      // aceptar_duelo_{retadorId}_{retadoId}_{numero}
      const retadorId = parts[2];
      const retadoId  = parts[3];
      const n1        = parseInt(parts[4]);

      if (user.id !== retadoId) {
        return interaction.reply({ content: '⛔ ¡Este duelo no es contigo!', ephemeral: true });
      }

      enGiro.add(user.id);
      await interaction.deferUpdate();

      // Animar giro del retado
      const n2 = await animarGiro(interaction, user.id);

      // Buscar usuario retador
      let retadorUser;
      try { retadorUser = await client.users.fetch(retadorId); } catch { retadorUser = { displayName: 'Retador', id: retadorId }; }

      await interaction.followUp({
        embeds: [embedDueloResult(retadorUser, user, n1, n2)],
      });
      return;
    }

    // -- RECHAZAR DUELO --
    if (customId.startsWith('rechazar_duelo_')) {
      const retadoId = customId.split('_')[2];
      if (user.id !== retadoId) {
        return interaction.reply({ content: '⛔ Solo el retado puede rechazar.', ephemeral: true });
      }
      await interaction.update({
        embeds: [
          new EmbedBuilder()
            .setColor(0x888888)
            .setTitle('🏳️ Duelo Rechazado')
            .setDescription(`> **${user.displayName}** rechazó el duelo.`)
        ],
        components: [],
      });
      return;
    }
  }
});

// ── INICIO ────────────────────────────────────
if (!TOKEN || !CLIENT_ID) {
  console.error('❌  Faltan TOKEN o CLIENT_ID en las variables de entorno.');
  console.error('    Ejecuta: TOKEN=xxx CLIENT_ID=yyy node index.js');
  process.exit(1);
}

client.login(TOKEN);
