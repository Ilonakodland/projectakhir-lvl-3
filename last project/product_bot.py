# product_bot.py 

import discord
from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta
from config import (
    PRODUCT_TOKEN, PRODUCT_PREFIX, PRODUCT_BOT_NAME, COLORS, EMOJIS,
    LOYALTY_CONFIG, QUIZ_CONFIG, RATE_LIMITS
)
from database import (
    get_product_by_id, get_products_by_category, get_all_categories,
    search_products, create_order, add_user_points, get_user_points,
    get_user_status, get_random_quiz, get_leaderboard, check_achievements,
    get_user_orders, products_db, update_user_streak
)

# Enhanced bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=PRODUCT_PREFIX,
    intents=intents,
    help_command=None,
    case_insensitive=True
)

# User cooldowns for rate limiting
user_cooldowns = {}
quiz_cooldowns = {}

@bot.event
async def on_ready():
    print(f'{EMOJIS["success"]} {PRODUCT_BOT_NAME} telah aktif sebagai {bot.user}!')
    print(f'{EMOJIS["info"]} Bot aktif di {len(bot.guilds)} server')
    
    # Set rich presence
    activity = discord.Activity(
        type=discord.ActivityType.watching,
        name="produk premium & loyalty rewards 🛍️"
    )
    await bot.change_presence(status=discord.Status.online, activity=activity)

@bot.command(name='help', aliases=['bantuan', 'h'])
async def help_command(ctx):
    """Enhanced help command"""
    embed = discord.Embed(
        title=f"{EMOJIS['rocket']} {PRODUCT_BOT_NAME} - Panduan Lengkap",
        description="Bot produk dan loyalty terdepan dengan fitur AI dan gamifikasi!",
        color=COLORS['primary']
    )
    
    embed.add_field(
        name=f"{EMOJIS['cart']} Fitur Produk",
        value="• **Smart Catalog**: Katalog interaktif dengan filter\n"
              "• **Advanced Search**: Pencarian cerdas multi-parameter\n"
              "• **Dynamic Pricing**: Harga otomatis berdasarkan status\n"
              "• **Real-time Stock**: Update stok real-time",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['gem']} Sistem Loyalty",
        value="• **Multi-tier Membership**: Regular → VIP → Premium\n"
              "• **Achievement System**: Badge dan reward khusus\n"
              "• **Daily Streaks**: Bonus aktivitas harian\n"
              "• **Interactive Quiz**: Kuis berhadiah poin",
        inline=False
    )
    
    embed.add_field(
        name=f"{EMOJIS['star']} Commands",
        value=f"`{PRODUCT_PREFIX}produk [kategori]` - Lihat katalog\n"
              f"`{PRODUCT_PREFIX}search <query>` - Cari produk\n"
              f"`{PRODUCT_PREFIX}beli <id> <qty>` - Beli produk\n"
              f"`{PRODUCT_PREFIX}points` - Cek poin loyalty\n"
              f"`{PRODUCT_PREFIX}quiz [difficulty]` - Ikuti kuis\n"
              f"`{PRODUCT_PREFIX}leaderboard` - Peringkat poin",
        inline=True
    )
    
    embed.add_field(
        name=f"{EMOJIS['crown']} Membership Benefits",
        value="🥉 **Regular**: Poin standar\n"
              "🥈 **VIP** (100+ poin): Diskon 10%\n"
              "👑 **Premium** (500+ poin): Diskon 20%",
        inline=True
    )
    
    embed.set_footer(text="Gunakan commands untuk menjelajahi produk dan kumpulkan poin!")
    await ctx.send(embed=embed)

