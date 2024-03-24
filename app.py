import sys
from flask import Flask,render_template,request,flash,redirect,url_for,jsonify,session
import urllib.request
import os
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import easyocr 
import io
from PIL import Image
import numpy as np
import pandas as pd
import re

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'secret_key'



class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self,email,password,name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self,password):
        return bcrypt.checkpw(password.encode('utf-8'),self.password.encode('utf-8'))

with app.app_context():
    db.create_all()

app.static_folder = 'static'


UPLOAD_FOLDER = 'static/uploads/'
 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/index')
        else:
            return render_template('login.html',error='Invalid user')

    return render_template('login.html')

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        # handle request
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name,email=email,password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')



    return render_template('register.html')


@app.route('/logout')
def logout():
    session.pop('email',None)
    return redirect('/login')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login_validation',methods=['POST'])
def login_validation():
    #email=request.form.get('email')
    #password=request.form.get('password')
    #return"The email is {} and the password is {}".format(email,password)
    return render_template('index.html')

@app.route("/upload", methods=["POST"])
def upload():
    print("inide upload")
    if request.method == "POST":
        uploaded_file = request.files["image"]
        # Initialize calculated_area to None
        calculated_area = None

        if uploaded_file.filename != "":
            # Save the uploaded file
            image_path = os.path.join("static", "uploaded_image.jpg")
            uploaded_file.save(image_path)

            # Extract text from the image
            extracted_text = extract_text(image_path)
            calculated_area = totalarea(extracted_text)
            extracted_text = ',<br>'.join(extracted_text)
            
            # Store the calculated area in the session
            session['calculated_area'] = calculated_area
            

            # Pass the extracted text to the area function and get the area
            
            
            # Display the uploaded image and extracted text
            return render_template('index.html', area_value=extracted_text,calculated_area=calculated_area)

def extract_text(image_path):
    reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    text = []
    for detection in result:
        text.append(detection[1])
        
    return text

def area(txt):
    if 'x' in txt and (txt[txt.index('x') - 1] != ' '):
        txt = txt.replace('x', ' x')

    if 'x' in txt and (txt[txt.index('x') + 1] != ' '):
        txt = txt.replace('x', 'x ')

    l = txt.split(' ')
    l.remove('x')
    s = l[-1]
    s = s[:-1]
    num1 = float(l[0])
    num2 = float(s)
    area = float(num1 * num2)
    print(area)
    return area

def totalarea(text):
    total_area = 0.0
    for i in range(1,len(text),3):
        txt = text[i]
        a = area(txt)
        total_area += a
    return total_area

#Here change the file name and location of the excel data


offers_dict = {
    'cement': {
        'off_price': 0.0,
        'max_val': 0.0,
        'min_val': 0.0,
        'pop_sel': ""
    },
    'sand': {
        'off_price': 0.0,
        'max_val': 0.0,
        'min_val': 0.0,
        'pop_sel': ""
    },
    'steel': {
        'off_price': 0.0,
        'max_val': 0.0,
        'min_val': 0.0,
        'pop_sel': ""
    },
    'brick': {
        'off_price': 0.0,
        'max_val': 0.0,
        'min_val': 0.0,
        'pop_sel': ""
    },
    'aggregates': {
        'off_price': 0.0,
        'max_val': 0.0,
        'min_val': 0.0,
        'pop_sel': ""
    },
    'tiles': {
        'off_price': 0.0,
        'max_val': 0.0,
        'min_val': 0.0,
        'pop_sel': ""
    }

}



@app.route('/categories')
def categories():
    cement()
    sand()
    steel()
    brick()
    aggregates()
    tiles()
    return render_template('categories.html', offer_prices = offers_dict)


