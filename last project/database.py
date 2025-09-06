# database.py 

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from config import LOYALTY_CONFIG, ACHIEVEMENTS, EMOJIS
import difflib

# Enhanced FAQ Database with Smart Matching
faq_db = {
    'pembayaran': {
        'answer': f'{EMOJIS["money"]} **Metode Pembayaran Terlengkap:**\n'
                 f'• {EMOJIS["success"]} Transfer Bank (BCA, Mandiri, BRI, BNI, CIMB)\n'
                 f'• {EMOJIS["success"]} E-wallet (OVO, Dana, GoPay, ShopeePay, LinkAja)\n'
                 f'• {EMOJIS["success"]} Kartu Kredit/Debit (Visa, Mastercard, JCB)\n'
                 f'• {EMOJIS["success"]} QRIS (Scan & Pay)\n'
                 f'• {EMOJIS["success"]} Cicilan 0% (3, 6, 12 bulan)\n\n'
                 f'{EMOJIS["info"]} *Pembayaran diverifikasi otomatis dalam 5 menit*',
        'keywords': ['pembayaran', 'bayar', 'payment', 'transfer', 'cicilan', 'kredit', 'debit'],
        'category': 'payment',
        'priority': 1
    },
    'pengiriman': {
        'answer': f'{EMOJIS["package"]} **Pengiriman Super Cepat:**\n'
                 f'• {EMOJIS["rocket"]} Same Day (Jakarta, Surabaya, Bandung)\n'
                 f'• {EMOJIS["success"]} Next Day (Jabodetabek)\n'
                 f'• {EMOJIS["success"]} 1-3 hari kerja (Seluruh Indonesia)\n'
                 f'• {EMOJIS["success"]} Ekspedisi: JNE, J&T, SiCepat, AnterAja, Ninja\n'
                 f'• {EMOJIS["success"]} Real-time tracking via WhatsApp\n'
                 f'• {EMOJIS["success"]} Asuransi gratis untuk semua paket',
        'keywords': ['pengiriman', 'kirim', 'shipping', 'delivery', 'ekspedisi', 'tracking'],
        'category': 'shipping',
        'priority': 1
    },
    'ongkir': {
        'answer': f'{EMOJIS["gift"]} **Ongkos Kirim Hemat:**\n'
                 f'• {EMOJIS["fire"]} GRATIS ONGKIR minimum Rp 75.000\n'
                 f'• {EMOJIS["success"]} Subsidi ongkir 50% untuk member VIP\n'
                 f'• {EMOJIS["success"]} Estimasi otomatis saat checkout\n'
                 f'• {EMOJIS["success"]} Promo ongkir Rp 1.000 setiap Jumat\n'
                 f'• {EMOJIS["info"]} Dihitung berdasarkan berat dan jarak',
        'keywords': ['ongkir', 'ongkos kirim', 'biaya kirim', 'gratis ongkir'],
        'category': 'shipping',
        'priority': 2
    },
    'garansi': {
        'answer': f'{EMOJIS["success"]} **Garansi Terpercaya:**\n'
                 f'• {EMOJIS["star"]} 2 tahun garansi resmi distributor\n'
                 f'• {EMOJIS["success"]} 30 hari garansi tukar baru\n'
                 f'• {EMOJIS["success"]} Berlaku untuk kerusakan pabrik\n'
                 f'• {EMOJIS["success"]} Klaim mudah via aplikasi\n'
                 f'• {EMOJIS["success"]} Pickup gratis untuk klaim garansi\n'
                 f'• {EMOJIS["info"]} Tidak berlaku: kerusakan fisik/air',
        'keywords': ['garansi', 'warranty', 'jaminan', 'klaim', 'rusak'],
        'category': 'warranty',
        'priority': 1
    },
    'kontak': {
        'answer': f'{EMOJIS["info"]} **Customer Service 24/7:**\n'
                 f'• {EMOJIS["success"]} WhatsApp: 0812-3456-7890\n'
                 f'• {EMOJIS["success"]} Telegram: @SemarakBotCS\n'
                 f'• {EMOJIS["success"]} Email: cs@semuabisakamubeli.com\n'
                 f'• {EMOJIS["success"]} Live Chat: Website resmi\n'
                 f'• {EMOJIS["success"]} Instagram: @semuabisakamubeli\n'
                 f'• {EMOJIS["info"]} Response time: < 5 menit (24/7)',
        'keywords': ['kontak', 'contact', 'hubungi', 'cs', 'customer service', 'bantuan'],
        'category': 'support',
        'priority': 1
    },
    'return': {
        'answer': f'{EMOJIS["success"]} **Kebijakan Return Fleksibel:**\n'
                 f'• {EMOJIS["success"]} 30 hari return tanpa alasan\n'
                 f'• {EMOJIS["success"]} Refund 100% jika barang tidak sesuai\n'
                 f'• {EMOJIS["success"]} Pickup gratis untuk return\n'
                 f'• {EMOJIS["success"]} Proses refund 1-3 hari kerja\n'
                 f'• {EMOJIS["info"]} Syarat: barang dalam kondisi baru',
        'keywords': ['return', 'retur', 'kembalikan', 'refund', 'tukar'],
        'category': 'return',
        'priority': 2
    }
}

