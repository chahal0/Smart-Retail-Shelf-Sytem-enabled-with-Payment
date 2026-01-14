from django.shortcuts import render, HttpResponse
import csv
import pandas as pd
import chardet
from io import StringIO
from .models import Order, Customer
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.conf import settings
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import urllib.parse
from utils.llm_helper import query_ollama
from .utils import generate_shelves

load_dotenv()

# --- Base Views ---

def index(request):
    return render(request, 'index.html')

def winter(request):
    return render(request, 'winter.html')

def summer(request):
    return render(request, 'summer.html')

def autumn(request):
    return render(request, 'autumn.html')

def spring(request):
    return render(request, 'spring.html')


def top_3_analysis(df, column_name):
    top_3 = df.nlargest(3, column_name)
    return top_3

def analyze_historical_sales(df):
    total_sales = df['product_price'].sum()
    average_sales = df['product_price'].mean()
    total_profit = df['profit'].sum()
    average_profit_margin = (df['profit'] / df['product_price']).mean() * 100
    return {
        'total_sales': total_sales,
        'average_sales': average_sales,
        'total_profit': total_profit,
        'average_profit_margin': average_profit_margin
    }

def identify_seasonal_trends(df):
    if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
         try:
            df['order_date'] = pd.to_datetime(df['order_date'], format='%d-%m-%Y')
         except:
             try:
                df['order_date'] = pd.to_datetime(df['order_date'])
             except:
                pass
    df['month'] = df['order_date'].dt.month
    monthly_sales = df.groupby('month')['product_price'].sum()
    return monthly_sales

def calculate_profit_margins(df):
    df['profit_margin'] = (df['profit'] / df['product_price']) * 100
    return df[['product_name', 'profit_margin']]

def max_sold_product_with_timeframes(df):
    if not pd.api.types.is_datetime64_any_dtype(df['order_date']):
         try:
            df['order_date'] = pd.to_datetime(df['order_date'], format='%d-%m-%Y')
         except:
            pass
    df['year'] = df['order_date'].dt.year
    yearly_product_quantity = df.groupby(['product_name', 'year'])['quantity'].sum()
    max_sold_product = yearly_product_quantity.idxmax()
    return max_sold_product

def upload_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
            return render(request, 'retailer/upload_csv.html', {'error_message': 'Please upload a CSV file.'})
        
        try:
            rawdata = csv_file.read()
            result = chardet.detect(rawdata)
            encoding = result['encoding'] or 'utf-8'
            csv_file.seek(0)
            
            try:
                decoded_data = rawdata.decode(encoding)
            except:
                 headings = ['utf-8', 'latin-1', 'ISO-8859-1']
                 for enc in headings:
                     try:
                        decoded_data = rawdata.decode(enc)
                        break
                     except: continue

            csv_data = StringIO(decoded_data)
            df = pd.read_csv(csv_data)
            
            # Select columns if they exist
            cols = ['order_id', 'product_name', 'product_price', 'profit', 'quantity', 'category', 'sub_category', 'payment_mode', 'order_date', 'customer_name', 'state', 'city', 'gender', 'age']
            # Basic validation
            if not all(col in df.columns for col in cols):
                 # Fallback or allow if partial? Original didn't check.
                 pass
            
            selected_columns = df
            
            top_3_product_price = top_3_analysis(selected_columns, 'product_price')
            top_3_profit = top_3_analysis(selected_columns, 'profit')
            top_3_quantity = top_3_analysis(selected_columns, 'quantity')
            
            top_3_product_price_html = top_3_product_price.to_html(index=False)
            top_3_profit_html = top_3_profit.to_html(index=False)
            top_3_quantity_html = top_3_quantity.to_html(index=False)
            
            analyze_historical_sales(df)
            identify_seasonal_trends(df)
            calculate_profit_margins(df)
            max_sold_product_with_timeframes(df)
            
            return render(request, 'retailer/upload_csv.html', {'top_3_product_price_html': top_3_product_price_html, 'top_3_profit_html': top_3_profit_html, 'top_3_quantity_html': top_3_quantity_html})
        
        except Exception as e:
            return render(request, 'retailer/upload_csv.html', {'error_message': str(e)})
    
    return render(request, 'retailer/upload_csv.html')