@app.route('/categories/cement',methods=['GET','POST'])
def cement():
    df = pd.read_excel("./static/extra/Scrape_Cement.xlsx")
   
    x_data, y_data = df['Seller'], df['Offer Price']
    max_value = abs(y_data.max())
    offers_dict['cement']['max_val'] = max_value
    min_value = abs(y_data.min())
    offers_dict['cement']['min_val'] = min_value

    pie_dataframe = x_data.value_counts()
    pie_labels =  pie_dataframe.index.tolist()
    pie_values =  pie_dataframe.tolist()
    x_data = x_data.tolist()
    y_data = y_data.tolist()
    table_heads = df.columns.tolist()
    table_contents = df.values.tolist()
    table_data = [(index, row.to_list()) for index, row in df.iterrows()]

    average_offer_price = df['Offer Price'].mean()
    # Find the seller whose offer price is closest to the average
    closest_seller = df.iloc[(df['Offer Price'] - average_offer_price).abs().argsort()[:1]]['Seller'].values[0]
    offers_dict['cement']['pop_sel'] = closest_seller


    if request.method == 'POST':
        # Get the selected rows based on the submitted form
        selected_rows = request.form.getlist('selected_rows')

        # Convert the selected row indices to integers
        selected_rows = list(map(int, selected_rows))

        # Filter the DataFrame based on selected rows
        selected_df = df.iloc[selected_rows]
       
        # Extract the "Offer Price" column from the selected DataFrame
        offer_price_column = selected_df['Offer Price']*0.4

        # Retrieve the calculated area from the session
        calculated_area = session.get('calculated_area', None)
        cem_offer_price=calculated_area*offer_price_column

        # Check if calculated_area is not None before using it
        if calculated_area is not None:
            # Initialize offer_price before using it
            cem_offer_price = None

            # Check if the 'Offer Price' column is present in the selected DataFrame
            if 'Offer Price' in selected_df.columns:
                # Extract the "Offer Price" column from the selected DataFrame
                cem_offer_price = round(selected_df['Offer Price'] * 0.4 * calculated_area, 3)
                offers_dict['cement']['off_price'] += cem_offer_price


            # You can return the selected offer prices to be displayed on the webpage
            return render_template('cement.html', cem_max_value=max_value, cem_min_value=min_value, labels=x_data,
                               values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                               table_data=table_data, offer_price=cem_offer_price,closest_seller=closest_seller)
        
        else:
            # Handle the case when calculated_area is None
            flash("Error: Calculated area is None.", "error")
            return redirect(url_for('upload'))  # Redirect to the upload page or handle as needed


    return render_template('cement.html', cem_max_value=max_value, cem_min_value=min_value, labels=x_data,
                           values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                           table_data=table_data,closest_seller=closest_seller)

@app.route('/categories/steel',methods=['GET','POST'])
def steel():
    df = pd.read_excel("./static/extra/Scrape_Steel.xlsx")
   
    x_data, y_data = df['Steel'], df['Price']
    max_value = y_data.max()
    offers_dict['steel']['max_val'] = max_value

    min_value = y_data.min()
    offers_dict['steel']['min_val'] = min_value
    
    average_offer_price = df['Price'].mean()
    # Find the seller whose offer price is closest to the average
    closest_seller = df.iloc[(df['Price'] - average_offer_price).abs().argsort()[:1]]['Steel'].values[0]
    offers_dict['steel']['pop_sel'] = closest_seller

    pie_dataframe = x_data.value_counts()
    pie_labels =  pie_dataframe.index.tolist()
    pie_values =  pie_dataframe.tolist()
    x_data = x_data.tolist()
    y_data = y_data.tolist()
    table_heads = df.columns.tolist()
    table_contents = df.values.tolist()
    table_data = [(index, row.to_list()) for index, row in df.iterrows()]


    if request.method == 'POST':
        # Get the selected rows based on the submitted form
        selected_rows = request.form.getlist('selected_rows')

        # Convert the selected row indices to integers
        selected_rows = list(map(int, selected_rows))

        # Filter the DataFrame based on selected rows
        selected_df = df.iloc[selected_rows]

        offer_price_column = selected_df['Price']*0.4

        calculated_area = session.get('calculated_area', None)
        ste_offer_price =calculated_area*offer_price_column

        # Check if calculated_area is not None before using it
        if calculated_area is not None:
            # Initialize offer_price before using it
            ste_offer_price = None

            # Check if the 'Offer Price' column is present in the selected DataFrame
            if 'Price' in selected_df.columns:
                # Extract the "Offer Price" column from the selected DataFrame
                ste_offer_price = round(selected_df['Price'] * 2.1 * calculated_area,3)
                print(f"Steel price: {ste_offer_price}")
                offers_dict['steel']['off_price'] += ste_offer_price


                return render_template('steel.html', steel_max_value=max_value, steel_min_value=min_value, labels=x_data,
                               values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                               table_data=table_data, offer_price=ste_offer_price,closest_seller=closest_seller)
            
        else:
            # Handle the case when calculated_area is None
            flash("Error: Calculated area is None.", "error")
            return redirect(url_for('upload'))  # Redirect to the upload page or handle as needed

    return render_template('steel.html', steel_max_value=max_value, steel_min_value=min_value, labels=x_data,
                           values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                           table_data=table_data,closest_seller=closest_seller)