# Enhanced Product Database
products_db = [
    {
        'id': 1, 
        'name': 'iPhone 15 Pro Max', 
        'category': 'elektronik', 
        'price': 18999000, 
        'stock': 15, 
        'description': 'iPhone terbaru dengan chip A17 Pro, kamera 48MP dengan zoom 5x, dan baterai tahan seharian',
        'rating': 4.9,
        'sold': 234,
        'tags': ['smartphone', 'apple', 'premium', 'flagship'],
        'image': 'https://example.com/iphone15.jpg'
    },
    {
        'id': 2, 
        'name': 'MacBook Air M3', 
        'category': 'elektronik', 
        'price': 16999000, 
        'stock': 8, 
        'description': 'Laptop ultra-tipis dengan chip M3, RAM 16GB, SSD 512GB, perfect untuk professional',
        'rating': 4.8,
        'sold': 156,
        'tags': ['laptop', 'apple', 'ultrabook', 'professional'],
        'image': 'https://example.com/macbook.jpg'
    },
    {
        'id': 3, 
        'name': 'Nike Air Jordan 1 Retro', 
        'category': 'fashion', 
        'price': 2299000, 
        'stock': 25, 
        'description': 'Sneakers legendaris dengan desain klasik, bahan premium leather, nyaman untuk daily wear',
        'rating': 4.7,
        'sold': 89,
        'tags': ['sneakers', 'nike', 'basketball', 'retro'],
        'image': 'https://example.com/jordan1.jpg'
    },
    {
        'id': 4, 
        'name': 'Tas Ransel Anti Maling', 
        'category': 'fashion', 
        'price': 599000, 
        'stock': 40, 
        'description': 'Backpack dengan fitur anti-theft, USB charging port, tahan air, cocok untuk travel',
        'rating': 4.6,
        'sold': 312,
        'tags': ['backpack', 'travel', 'anti-theft', 'waterproof'],
        'image': 'https://example.com/backpack.jpg'
    },
    {
        'id': 5, 
        'name': 'Skincare Set K-Beauty Premium', 
        'category': 'kecantikan', 
        'price': 899000, 
        'stock': 30, 
        'description': 'Set lengkap perawatan wajah Korea dengan snail mucin, hyaluronic acid, dan vitamin C',
        'rating': 4.9,
        'sold': 445,
        'tags': ['skincare', 'korean', 'anti-aging', 'premium'],
        'image': 'https://example.com/skincare.jpg'
    },
    {
        'id': 6,
        'name': 'Gaming Chair RGB Pro',
        'category': 'elektronik',
        'price': 3499000,
        'stock': 12,
        'description': 'Kursi gaming ergonomis dengan RGB lighting, memory foam, dan reclining 180 derajat',
        'rating': 4.5,
        'sold': 78,
        'tags': ['gaming', 'chair', 'rgb', 'ergonomic'],
        'image': 'https://example.com/gamingchair.jpg'
    }
]