@bot.command(name='produk', aliases=['catalog', 'katalog'])
async def produk_command(ctx, category=None):
    """Enhanced product catalog"""
    if category and category.lower() != 'all':
        products = get_products_by_category(category)
        if not products:
            available_categories = get_all_categories()
            embed = discord.Embed(
                title=f"{EMOJIS['error']} Kategori Tidak Ditemukan",
                description=f"Kategori '{category}' tidak tersedia.",
                color=COLORS['error']
            )
            embed.add_field(
                name="📂 Kategori Tersedia",
                value=", ".join([cat.title() for cat in available_categories]),
                inline=False
            )
            await ctx.send(embed=embed)
            return
    else:
        products = products_db
    
    embed = discord.Embed(
        title=f"{EMOJIS['cart']} Katalog Produk Premium",
        description=f"Total {len(products)} produk tersedia",
        color=COLORS['primary']
    )
    
    for product in products[:5]:  # Show first 5 products
        # Calculate discount for VIP/Premium users
        vip_price = product['price'] * (1 - LOYALTY_CONFIG['vip_discount'])
        premium_price = product['price'] * (1 - LOYALTY_CONFIG['premium_discount'])
        
        rating_stars = "⭐" * int(product['rating'])
        
        value = (
            f"💰 **Rp {product['price']:,}**\n"
            f"🥈 VIP: Rp {vip_price:,.0f} (10% off)\n"
            f"👑 Premium: Rp {premium_price:,.0f} (20% off)\n"
            f"📦 Stok: {product['stock']} • {rating_stars} ({product['rating']})\n"
            f"🔥 Terjual: {product['sold']} unit\n"
            f"📝 {product['description'][:80]}...\n"
            f"🏷️ Tags: {', '.join(product['tags'][:3])}"
        )
        
        embed.add_field(
            name=f"{EMOJIS['package']} ID: {product['id']} - {product['name']}",
            value=value,
            inline=False
        )
    
    embed.set_footer(text="Gunakan ?beli <id> <jumlah> untuk membeli • ?search <kata kunci> untuk mencari")
    await ctx.send(embed=embed)

@bot.command(name='search', aliases=['cari'])
async def search_command(ctx, *, query):
    """Search products"""
    results = search_products(query)
    
    if not results:
        embed = discord.Embed(
            title=f"{EMOJIS['error']} Produk Tidak Ditemukan",
            description=f"Tidak ada produk yang cocok dengan '{query}'",
            color=COLORS['error']
        )
        await ctx.send(embed=embed)
        return
    
    embed = discord.Embed(
        title=f"🔍 Hasil Pencarian: '{query}'",
        description=f"Ditemukan {len(results)} produk",
        color=COLORS['primary']
    )
    
    for product in results[:3]:  # Show top 3 results
        embed.add_field(
            name=f"ID: {product['id']} - {product['name']}",
            value=f"Rp {product['price']:,} | Stok: {product['stock']} | Rating: {product['rating']}⭐",
            inline=False
        )
    
    await ctx.send(embed=embed)

@bot.command(name='beli', aliases=['buy'])
async def beli_command(ctx, product_id: int, quantity: int = 1):
    """Purchase product"""
    if quantity <= 0:
        await ctx.send(f"{EMOJIS['error']} Jumlah pembelian harus lebih dari 0!")
        return
    
    product = get_product_by_id(product_id)
    if not product:
        await ctx.send(f"{EMOJIS['error']} Produk dengan ID {product_id} tidak ditemukan!")
        return
    
    if product['stock'] < quantity:
        await ctx.send(f"{EMOJIS['error']} Stok tidak mencukupi! Stok tersedia: {product['stock']}")
        return
    
    order = create_order(ctx.author, product_id, quantity)
    if not order:
        await ctx.send(f"{EMOJIS['error']} Gagal membuat pesanan!")
        return
    
    points_earned = int(order['final_total'] / 10000) * LOYALTY_CONFIG['points_per_purchase']
    add_user_points(ctx.author.id, points_earned)
    
    embed = discord.Embed(
        title=f"{EMOJIS['celebration']} Pesanan Berhasil!",
        description=f"Terima kasih {ctx.author.mention}!",
        color=COLORS['success']
    )
    
    embed.add_field(name="ID Pesanan", value=f"#{order['id']}", inline=True)
    embed.add_field(name="Produk", value=order['product_name'], inline=True)
    embed.add_field(name="Total", value=f"Rp {order['final_total']:,.0f}", inline=True)
    embed.add_field(name="Poin Earned", value=f"+{points_earned} poin", inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name='points', aliases=['poin'])
async def points_command(ctx):
    """Show user points"""
    user_points = get_user_points(ctx.author.id)
    user_status = get_user_status(ctx.author.id)
    
    embed = discord.Embed(
        title=f"{EMOJIS['gem']} Loyalty Points",
        description=f"Status untuk {ctx.author.mention}",
        color=COLORS['primary']
    )
    
    embed.add_field(name="Total Poin", value=f"{user_points:,} poin", inline=True)
    embed.add_field(name="Status", value=user_status, inline=True)
    
    if user_status == 'Regular':
        needed = LOYALTY_CONFIG['vip_threshold'] - user_points
        embed.add_field(name="Progress ke VIP", value=f"{needed} poin lagi", inline=False)
    elif user_status == 'VIP':
        needed = LOYALTY_CONFIG['premium_threshold'] - user_points
        embed.add_field(name="Progress ke Premium", value=f"{needed} poin lagi", inline=False)
    
    await ctx.send(embed=embed)

