# ADHD 青少年親子精選

給家長閱讀的每日精選靜態網站，風格接近溫暖的親子刊物。每期一頁，總覽列在首頁。

線上閱讀：<https://addielu-phy.github.io/adhd-parenting-digest/>

## 發佈新的一天

在本倉庫根目錄執行：

```bash
# 1. 新增當日資料（檔名必須等於 date 欄位）
#    例如 data/2026-11-15.json

# 2. 產生靜態頁面
python3 build.py

# 3. 提交並推送到 GitHub
git add data/YYYY-MM-DD.json YYYY-MM-DD/ index.html
git commit -m "Add digest YYYY-MM-DD"
git push origin main
```

推送後約 1 到 2 分鐘，GitHub Pages 會更新：

- 總覽：https://addielu-phy.github.io/adhd-parenting-digest/
- 當日：https://addielu-phy.github.io/adhd-parenting-digest/YYYY-MM-DD/

## 資料格式 `data/YYYY-MM-DD.json`

```json
{
  "date": "2026-11-14",
  "summary": "本期共同主題或導讀（一句話）",
  "tonight_one_thing": "最上方「今晚只試一件事」的具體建議",
  "items": [
    {
      "title": "標題",
      "source": "來源與出處說明",
      "credibility": "同儕審查研究",
      "limitation": "選填。研究限制，沒有就省略此欄",
      "summary": "白話摘要",
      "try_tonight": "今晚可以試的做法",
      "link": "https://example.com/original"
    }
  ]
}
```

欄位說明：

| 欄位 | 必填 | 說明 |
| --- | --- | --- |
| `date` | 是 | `YYYY-MM-DD`，必須與檔名相同 |
| `summary` | 是 | 本期導讀，也會出現在總覽卡片 |
| `tonight_one_thing` | 是 | 「今晚只試一件事」 |
| `items` | 是 | 當日精選，通常 3 到 5 則 |
| `items[].title` | 是 | 標題 |
| `items[].source` | 是 | 來源行 |
| `items[].credibility` | 是 | 可信度標籤。內建樣式：`同儕審查研究`、`專業衛教`、`實務經驗分享`，其他文字會用預設樣式 |
| `items[].limitation` | 否 | 研究限制；空白或省略則不顯示 |
| `items[].summary` | 是 | 白話摘要 |
| `items[].try_tonight` | 是 | 「今晚可以試」 |
| `items[].link` | 是 | 原文網址 |

頁面上的中文日期（例如「2026 年 11 月 14 日（六）」）由 `build.py` 依 `date` 自動產生。

## 注意事項

這是公開網站。請不要寫入可辨識特定孩子或家庭的資訊，例如孩子的名字、學校，或「某位孩子被診斷為 ADHD」這類敘述。內文請用「孩子」。
