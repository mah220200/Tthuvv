import random
import time
import requests
from bs4 import BeautifulSoup
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)

# Kích hoạt CORS. Để đơn giản cho thử nghiệm, sử dụng ký tự đại diện (*).
# Cảnh báo: Trong sản xuất, cần khai báo domain frontend cụ thể.
CORS(app)

# Dữ liệu dự phòng (Fallback Database) trích xuất từ bảng phân tích ở Phần 2.
# Đảm bảo hệ thống không bao giờ bị gián đoạn nếu scraping bị chặn (Rate Limit / 404).
FALLBACK_WISHES = [
    "Trăng rằm đẹp nhất khi tròn đầy, còn những ngày của anh đẹp nhất khi có em bên cạnh. Chúc em một mùa Trung thu thật ngọt ngào, ấm áp và hạnh phúc nhé, cô gái của anh!",
    "Em à, đêm nay trăng sáng lắm, nhưng nụ cười em mới làm lòng anh an yên. Chúc vợ một đêm Trung thu nhẹ nhàng, ngủ ngon nhé.",
    "Chúc em Trung thu vui vẻ nhé! Bánh Trung thu có nhiều nhân, còn trái tim anh thì chỉ có một 'nhân' là em thôi.",
    "Khoảng cách có thể chia cắt chúng ta, nhưng tình yêu của chúng ta không có ranh giới. Cầu mong trăng tròn mang tình yêu của anh đến bên em đêm nay.",
    "Trung thu đầu tiên có em bên cạnh, anh chỉ mong những mùa trăng sau mình vẫn sẽ cùng nhau ngắm trăng, ăn bánh và nắm tay thật chặt."
]

def scrape_mid_autumn_wishes():
    """Hàm trích xuất dữ liệu lời chúc từ trang web mục tiêu."""
    # URL ví dụ (có thể thay đổi thành các nguồn tin thực tế)
    url = 'https://example-love-quotes.com/loi-chuc-trung-thu'
    
    # Mô phỏng User-Agent của Google Chrome
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36'
    }
    
    wishes = []
    try:
        # Thời gian trễ ngẫu nhiên mô phỏng con người
        time.sleep(random.uniform(0.5, 1.5))
        
        response = requests.get(url, headers=headers, timeout=5)
        
        # Chỉ parse HTML khi server trả về 200 OK
        if response.status_code == 200:
            # Sử dụng html.parser chuẩn của Python
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cào tất cả các đoạn văn bản chứa lời chúc
            # Giả định cấu trúc DOM là <p class="wish-item">
            wish_elements = soup.find_all('p', class_='wish-item')
            
            for element in wish_elements:
                text = element.get_text(strip=True)
                if text:
                    wishes.append(text)
    except requests.exceptions.RequestException as e:
        print(f"Scraping Error: Lỗi kết nối mạng: {e}")
        
    return wishes

@app.route('/api/v1/wishes/random', methods=['GET'])
def get_random_wish():
    """Điểm cuối API trả về một lời chúc ngẫu nhiên dưới định dạng JSON."""
    try:
        # Trong thực tế, quá trình scraping nên chạy nền (cron job) 
        # và API lấy dữ liệu từ Database. Ở đây chạy trực tiếp để minh họa.
        wishes = scrape_mid_autumn_wishes()
        
        # Cơ chế dự phòng nếu mảng rỗng (do scraping thất bại)
        if not wishes:
            wishes = FALLBACK_WISHES
            
        selected_wish = random.choice(wishes)
        
        # Hàm jsonify tự động gán Content-Type: application/json
        return jsonify({
            "status": "success",
            "source": "scraper" if len(wishes) > len(FALLBACK_WISHES) else "fallback",
            "data": {
                "wish": selected_wish
            }
        }), 200
        
    except Exception as e:
        # Xử lý ngoại lệ, trả về lỗi 500 định dạng JSON thay vì HTML
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Khởi chạy server tại cổng 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