@app.route('/categories/sand',methods=['GET','POST'])
def sand():
    df = pd.read_excel("./static/extra/Scrape_Sand.xlsx")
   
    x_data, y_data = df['Sand'], df['Price']
    max_value = y_data.max()
    offers_dict['sand']['max_val'] = max_value

    min_value = y_data.min()
    offers_dict['sand']['min_val'] = min_value


    average_offer_price = df['Price'].mean()
    # Find the seller whose offer price is closest to the average
    closest_seller = df.iloc[(df['Price'] - average_offer_price).abs().argsort()[:1]]['Sand'].values[0]
    offers_dict['sand']['pop_sel'] = closest_seller

    pie_dataframe = x_data.value_counts()
    pie_labels =  pie_dataframe.index.tolist()
    pie_values =  pie_dataframe.tolist()
    x_data = x_data.tolist()
    y_data = y_data.tolist()
    table_heads = df.columns.tolist()
    table_contents = df.values.tolist()
    table_data = [(index, row.to_list()) for index, row in df.iterrows()]


    if request.method == 'POST':
        # Get the selected rows based on the submitted form
        selected_rows = request.form.getlist('selected_rows')

        # Convert the selected row indices to integers
        selected_rows = list(map(int, selected_rows))

        # Filter the DataFrame based on selected rows
        selected_df = df.iloc[selected_rows]

        offer_price_column = selected_df['Price']*2.1

        calculated_area = session.get('calculated_area', None)
        sand_offer_price=calculated_area*offer_price_column

        # Check if calculated_area is not None before using it
        if calculated_area is not None:
            # Initialize offer_price before using it
            sand_offer_price = None

            # Check if the 'Offer Price' column is present in the selected DataFrame
            if 'Price' in selected_df.columns:
                # Extract the "Offer Price" column from the selected DataFrame
                sand_offer_price = round(selected_df['Price'] * 2.1 * calculated_area,3)
                print(f"Sand price: {sand_offer_price}")
                offers_dict['sand']['off_price'] += sand_offer_price
                return render_template('sand.html', sand_max_value=max_value, sand_min_value=min_value, labels=x_data,
                               values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                               table_data=table_data, offer_price=sand_offer_price,closest_seller=closest_seller)
            
        else:
            # Handle the case when calculated_area is None
            flash("Error: Calculated area is None.", "error")
            return redirect(url_for('upload'))  # Redirect to the upload page or handle as needed

    return render_template('sand.html', sand_max_value=max_value, sand_min_value=min_value, labels=x_data,
                           values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                           table_data=table_data,closest_seller=closest_seller)



