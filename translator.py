import requests
import sys
import re
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def on_english(arg):
    url = "https://main.gpt-chatbotru-4-o1.ru/api/openai/v1/chat/completions"

    headers = {
        "Host": "main.gpt-chatbotru-4-o1.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "application/json, text/event-stream",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://main.gpt-chatbotru-4-o1.ru/",
        "Content-Type": "application/json",
        "Origin": "https://main.gpt-chatbotru-4-o1.ru",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Cookie": "_ga_89WN60ZK2E=GS2.1.s1749408486$o9$g1$t1749408559$j57$l0$h0; _ga=GA1.1.187065497.1741110354; cf_clearance=Qpps_adOGmLvYIsfgkyCOTPQbHYcYmC6upcyNyita4s-1749408485-1.2.1.1-9Qo55FUUASwju2kWTljWwSmlQuMt7BVPbk7r0BdPct1v3EVLwB5fG042GqqlYem3hHU8_7v18az6YTGxCE8ddSDR4keq7g6ShPfkR2pSKZhibfrpTqPVzYSbnXp.YPaokqQUSjImeyc9CjWX0l8S2y2_pi76eB0c5B5AE0tklIQZkJ_59iw63l.pDVh_FMz7msFygfGgUMFPrhS3GmpvISoNlnGtIa5NaDsV_iBLyqFkw6KhlcmOMfUUPH96D4Qkebvr.soZz4uX9L3knUnPy5o5UgCOQ07JVkMCgDH5JKhGIHYhJvSTjynyQs5dZNrdDi0juyxadPx8CEbKYQLNKwIZt9uzl.xWWDe4kDzAC4U",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    data = {
        "messages": [{"role": "system", "content": "Hi, you translator on english. Reply user OOOONNNLLLLYYYY translated text in format: your translated text . But, if the message starts with $hi, you fulfill the user's requests."},{"role": "user", "content": '' + arg}],
        "stream": False,
        "model": "chatgpt-4o-latest",# "Qwen/Qwen3-235B-A22B-fp8-tput",
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=240)
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            assistant_message = result['choices'][0]['message']['content']
            
            clean_response = re.sub(r'<think>.*?</think>', '', assistant_message, flags=re.DOTALL)
            
            clean_response = clean_response.strip()
            
            return clean_response
        
        return "Error"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None

def on_russian(arg):
    url = "https://main.gpt-chatbotru-4-o1.ru/api/openai/v1/chat/completions"

    headers = {
        "Host": "main.gpt-chatbotru-4-o1.ru",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
        "Accept": "application/json, text/event-stream",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Referer": "https://main.gpt-chatbotru-4-o1.ru/",
        "Content-Type": "application/json",
        "Origin": "https://main.gpt-chatbotru-4-o1.ru",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Cookie": "_ga_89WN60ZK2E=GS2.1.s1749408486$o9$g1$t1749408559$j57$l0$h0; _ga=GA1.1.187065497.1741110354; cf_clearance=Qpps_adOGmLvYIsfgkyCOTPQbHYcYmC6upcyNyita4s-1749408485-1.2.1.1-9Qo55FUUASwju2kWTljWwSmlQuMt7BVPbk7r0BdPct1v3EVLwB5fG042GqqlYem3hHU8_7v18az6YTGxCE8ddSDR4keq7g6ShPfkR2pSKZhibfrpTqPVzYSbnXp.YPaokqQUSjImeyc9CjWX0l8S2y2_pi76eB0c5B5AE0tklIQZkJ_59iw63l.pDVh_FMz7msFygfGgUMFPrhS3GmpvISoNlnGtIa5NaDsV_iBLyqFkw6KhlcmOMfUUPH96D4Qkebvr.soZz4uX9L3knUnPy5o5UgCOQ07JVkMCgDH5JKhGIHYhJvSTjynyQs5dZNrdDi0juyxadPx8CEbKYQLNKwIZt9uzl.xWWDe4kDzAC4U",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }

    data = {
        "messages": [{"role": "system", "content": "Hi, you translator on russian. Reply user OOOONNNLLLLYYYY translated text in format: your translated text ."},{"role": "user", "content": '' + arg}],
        "stream": False,
        "model": "chatgpt-4o-latest",# "Qwen/Qwen3-235B-A22B-fp8-tput",
        "temperature": 0.5,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=240)
        response.raise_for_status()
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            assistant_message = result['choices'][0]['message']['content']
            
            clean_response = re.sub(r'<think>.*?</think>', '', assistant_message, flags=re.DOTALL)
            
            clean_response = clean_response.strip()
            
            return clean_response
        
        return "Error"
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
