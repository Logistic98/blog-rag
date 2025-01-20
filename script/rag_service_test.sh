curl --location 'http://127.0.0.1:18888/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer sk-67hBSTsaf0qqvpTN2eA5A4433c2343D3867d0f74D8F0322' \
--data '{
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": "docker容器如何迁移"
    }
  ],
  "stream": true
}'