# Enhanced Quiz Database with Difficulty Levels
quiz_db = [
    {
        'question': 'Apa kepanjangan dari "E-commerce"?',
        'options': ['Electronic Commerce', 'Easy Commerce', 'Economic Commerce', 'Effective Commerce'],
        'answer': 0,
        'difficulty': 'easy',
        'category': 'general',
        'explanation': 'E-commerce adalah singkatan dari Electronic Commerce, yaitu perdagangan elektronik.'
    },
    {
        'question': 'Metode pembayaran mana yang paling aman untuk transaksi online?',
        'options': ['Transfer Bank', 'Kartu Kredit dengan 3D Secure', 'E-wallet', 'Semua sama amannya jika menggunakan platform terpercaya'],
        'answer': 3,
        'difficulty': 'medium',
        'category': 'payment',
        'explanation': 'Semua metode pembayaran aman jika menggunakan platform terpercaya dengan enkripsi SSL.'
    },
    {
        'question': 'Apa keuntungan berbelanja di "Semua Bisa Kamu Beli"?',
        'options': ['Harga kompetitif', 'Gratis ongkir', 'Garansi resmi', 'Semua benar'],
        'answer': 3,
        'difficulty': 'easy',
        'category': 'store',
        'explanation': 'Semua Bisa Kamu Beli menawarkan harga kompetitif, gratis ongkir, dan garansi resmi.'
    },
    {
        'question': 'Berapa lama masa garansi standar untuk produk elektronik?',
        'options': ['6 bulan', '1 tahun', '2 tahun', '3 tahun'],
        'answer': 2,
        'difficulty': 'medium',
        'category': 'warranty',
        'explanation': 'Produk elektronik di toko kami memiliki garansi standar 2 tahun.'
    },
    {
        'question': 'Apa yang dimaksud dengan "Same Day Delivery"?',
        'options': ['Pengiriman dalam 24 jam', 'Pengiriman di hari yang sama', 'Pengiriman express', 'Pengiriman gratis'],
        'answer': 1,
        'difficulty': 'easy',
        'category': 'shipping',
        'explanation': 'Same Day Delivery adalah layanan pengiriman di hari yang sama saat pemesanan.'
    }
]

# Enhanced Database Storage
loyalty_db = {}
orders_db = []
questions_db = []
user_stats = {}
achievements_db = {}
daily_streaks = {}

# Helper Functions
def find_faq_answer(message: str) -> Optional[str]:
    """Enhanced FAQ search with fuzzy matching"""
    message_lower = message.lower()
    best_match = None
    best_score = 0
    
    for category, data in faq_db.items():
        # Exact keyword matching (highest priority)
        for keyword in data['keywords']:
            if keyword in message_lower:
                return data['answer']
        
        # Fuzzy matching for similar words
        for keyword in data['keywords']:
            ratio = difflib.SequenceMatcher(None, keyword, message_lower).ratio()
            if ratio > 0.7 and ratio > best_score:
                best_score = ratio
                best_match = data['answer']
    
    return best_match if best_score > 0.7 else None

def get_product_by_id(product_id: int) -> Optional[Dict]:
    """Get product by ID with enhanced data"""
    for product in products_db:
        if product['id'] == product_id:
            return product
    return None

def get_products_by_category(category: str) -> List[Dict]:
    """Get products by category with sorting"""
    products = [p for p in products_db if p['category'] == category.lower()]
    return sorted(products, key=lambda x: (x['rating'], x['sold']), reverse=True)