def upload_csv_data(request):
    if request.method == 'POST':
        try:
            order_file = request.FILES.get('order_file')
            customer_file = request.FILES.get('customer_file')
            if not order_file or not customer_file:
                 return HttpResponse('Error: Please upload both files.')

            # Process order CSV
            order_data = csv.DictReader(order_file.read().decode('utf-8').splitlines())
            # Bulk create or loop? Original looped.
            for row in order_data:
                # Key mapping
                Order.objects.create(
                    order_id=row['Order ID'],
                    amount=row['Amount'],
                    profit=row['Profit'],
                    quantity=row['Quantity'],
                    category=row['Category'],
                    sub_category=row['Sub-Category'],
                    payment_mode=row['PaymentMode']
                )

            # Process customer CSV
            customer_data = csv.DictReader(customer_file.read().decode('utf-8').splitlines())
            for row in customer_data:
                    orders = Order.objects.filter(order_id=row['Order ID'])
                    if orders.exists():
                        order = orders.first()
                        try:
                            order_date = datetime.strptime(row['Order Date'], '%d-%m-%Y').strftime('%Y-%m-%d')
                        except ValueError:
                             try:
                                order_date = datetime.strptime(row['Order Date'], '%Y-%m-%d').strftime('%Y-%m-%d')
                             except:
                                return HttpResponse(f"Error: Invalid date format for Order ID {row['Order ID']}")
                        
                        Customer.objects.create(
                            order=order,
                            order_date=order_date,
                            customer_name=row['CustomerName'],
                            state=row['State'],
                            city=row['City']
                        )
            return HttpResponse("Upload success")
        except Exception as e:
            return HttpResponse(f"Error: {str(e)}")
    return render(request, 'retailer/upload_data.html')

def popular_products(request):
    monthly_most_sold = Order.objects.values('category', 'sub_category').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
    prime_category = Order.objects.values('category').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity').first()
    monthly_most_sold_list = list(monthly_most_sold)
    
    top_categories = monthly_most_sold.values('category').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')[:3]
    top_categories_subcategories = []
    for category_data in top_categories:
        category = category_data['category']
        subcategories = monthly_most_sold.filter(category=category).order_by('-total_quantity')[:3]
        top_categories_subcategories.append({'category': category, 'subcategories': subcategories})

    subcategory_profit = Order.objects.values('sub_category').annotate(total_profit=Sum('profit')).order_by('-total_profit')
    top_profit_subcategories = []
    for subcategory_data in subcategory_profit[:6]:
        top_profit_subcategories.append({'sub_category': subcategory_data['sub_category'], 'total_profit': subcategory_data['total_profit']})

    total_profits = Order.objects.aggregate(total_profits=Sum('profit'))
    total_sales = Order.objects.aggregate(total_sales=Sum('amount'))
    total_quantity_sold = Order.objects.aggregate(total_quantity_sold=Sum('quantity'))
    total_amount_by_state = Customer.objects.values('state').annotate(total_amount=Sum('order__amount'))
    total_amount_by_customer = Customer.objects.values('customer_name').annotate(total_amount=Sum('order__amount'))
    total_profit_by_month = Order.objects.annotate(month=TruncMonth('customer__order_date')).values('month').annotate(total_profit=Sum('profit'))
    total_quantity_by_payment_mode = Order.objects.values('payment_mode').annotate(total_quantity=Sum('quantity'))

    context = {
            'top_categories_subcategories': top_categories_subcategories,
            'monthly_most_sold_list': monthly_most_sold_list,      
            'prime_category': prime_category,
            'top_profit_subcategories': top_profit_subcategories,
            'total_profits': total_profits['total_profits'] or 0,
            'total_sales': total_sales['total_sales'] or 0,
            'total_quantity_sold': total_quantity_sold['total_quantity_sold'] or 0,
            'total_amount_by_state': total_amount_by_state,
            'total_amount_by_customer': total_amount_by_customer,
            'total_profit_by_month': total_profit_by_month,
            'total_quantity_by_payment_mode': total_quantity_by_payment_mode,
            }
    return render(request, 'retailer/popular_products.html', context)


# --- AI / Gemini Replacement (Ollama) ---

