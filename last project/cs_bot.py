# cs_bot.py 

import discord
from discord.ext import commands
import asyncio
from datetime import datetime
from config import (
    CS_TOKEN, CS_PREFIX, CS_BOT_NAME, COLORS, EMOJIS, RATE_LIMITS,
    LOYALTY_CONFIG, FEATURES
)
from database import (
    find_faq_answer, save_question, get_pending_questions, close_question,
    add_user_points, get_user_points, get_user_status, update_user_streak,
    check_achievements, faq_db, get_statistics
)

# Enhanced bot setup with all intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(
    command_prefix=CS_PREFIX,
    intents=intents,
    help_command=None,  # Custom help command
    case_insensitive=True
)

# Rate limiting dictionary
user_cooldowns = {}

class CSBotView(discord.ui.View):
    """Interactive view for CS Bot with buttons"""
    
    def __init__(self):
        super().__init__(timeout=300)
    
    @discord.ui.button(label="📋 FAQ", style=discord.ButtonStyle.primary, emoji="❓")
    async def faq_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()
            await show_faq_categories(interaction)
        except Exception as e:
            print(f"Error in faq_button: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)
    
    @discord.ui.button(label="📊 Status Poin", style=discord.ButtonStyle.secondary, emoji="💎")
    async def points_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()
            await show_user_points(interaction)
        except Exception as e:
            print(f"Error in points_button: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)
    
    @discord.ui.button(label="🎯 Statistik", style=discord.ButtonStyle.success, emoji="📈")
    async def stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        try:
            await interaction.response.defer()
            await show_statistics(interaction)
        except Exception as e:
            print(f"Error in stats_button: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)

class FAQCategorySelect(discord.ui.Select):
    """Dropdown for FAQ categories"""
    
    def __init__(self):
        options = [
            discord.SelectOption(
                label="💳 Pembayaran",
                description="Info metode pembayaran dan cicilan",
                value="pembayaran",
                emoji="💳"
            ),
            discord.SelectOption(
                label="🚚 Pengiriman",
                description="Info pengiriman dan tracking",
                value="pengiriman",
                emoji="🚚"
            ),
            discord.SelectOption(
                label="🎁 Ongkos Kirim",
                description="Info biaya dan promo ongkir",
                value="ongkir",
                emoji="🎁"
            ),
            discord.SelectOption(
                label="🛡️ Garansi",
                description="Info garansi dan klaim",
                value="garansi",
                emoji="🛡️"
            ),
            discord.SelectOption(
                label="📞 Kontak CS",
                description="Info customer service",
                value="kontak",
                emoji="📞"
            ),
            discord.SelectOption(
                label="🔄 Return & Refund",
                description="Kebijakan pengembalian",
                value="return",
                emoji="🔄"
            )
        ]
        super().__init__(placeholder="Pilih kategori FAQ yang ingin Anda lihat...", options=options)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            selected_faq = faq_db.get(self.values[0])
            if selected_faq:
                embed = discord.Embed(
                    title=f"{EMOJIS['info']} FAQ - {self.values[0].title()}",
                    description=selected_faq['answer'],
                    color=COLORS['primary']
                )
                embed.set_footer(text=f"Dijawab oleh {CS_BOT_NAME} • Ketik pertanyaan untuk mendapat jawaban otomatis")
                await interaction.response.edit_message(embed=embed, view=self.view)
            else:
                await interaction.response.send_message("FAQ tidak ditemukan.", ephemeral=True)
        except Exception as e:
            print(f"Error in FAQ select callback: {e}")
            if not interaction.response.is_done():
                await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)

class FAQView(discord.ui.View):
    """View for FAQ with category selector"""
    
    def __init__(self):
        super().__init__(timeout=300)
        self.add_item(FAQCategorySelect())

@bot.event
async def on_ready():
    print(f'{EMOJIS["success"]} {CS_BOT_NAME} telah aktif sebagai {bot.user}!')
    print(f'{EMOJIS["info"]} Bot aktif di {len(bot.guilds)} server')
    
    # Set rich presence
    activity = discord.Activity(
        type=discord.ActivityType.listening,
        name="pertanyaan pelanggan 24/7 🎧"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)
    
    # Sync slash commands
    try:
        synced = await bot.tree.sync()
        print(f'{EMOJIS["success"]} Synced {len(synced)} slash command(s)')
    except Exception as e:
        print(f'{EMOJIS["error"]} Failed to sync commands: {e}')

@bot.event
async def on_message(message):
    # Skip bot messages
    if message.author == bot.user:
        return
    
    # Skip commands
    if message.content.startswith(CS_PREFIX):
        await bot.process_commands(message)
        return
    
    # Rate limiting check
    user_id = message.author.id
    now = datetime.now()
    
    if user_id in user_cooldowns:
        last_message = user_cooldowns[user_id]
        if (now - last_message).seconds < 2:  # 2 second cooldown
            return
    
    user_cooldowns[user_id] = now
    
    # Update user streak
    update_user_streak(user_id)
    
    # Search for FAQ answer
    answer = find_faq_answer(message.content)
    
    if answer:
        # Send FAQ answer with enhanced embed
        embed = discord.Embed(
            title=f"{EMOJIS['success']} Informasi Ditemukan!",
            description=answer,
            color=COLORS['primary']
        )
        embed.set_author(
            name=CS_BOT_NAME,
            icon_url=bot.user.avatar.url if bot.user.avatar else None
        )
        embed.add_field(
            name=f"{EMOJIS['star']} Poin Reward",
            value=f"+{LOYALTY_CONFIG['points_per_question']} poin loyalty",
            inline=True
        )
        embed.set_footer(text="Ketik !help untuk melihat semua fitur bot")
        
        # Add reaction buttons with proper error handling
        view = discord.ui.View(timeout=60)
        
        helpful_button = discord.ui.Button(
            label="Membantu",
            emoji="👍",
            style=discord.ButtonStyle.success
        )
        
        not_helpful_button = discord.ui.Button(
            label="Kurang Membantu",
            emoji="👎",
            style=discord.ButtonStyle.secondary
        )
        
        async def helpful_callback(interaction):
            try:
                await interaction.response.send_message(
                    f"{EMOJIS['heart']} Terima kasih atas feedback positifnya! "
                    f"Anda mendapat bonus +1 poin!", 
                    ephemeral=True
                )
                add_user_points(interaction.user.id, 1)
            except Exception as e:
                print(f"Error in helpful callback: {e}")
        
        async def not_helpful_callback(interaction):
            try:
                await interaction.response.send_message(
                    f"{EMOJIS['info']} Maaf jawaban kurang membantu. "
                    f"Silakan hubungi CS untuk bantuan lebih lanjut.", 
                    ephemeral=True
                )
            except Exception as e:
                print(f"Error in not helpful callback: {e}")
        
        helpful_button.callback = helpful_callback
        not_helpful_button.callback = not_helpful_callback
        
        view.add_item(helpful_button)
        view.add_item(not_helpful_button)
        
        await message.reply(embed=embed, view=view)
        
        # Add points
        points_earned = add_user_points(user_id, LOYALTY_CONFIG['points_per_question'])
        
        # Check for new achievements
        new_achievements = check_achievements(user_id)
        if new_achievements:
            await send_achievement_notification(message.channel, message.author, new_achievements)
    
    else:
        # Save question and send confirmation
        question_id = save_question(message.author, message.content)
        
        embed = discord.Embed(
            title=f"{EMOJIS['loading']} Pertanyaan Diterima!",
            description=f"Halo {message.author.mention}! Pertanyaan Anda telah diterima dan akan dijawab oleh tim CS kami.",
            color=COLORS['warning']
        )
        embed.add_field(
            name=f"{EMOJIS['info']} ID Pertanyaan",
            value=f"#{question_id}",
            inline=True
        )
        embed.add_field(
            name=f"{EMOJIS['star']} Poin Reward",
            value=f"+{LOYALTY_CONFIG['points_per_question'] * 2} poin",
            inline=True
        )
        embed.add_field(
            name=f"{EMOJIS['info']} Estimasi Respon",
            value="< 1 jam (24/7)",
            inline=False
        )
        embed.set_footer(text="Tim CS profesional kami akan segera membantu Anda!")
        
        await message.reply(embed=embed)
        
        # Add double points for new questions
        add_user_points(user_id, LOYALTY_CONFIG['points_per_question'] * 2)
    
    await bot.process_commands(message)

async def send_achievement_notification(channel, user, achievements):
    """Send achievement notification"""
    from config import ACHIEVEMENTS
    
    embed = discord.Embed(
        title=f"{EMOJIS['celebration']} Achievement Unlocked!",
        description=f"Selamat {user.mention}! Anda telah meraih pencapaian baru!",
        color=COLORS['gold']
    )
    
    for achievement_id in achievements:
        achievement = ACHIEVEMENTS[achievement_id]
        embed.add_field(
            name=f"{achievement['emoji']} {achievement['name']}",
            value=f"{achievement['description']}\n+{achievement['points']} poin bonus!",
            inline=False
        )
    
    embed.set_thumbnail(url=user.avatar.url if user.avatar else None)
    await channel.send(embed=embed)

async def show_faq_categories(interaction):
    """Show FAQ categories with interactive menu"""
    embed = discord.Embed(
        title=f"{EMOJIS['info']} Frequently Asked Questions",
        description="Pilih kategori FAQ yang ingin Anda lihat dari menu di bawah ini:",
        color=COLORS['primary']
    )
    embed.add_field(
        name=f"{EMOJIS['star']} Tips",
        value="Anda juga bisa langsung mengetik pertanyaan untuk mendapat jawaban otomatis!",
        inline=False
    )
    embed.set_footer(text="FAQ diperbarui secara berkala untuk memberikan informasi terbaru")
    
    view = FAQView()
    try:
        await interaction.followup.send(embed=embed, view=view)
    except Exception as e:
        print(f"Error in show_faq_categories: {e}")
        await interaction.followup.send("Terjadi kesalahan saat menampilkan FAQ.", ephemeral=True)

async def show_user_points(interaction):
    """Show user points and status"""
    user_points = get_user_points(interaction.user.id)
    user_status = get_user_status(interaction.user.id)
    
    # Status color based on membership
    status_colors = {
        'Regular': COLORS['info'],
        'VIP': COLORS['warning'],
        'Premium': COLORS['gold']
    }
    
    status_emojis = {
        'Regular': '🥉',
        'VIP': '🥈',
        'Premium': '👑'
    }
    
    embed = discord.Embed(
        title=f"{EMOJIS['gem']} Status Loyalty Points",
        description=f"Halo {interaction.user.mention}! Berikut status poin Anda:",
        color=status_colors.get(user_status, COLORS['info'])
    )
    
    embed.add_field(
        name=f"{EMOJIS['trophy']} Total Poin",
        value=f"**{user_points:,}** poin",
        inline=True
    )
    
    embed.add_field(
        name=f"{status_emojis[user_status]} Status",
        value=f"**{user_status}** Member",
        inline=True
    )
    
    # Progress to next level
    if user_status == 'Regular':
        next_threshold = LOYALTY_CONFIG['vip_threshold']
        progress = min(user_points / next_threshold * 100, 100)
        embed.add_field(
            name=f"{EMOJIS['fire']} Progress ke VIP",
            value=f"{progress:.1f}% ({next_threshold - user_points} poin lagi)",
            inline=False
        )
    elif user_status == 'VIP':
        next_threshold = LOYALTY_CONFIG['premium_threshold']
        progress = min(user_points / next_threshold * 100, 100)
        embed.add_field(
            name=f"{EMOJIS['crown']} Progress ke Premium",
            value=f"{progress:.1f}% ({next_threshold - user_points} poin lagi)",
            inline=False
        )
    
    embed.add_field(
        name=f"{EMOJIS['gift']} Cara Dapat Poin",
        value="• Tanya FAQ: +2 poin\n• Pertanyaan baru: +4 poin\n• Ikuti kuis: +15 poin\n• Beli produk: +5 poin/10rb",
        inline=False
    )
    
    embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else None)
    try:
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Error in show_user_points: {e}")
        await interaction.followup.send("Terjadi kesalahan saat menampilkan poin.", ephemeral=True)

async def show_statistics(interaction):
    """Show platform statistics"""
    stats = get_statistics()
    
    embed = discord.Embed(
        title=f"{EMOJIS['rocket']} Statistik Platform",
        description="Statistik real-time platform Semua Bisa Kamu Beli",
        color=COLORS['success']
    )
    
    embed.add_field(
        name=f"{EMOJIS['star']} Total Pengguna",
        value=f"{stats['total_users']:,}",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['cart']} Total Pesanan",
        value=f"{stats['total_orders']:,}",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['info']} Pertanyaan Dijawab",
        value=f"{stats['total_questions']:,}",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['gem']} Total Poin Terdistribusi",
        value=f"{stats['total_points_distributed']:,}",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['package']} Produk Tersedia",
        value=f"{stats['total_products']} produk",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['trophy']} Rata-rata Poin/User",
        value=f"{stats['average_points_per_user']:.1f}",
        inline=True
    )
    
    embed.set_footer(text="Data diperbarui secara real-time")
    try:
        await interaction.followup.send(embed=embed)
    except Exception as e:
        print(f"Error in show_statistics: {e}")
        await interaction.followup.send("Terjadi kesalahan saat menampilkan statistik.", ephemeral=True)

