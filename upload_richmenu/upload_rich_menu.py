import requests
import json
import os
from dotenv import load_dotenv

# 只在本地開發時載入 .env（避免在 Render 重複讀取）
if os.getenv("RENDER") is None:  # Render 上會內建設定 RENDER=True
    load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
HEADERS = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

# Step 1: 上傳 rich menu 結構
with open('richmenu.json', 'r', encoding='utf-8') as f:
    richmenu_data = json.load(f)

response = requests.post(
    'https://api.line.me/v2/bot/richmenu',
    headers=HEADERS,
    json=richmenu_data
)

if response.status_code != 200:
    print('❌ 建立 RichMenu 失敗:', response.text)
    exit()

richmenu_id = response.json()["richMenuId"]
print('✅ RichMenu ID:', richmenu_id)

# Step 2: 上傳圖片
IMAGE_PATH = 'image_843.png'
headers_img = {
    "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}",
    "Content-Type": "image/png"
}

with open(IMAGE_PATH, 'rb') as f:
    image_response = requests.post(
        f'https://api-data.line.me/v2/bot/richmenu/{richmenu_id}/content',
        headers=headers_img,
        data=f
    )

if image_response.status_code != 200:
    print('❌ 上傳圖片失敗:', image_response.text)
    exit()
else:
    print('✅ 圖片上傳成功')

# Step 3: 設定為預設 rich menu
set_default = requests.post(
    f'https://api.line.me/v2/bot/user/all/richmenu/{richmenu_id}',
    headers=HEADERS
)

if set_default.status_code != 200:
    print('❌ 設為預設失敗:', set_default.text)
else:
    print('✅ 設為預設 RichMenu 成功！')


# # Headers
# headers = {
#     "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
# }

# # Step 1: 取得所有 Rich Menu 列表
# def get_all_richmenus():
#     url = "https://api.line.me/v2/bot/richmenu/list"
#     response = requests.get(url, headers=headers)
#     if response.status_code == 200:
#         return response.json().get("richmenus", [])
#     else:
#         print("取得 richmenu 失敗：", response.status_code, response.text)
#         return []

# # Step 2: 刪除特定 Rich Menu
# def delete_richmenu(richmenu_id):
#     url = f"https://api.line.me/v2/bot/richmenu/{richmenu_id}"
#     response = requests.delete(url, headers=headers)
#     if response.status_code == 200:
#         print(f"✅ 已刪除 Rich Menu: {richmenu_id}")
#     else:
#         print(f"❌ 刪除失敗: {richmenu_id} - {response.status_code} {response.text}")

# # 主流程：刪除所有 Rich Menu
# def delete_all_richmenus():
#     richmenus = get_all_richmenus()
#     if not richmenus:
#         print("目前沒有任何 Rich Menu")
#         return

#     for richmenu in richmenus:
#         delete_richmenu(richmenu["richMenuId"])

# # 執行
# delete_all_richmenus()