def search_products(query: str) -> List[Dict]:
    """Search products by name, description, or tags"""
    query_lower = query.lower()
    results = []
    
    for product in products_db:
        score = 0
        
        # Name matching
        if query_lower in product['name'].lower():
            score += 3
        
        # Description matching
        if query_lower in product['description'].lower():
            score += 2
        
        # Tags matching
        for tag in product['tags']:
            if query_lower in tag.lower():
                score += 1
        
        if score > 0:
            product_copy = product.copy()
            product_copy['relevance_score'] = score
            results.append(product_copy)
    
    return sorted(results, key=lambda x: x['relevance_score'], reverse=True)

def get_all_categories() -> List[str]:
    """Get all unique categories"""
    return list(set(p['category'] for p in products_db))

def get_random_quiz(difficulty: str = None) -> Dict:
    """Get random quiz with optional difficulty filter"""
    if difficulty:
        filtered_quizzes = [q for q in quiz_db if q['difficulty'] == difficulty]
        return random.choice(filtered_quizzes) if filtered_quizzes else random.choice(quiz_db)
    return random.choice(quiz_db)

def get_user_points(user_id: int) -> int:
    """Get user loyalty points"""
    return loyalty_db.get(str(user_id), 0)

def add_user_points(user_id: int, points: int) -> int:
    """Add points to user with achievement checking"""
    user_id_str = str(user_id)
    old_points = loyalty_db.get(user_id_str, 0)
    new_points = old_points + points
    loyalty_db[user_id_str] = new_points
    
    # Update user stats
    if user_id_str not in user_stats:
        user_stats[user_id_str] = {
            'total_points_earned': 0,
            'quizzes_answered': 0,
            'purchases_made': 0,
            'questions_asked': 0,
            'join_date': datetime.now().isoformat()
        }
    
    user_stats[user_id_str]['total_points_earned'] += points
    
    # Check for achievements
    check_achievements(user_id)
    
    return new_points

def get_user_status(user_id: int) -> str:
    """Get user membership status"""
    points = get_user_points(user_id)
    if points >= LOYALTY_CONFIG['premium_threshold']:
        return 'Premium'
    elif points >= LOYALTY_CONFIG['vip_threshold']:
        return 'VIP'
    else:
        return 'Regular'

def check_achievements(user_id: int) -> List[str]:
    """Check and award achievements"""
    user_id_str = str(user_id)
    new_achievements = []
    
    if user_id_str not in achievements_db:
        achievements_db[user_id_str] = []
    
    user_achievements = achievements_db[user_id_str]
    points = get_user_points(user_id)
    stats = user_stats.get(user_id_str, {})
    
    # Check various achievements
    achievement_checks = {
        'first_purchase': stats.get('purchases_made', 0) >= 1,
        'quiz_master': stats.get('quizzes_answered', 0) >= 10,
        'loyal_customer': points >= 500,
        'streak_champion': get_user_streak(user_id) >= 7
    }
    
    for achievement_id, condition in achievement_checks.items():
        if condition and achievement_id not in user_achievements:
            user_achievements.append(achievement_id)
            new_achievements.append(achievement_id)
            # Award achievement points
            add_user_points(user_id, ACHIEVEMENTS[achievement_id]['points'])
    
    return new_achievements

def get_user_streak(user_id: int) -> int:
    """Get user's current daily streak"""
    user_id_str = str(user_id)
    if user_id_str not in daily_streaks:
        return 0
    
    streak_data = daily_streaks[user_id_str]
    last_activity = datetime.fromisoformat(streak_data['last_activity'])
    
    # Check if streak is still valid (within 48 hours)
    if datetime.now() - last_activity > timedelta(hours=48):
        daily_streaks[user_id_str]['streak'] = 0
        return 0
    
    return streak_data['streak']