@bot.command(name='help', aliases=['bantuan', 'h'])
async def help_command(ctx):
    """Enhanced help command with interactive elements"""
    embed = discord.Embed(
        title=f"{EMOJIS['rocket']} {CS_BOT_NAME} - Panduan Lengkap",
        description="Bot Customer Service terdepan dengan AI dan fitur interaktif!",
        color=COLORS['primary']
    )
    
    embed.add_field(
        name=f"{EMOJIS['info']} Fitur Utama",
        value="• **Auto FAQ**: Jawaban otomatis untuk pertanyaan umum\n"
              "• **Smart Search**: Pencarian cerdas dengan fuzzy matching\n"
              "• **Loyalty Points**: Sistem poin reward terintegrasi\n"
              "• **Achievement**: Pencapaian dan badge khusus\n"
              "• **Interactive UI**: Tombol dan menu interaktif",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['star']} Commands",
        value=f"`{CS_PREFIX}help` - Panduan ini\n"
              f"`{CS_PREFIX}faq` - Lihat FAQ interaktif\n"
              f"`{CS_PREFIX}points` - Cek poin loyalty\n"
              f"`{CS_PREFIX}pending` - Pertanyaan pending (Admin)\n"
              f"`{CS_PREFIX}close <id>` - Tutup pertanyaan (Admin)\n"
              f"`{CS_PREFIX}stats` - Statistik platform",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['crown']} Tips Pro",
        value="• Ketik pertanyaan langsung untuk jawaban instan\n"
              "• Gunakan tombol interaktif untuk navigasi mudah\n"
              "• Kumpulkan poin untuk status VIP/Premium\n"
              "• Berikan feedback untuk meningkatkan layanan",
        inline=True
    )
    
    embed.set_footer(text="Ketik pertanyaan apa saja untuk mendapat bantuan otomatis!")
    embed.set_thumbnail(url=bot.user.avatar.url if bot.user.avatar else None)
    
    view = CSBotView()
    await ctx.send(embed=embed, view=view)

