import streamlit as st
from PIL import Image
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import random
from datetime import datetime
import os
import sys

if hasattr(sys, '_MEIPASS'):
    os.environ['PYTHONPATH'] = sys._MEIPASS

pdfmetrics.registerFont(TTFont('Cubby', 'cubby.ttf'))

CAFE_NAMES = ['Kopigoyang', 'intinya', 'ngopi ga?', 'kopisore', 'HAUS']
CASHIERS = ['Mikael', 'miguel', 'Albert', 'Sanchez', 'Dewi']
COFFEE_ITEMS = ['Kopi satu', 'kopi frappe', 'kopi apa?', 'kopi sakit']
TEA_ITEMS = ['Teh Tarik', 'Teh Kaki kecoa', 'Teh Semut', 'Teh Earl Grey']
SNACK_ITEMS = ['Kopi apaan', 'Kopi siapa', 'Kopi sumpah', 'Kopi wkwkwk', 'Kopi air mineral', 'Teh laut']
PAYMENT_METHODS = ['VA BCA', 'VA BNI', 'Seabank', 'Transfer', 'QRIS']
MOTIVATIONAL_MESSAGES = [
    'Enjoy your drink!',
    'Have a brew-tiful day!',
    'Thanks a latte!',
    'Espresso yourself!',
    'You mocha me happy!',
    'Ngopii brow!'
]

def generate_order_number():
    return f"{random.randint(1, 999):03d}-{random.randint(1, 999):03d}"

def generate_random_items(num_items):
    items = []
    available_items = COFFEE_ITEMS + TEA_ITEMS + SNACK_ITEMS
    
    for _ in range(num_items):
        if available_items:
            product = random.choice(available_items)
            available_items.remove(product)
            quantity = 1
            price = random.randint(5000, 10000)
            items.append({"name": product, "quantity": quantity, "price": price})
        else:
            break
    
    return items

def create_receipt(logo_path, cafe_name, order_number, cashier_name, receipt_date, items, subtotal, tax, tip, total, payment_method, motivational_message):
    buffer = io.BytesIO()
    width, height = 48 * mm, 210 * mm
    c = canvas.Canvas(buffer, pagesize=(width, height))
    
    padding = 3 * mm
    content_width = width - 1 * padding
    y = height

    logo = Image.open(logo_path)
    logo_width = width
    logo_height = (logo.height / logo.width) * logo_width
    c.drawImage(logo_path, 0, y - logo_height, width=logo_width, height=logo_height)
    y -= logo_height + 3*mm

    c.setFont("Cubby", 20)
    c.drawCentredString(width/2, y, cafe_name)
    y -= 5*mm

    c.setStrokeColorRGB(0, 0, 0)
    c.setLineWidth(1)
    c.line(padding, y, width - padding, y)
    y -= 6*mm

    c.setFont("Helvetica", 8)
    c.drawString(padding, y, "")
    cashier_text = f"#{order_number} - {cashier_name}"
    cashier_width = c.stringWidth(cashier_text, "Helvetica-Bold", 8)
    c.drawString(width - padding - cashier_width, y, cashier_text)
    y -= 7*mm

    c.setFont("Helvetica-Bold", 10)
    date_text = f"DATE: {receipt_date.strftime('%d-%m-%Y   %H:%M')}"
    date_width = c.stringWidth(date_text, "Helvetica-Bold", 8)
    c.drawString((width - date_width) / 4, y, date_text)
    y -= 12*mm

    c.setFont("Helvetica-Bold", 9)
    for item in items:
        name, quantity, price = item['name'], item['quantity'], item['price']
        item_total = price * quantity
        item_text = f"{name} (x{quantity})"
        price_text = f"Rp {item_total:,.0f}"
        c.drawString(padding, y, item_text)
        price_width = c.stringWidth(price_text, "Helvetica", 9)
        c.drawString(width - padding - price_width, y, price_text)
        y -= 5*mm

    y -= 1*mm
    c.line(padding, y, width - padding, y)
    y -= 6*mm

    c.setFont("Helvetica", 8)
    c.drawString(padding, y, "Subtotal:")
    c.drawRightString(width - padding, y, f"Rp {subtotal:,.0f}")
    y -= 4*mm
    c.drawString(padding, y, "Pajak (12%):")
    c.drawRightString(width - padding, y, f"Rp {tax:,.0f}")
    y -= 4*mm
    c.drawString(padding, y, "Tip:")
    c.drawRightString(width - padding, y, f"Rp {tip:,.0f}")
    y -= 4*mm
    c.setFont("Helvetica-Bold", 9)
    c.drawString(padding, y, "Total:")
    c.drawRightString(width - padding, y, f"Rp {total:,.0f}")
    y -= 5*mm

    c.setFont("Helvetica-Bold", 8)
    c.drawString(padding, y, f"Bayar pake: {payment_method}")
    y -= 5*mm

    c.line(padding, y, width - padding, y)
    y -= 6*mm

    c.setFont("Cubby", 10)
    message_width = c.stringWidth(motivational_message, "Cubby", 10)
    c.drawString((width - message_width) / 2, y, motivational_message)

    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

