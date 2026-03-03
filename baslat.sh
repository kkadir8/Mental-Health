#!/bin/bash
# Bulundugu klasore git
cd "$(dirname "$0")"

# Venv olustur (yoksa)
if [ ! -d "venv" ]; then
    echo "Sanal ortam (venv) oluşturuluyor..."
    python3 -m venv venv
    ./venv/bin/pip install --upgrade pip
fi

# Kutuphaneleri yukle (eksik varsa)
echo "Kütüphaneler kontrol ediliyor..."
./venv/bin/pip install PyQt6 pandas scikit-learn xgboost matplotlib seaborn deep-translator python-docx joblib numpy > /dev/null 2>&1

# Uygulamayi baslat
echo "Uygulama başlatılıyor..."
./venv/bin/python main_app.py