@bot.command(name='faq')
async def faq_command(ctx):
    """Interactive FAQ command"""
    # Create a mock interaction object for compatibility
    class MockInteraction:
        def __init__(self, user, followup_func):
            self.user = user
            self.followup = type('obj', (object,), {'send': followup_func})()
    
    mock_interaction = MockInteraction(ctx.author, ctx.send)
    await show_faq_categories(mock_interaction)

@bot.command(name='points', aliases=['poin', 'loyalty'])
async def points_command(ctx):
    """Show user points"""
    class MockInteraction:
        def __init__(self, user, followup_func):
            self.user = user
            self.followup = type('obj', (object,), {'send': followup_func})()
    
    mock_interaction = MockInteraction(ctx.author, ctx.send)
    await show_user_points(mock_interaction)

@bot.command(name='stats', aliases=['statistik'])
async def stats_command(ctx):
    """Show platform statistics"""
    class MockInteraction:
        def __init__(self, followup_func):
            self.followup = type('obj', (object,), {'send': followup_func})()
    
    mock_interaction = MockInteraction(ctx.send)
    await show_statistics(mock_interaction)

@bot.command(name='pending')
@commands.has_permissions(manage_messages=True)
async def pending_command(ctx):
    """Show pending questions (Admin only)"""
    questions = get_pending_questions()
    
    if not questions:
        embed = discord.Embed(
            title=f"{EMOJIS['success']} Tidak Ada Pertanyaan Pending",
            description="Semua pertanyaan sudah dijawab! Tim CS bekerja dengan baik.",
            color=COLORS['success']
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"{EMOJIS['loading']} Pertanyaan Pending",
        description=f"Total: **{len(questions)}** pertanyaan menunggu jawaban",
        color=COLORS['warning']
    )
    
    for i, q in enumerate(questions[:5]):  # Show max 5 questions
        timestamp = datetime.fromisoformat(q['timestamp']).strftime("%d/%m %H:%M")
        embed.add_field(
            name=f"#{q['id']} - {q['user']} ({timestamp})",
            value=f"q['question'][:100]{'...' if len(q['question']) > 100 else ''}",
            inline=False
        )
    
    if len(questions) > 5:
        embed.set_footer(text=f"Menampilkan 5 dari {len(questions)} pertanyaan. Gunakan !close <id> untuk menutup.")
    else:
        embed.set_footer(text="Gunakan !close <id> untuk menandai pertanyaan selesai.")
    
    await ctx.send(embed=embed)

