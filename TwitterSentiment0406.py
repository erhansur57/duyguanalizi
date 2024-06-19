import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import requests
import pandas as pd
import json
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from PIL import Image, ImageTk  # PIL kütüphanesi

# Twitter API ayarları
BEARER_TOKEN = ''

# Azure Sentiment Analysis ayarları
AZURE_ENDPOINT = ""
AZURE_KEY = ""

search_url = "https://api.twitter.com/2/tweets/search/recent"

def create_headers(bearer_token):
    headers = {"Authorization": f"Bearer {bearer_token}"}
    return headers

def connect_to_endpoint(url, headers, params):
    response = requests.get(url, headers=headers, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(f"Request returned an error: {response.status_code} {response.text}")
    return response.json()

def authenticate_client():
    ta_credential = AzureKeyCredential(AZURE_KEY)
    text_analytics_client = TextAnalyticsClient(
            endpoint=AZURE_ENDPOINT, 
            credential=ta_credential)
    return text_analytics_client

def fetch_and_analyze_tweets(query, start_time, end_time, max_results):
    headers = create_headers(BEARER_TOKEN)
    query += " -is:retweet"  # Retweetleri hariç tutmak için sorguya ekleme yapılıyor
    params = {
        'query': query,
        'start_time': start_time,
        'end_time': end_time,
        'max_results': max_results,
        'tweet.fields': 'created_at,text'
    }
    json_response = connect_to_endpoint(search_url, headers, params)
    tweets = json_response['data'] if 'data' in json_response else []

    text_analytics_client = authenticate_client()
    result = []
    for tweet in tweets:
        response = text_analytics_client.analyze_sentiment([tweet['text']], language="tr")
        for doc in response:
            if not doc.is_error:
                result.append({
                    'tweet_created_at': tweet['created_at'],                    
                    'id_str': tweet['id'],                    
                    'text': tweet['text'],                                   
                    'SentimentPozitif': doc.confidence_scores.positive,
                    'SentimentNotr': doc.confidence_scores.neutral,
                    'SentimentNegatif': doc.confidence_scores.negative,
                    'Tweet_Genel_Durum': doc.sentiment
                })
    return result
def fetch_and_analyze_tweets(query, start_time, end_time, max_results):
    headers = create_headers(BEARER_TOKEN)
    query += " -is:retweet"  # Retweetleri hariç tutmak için sorguya ekleme yapılıyor
    params = {
        'query': query,
        'start_time': start_time,
        'end_time': end_time,
        'max_results': max_results,
        'tweet.fields': 'created_at,text'
    }
    json_response = connect_to_endpoint(search_url, headers, params)
    tweets = json_response['data'] if 'data' in json_response else []

    text_analytics_client = authenticate_client()
    result = []
    for tweet in tweets:
        response = text_analytics_client.analyze_sentiment([tweet['text']], language="tr")
        for doc in response:
            if not doc.is_error:
                result.append({
                    'tweet_created_at': tweet['created_at'],                    
                    'id_str': tweet['id'],                    
                    'text': tweet['text'],                                   
                    'SentimentPozitif': doc.confidence_scores.positive,
                    'SentimentNotr': doc.confidence_scores.neutral,
                    'SentimentNegatif': doc.confidence_scores.negative,
                    'Tweet_Genel_Durum': doc.sentiment
                })
    return result


def save_tweets_to_json(tweets, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tweets, f, ensure_ascii=False, indent=4)

def save_tweets_to_excel(tweets, filename):
    df = pd.DataFrame(tweets)
    df.to_excel(filename, index=False)

def on_submit():
    query = query_entry.get().strip()
    if not query:
        messagebox.showerror("Arama Terimi", "Bu alan boş olamaz.")
        return
    
    start_date = f"{start_year_cb.get()}-{start_month_cb.get()}-{start_day_cb.get()}T{start_hour_cb.get()}:{start_minute_cb.get()}:00Z"
    end_date = f"{end_year_cb.get()}-{end_month_cb.get()}-{end_day_cb.get()}T{end_hour_cb.get()}:{end_minute_cb.get()}:00Z"
    
    try:
        max_results = int(max_results_entry.get())
    except ValueError:
        messagebox.showerror("Geçersiz Değer", "Lütfen en fazla değeri giriniz")
        return

    try:
        tweets = fetch_and_analyze_tweets(query, start_date, end_date, max_results)
        # tweets değişkenini global yaparak diğer fonksiyonlarda kullanılmasını sağlayın
        global fetched_tweets
        fetched_tweets = tweets
    except Exception as e:
        messagebox.showerror("Hata", str(e))
        return
    
    messagebox.showinfo("Başarılı", "Tweetler başarıyla analiz edildi")

def save_to_json():
    json_filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Dosyası", "*.json")])
    if json_filename:
        save_tweets_to_json(fetched_tweets, json_filename)
        messagebox.showinfo("Başarılı", f"Tweetler kaydedildi {json_filename}")

def save_to_excel():
    excel_filename = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Dosyası", "*.xlsx")])
    if excel_filename:
        save_tweets_to_excel(fetched_tweets, excel_filename)
        messagebox.showinfo("Başarılı", f"Tweetler kaydedildi {excel_filename}")


app = tk.Tk()
app.title("Twitter Duygu Analizi")
app.geometry("950x610")
app.resizable(False, False)


# Gazi Üniversitesi logosunu ekleyin ve boyutunu ayarlayın
try:
    image = Image.open("C:/Users/erhan/gazilogo.png")
    image = image.resize((250, 250), Image.LANCZOS)  # Image.ANTIALIAS yerine Image.LANCZOS kullanın
    logo = ImageTk.PhotoImage(image)
    logo_label = tk.Label(app, image=logo)
    logo_label.place(relx=1.0, rely=0, anchor='ne')  # Logoyu sağ üst köşeye yerleştirir
except Exception as e:
    messagebox.showerror("Logo Yükleme Hatası", f"Logo yüklenemedi: {e}")

tk.Label(app, text="Arama Kelimesini Girin:", font=("Helvetica", 14)).grid(row=0, column=0, columnspan=6, padx=10, pady=10, sticky="w")
query_entry = tk.Entry(app, width=70, font=("Helvetica", 12))
query_entry.grid(row=1, column=0, columnspan=6, padx=10, pady=10, sticky="w")

# Combobox Değeri
years = [str(year) for year in range(2024, 2025)]
months = [f"{month:02}" for month in range(1, 13)]
days = [f"{day:02}" for day in range(1, 32)]
hours = [f"{hour:02}" for hour in range(0, 24)]
minutes = [f"{minute:02}" for minute in range(0, 60)]

# Varsayılan tarih ve saatler (şu anki tarih ve bir saat sonrası)
now = datetime.utcnow()
default_start_time = now 
default_end_time = now

# Başlangıç Tarihi
tk.Label(app, text="Başlangıç Tarihi:", font=("Helvetica", 14)).grid(row=2, column=0, padx=10, pady=10, sticky="w")

start_frame = tk.Frame(app)
start_frame.grid(row=3, column=0, padx=10, pady=5, sticky="w")

start_year_cb = ttk.Combobox(start_frame, values=years, width=5, font=("Helvetica", 12))
start_year_cb.set(default_start_time.year)
start_year_cb.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
start_month_cb = ttk.Combobox(start_frame, values=months, width=3, font=("Helvetica", 12))
start_month_cb.set(f"{default_start_time.month:02}")
start_month_cb.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
start_day_cb = ttk.Combobox(start_frame, values=days, width=3, font=("Helvetica", 12))
start_day_cb.set(f"{default_start_time.day:02}")
start_day_cb.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
start_hour_cb = ttk.Combobox(start_frame, values=hours, width=3, font=("Helvetica", 12))
start_hour_cb.set(f"{default_start_time.hour:02}")
start_hour_cb.grid(row=0, column=3, padx=(0, 5), pady=5, sticky="w")
start_minute_cb = ttk.Combobox(start_frame, values=minutes, width=3, font=("Helvetica", 12))
start_minute_cb.set(f"{default_start_time.minute:02}")
start_minute_cb.grid(row=0, column=4, padx=(0, 5), pady=5, sticky="w")

# Bitiş Tarihi
tk.Label(app, text="Bitiş Tarihi:", font=("Helvetica", 14)).grid(row=4, column=0, padx=10, pady=10, sticky="w")

end_frame = tk.Frame(app)
end_frame.grid(row=5, column=0, padx=10, pady=5, sticky="w")

end_year_cb = ttk.Combobox(end_frame, values=years, width=5, font=("Helvetica", 12))
end_year_cb.set(default_end_time.year)
end_year_cb.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")
end_month_cb = ttk.Combobox(end_frame, values=months, width=3, font=("Helvetica", 12))
end_month_cb.set(f"{default_end_time.month:02}")
end_month_cb.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")
end_day_cb = ttk.Combobox(end_frame, values=days, width=3, font=("Helvetica", 12))
end_day_cb.set(f"{default_end_time.day:02}")
end_day_cb.grid(row=0, column=2, padx=(0, 5), pady=5, sticky="w")
end_hour_cb = ttk.Combobox(end_frame, values=hours, width=3, font=("Helvetica", 12))
end_hour_cb.set(f"{default_end_time.hour:02}")
end_hour_cb.grid(row=0, column=3, padx=(0, 5), pady=5, sticky="w")
end_minute_cb = ttk.Combobox(end_frame, values=minutes, width=3, font=("Helvetica", 12))
end_minute_cb.set(f"{default_end_time.minute:02}")
end_minute_cb.grid(row=0, column=4, padx=(0, 5), pady=5, sticky="w")

tk.Label(app, text="Kaç tweet getirilecek '10-100':", font=("Helvetica", 14)).grid(row=6, column=0, padx=10, pady=10, sticky="w")
max_results_entry = tk.Entry(app, width=10, font=("Helvetica", 12))
max_results_entry.grid(row=7, column=0, padx=10, pady=10, sticky="w")

tk.Button(app, text="Gönder", command=on_submit, font=("Helvetica", 14)).grid(row=8, column=0, padx=10, pady=10, sticky="w")



# Save buttons
save_json_button = tk.Button(app, text="Analzi JSON olarak Kaydet", command=save_to_json, font=("Helvetica", 14))
save_json_button.grid(row=10, column=0, padx=10, pady=10, sticky="w")

save_excel_button = tk.Button(app, text="Analizi Excel olarak Kaydet", command=save_to_excel, font=("Helvetica", 14))
save_excel_button.grid(row=11, column=0, padx=10, pady=10, sticky="w")

app.mainloop()