@app.route('/categories/brick',methods=['GET','POST'])
def brick():
    df = pd.read_excel("./static/extra/Scrape_Brick.xlsx")
   
    x_data, y_data = df['Name'], df['Price']
    max_value = y_data.max()
    offers_dict['brick']['max_val'] = max_value

    min_value = y_data.min()
    offers_dict['brick']['min_val'] = min_value

    average_offer_price = df['Price'].mean()
    # Find the seller whose offer price is closest to the average
    closest_seller = df.iloc[(df['Price'] - average_offer_price).abs().argsort()[:1]]['Name'].values[0]
    offers_dict['brick']['pop_sel'] = closest_seller

    pie_dataframe = x_data.value_counts()
    pie_labels =  pie_dataframe.index.tolist()
    pie_values =  pie_dataframe.tolist()
    x_data = x_data.tolist()
    y_data = y_data.tolist()
    table_heads = df.columns.tolist()
    table_contents = df.values.tolist()
    table_data = [(index, row.to_list()) for index, row in df.iterrows()]


    if request.method == 'POST':
        # Get the selected rows based on the submitted form
        selected_rows = request.form.getlist('selected_rows')

        # Convert the selected row indices to integers
        selected_rows = list(map(int, selected_rows))

        # Filter the DataFrame based on selected rows
        selected_df = df.iloc[selected_rows]

        offer_price_column = selected_df['Price']*30

        calculated_area = session.get('calculated_area', None)
        brick_offer_price=calculated_area*offer_price_column

        # Check if calculated_area is not None before using it
        if calculated_area is not None:
            # Initialize offer_price before using it
            brick_offer_price = None

            # Check if the 'Offer Price' column is present in the selected DataFrame
            if 'Price' in selected_df.columns:
                # Extract the "Offer Price" column from the selected DataFrame
                brick_offer_price = selected_df['Price'] * 30 * calculated_area
                print(f"Brick price: {brick_offer_price}")
                offers_dict['brick']['off_price'] += brick_offer_price

                return render_template('brick.html', brick_max_value=max_value, brick_min_value=min_value, labels=x_data,
                               values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                               table_data=table_data, offer_price=brick_offer_price,closest_seller=closest_seller)
            
        else:
            # Handle the case when calculated_area is None
            flash("Error: Calculated area is None.", "error")
            return redirect(url_for('upload'))  # Redirect to the upload page or handle as needed

    return render_template('brick.html', brick_max_value=max_value, brick_min_value=min_value, labels=x_data,
                           values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                           table_data=table_data,closest_seller=closest_seller)

@app.route('/categories/aggregates',methods=['GET','POST'])
def aggregates():
    df = pd.read_excel("./static/extra/Scrape_aggregates.xlsx")
   
    x_data, y_data = df['Name'], df['Price']
    max_value = y_data.max()
    offers_dict['aggregates']['max_val'] = max_value

    min_value = y_data.min()
    offers_dict['aggregates']['min_val'] = min_value

    average_offer_price = df['Price'].mean()
    # Find the seller whose offer price is closest to the average
    closest_seller = df.iloc[(df['Price'] - average_offer_price).abs().argsort()[:1]]['Name'].values[0]
    offers_dict['aggregates']['pop_sel'] = closest_seller

    pie_dataframe = x_data.value_counts()
    pie_labels =  pie_dataframe.index.tolist()
    pie_values =  pie_dataframe.tolist()
    x_data = x_data.tolist()
    y_data = y_data.tolist()
    table_heads = df.columns.tolist()
    table_contents = df.values.tolist()
    table_data = [(index, row.to_list()) for index, row in df.iterrows()]


    if request.method == 'POST':
        # Get the selected rows based on the submitted form
        selected_rows = request.form.getlist('selected_rows')

        # Convert the selected row indices to integers
        selected_rows = list(map(int, selected_rows))

        # Filter the DataFrame based on selected rows
        selected_df = df.iloc[selected_rows]

        offer_price_column = selected_df['Price']*1.35

        calculated_area = session.get('calculated_area', None)
        aggregates_offer_price=calculated_area*offer_price_column

        # Check if calculated_area is not None before using it
        if calculated_area is not None:
            # Initialize offer_price before using it
            aggregates_offer_price = None

            # Check if the 'Offer Price' column is present in the selected DataFrame
            if 'Price' in selected_df.columns:
                # Extract the "Offer Price" column from the selected DataFrame
                aggregates_offer_price = selected_df['Price'] * 30 * calculated_area
                print(f"Aggregates price: {aggregates_offer_price}")
                offers_dict['aggregates']['off_price'] += aggregates_offer_price

                return render_template('aggregates.html', agg_max_value=max_value, agg_min_value=min_value, labels=x_data,
                               values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                               table_data=table_data, offer_price=aggregates_offer_price,closest_seller=closest_seller)
            
        else:
            # Handle the case when calculated_area is None
            flash("Error: Calculated area is None.", "error")
            return redirect(url_for('upload'))  # Redirect to the upload page or handle as needed

    return render_template('aggregates.html', agg_max_value=max_value, agg_min_value=min_value, labels=x_data,
                           values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                           table_data=table_data,closest_seller=closest_seller)