@bot.command(name='close')
@commands.has_permissions(manage_messages=True)
async def close_command(ctx, question_id: int):
    """Close a question (Admin only)"""
    if close_question(question_id):
        embed = discord.Embed(
            title=f"{EMOJIS['success']} Pertanyaan Ditutup",
            description=f"Pertanyaan ID #{question_id} telah ditandai selesai.",
            color=COLORS['success']
        )
    else:
        embed = discord.Embed(
            title=f"{EMOJIS['error']} ID Tidak Ditemukan",
            description=f"Pertanyaan dengan ID #{question_id} tidak ditemukan atau sudah ditutup.",
            color=COLORS['error']
        )
    
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    """Enhanced error handling"""
    if isinstance(error, commands.MissingPermissions):
        embed = discord.Embed(
            title=f"{EMOJIS['error']} Akses Ditolak",
            description="Anda tidak memiliki izin untuk menggunakan perintah ini.",
            color=COLORS['error']
        )
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(
            title=f"{EMOJIS['info']} Command Tidak Ditemukan",
            description=f"Ketik `{CS_PREFIX}help` untuk melihat daftar perintah yang tersedia.",
            color=COLORS['warning']
        )
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=f"{EMOJIS['warning']} Parameter Kurang",
            description=f"Perintah ini memerlukan parameter tambahan. Ketik `{CS_PREFIX}help` untuk panduan.",
            color=COLORS['warning']
        )
    else:
        embed = discord.Embed(
            title=f"{EMOJIS['error']} Terjadi Kesalahan",
            description="Maaf, terjadi kesalahan sistem. Tim teknis telah diberitahu.",
            color=COLORS['error']
        )
        print(f"Unhandled error: {error}")
    
    await ctx.send(embed=embed)

