#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import openai

# 设置 API 密钥
YI_KEY = '81b5e2e'

# 使用 OpenAI API
response = openai.Completion.create(
  engine="text-davinci-003",
  prompt="Hello, how are you?",
  max_tokens=5
)

print(response)