def save_orders_from_excel(excel_file):
    df = pd.read_excel(excel_file)
    orders = []
    for _, row in df.iterrows():
        order = Order(
            order_id=row['order_id'],
            product_name=row['product_name'],
            product_price=row['product_price'],
            profit=row['profit'],
            quantity=row['quantity'],
            category=row['category'],
            sub_category=row['sub_category'],
            payment_mode=row['payment_mode'],
            order_date=row['order_date'],
            customer_name=row['customer_name'],
            state=row['state'],
            city=row['city'],
            gender=row['gender'],
            age=row['age']
        )
        orders.append(order)
    Order.objects.bulk_create(orders)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def get_text_chunks(text):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    chunks = text_splitter.split_text(text)
    return chunks

def get_vector_store(text_chunks):
    # Using Ollama Embeddings
    embeddings = OllamaEmbeddings(model="llama3") 
    vector_store = FAISS.from_texts(text_chunks, embedding=embeddings)
    try:
        vector_store.save_local(os.path.join(settings.BASE_DIR, "faiss_index"))
    except:
        pass # Handle permission error if needed
    return vector_store

def user_input(user_question):
    embeddings = OllamaEmbeddings(model="llama3") 
    try:
        new_db = FAISS.load_local(os.path.join(settings.BASE_DIR, "faiss_index"), embeddings, allow_dangerous_deserialization=True)
        docs = new_db.similarity_search(user_question)
        context_text = "\n\n".join([doc.page_content for doc in docs])
    except:
        context_text = "No context available from uploaded documents."

    prompt = f"""
    As a data analyst, analyze the following data context and answer the question.
    
    Context:
    {context_text}
    
    Question:
    {user_question}
    
    Answer thoroughly and provide insights (narrative style).
    """
    
    response_text = query_ollama(prompt)
    if not response_text:
        response_text = "Could not generate response. Please ensure Ollama is running (`ollama run llama3`)."
        
    return response_text

def search_related_content(query):
    # Mocking or basic scraping to avoid Google API
    try:
         search_query = urllib.parse.quote(query)
         url = f"https://www.google.com/search?q={search_query}"
         headers = {'User-Agent': 'Mozilla/5.0'}
         response = requests.get(url, headers=headers)
         soup = BeautifulSoup(response.text, 'html.parser')
         # Extract text from simple results
         results = [div.get_text() for div in soup.select('.BNeawe')]
         return results[:3]
    except:
        return ["Analysis requires internet connection for web search."]

def display_related_content(related_content):
    return related_content

def gemini(request):
    if request.method == 'POST':
        if 'pdf_files' in request.FILES:
            pdf_docs = request.FILES.getlist('pdf_files')
            if pdf_docs:
                raw_text = get_pdf_text(pdf_docs)
                text_chunks = get_text_chunks(raw_text)
                get_vector_store(text_chunks)

        user_question = request.POST.get('user_question')
        response_text = user_input(user_question)
        related_content = search_related_content(user_question)

        return render(request, 'retailer/gemini.html', {'response_text': response_text, 'related_content': related_content})
    else:
        return render(request, 'retailer/gemini.html')

# --- Visualization Views ---

def visualize_shelves(request):
    data_file = os.path.join(settings.BASE_DIR, 'mbd.csv')
    if not os.path.exists(data_file):
        # Fallback if mbd.csv not found, maybe create dummy?
        shelves, frequent_itemsets, top_selling = {}, {}, {}
    else:
        shelves, frequent_itemsets_dict, top_selling_dict = generate_shelves(data_file)
        frequent_itemsets = [([item for item in itemset], round(support, 4)) for itemset, support in frequent_itemsets_dict.items()]
        top_selling = [(k, v) for k, v in top_selling_dict.items()]

    return render(request, 'retailer/visualize_shelves.html', {'shelves': shelves, 'frequent_itemsets': frequent_itemsets, 'top_selling_products': top_selling})

def distribute_products_across_shelves(popular_products, num_shelves, products_per_shelf):
    shelves = {}
    assigned_products = set()
    if isinstance(popular_products, (pd.DataFrame, pd.Series)):
        popular_list = popular_products.index.tolist()
    else:
        popular_list = popular_products
    
    for i in range(num_shelves):
        start_idx = i * products_per_shelf
        end_idx = min((i + 1) * products_per_shelf, len(popular_list))
        shelf_products = []
        for product in popular_list[start_idx:end_idx]:
            if product not in assigned_products:
                shelf_products.append(product)
                assigned_products.add(product)
        shelves[f"Shelf {i+1}"] = shelf_products
    return shelves

