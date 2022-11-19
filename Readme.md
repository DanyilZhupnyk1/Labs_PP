from flask import Flask                  додаємо Flask
from waitress import serve               додаємо з вайтрес властивість Serve

app = Flask(__name__)                    даємо ім'я

@app.route('/')                             
def index():                             функція повернення нашого тексту
    return 'Hello, World 7'

if __name__ == '__main__':                                                                      Перевірка імені
    serve(app, host='0.0.0.0', port=50100, threads=1, url_prefix="/api/v1/hello-world-7")       надання даних про хост, порт, адресу


python --version - перевірка версії
.\poetry\Scripts\activate - запуск вірт середовища
py -m virtualenv -p="C:\Users\111\AppData\Local\Programs\Python\Python37\python.exe" poetry - шлях до пайтону