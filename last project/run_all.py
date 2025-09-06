# run_all.py 

import subprocess
import sys
import time
import os
import signal
from datetime import datetime
from config import EMOJIS

class BotManager:
    def __init__(self):
        self.bots = []
        self.running = False
    
    def run_bot(self, script_name):
        """Start a bot in separate process"""
        print(f"{EMOJIS['loading']} Memulai {script_name}...")
        try:
            process = subprocess.Popen(
                [sys.executable, script_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return process
        except Exception as e:
            print(f"{EMOJIS['error']} Gagal menjalankan {script_name}: {e}")
            return None
    
    def check_files(self):
        """Check if all required files exist"""
        required_files = ['config.py', 'database.py', 'cs_bot.py', 'product_bot.py']
        missing_files = []
        
        for file in required_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"{EMOJIS['error']} File tidak ditemukan: {', '.join(missing_files)}")
            return False
        
        print(f"{EMOJIS['success']} Semua file ditemukan!")
        return True
    
    def start_all_bots(self):
        """Start all bots"""
        if not self.check_files():
            return False
        
        print(f"\n{EMOJIS['rocket']} Menjalankan SemarakBot System...")
        print("=" * 50)
        
        # Start CS Bot
        cs_bot = self.run_bot("cs_bot.py")
        if cs_bot:
            self.bots.append(('CS Bot', cs_bot))
            print(f"{EMOJIS['success']} CS Bot berhasil dijalankan (PID: {cs_bot.pid})")
        
        # Start Product Bot  
        product_bot = self.run_bot("product_bot.py")
        if product_bot:
            self.bots.append(('Product Bot', product_bot))
            print(f"{EMOJIS['success']} Product Bot berhasil dijalankan (PID: {product_bot.pid})")
        
        if not self.bots:
            print(f"{EMOJIS['error']} Tidak ada bot yang berhasil dijalankan!")
            return False
        
        self.running = True
        print(f"\n{EMOJIS['celebration']} Semua bot telah aktif!")
        print(f"{EMOJIS['info']} Total bot berjalan: {len(self.bots)}")
        print(f"{EMOJIS['warning']} Tekan Ctrl+C untuk menghentikan semua bot")
        print("=" * 50)
        
        return True
    
    def monitor_bots(self):
        """Monitor bot health"""
        while self.running:
            try:
                time.sleep(5)  # Check every 5 seconds
                
                for name, process in self.bots[:]:  # Use slice to avoid modification during iteration
                    if process.poll() is not None:  # Process has terminated
                        print(f"{EMOJIS['warning']} {name} telah berhenti (Exit code: {process.returncode})")
                        self.bots.remove((name, process))
                        
                        # Try to restart
                        print(f"{EMOJIS['loading']} Mencoba restart {name}...")
                        if name == 'CS Bot':
                            new_process = self.run_bot("cs_bot.py")
                        else:
                            new_process = self.run_bot("product_bot.py")
                        
                        if new_process:
                            self.bots.append((name, new_process))
                            print(f"{EMOJIS['success']} {name} berhasil di-restart!")
                        else:
                            print(f"{EMOJIS['error']} Gagal restart {name}")
                
                if not self.bots:
                    print(f"{EMOJIS['error']} Semua bot telah berhenti!")
                    self.running = False
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"{EMOJIS['error']} Error monitoring: {e}")
    
    def stop_all_bots(self):
        """Stop all bots gracefully"""
        print(f"\n{EMOJIS['warning']} Menghentikan semua bot...")
        
        for name, process in self.bots:
            try:
                print(f"{EMOJIS['loading']} Menghentikan {name}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                    print(f"{EMOJIS['success']} {name} dihentikan dengan baik")
                except subprocess.TimeoutExpired:
                    print(f"{EMOJIS['warning']} {name} tidak merespons, paksa hentikan...")
                    process.kill()
                    process.wait()
                    print(f"{EMOJIS['success']} {name} dipaksa berhenti")
                    
            except Exception as e:
                print(f"{EMOJIS['error']} Error menghentikan {name}: {e}")
        
        self.bots.clear()
        self.running = False
        print(f"{EMOJIS['success']} Semua bot telah dihentikan!")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print(f"\n{EMOJIS['info']} Sinyal penghentian diterima...")
    manager.stop_all_bots()
    sys.exit(0)

if __name__ == "__main__":
    # Setup signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print(f"{EMOJIS['rocket']} SemarakBot System Manager")
    print(f"{EMOJIS['info']} Waktu mulai: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    manager = BotManager()
    
    if manager.start_all_bots():
        try:
            manager.monitor_bots()
        except KeyboardInterrupt:
            pass
        finally:
            manager.stop_all_bots()
    else:
        print(f"{EMOJIS['error']} Gagal menjalankan sistem bot!")
        sys.exit(1)