def get_top_and_least_sold_products_for_season(season, data):
    season_data = data[data['Season'] == season]
    product_sales = season_data.groupby('Product')['Quantity'].sum().reset_index()
    sorted_products = product_sales.sort_values(by='Quantity', ascending=False)
    top_products = sorted_products['Product'].head(3).tolist()
    least_sold_products = sorted_products.tail(3)['Product'].tolist()
    return top_products, least_sold_products

def seasonal_analysis_view(request):
    csv_path = os.path.join(settings.BASE_DIR, 'Book2.csv')
    if not os.path.exists(csv_path):
        return HttpResponse("Book2.csv not found.")
        
    data = pd.read_csv(csv_path)
    seasons = ['Winter', 'Spring', 'Summer', 'Autumn']
    seasonal_data = {}
    
    for season in seasons:
        top_products, least_sold_products = get_top_and_least_sold_products_for_season(season, data)
        # Mocking distribute for context
        shelves = distribute_products_across_shelves(top_products, num_shelves=1, products_per_shelf=3)
        seasonal_data[f'{season}, 1 Shelf'] = {'top_products': top_products, 'least_sold_products': least_sold_products, 'shelves': shelves}
    
    return render(request, 'retailer/season_analysis.html', {'seasonal_data': seasonal_data})

def threed_shelf(request):
    return render(request, 'retailer/3d.html')

# --- Other Views ---

def index1(request):
    return render(request, 'index1.html')

def login(request):
    return render(request, 'pages/sign-in.html')

def send_report_via_sms(request):
    # This uses Twilio. Paid API?
    # User said "ZERO PAID APIS".
    # I should comment this out or Mock it.
    # "Ensure NO Google API key...". Twilio is also paid.
    # I'll disable it or adding a print.
    print("Sending SMS report (Mocked - No Paid APIs)")
    return HttpResponse("SMS Sent (Mocked)")

def optimization(request):
    products = [
        {"name": "Iphone 15", "profit_priority": 1, "most_sold_priority": 1, "seasonal_priority": 1, "average_value": 1},
        {"name": "PlayStation", "profit_priority": 2, "most_sold_priority": 3, "seasonal_priority": 2, "average_value": 2},
        # ... (Abbreviated for prompt, but I will write it all)
        {"name": "Hoodies", "profit_priority": 4, "most_sold_priority": 2, "seasonal_priority": 3, "average_value": 3},
        {"name": "Floral Perfume", "profit_priority": 3, "most_sold_priority": 5, "seasonal_priority": 5, "average_value": 4},
        {"name": "Body Lotion", "profit_priority": 5, "most_sold_priority": 4, "seasonal_priority": 6, "average_value": 5},
        {"name": "Shower Gel", "profit_priority": 6, "most_sold_priority": 6, "seasonal_priority": 4, "average_value": 6},
        {"name": "Water Bottles", "profit_priority": 7, "most_sold_priority": 7, "seasonal_priority": 7, "average_value": 7},
        {"name": "Soap", "profit_priority": 9, "most_sold_priority": 8, "seasonal_priority": 8, "average_value": 8},
        {"name": "Hand Cream", "profit_priority": 8, "most_sold_priority": 9, "seasonal_priority": 9, "average_value": 9},
        {"name": "Serum", "profit_priority": 10, "most_sold_priority": 10, "seasonal_priority": 11, "average_value": 10},
        {"name": "Facewash", "profit_priority": 11, "most_sold_priority": 11, "seasonal_priority": 10, "average_value": 11},
        {"name": "Baidyanath Amla Juice", "profit_priority": 12, "most_sold_priority": 12, "seasonal_priority": 12, "average_value": 12},
    ]
    return render(request, 'retailer/optimization.html', {'products': products})

def optimized_products(request):
    return render(request, 'retailer/optimized_products.html')

def upload(request):
    if request.method == 'POST' and 'csv_file' in request.FILES:   
        csv_file = request.FILES['csv_file']
        if not csv_file.name.endswith('.csv'):
             return render(request, 'pages/upload.html', {'error_message': 'Please upload a CSV file.'})
        try:
             df = pd.read_csv(csv_file, encoding='utf-8')
             products_list = df['Product'].unique().tolist()
             total_products = len(products_list)
             return render(request, 'pages/upload.html', {'products_list': products_list, 'total_products': total_products})
        except Exception as e:
             return render(request, 'pages/upload.html', {'error_message': str(e)})
    return render(request, 'pages/upload.html')