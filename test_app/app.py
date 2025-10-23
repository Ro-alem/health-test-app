# Полный готовый блок для Google Colab.
# Вставьте в одну ячейку и запустите. Перед запуском вставьте ваш ngrok-токен в переменную NGROK_TOKEN ниже.

# Установка нужных библиотек
!pip install -q streamlit pyngrok fpdf pandas openpyxl

# ====== Конфигурация ======
NGROK_TOKEN = "34MeG6Dol04SuYURj74P3u0JnPz_4NHTsokVSWMw2XER3KXfS"  # <-- вставьте сюда свой ngrok authtoken (обязательно для внешней ссылки)

# ====== Создание Streamlit-приложения (app.py) ======
app_code = r'''
import streamlit as st
import pandas as pd
from io import BytesIO
from fpdf import FPDF
from datetime import datetime

st.set_page_config(page_title="Когнитивная диагностика", layout="centered")

# Тесты и допустимые диапазоны по возрастам
tests_by_age = {
    0: [
        {"key": "Bayley Scales (BSID-III)", "min": 0, "max": 150},
        {"key": "ASQ-3 (проценты)", "min": 0, "max": 100},
        {"key": "M-CHAT-R/F", "min": 0, "max": 20}
    ],
    5: [
        {"key": "NEPSY-II (stens)", "min": 0, "max": 20},
        {"key": "KABC-II (IQ)", "min": 40, "max": 160},
        {"key": "CARS-2", "min": 0, "max": 60},
        {"key": "Conners EC (T)", "min": 0, "max": 100},
        {"key": "Stroop (секунды)", "min": 0, "max": 120},
        {"key": "WPPSI-IV (IQ)", "min": 40, "max": 160},
        {"key": "Vineland Adaptive", "min": 0, "max": 150}
    ],
    10: [
        {"key": "WISC-V (IQ)", "min": 40, "max": 160},
        {"key": "Stroop (секунды)", "min": 0, "max": 120},
        {"key": "CPT (ошибки %)", "min": 0, "max": 100},
        {"key": "TMT A (сек)", "min": 0, "max": 300},
        {"key": "TMT B (сек)", "min": 0, "max": 300},
        {"key": "SRS-2 (T)", "min": 0, "max": 120},
        {"key": "RAVLT (слов)", "min": 0, "max": 15},
        {"key": "Tower of London (категории)", "min": 0, "max": 6},
        {"key": "Digit Span (цифры)", "min": 0, "max": 9}
    ],
    15: [
        {"key": "WCST (категории)", "min": 0, "max": 6},
        {"key": "TMT B (сек)", "min": 0, "max": 180},
        {"key": "RAVLT (слов)", "min": 0, "max": 15},
        {"key": "PHQ-A (баллы)", "min": 0, "max": 27},
        {"key": "CPT-II (ошибки %)", "min": 0, "max": 100},
        {"key": "Tower of Hanoi (ходы)", "min": 0, "max": 25},
        {"key": "Emotional Stroop (разница сек)", "min": 0, "max": 120}
    ],
    18: [
        {"key": "MoCA (баллы)", "min": 0, "max": 30},
        {"key": "WAIS-IV (IQ)", "min": 40, "max": 160},
        {"key": "WCST (категории)", "min": 0, "max": 6},
        {"key": "TMT B (сек)", "min": 0, "max": 180},
        {"key": "Stroop (секунды/ошибки)", "min": 0, "max": 120},
        {"key": "GAD-7 (баллы)", "min": 0, "max": 21},
        {"key": "BDI-II (баллы)", "min": 0, "max": 63},
        {"key": "RAVLT (слов)", "min": 0, "max": 15}
    ]
}

# Расширенные рекомендации: по возрастам и по итоговым уровням
recommendations = {
    0: {
        "Норма": (
            "Развитие соответствует возрасту. Рекомендуется: ежедневное общение и чтение вслух, "
            "сенсорные игры (тактильные, звуковые), массаж и гимнастика для младенцев, "
            "соблюдать режим сна и кормления, посещать педиатра по графику."
        ),
        "Риск": (
            "Наблюдаются лёгкие задержки моторики или речи. Рекомендации: ежедневные упражнения для моторики, "
            "сенсорные игры, логопедическая профилактика, проверка слуха и зрения, консультация невролога/логопеда."
        ),
        "Отклонение": (
            "Выраженные признаки задержки или аутистического спектра. Немедленная консультация невролога, психиатра и дефектолога. "
            "Ранняя коррекция: сенсорная интеграция, логопедия, ЛФК, семейная поддержка."
        )
    },
    5: {
        "Норма": (
            "Ребёнок справляется с заданиями. Рекомендуется: развивающие игры (пазлы, конструкторы), чтение, уроки речи, "
            "физическая активность, режим дня, совместная игра с взрослыми."
        ),
        "Риск": (
            "Проблемы с вниманием или слабая речь. Рекомендуется: уменьшить экранное время, ввести короткие тренировки внимания, "
            "консультация нейропсихолога, логопеда; мягкая игровая коррекция."
        ),
        "Отклонение": (
            "Нарушения речи, аутичные или поведенческие признаки. Требуется психиатрическое и логопедическое обследование, "
            "индивидуальная программа коррекции (ABA, сенсомоторные занятия)."
        )
    },
    10: {
        "Норма": (
            "Когнитивные функции в норме. Рекомендуется: чтение, шахматы, задания на память, спорт и поддержание режима сна."
        ),
        "Риск": (
            "Трудности с вниманием или памятью. Рекомендуется: снижать информационную нагрузку, упражнения на концентрацию, "
            "контроль сна и питания, консультация школьного психолога."
        ),
        "Отклонение": (
            "Значимые когнитивные или эмоциональные проблемы. Рекомендуется: медицинское обследование (невролог, психотерапевт), "
            "индивидуальная образовательная программа, психотерапия."
        )
    },
    15: {
        "Норма": (
            "Подросток в норме. Рекомендуется: поддерживать баланс учёбы и отдыха, социальные и спортивные активности, "
            "формировать навыки саморегуляции и планирования."
        ),
        "Риск": (
            "Снижение мотивации или тревожность. Рекомендации: тренировки по стрессоустойчивости, физическая активность, "
            "ограничение гаджетов, консультация психолога."
        ),
        "Отклонение": (
            "Выраженные психоэмоциональные или когнитивные расстройства. Рекомендуется срочная консультация психиатра и психотерапевта, "
            "поддержка семьи, корректировка нагрузки."
        )
    },
    18: {
        "Норма": (
            "Взрослый уровень когнитивной функции в норме. Рекомендуется: поддержание умственной и физической активности, "
            "регулярный сон и профилактические обследования."
        ),
        "Риск": (
            "Снижение концентрации или тревожность. Рекомендуется: дыхательные практики, консультация психолога, ограничение кофеина и гаджетов."
        ),
        "Отклонение": (
            "Выраженные тревожные или депрессивные состояния. Рекомендуется медицинское обследование (психиатр, невролог), "
            "психотерапия (КБТ) и поддержка."
        )
    }
}

# Функция анализа: суммируем процентные достижения по каждому тесту (score/max)
def compute_overall_level(age, entered):
    # entered: list of numeric values with same order as tests_by_age[age]
    tests = tests_by_age[age]
    total_percent = 0.0
    for val, test in zip(entered, tests):
        maxv = test["max"]
        if maxv == 0:
            continue
        # Для some tests (where lower is better) we could invert, but we assume higher=better except M-CHAT/CARS/GAD/BDI where higher=problem.
        # We'll handle known "higher worse" tests by name:
        name = test["key"].lower()
        if any(x in name for x in ("m-chat", "cars-2", "cars", "gad-7", "bdi", "bdi-ii", "phq", "cpt", "cpt-ii", "stroop", "tmt")):
            # For these, lower is better -> convert to (max - val) / max
            pct = max(0.0, (maxv - val) / maxv) * 100.0
        else:
            pct = max(0.0, val / maxv) * 100.0
        total_percent += pct
    # average percent across tests
    avg_percent = total_percent / len(tests) if len(tests) > 0 else 0
    if avg_percent >= 75:
        level = "Норма"
    elif avg_percent >= 50:
        level = "Риск"
    else:
        level = "Отклонение"
    return level, avg_percent

# Интерфейс
st.title("Когнитивная диагностика по возрастам")
st.write("Выберите возраст, введите результаты (числовые). Итог — единый общий уровень и подробные рекомендации.")

age = st.selectbox("Возраст (лет):", [0, 5, 10, 15, 18])

st.header("Ввод результатов тестов")
entered_values = []
cols = st.columns(2)
tests = tests_by_age[age]
for i, test in enumerate(tests):
    label = f"{test['key']} (диапазон {test['min']} – {test['max']})"
    # Используем шаг 1, вывод целых; если потребуется дробный ввод, можно изменить step=0.1
    value = cols[i % 2].number_input(label, min_value=test['min'], max_value=test['max'], value=test['min'], step=1, format="%d")
    entered_values.append(value)

if st.button("Рассчитать итог"):
    level, avg_percent = compute_overall_level(age, entered_values)

    # Цвет блока в зависимости от уровня
    color_map = {"Норма": "#d4f7d8", "Риск": "#fff3cd", "Отклонение": "#f8d7da"}
    border_map = {"Норма": "#28a745", "Риск": "#ffc107", "Отклонение": "#dc3545"}
    bg = color_map.get(level, "#ffffff")
    border = border_map.get(level, "#000000")

    # Показываем блок с цветом и информацией
    st.markdown(f"""
    <div style="background:{bg}; padding:18px; border-left:6px solid {border}; border-radius:6px">
        <h2>Итог: {level}</h2>
        <p>Средний процент по тестам: {avg_percent:.1f}%</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Подробные рекомендации")
    st.write(recommendations[age][level])

    st.subheader("Введённые результаты")
    df_rows = []
    for t, v in zip(tests, entered_values):
        df_rows.append({"Тест": t["key"], "Результат": v, "Максимум": t["max"]})
    df = pd.DataFrame(df_rows)
    st.table(df)

    # Скачивание PDF отчёта
    if st.button("Сформировать PDF-отчёт"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 8, "Отчёт по когнитивной диагностике", ln=True, align="C")
        pdf.ln(4)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 6, f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
        pdf.cell(0, 6, f"Возраст: {age} лет", ln=True)
        pdf.cell(0, 6, f"Итог: {level}", ln=True)
        pdf.cell(0, 6, f"Средний процент: {avg_percent:.1f}%", ln=True)
        pdf.ln(4)
        pdf.multi_cell(0, 6, "Рекомендации:")
        pdf.multi_cell(0, 6, recommendations[age][level])
        pdf.ln(4)
        pdf.cell(0, 6, "Результаты тестов:", ln=True)
        for row in df_rows:
            pdf.cell(0, 6, f"{row['Тест']}: {row['Результат']} / {row['Максимум']}", ln=True)

        buf = BytesIO()
        pdf.output(buf)
        st.download_button("Скачать PDF", data=buf.getvalue(), file_name=f"report_age{age}.pdf", mime="application/pdf")
'''

# Запись файла
with open("app.py", "w", encoding="utf-8") as f:
    f.write(app_code)

# ====== Запуск Streamlit + ngrok туннеля ======
import os, time, signal, subprocess
from pyngrok import ngrok

# Очищаем старые процессы (если есть)
os.system("pkill -f streamlit || true")
os.system("pkill -f ngrok || true")
time.sleep(1)

# Устанавливаем токен ngrok если он задан
if NGROK_TOKEN and NGROK_TOKEN != "ВСТАВЬТЕ_СВОЙ_NGROK_AUTHTOKEN_ЗДЕСЬ":
    ngrok.set_auth_token(NGROK_TOKEN)

# Запускаем streamlit в фоне
streamlit_cmd = "nohup streamlit run app.py --server.port 8501 &>/dev/null &"
os.system(streamlit_cmd)
time.sleep(1)

# Создаём туннель
try:
    public_url = ngrok.connect(8501)
    print("Streamlit запущен. Откройте приложение по адресу:")
    print(public_url)
except Exception as e:
    print("Не удалось создать туннель ngrok. Если вы используете бесплатный аккаунт, "
          "убедитесь, что у вас не превышен лимит туннелей или вставьте корректный NGROK_TOKEN.")
    raise
