import asyncio
import sys
import os
import aiosqlite
from colorama import Fore, Style, init

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))

from proxy_manager.core.storage import StorageManager

init(autoreset=True)

async def main():
    try:
        storage = StorageManager()
        db_path = storage.db_path
        
        print(f"\n🕵️  {Style.BRIGHT}Proxy Assessment for Pentesting (Indonesia){Style.RESET_ALL}")
        print(f"Checking DB: {db_path}\n")
        
        async with aiosqlite.connect(db_path) as db:
            query = """
                SELECT ip, port, protocol, response_time_ms, health_score, anonymity, isp 
                FROM proxies 
                WHERE country='ID'
            """
            async with db.execute(query) as cursor:
                proxies = await cursor.fetchall()
                
                pentest_grade = []
                general_grade = []
                poor_grade = []
                
                for p in proxies:
                    ip, port, proto, latency, score, anon, isp = p
                    p_dict = {
                        "addr": f"{ip}:{port}",
                        "proto": proto,
                        "lat": latency,
                        "score": score,
                        "anon": anon,
                        "isp": isp
                    }
                    
                    # Criteria for Pentest Grade:
                    # 1. Anonymity: elite or anonymous (NOT transparent)
                    # 2. Latency: < 2000ms (2s)
                    # 3. Health Score: > 50
                    # 4. Protocol: SOCKS5/4 preferred, HTTP ok if CONNECT supported (assumed yes for now)
                    
                    is_anon = anon in ['elite', 'anonymous']
                    is_fast = latency < 2000
                    is_healthy = score > 50
                    
                    if is_anon and is_fast and is_healthy:
                        pentest_grade.append(p_dict)
                    elif latency < 5000 and score > 20:
                        general_grade.append(p_dict)
                    else:
                        poor_grade.append(p_dict)
                        
                # Display Results
                print(f"{Fore.GREEN}✅ Pentest Grade (Elite/Anon, <2s, Stable): {len(pentest_grade)}{Style.RESET_ALL}")
                if pentest_grade:
                    print(f"{'Address':<22} | {'Proto':<6} | {'Lat':<6} | {'Anon':<10} | {'ISP'}")
                    print("-" * 70)
                    for p in pentest_grade:
                        print(f"{p['addr']:<22} | {p['proto']:<6} | {p['lat']:<4}ms | {p['anon']:<10} | {p['isp']}")
                else:
                    print("   (No proxies meet strict pentest standards yet)")

                print(f"\n{Fore.YELLOW}⚠️  General Grade (Usable for Browsing): {len(general_grade)}{Style.RESET_ALL}")
                if general_grade:
                     # Limit display
                     for p in general_grade[:5]:
                         print(f"   {p['addr']} ({p['lat']}ms) - {p['anon']}")
                     if len(general_grade) > 5:
                         print(f"   ... and {len(general_grade)-5} more")

                print(f"\n{Fore.RED}❌ Poor Quality (Slow/Dead): {len(poor_grade)}{Style.RESET_ALL}")
                
                # Summary Advice
                print("\n" + "="*50)
                print("💡 ASSESSMENT SUMMARY")
                if len(pentest_grade) > 0:
                    print(f"{Fore.GREEN}SUCCESS: You have {len(pentest_grade)} proxies ready for Pentest tools (Burp/SQLMap).")
                    print(f"Recommended: Use Gateway (`python -m proxy_manager.main --serve`) to rotate through them.{Style.RESET_ALL}")
                else:
                    print(f"{Fore.YELLOW}WARNING: No 'Pentest Grade' proxies found yet.")
                    print("Advice: Run the Masscan pipeline to find reliable candidates.")
                    print("Public lists are often slow/transparent.{Style.RESET_ALL}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Force UTF-8
    sys.stdout.reconfigure(encoding='utf-8')
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