# Slash Commands
@bot.tree.command(name="help", description="Panduan lengkap CS Bot")
async def slash_help(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        
        embed = discord.Embed(
            title=f"{EMOJIS['rocket']} {CS_BOT_NAME} - Panduan Lengkap",
            description="Bot Customer Service terdepan dengan AI dan fitur interaktif!",
            color=COLORS['primary']
        )
        
        embed.add_field(
            name=f"{EMOJIS['info']} Cara Menggunakan",
            value="• Ketik pertanyaan langsung untuk jawaban otomatis\n"
                  "• Gunakan tombol di bawah untuk navigasi cepat\n"
                  "• Kumpulkan poin loyalty dengan berinteraksi",
            inline=False
        )
        
        view = CSBotView()
        await interaction.followup.send(embed=embed, view=view)
    except Exception as e:
        print(f"Error in slash_help: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)

@bot.tree.command(name="points", description="Cek poin loyalty Anda")
async def slash_points(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        await show_user_points(interaction)
    except Exception as e:
        print(f"Error in slash_points: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)

@bot.tree.command(name="faq", description="Lihat FAQ interaktif")
async def slash_faq(interaction: discord.Interaction):
    try:
        await interaction.response.defer()
        await show_faq_categories(interaction)
    except Exception as e:
        print(f"Error in slash_faq: {e}")
        if not interaction.response.is_done():
            await interaction.response.send_message("Terjadi kesalahan, silakan coba lagi.", ephemeral=True)

if __name__ == '__main__':
    try:
        print(f"{EMOJIS['loading']} Starting {CS_BOT_NAME}...")
        bot.run(CS_TOKEN)
    except discord.errors.LoginFailure:
        print(f"{EMOJIS['error']} ERROR: Token tidak valid! Silakan periksa token di config.py")
    except Exception as e:
        print(f"{EMOJIS['error']} ERROR: {e}")