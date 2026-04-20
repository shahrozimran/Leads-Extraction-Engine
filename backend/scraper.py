import os
import json
import time
from urllib.parse import urlparse
import urllib.request
import urllib.error
import re
from typing import Iterator, Dict
from ddgs import DDGS
from dotenv import load_dotenv
import openai

# Load environment variables
load_dotenv()

# Initialize OpenAI Client
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def is_valid_company_lead_heuristic(url: str, title: str, description: str) -> bool:
    """Basic domain checking to quickly reject massive obvious hubs."""
    url_lower = url.lower()
    
    blacklisted_domains = [
        "youtube.com", "facebook.com", "instagram.com", "linkedin.com", "pinterest.com",
        "twitter.com", "tiktok.com", "amazon.", "ebay.", "alibaba.com", "aliexpress.com",
        "indiamart.com", "tradekey.com", "flipkart.com", "wikipedia.org", "nordstrom.com",
        "macys.com", "justdial.com", "yelp.com", "google.com", "yahoo.com", "bloomberg.com",
        "forbes.com", "quora.com", "reddit.com", "etsy.com", "target.com", "walmart.com",
        "kompass.com", "thomasnet.com", "yellowpages.com"
    ]
    try:
        domain = urlparse(url).netloc.lower()
    except Exception:
        domain = url_lower

    for b_domain in blacklisted_domains:
        if b_domain in domain:
            return False

    blacklisted_url_keywords = ["/blog", "/news", "/article", 
                                "directory", "top-10", "top-20", "list-of", "best-companies"]
    for keyword in blacklisted_url_keywords:
        if keyword in url_lower or keyword in title.lower():
            return False

    return True

def extract_email_from_url(url: str) -> str:
    """Attempts to fetch the homepage and regex an email address."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        with urllib.request.urlopen(req, timeout=5) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Regex for standard emails
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, html)
            
            for e in emails:
                e_lower = e.lower()
                # Exclude image/asset extensions and common noreplies
                if e_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.css', '.js', '.svg', '.webp')):
                    continue
                if e_lower.startswith(('sentry', 'noreply', 'no-reply')):
                    continue
                return e  # Return the first valid-looking email
    except Exception:
        pass
    return ""

def llm_verify_lead(query: str, url: str, title: str, description: str) -> bool:
    """Uses ChatGPT to verify if a lead matches the explicit target."""
    try:
        if not os.getenv("OPENAI_API_KEY"):
            # Avoid crashing if key missing, just fallback to heuristic
            return True
            
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a ruthless B2B Lead Qualifier. Your job is to read a website's metadata and decide if it is EXACTLY the target requested by the user. Reject accessory vendors, distributors, blogs, news articles, repair shops, marketplaces, and directory lists. Reply ONLY with the word 'YES' if it aligns with the core intent, or 'NO' if it does not."},
                {"role": "user", "content": f"User Search Intent: {query}\n\nTarget URL: {url}\nTitle: {title}\nDescription: {description}\n\nIs this a direct, primary provider/company matching the search intent exactly?"}
            ],
            temperature=0.0,
            max_tokens=2
        )
        answer = response.choices[0].message.content.strip().upper()
        return answer.startswith('YES')
    except Exception as e:
        print(f"OpenAI error: {e}")
        # If OpenAI fails, fallback to passing it if heuristics passed
        return True

def search_leads_stream(query: str, max_results: int = 50, country: str = "") -> Iterator[Dict]:
    """
    Generator that searches DDG and yields progress/leads dynamically via Dictionary.
    """
    loc_msg = f" in '{country}'" if country else ""
    yield {"type": "log", "message": f"[*] Searching for: '{query}'{loc_msg}"}
    
    # Append the country/location to the search query if provided intelligently
    base_query = f'{query} "{country}"' if country else query
    search_query = base_query + ' -"directory" -"blog"'
    
    results = []
    
    try:
        with DDGS() as ddgs:
            results_generator = ddgs.text(search_query, max_results=max_results * 5)
            
            for index, result in enumerate(results_generator):
                if len(results) >= max_results:
                    break
                    
                url = result.get("href", "")
                title = result.get("title", "")
                description = result.get("body", "")
                
                # Check basic heuristics first (fast, free)
                if is_valid_company_lead_heuristic(url, title, description):
                    domain = urlparse(url).netloc
                    yield {"type": "log", "message": f"[AI Validator] Inspecting {domain}..."}
                    
                    # AI Context verification (slower, extremely accurate)
                    is_valid = llm_verify_lead(query, url, title, description)
                    
                    if is_valid:
                        yield {"type": "log", "message": f"  [✓] Lead Approved: {domain}"}
                        
                        yield {"type": "log", "message": f"  [*] Scanning {domain} for contact emails..."}
                        email = extract_email_from_url(url)
                        if email:
                            yield {"type": "log", "message": f"  [+] Found Email: {email}"}
                        else:
                            yield {"type": "log", "message": f"  [-] No Email found."}

                        lead = {
                            "title": title,
                            "url": url,
                            "email": email,
                            "description": description
                        }
                        results.append(lead)
                        yield {"type": "lead", "data": lead}
                    else:
                        yield {"type": "log", "message": f"  [✗] Lead rejected by AI: Not relevant to search intent."}
                    
                # Rate limit prevention
                time.sleep(0.1)
                
        yield {"type": "done", "results": results}
        
    except Exception as e:
        yield {"type": "error", "message": f"[!] Error during search: {e}"}