@bot.command(name='quiz')
async def quiz_command(ctx, difficulty='random'):
    """Interactive quiz with proper error handling"""
    try:
        question_data = get_random_quiz()
        
        embed = discord.Embed(
            title=f"{EMOJIS['star']} Kuis Loyalty Points",
            description="Jawab pertanyaan berikut dengan benar!",
            color=COLORS['primary']
        )
        
        embed.add_field(name="Pertanyaan", value=question_data['question'], inline=False)
        
        options_text = ""
        for i, option in enumerate(question_data['options']):
            options_text += f"**{i+1}.** {option}\n"
        
        embed.add_field(name="Pilihan", value=options_text, inline=False)
        embed.set_footer(text="Ketik nomor jawaban (1-4)")
        
        await ctx.send(embed=embed)
        
        def check(m):
            return m.author == ctx.author and m.content.isdigit() and 1 <= int(m.content) <= 4
        
        try:
            msg = await bot.wait_for('message', check=check, timeout=30)
            
            answer_index = int(msg.content) - 1
            if answer_index == question_data['answer']:
                points = LOYALTY_CONFIG['points_per_correct_quiz']
                add_user_points(ctx.author.id, points)
                await ctx.send(f"{EMOJIS['celebration']} Benar! +{points} poin!")
            else:
                correct = question_data['options'][question_data['answer']]
                await ctx.send(f"{EMOJIS['error']} Salah! Jawaban benar: **{correct}**")
        
        except asyncio.TimeoutError:
            await ctx.send(f"{EMOJIS['warning']} Waktu habis!")
    
    except Exception as e:
        print(f"Error in quiz_command: {e}")
        await ctx.send(f"{EMOJIS['error']} Terjadi kesalahan saat memuat kuis!")

@bot.command(name='leaderboard', aliases=['top'])
async def leaderboard_command(ctx):
    """Show leaderboard with error handling"""
    try:
        leaderboard_data = get_leaderboard(10)
        
        embed = discord.Embed(
            title=f"{EMOJIS['trophy']} Leaderboard",
            description="Top 10 member dengan poin tertinggi",
            color=COLORS['gold']
        )
        
        medals = ["🥇", "🥈", "🥉"]
        
        for i, entry in enumerate(leaderboard_data):
            try:
                user = await bot.fetch_user(int(entry['user_id']))
                medal = medals[i] if i < 3 else f"#{i+1}"
                status = get_user_status(int(entry['user_id']))
                embed.add_field(
                    name=f"{medal} {user.display_name}",
                    value=f"{entry['points']:,} poin ({status})",
                    inline=False
                )
            except Exception as user_error:
                print(f"Error fetching user {entry['user_id']}: {user_error}")
                embed.add_field(
                    name=f"#{i+1} User {entry['user_id']}",
                    value=f"{entry['points']:,} poin",
                    inline=False
                )
        
        await ctx.send(embed=embed)
    
    except Exception as e:
        print(f"Error in leaderboard_command: {e}")
        await ctx.send(f"{EMOJIS['error']} Terjadi kesalahan saat memuat leaderboard!")

@bot.event
async def on_command_error(ctx, error):
    """Enhanced error handling"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{EMOJIS['warning']} Parameter kurang! Ketik `?help` untuk panduan.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"{EMOJIS['error']} Format parameter salah! Ketik `?help` untuk panduan.")
    elif isinstance(error, commands.CommandNotFound):
        # Silently ignore command not found errors for product bot
        pass
    else:
        print(f"Unhandled error in product bot: {error}")
        await ctx.send(f"{EMOJIS['error']} Terjadi kesalahan! Silakan coba lagi.")

if __name__ == '__main__':
    try:
        print(f"{EMOJIS['loading']} Starting {PRODUCT_BOT_NAME}...")
        bot.run(PRODUCT_TOKEN)
    except discord.errors.LoginFailure:
        print(f"{EMOJIS['error']} ERROR: Token tidak valid!")
    except Exception as e:
        print(f"{EMOJIS['error']} ERROR: {e}")