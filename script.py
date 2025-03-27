from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time

# Configurações
EMAIL = "******"
SENHA = "******"
QUERY = "sorvete frosty"
MAX_TWEETS = 1000  

driver = webdriver.Chrome()

def coleta_tweets():
    tweets_data = []
    last_height = driver.execute_script("return document.body.scrollHeight")
    tentativas = 0

    while len(tweets_data) < MAX_TWEETS and tentativas < 20:
    
        for _ in range(3):
            driver.execute_script("window.scrollBy(0, 1500);")
            time.sleep(1.5) 
            
      
        novos_tweets = driver.find_elements(By.CSS_SELECTOR, 'article[data-testid="tweet"]:not([data-coletado="true"])')
        
        for tweet in novos_tweets:
            try:
               
                driver.execute_script("arguments[0].setAttribute('data-coletado', 'true')", tweet)
                
                user_info = tweet.find_element(By.CSS_SELECTOR, 'div[data-testid="User-Name"]')
                username = user_info.find_element(By.XPATH, './/span[contains(text(), "@")]').text
                name = user_info.find_elements(By.TAG_NAME, 'span')[0].text
                
                date_element = tweet.find_element(By.TAG_NAME, 'time')
                date = date_element.get_attribute('datetime')
                
                text = tweet.find_element(By.CSS_SELECTOR, 'div[lang]').text
                tweet_id = tweet.find_element(By.XPATH, './/a[contains(@href, "/status/")]').get_attribute('href').split('/')[-1]

                tweets_data.append({
                    'id': tweet_id,
                    'username': username,
                    'name': name,
                    'date': date,
                    'text': text,
                    'url': f"https://twitter.com{username}/status/{tweet_id}"
                })

            except Exception as e:
                continue

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            tentativas += 1
            time.sleep(1)
        else:
            tentativas = 0
            last_height = new_height

    return tweets_data[:MAX_TWEETS]

try:
    # Login
    driver.get("https://twitter.com/i/flow/login")
    time.sleep(3)
    
    # Preenche e-mail
    email_field = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="username"]')
    email_field.send_keys(EMAIL + Keys.RETURN)
    time.sleep(2)
    
    # Preenche senha
    password_field = driver.find_element(By.CSS_SELECTOR, 'input[autocomplete="current-password"]')
    password_field.send_keys(SENHA + Keys.RETURN)
    time.sleep(5)
    
    # Busca avançada
    driver.get(f"https://twitter.com/search?q={QUERY}%20lang%3Apt%20-filter%3Areplies&src=typed_query&f=live")
    time.sleep(5)
    
    # Coleta tweets
    tweets_data = coleta_tweets()
    
    # Cria e exporta DataFrame
    df = pd.DataFrame(tweets_data)
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
    
    df.to_csv('tweets_coletados.csv', index=False)
    print(f"\n✅ CSV exportado com {len(df)} tweets!")
    print(df.head())

except Exception as e:
    print(f"Erro durante a execução: {str(e)}")
    
finally:
    driver.quit()