@app.route('/categories/tiles',methods=['GET','POST'])
def tiles():
    df = pd.read_excel("./static/extra/Scrape_tiles.xlsx")
   
    x_data, y_data = df['Name'], df['Price']
    max_value = y_data.max()
    offers_dict['tiles']['max_val'] = max_value

    min_value = y_data.min()
    offers_dict['tiles']['min_val'] = min_value

    average_offer_price = df['Price'].mean()
    # Find the seller whose offer price is closest to the average
    closest_seller = df.iloc[(df['Price'] - average_offer_price).abs().argsort()[:1]]['Name'].values[0]
    offers_dict['tiles']['pop_sel'] = closest_seller

    pie_dataframe = x_data.value_counts()
    pie_labels =  pie_dataframe.index.tolist()
    pie_values =  pie_dataframe.tolist()
    x_data = x_data.tolist()
    y_data = y_data.tolist()
    table_heads = df.columns.tolist()
    table_contents = df.values.tolist()
    table_data = [(index, row.to_list()) for index, row in df.iterrows()]


    if request.method == 'POST':
        # Get the selected rows based on the submitted form
        selected_rows = request.form.getlist('selected_rows')

        # Convert the selected row indices to integers
        selected_rows = list(map(int, selected_rows))

        # Filter the DataFrame based on selected rows
        selected_df = df.iloc[selected_rows]

        tiles_offer_price_column = selected_df['Price']*20

        calculated_area = session.get('calculated_area', None)
        tiles_offer_price=calculated_area*tiles_offer_price_column

        # Check if calculated_area is not None before using it
        if calculated_area is not None:
            # Initialize offer_price before using it
            tiles_offer_price = None

            # Check if the 'Offer Price' column is present in the selected DataFrame
            if 'Price' in selected_df.columns:
                # Extract the "Offer Price" column from the selected DataFrame
                tiles_offer_price = selected_df['Price'] * 20 * calculated_area
                print(f"Tiles price: {tiles_offer_price}")
                offers_dict['tiles']['off_price'] += tiles_offer_price

                return render_template('tiles.html', tiles_max_value=max_value, tiles_min_value=min_value, labels=x_data,
                               values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                               table_data=table_data, offer_price=tiles_offer_price,closest_seller=closest_seller)
            
        else:
            # Handle the case when calculated_area is None
            flash("Error: Calculated area is None.", "error")
            return redirect(url_for('upload'))  # Redirect to the upload page or handle as needed

    return render_template('tiles.html', tiles_max_value=max_value, tiles_min_value=min_value, labels=x_data,
                           values=y_data, pie_labels=pie_labels, pie_values=pie_values, headings=table_heads,
                           table_data=table_data,closest_seller=closest_seller)

# def aggregate_data():
#     cement_data = {
#         'max_val': offers_dict['cement']['max_val'],
#         'min_val': offers_dict['cement']['min_val'],
#         'pop_sel': offers_dict['cement']['pop_sel'],
#         'off_price': float(offers_dict['cement']['off_price'])
#     }

#     sand_data = {
#         'max_val': offers_dict['sand']['max_val'],
#         'min_val': offers_dict['sand']['min_val'],
#         'pop_sel': offers_dict['sand']['pop_sel'],
#         'off_price': float(offers_dict['sand']['off_price'])
#     }

#     steel_data = {
#         'max_val': offers_dict['steel']['max_val'],
#         'min_val': offers_dict['steel']['min_val'],
#         'pop_sel': offers_dict['steel']['pop_sel'],
#         'off_price': float(offers_dict['steel']['off_price'])
#     }

#     brick_data = {
#         'max_val': offers_dict['brick']['max_val'],
#         'min_val': offers_dict['brick']['min_val'],
#         'pop_sel': offers_dict['brick']['pop_sel'],
#         'off_price': float(offers_dict['brick']['off_price'])
#     }

#     aggregates_data = {
#         'max_val': offers_dict['aggregates']['max_val'],
#         'min_val': offers_dict['aggregates']['min_val'],
#         'pop_sel': offers_dict['aggregates']['pop_sel'],
#         'off_price': float(offers_dict['aggregates']['off_price'])
#     }

