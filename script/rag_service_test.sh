curl --location 'http://127.0.0.1:18888/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer sk-67hBSTsaf0qqvpTN2eA5A4433c2343D3867d0f74D8F0322' \
--data '{
  "model": "gpt-4o-mini-2024-07-18",
  "messages": [
    {
      "role": "user",
      "content": "docker容器如何迁移"
    }
  ],
  "tools": [],
  "do_sample": true,
  "temperature": 0,
  "top_p": 0,
  "n": 1,
  "max_tokens": 0,
  "stream": true
}'