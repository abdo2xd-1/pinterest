name: Publish to Pinterest

on:
  workflow_dispatch: # يتيح لك تشغيل الكود يدوياً من واجهة جيت هاب

jobs:
  post-pin:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests

      - name: Run Pinterest Publisher
        env:
          # ربط الأسرار من إعدادات المستودع
          PINTEREST_ACCESS_TOKEN: ${{ secrets.PINTEREST_ACCESS_TOKEN }}
          PINTEREST_BOARD_ID: ${{ secrets.PINTEREST_BOARD_ID }}
        run: python publish_pin.py