def update_user_streak(user_id: int):
    """Update user's daily streak"""
    user_id_str = str(user_id)
    today = datetime.now().date()
    
    if user_id_str not in daily_streaks:
        daily_streaks[user_id_str] = {
            'streak': 1,
            'last_activity': datetime.now().isoformat(),
            'last_date': today.isoformat()
        }
        return
    
    streak_data = daily_streaks[user_id_str]
    last_date = datetime.fromisoformat(streak_data['last_date']).date()
    
    if today == last_date:
        # Same day, just update activity time
        streak_data['last_activity'] = datetime.now().isoformat()
    elif today == last_date + timedelta(days=1):
        # Next day, increment streak
        streak_data['streak'] += 1
        streak_data['last_activity'] = datetime.now().isoformat()
        streak_data['last_date'] = today.isoformat()
    else:
        # Streak broken, reset
        streak_data['streak'] = 1
        streak_data['last_activity'] = datetime.now().isoformat()
        streak_data['last_date'] = today.isoformat()

def save_question(user, question: str) -> int:
    """Save user question with enhanced data"""
    question_data = {
        'id': len(questions_db) + 1,
        'user': str(user),
        'user_id': user.id,
        'question': question,
        'status': 'pending',
        'timestamp': datetime.now().isoformat(),
        'category': 'general'
    }
    questions_db.append(question_data)
    
    # Update user stats
    user_id_str = str(user.id)
    if user_id_str in user_stats:
        user_stats[user_id_str]['questions_asked'] += 1
    
    return question_data['id']

def get_pending_questions() -> List[Dict]:
    """Get all pending questions"""
    return [q for q in questions_db if q['status'] == 'pending']

def close_question(question_id: int) -> bool:
    """Close a question"""
    for q in questions_db:
        if q['id'] == question_id:
            q['status'] = 'closed'
            q['closed_at'] = datetime.now().isoformat()
            return True
    return False

def create_order(user, product_id: int, quantity: int) -> Optional[Dict]:
    """Create order with enhanced features"""
    product = get_product_by_id(product_id)
    if not product or product['stock'] < quantity:
        return None
    
    # Calculate pricing with discounts
    base_total = product['price'] * quantity
    user_status = get_user_status(user.id)
    discount = 0
    
    if user_status == 'Premium':
        discount = LOYALTY_CONFIG['premium_discount']
    elif user_status == 'VIP':
        discount = LOYALTY_CONFIG['vip_discount']
    
    discounted_total = base_total * (1 - discount)
    
    # Update stock
    product['stock'] -= quantity
    product['sold'] += quantity
    
    order = {
        'id': len(orders_db) + 1,
        'user': str(user),
        'user_id': user.id,
        'product_id': product_id,
        'product_name': product['name'],
        'quantity': quantity,
        'price': product['price'],
        'base_total': base_total,
        'discount_percent': discount * 100,
        'discount_amount': base_total - discounted_total,
        'final_total': discounted_total,
        'status': 'pending',
        'timestamp': datetime.now().isoformat(),
        'estimated_delivery': (datetime.now() + timedelta(days=3)).isoformat()
    }
    orders_db.append(order)
    
    # Update user stats
    user_id_str = str(user.id)
    if user_id_str in user_stats:
        user_stats[user_id_str]['purchases_made'] += 1
    
    return order

def get_user_orders(user_id: int) -> List[Dict]:
    """Get all orders for a user"""
    return [order for order in orders_db if order['user_id'] == user_id]

def get_leaderboard(limit: int = 10) -> List[Dict]:
    """Get loyalty points leaderboard"""
    sorted_users = sorted(loyalty_db.items(), key=lambda x: x[1], reverse=True)
    return [{'user_id': user_id, 'points': points} for user_id, points in sorted_users[:limit]]

def get_statistics() -> Dict:
    """Get platform statistics"""
    return {
        'total_users': len(loyalty_db),
        'total_orders': len(orders_db),
        'total_questions': len(questions_db),
        'pending_questions': len(get_pending_questions()),
        'total_products': len(products_db),
        'categories': len(get_all_categories()),
        'total_points_distributed': sum(loyalty_db.values()),
        'average_points_per_user': sum(loyalty_db.values()) / len(loyalty_db) if loyalty_db else 0
    }