#     tiles_data = {
#         'max_val': offers_dict['tiles']['max_val'],
#         'min_val': offers_dict['tiles']['min_val'],
#         'pop_sel': offers_dict['tiles']['pop_sel'],
#         'off_price': float(offers_dict['tiles']['off_price'])
#     }

#     # Calculate the sum of all off_price values
#     total_off_price = sum([
#         offers_dict['cement']['off_price'],
#         offers_dict['sand']['off_price'],
#         offers_dict['steel']['off_price'],
#         offers_dict['brick']['off_price'],
#         offers_dict['aggregates']['off_price'],
#         offers_dict['tiles']['off_price']
#     ])

    

#     summary_data = {
#         'cement': cement_data,
#         'sand': sand_data,
#         'steel': steel_data,
#         'brick': brick_data,
#         'aggregates': aggregates_data,
#         'tiles': tiles_data,
#         'total_off_price': total_off_price
#     }

#     print(summary_data)

#     return summary_data

# @app.route('/summary',methods=['GET','POST'])
# def summary():
#     aggregated_data = aggregate_data()
#     print(aggregated_data)
#     return render_template('summary.html', aggregated_data=aggregated_data)

def aggregate_data():
    cement_data = {
        'max_val': offers_dict['cement']['max_val'],
        'min_val': offers_dict['cement']['min_val'],
        'pop_sel': offers_dict['cement']['pop_sel'],
        'off_price': offers_dict['cement']['off_price']
    }

    sand_data = {
        'max_val': offers_dict['sand']['max_val'],
        'min_val': offers_dict['sand']['min_val'],
        'pop_sel': offers_dict['sand']['pop_sel'],
        'off_price': offers_dict['sand']['off_price']
    }

    steel_data = {
        'max_val': offers_dict['steel']['max_val'],
        'min_val': offers_dict['steel']['min_val'],
        'pop_sel': offers_dict['steel']['pop_sel'],
        'off_price': offers_dict['steel']['off_price']
    }

    brick_data = {
        'max_val': offers_dict['brick']['max_val'],
        'min_val': offers_dict['brick']['min_val'],
        'pop_sel': offers_dict['brick']['pop_sel'],
        'off_price': offers_dict['brick']['off_price']
    }

    aggregates_data = {
        'max_val': offers_dict['aggregates']['max_val'],
        'min_val': offers_dict['aggregates']['min_val'],
        'pop_sel': offers_dict['aggregates']['pop_sel'],
        'off_price': offers_dict['aggregates']['off_price']
    }

    tiles_data = {
        'max_val': offers_dict['tiles']['max_val'],
        'min_val': offers_dict['tiles']['min_val'],
        'pop_sel': offers_dict['tiles']['pop_sel'],
        'off_price': offers_dict['tiles']['off_price']
    }

    # Calculate the sum of all off_price values
    # total_off_price = sum([
    #     offers_dict['cement']['off_price'],
    #     offers_dict['sand']['off_price'],
    #     offers_dict['steel']['off_price'],
    #     offers_dict['brick']['off_price'],
    #     offers_dict['aggregates']['off_price'],
    #     offers_dict['tiles']['off_price']
    # ])

    total_off_price = cement_data['off_price'].iloc[0]+sand_data['off_price'].iloc[0]+steel_data['off_price'].iloc[0]+brick_data['off_price'].iloc[0]+aggregates_data['off_price'].iloc[0]+tiles_data['off_price'].iloc[0]
    # print(total_off_price)

    return cement_data['off_price'].iloc[0], sand_data['off_price'].iloc[0], steel_data['off_price'].iloc[0], brick_data['off_price'].iloc[0], aggregates_data['off_price'].iloc[0], tiles_data['off_price'].iloc[0], total_off_price

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    cement_data, sand_data, steel_data, brick_data, aggregates_data, tiles_data, total_off_price = aggregate_data()
    print(cement_data, sand_data, steel_data, brick_data, aggregates_data, tiles_data, total_off_price)
    return render_template(
        'summary.html',
        cement_data=cement_data,
        sand_data=sand_data,
        steel_data=steel_data,
        brick_data=brick_data,
        aggregates_data=aggregates_data,
        tiles_data=tiles_data,
        total_off_price=total_off_price
    )



if __name__=='__main__':
    app.run('0.0.0.0', port=5000)