st.title("☕🍵 摇摇咖啡与茶，来喝茶吧！")

if 'items' not in st.session_state:
    st.session_state['items'] = []
if 'order_number' not in st.session_state:
    st.session_state['order_number'] = generate_order_number()

with st.expander("咖啡店设置", expanded=False):
    use_random_cafe = st.checkbox("使用随机咖啡店名称", value=True)
    if use_random_cafe:
        cafe_name = random.choice(CAFE_NAMES)
    else:
        cafe_name = st.selectbox("选择咖啡店名称", CAFE_NAMES)

    st.session_state['order_number'] = st.text_input("订单号码", value=st.session_state['order_number'])

    use_random_cashier = st.checkbox("使用随机收银员", value=True)
    if use_random_cashier:
        cashier_name = random.choice(CASHIERS)
    else:
        cashier_name = st.selectbox("选择收银员", CASHIERS)

with st.expander("时间设置", expanded=False):
    use_current_datetime = st.checkbox("使用当前日期和时间", value=False)
    if use_current_datetime:
        receipt_datetime = datetime.now()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            receipt_date = st.date_input("选择日期", value=datetime.now())
        with col2:
            receipt_hour = st.number_input("小时", min_value=0, max_value=23, value=datetime.now().hour)
        with col3:
            receipt_minute = st.number_input("分钟", min_value=0, max_value=59, value=datetime.now().minute)
        receipt_datetime = datetime.combine(receipt_date, datetime.min.time()).replace(hour=receipt_hour, minute=receipt_minute)

with st.expander("订单设置", expanded=True):
    num_items = st.number_input("项目数量", min_value=1, max_value=len(COFFEE_ITEMS + TEA_ITEMS + SNACK_ITEMS), value=1)
    use_random_items = st.checkbox("创建随机项目", value=True)

    if use_random_items:
        st.session_state['items'] = generate_random_items(num_items)
    else:
        st.session_state['items'] = []
        available_items = COFFEE_ITEMS + TEA_ITEMS + SNACK_ITEMS
        for i in range(num_items):
            if not available_items:
                break
            col1, col2, col3 = st.columns([3, 1, 2])
            with col1:
                item = st.selectbox(f"项目 {i+1}", available_items, key=f"item_{i}")
            with col2:
                quantity = st.number_input(f"数量 {i+1}", min_value=1, max_value=10, value=1, key=f"qty_{i}")
            with col3:
                price = st.number_input(f"价格 {i+1}", min_value=1000, value=15000, step=1000, key=f"price_{i}")
            st.session_state['items'].append({"name": item, "quantity": quantity, "price": price})
            if item in available_items:
                available_items.remove(item)


subtotal = sum(item['quantity'] * item['price'] for item in st.session_state['items'])
tax = int(subtotal * 0.12)
tip = st.number_input("小费", min_value=0, value=0, step=1000)
total = subtotal + tax + tip

st.write(f"小计: Rp {subtotal:,.0f}")
st.write(f"税 (12%): Rp {tax:,.0f}")
st.write(f"小费: Rp {tip:,.0f}")
st.write(f"总计: Rp {total:,.0f}")

with st.expander("支付和信息设置", expanded=False):
    use_random_payment = st.checkbox("使用随机支付方式", value=True)
    if use_random_payment:
        payment_method = random.choice(PAYMENT_METHODS)
    else:
        payment_method = st.selectbox("选择支付方式", PAYMENT_METHODS)

    use_random_message = st.checkbox("使用随机励志信息", value=True)
    if use_random_message:
        motivational_message = random.choice(MOTIVATIONAL_MESSAGES)
    else:
        motivational_message = st.selectbox("选择励志信息", MOTIVATIONAL_MESSAGES)

logo_options = ["1.png", "2.png", "3.png"]
selected_logo = random.choice(logo_options)

if st.button("生成收据"):
    pdf_buffer = create_receipt(
        selected_logo,
        cafe_name,
        st.session_state['order_number'],
        cashier_name,
        receipt_datetime,
        st.session_state['items'],
        subtotal,
        tax,
        tip,
        total,
        payment_method,
        motivational_message
    )

    st.download_button(
        label="下载收据",
        data=pdf_buffer,
        file_name="咖啡收据.pdf",
        mime="application/pdf"
    )

    st.subheader("收据预览")
    pdf_bytes = pdf_buffer.getvalue()
    b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="400" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

print("代码已按照您的要求更新，朋友！")
