from flask import Flask, render_template, redirect, request,flash
import mysql.connector
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVR
from sklearn.ensemble import RandomForestRegressor, StackingRegressor
from xgboost import XGBRegressor
from keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
from keras.models import load_model
from keras.metrics import MeanSquaredError
from sklearn.preprocessing import LabelEncoder
import logging
from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestRegressor
import folium
import geopandas as gpd
import os
import logging

import os
import pandas as pd
import numpy as np
from flask import Flask, render_template, redirect, url_for
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, OneHotEncoder, MinMaxScaler
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, StackingRegressor
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error, make_scorer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf
from werkzeug.utils import secure_filename
from werkzeug.utils import secure_filename

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
print("start")

# mydb = mysql.connector.connect(
#     host='localhost',
#     port=3306,
#     user='root',
#     passwd='',
#     database='Groundwater'
# )

# mycur = mydb.cursor()

import pymysql

mydb = pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    port=3306,
    database="Groundwater"
)
mycur = mydb.cursor()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        phonenumber= request.form['phonenumber']
        age  = request.form['age']
        if password == confirmpassword:
            sql = 'SELECT * FROM users WHERE email = %s'
            val = (email,)
            mycur.execute(sql, val)
            data = mycur.fetchone()
            if data is not None:
                msg = 'User already registered!'
                return render_template('registration.html', msg=msg)
            else:
                sql = 'INSERT INTO users (name, email, password,`phone number`,age) VALUES (%s, %s, %s, %s,%s)'
                val = (name, email, password, phonenumber,age)
                mycur.execute(sql, val)
                mydb.commit()
                
                msg = 'User registered successfully!'
                return render_template('registration.html', msg=msg)
        else:
            msg = 'Passwords do not match!'
            return render_template('registration.html', msg=msg)
    return render_template('registration.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sql = 'SELECT * FROM users WHERE email=%s'
        val = (email,)
        mycur.execute(sql, val)
        data = mycur.fetchone()

        if data:
            stored_password = data[2]
            if password == stored_password:
               msg = 'user logged successfully'
               return redirect("/upload")
            else:
                msg = 'Password does not match!'
                return render_template('login.html', msg=msg)
        else:
            msg = 'User with this email does not exist. Please register.'
            return render_template('login.html', msg=msg)
    return render_template('login.html')
                            
# Set a secret key for session management (for flash messages)
app.secret_key = 'bhuvana'

# Define the upload folder and allowed file extensions
UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = {'csv'}

# Create the upload folder if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Checks if the file extension is allowed (CSV only)."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'error')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Sanitize the filename
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            try:
                file.save(file_path)
                # Read the CSV file
                dataset = pd.read_csv(file_path)
                dataset_dict = dataset.to_dict(orient='records')
                flash('CSV file uploaded successfully!', 'success')
                return render_template('upload.html', dataset=dataset_dict)
            except PermissionError:
                flash('Permission denied while saving the file. Please check directory permissions.', 'error')
                return redirect(request.url)
            except Exception as e:
                flash(f'Error saving file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Only CSV files are allowed!', 'error')
            return redirect(request.url)

    return render_template('upload.html', dataset=None)













# @app.route('/algo')
# def algo():
#     # Load and preprocess the dataset
#     df = pd.read_csv('uploads\Forecasting_Dataset.csv')

#     # Fill missing values with median (for numerical data) and mode (for categorical data)
#     for col in df.columns:
#         if df[col].dtype == 'object':
#             df[col].fillna(df[col].mode()[0], inplace=True)
#         else:
#             df[col].fillna(df[col].median(), inplace=True)
#     #label encoding the data.
#     # Convert categorical columns to numerical using label encoding if needed
#     from sklearn.preprocessing import LabelEncoder
#     # Store original column names
#     original_columns = df.select_dtypes(include='object').columns

#     # Initialize LabelEncoder
#     label_encoders = {}

#     # Apply LabelEncoder to each categorical variable
#     for col in original_columns:
#         label_encoders[col] = LabelEncoder()
#         df[col] = label_encoders[col].fit_transform(df[col])

#     # Print the mapping between original categories and numerical labels
#     for col, encoder in label_encoders.items():
#         print(f"Mapping for column '{col}':")
#         for label, category in enumerate(encoder.classes_):
#             print(f"Label {label}: {category}")
    
#     # Drop 'S.no.' column and handle missing values
#     df = df.drop(columns=['S.no.'])
#     df.fillna(df.median(), inplace=True)

#     # Define features and target variable
#     X = df.drop(columns=['Net Ground Water Availability for future use'])
#     y = df['Net Ground Water Availability for future use']
    
#     # Split data into training and testing sets (80% train, 20% test)
#     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#     # Standardize the features
#     scaler = StandardScaler()
#     X_train_scaled = scaler.fit_transform(X_train)
#     X_test_scaled = scaler.transform(X_test)

#     # Initialize models
#     svm_model = SVR(kernel='rbf')
#     rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
#     xgb_model = XGBRegressor(n_estimators=100, learning_rate=0.1, random_state=42)

#     # Train models
#     svm_model.fit(X_train_scaled, y_train)
#     rf_model.fit(X_train_scaled, y_train)
#     xgb_model.fit(X_train_scaled, y_train)

#     # Evaluate models
#     models = {"SVM": svm_model, "Random Forest": rf_model, "XGBoost": xgb_model}
#     results = {}

#     for name, model in models.items():
#         y_pred = model.predict(X_test_scaled)
#         results[name] = {
#             "MAE": mean_absolute_error(y_test, y_pred),
#             "MSE": mean_squared_error(y_test, y_pred),
#             "R2 Score": r2_score(y_test, y_pred)
#         }

#     # Train LSTM model
#     X_train_lstm = X_train_scaled.reshape((X_train_scaled.shape[0], X_train_scaled.shape[1], 1))
#     X_test_lstm = X_test_scaled.reshape((X_test_scaled.shape[0], X_test_scaled.shape[1], 1))

#     lstm_model = Sequential([
#         LSTM(50, return_sequences=True, input_shape=(X_train_lstm.shape[1], 1)),
#         Dropout(0.2),
#         LSTM(50, return_sequences=False),
#         Dropout(0.2),
#         Dense(25, activation='relu'),
#         Dense(1)
#     ])

#     lstm_model.compile(optimizer='adam', loss='mse')
#     lstm_model.fit(X_train_lstm, y_train, epochs=20, batch_size=16, validation_data=(X_test_lstm, y_test), verbose=1)

#     # Predict using LSTM
#     y_pred_lstm = lstm_model.predict(X_test_lstm)
#     results["LSTM"] = {
#         "MAE": mean_absolute_error(y_test, y_pred_lstm),
#         "MSE": mean_squared_error(y_test, y_pred_lstm),
#         "R2 Score": r2_score(y_test, y_pred_lstm)
#     }

#     # Stacking Model (meta learner: XGBoost)
#     stacking_model = StackingRegressor(
#         estimators=[('rf', rf_model), ('svm', svm_model), ('xgb', xgb_model)],
#         final_estimator=XGBRegressor(n_estimators=50, learning_rate=0.1, random_state=42)
#     )
#     stacking_model.fit(X_train_scaled, y_train)

#     # Predict using Stacking model
#     y_pred_stacking = stacking_model.predict(X_test_scaled)
#     results["Stacking"] = {
#         "MAE": mean_absolute_error(y_test, y_pred_stacking),
#         "MSE": mean_squared_error(y_test, y_pred_stacking),
#         "R2 Score": r2_score(y_test, y_pred_stacking)
#     }

#     # Pass the results to the frontend template
#     return render_template('algo.html', results=results)






@app.route('/algo')
def algo():
    # Load the dataset
    df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], 'Forecasting_Dataset.csv'))
    
    # Clean column names
    df.columns = df.columns.str.strip()  # Remove leading/trailing spaces
    df.columns = df.columns.str.replace(r'\s+', ' ', regex=True)  # Replace multiple spaces with single space
    
    # Debug: Print column names
    print("Columns in DataFrame:", df.columns.tolist())
    
    # Define target and categorical columns
    target_column = 'Net Ground Water Availability for future use'
    categorical_cols = ['Name of State', 'Name of District']
    
    # Check for missing columns
    missing_cols = [col for col in categorical_cols + [target_column] if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns {missing_cols} not found in DataFrame")

    # Handle missing values
    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].fillna(df[col].mode()[0])

    # Clip outliers in numerical columns
    numerical_cols = df.select_dtypes(include=np.number).columns.tolist()
    if target_column in numerical_cols:
        numerical_cols.remove(target_column)  # Exclude target from numerical columns
    for col in numerical_cols:
        df[col] = np.clip(df[col], df[col].quantile(0.05), df[col].quantile(0.95))

    # Convert non-numeric columns to numeric where possible
    for col in df.columns:
        if col not in categorical_cols and not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                df[col] = df[col].fillna(df[col].median())
            except:
                pass

    # Drop duplicates
    df.drop_duplicates(inplace=True)

    # Ensure categorical columns are not in numerical columns
    for col in categorical_cols:
        if col in numerical_cols:
            numerical_cols.remove(col)

    # Preprocessing pipeline
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=False, drop='first')
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numerical_transformer, numerical_cols),
            ('cat', categorical_transformer, categorical_cols)
        ]
    )

    # Transform the dataset
    df_processed = preprocessor.fit_transform(df)
    feature_names = numerical_cols.copy()
    feature_names.extend(preprocessor.named_transformers_['cat'].get_feature_names_out(categorical_cols))
    df_processed = pd.DataFrame(df_processed, columns=feature_names)

    # Define features and target
    X = df_processed
    y = df[target_column]

    # Split the data
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

    # Initialize models
    rf_model = RandomForestRegressor()
    gb_model = GradientBoostingRegressor()
    lr_model = LinearRegression()

    # Define hyperparameter grids
    param_grid_rf = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5, 10]
    }
    param_grid_gb = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01, 0.1, 1],
        'max_depth': [3, 5, 7]
    }
    param_grid_lr = {
        'fit_intercept': [True, False],
        'positive': [True, False]
    }

    # Perform GridSearchCV
    scorer = make_scorer(mean_squared_error, greater_is_better=False)
    grid_search_rf = GridSearchCV(estimator=rf_model, param_grid=param_grid_rf, scoring=scorer, cv=5)
    grid_search_gb = GridSearchCV(estimator=gb_model, param_grid=param_grid_gb, scoring=scorer, cv=5)
    grid_search_lr = GridSearchCV(estimator=lr_model, param_grid=param_grid_lr, scoring=scorer, cv=5)

    # Fit GridSearchCV on validation set
    grid_search_rf.fit(X_val, y_val)
    grid_search_gb.fit(X_val, y_val)
    grid_search_lr.fit(X_val, y_val)

    # Get best models
    best_rf_model = grid_search_rf.best_estimator_
    best_gb_model = grid_search_gb.best_estimator_
    best_lr_model = grid_search_lr.best_estimator_

    # Train best models on training data
    best_rf_model.fit(X_train, y_train)
    best_gb_model.fit(X_train, y_train)
    best_lr_model.fit(X_train, y_train)

    # Predict on validation set
    y_pred_rf = best_rf_model.predict(X_val)
    y_pred_gb = best_gb_model.predict(X_val)
    y_pred_lr = best_lr_model.predict(X_val)

    # LSTM Model
    X_train_lstm = X_train.values.reshape((X_train.shape[0], 1, X_train.shape[1]))
    X_val_lstm = X_val.values.reshape((X_val.shape[0], 1, X_val.shape[1]))

    # Scale features
    scaler_X = MinMaxScaler()
    X_train_lstm = scaler_X.fit_transform(X_train_lstm.reshape(-1, X_train_lstm.shape[2])).reshape(X_train_lstm.shape)
    X_val_lstm = scaler_X.transform(X_val_lstm.reshape(-1, X_val_lstm.shape[2])).reshape(X_val_lstm.shape)

    # Scale target
    scaler_y = MinMaxScaler()
    y_train_scaled = scaler_y.fit_transform(y_train.values.reshape(-1, 1)).flatten()
    y_val_scaled = scaler_y.transform(y_val.values.reshape(-1, 1)).flatten()

    # Debug: Print shapes and ranges
    print("X_train_lstm shape:", X_train_lstm.shape)
    print("y_train range:", y_train.min(), y_train.max())
    print("y_train_scaled range:", y_train_scaled.min(), y_train_scaled.max())
    print("y_val range:", y_val.min(), y_val.max())
    print("y_val_scaled range:", y_val_scaled.min(), y_val_scaled.max())

    # Define LSTM model
    model_lstm = Sequential()
    model_lstm.add(LSTM(units=50, return_sequences=True, input_shape=(X_train_lstm.shape[1], X_train_lstm.shape[2])))
    model_lstm.add(Dropout(0.2))
    model_lstm.add(LSTM(units=50, return_sequences=False))
    model_lstm.add(Dropout(0.2))
    model_lstm.add(Dense(units=1))
    model_lstm.compile(optimizer='adam', loss='mean_squared_error')

    # Early stopping
    early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

    # Fit the model
    model_lstm.fit(
        X_train_lstm, y_train_scaled,
        validation_data=(X_val_lstm, y_val_scaled),
        epochs=50, batch_size=32, verbose=0,
        callbacks=[early_stopping]
    )

    # Predict and inverse-transform predictions
    lstm_pred_scaled = model_lstm.predict(X_val_lstm, verbose=0).flatten()
    lstm_pred = scaler_y.inverse_transform(lstm_pred_scaled.reshape(-1, 1)).flatten()

    # Debug: Print sample predictions
    print("Sample lstm_pred (unscaled):", lstm_pred[:5])
    print("Sample y_val:", y_val[:5].values)

    # Stacking Regressor
    base_learners = [
        ('rf', RandomForestRegressor(n_estimators=100, random_state=42)),
        ('gb', GradientBoostingRegressor(n_estimators=100, random_state=42)),
        ('lr', LinearRegression())
    ]
    meta_model = Ridge(alpha=1.0)
    stacking_model = StackingRegressor(estimators=base_learners, final_estimator=meta_model)
    stacking_model.fit(X_train, y_train)
    stacking_pred = stacking_model.predict(X_val)

    # Collect evaluation metrics
    results = [
        {
            'Model': 'Random Forest',
            'R² Score': r2_score(y_val, y_pred_rf),
            'MAE': mean_absolute_error(y_val, y_pred_rf),
            'MSE': mean_squared_error(y_val, y_pred_rf)
        },
        {
            'Model': 'Gradient Boosting',
            'R² Score': r2_score(y_val, y_pred_gb),
            'MAE': mean_absolute_error(y_val, y_pred_gb),
            'MSE': mean_squared_error(y_val, y_pred_gb)
        },
        {
            'Model': 'Linear Regression',
            'R² Score': r2_score(y_val, y_pred_lr),
            'MAE': mean_absolute_error(y_val, y_pred_lr),
            'MSE': mean_squared_error(y_val, y_pred_lr)
        },
        {
            'Model': 'LSTM',
            'R² Score': r2_score(y_val, lstm_pred),
            'MAE': mean_absolute_error(y_val, lstm_pred),
            'MSE': mean_squared_error(y_val, lstm_pred)
        },
        {
            'Model': 'Stacking',
            'R² Score': r2_score(y_val, stacking_pred),
            'MAE': mean_absolute_error(y_val, stacking_pred),
            'MSE': mean_squared_error(y_val, stacking_pred)
        }
    ]

    # Debug: Print LSTM metrics
    print("LSTM R² Score:", r2_score(y_val, lstm_pred))
    print("LSTM MAE:", mean_absolute_error(y_val, lstm_pred))
    print("LSTM MSE:", mean_squared_error(y_val, lstm_pred))

    # Pass the results to the frontend template
    return render_template('algo.html', results=results)






# @app.route('/prediction', methods=['GET', 'POST'])
# def prediction():
#     if request.method == 'POST':
#         # Extract input values from the form
#         data = {
#             'Name of State': request.form['state'],
#             'Name of District': request.form['district'],
#             'Recharge from rainfall During Monsoon Season': float(request.form['rainfall_monsoon']),
#             'Recharge from other sources During Monsoon Season': float(request.form['other_sources_monsoon']),
#             'Recharge from rainfall During Non Monsoon Season': float(request.form['rainfall_non_monsoon']),
#             'Recharge from other sources During Non Monsoon Season': float(request.form['other_sources_non_monsoon']),
#             'Total Annual Ground Water Recharge': float(request.form['total_annual_recharge']),
#             'Total Natural Discharges': float(request.form['total_natural_discharge']),
#             'Annual Extractable Ground Water Resource': float(request.form['extractable_gw']),
#             'Current Annual Ground Water Extraction For Irrigation': float(request.form['current_annual_extraction_irrigation']),
#             'Current Annual Ground Water Extraction For Domestic & Industrial Use': float(request.form['current_annual_extraction_domestic']),
#             'Total Current Annual Ground Water Extraction': float(request.form['Total_Current_Annual_Ground_Water_Extraction']),
#             'Annual GW Allocation for Domestic Use as on 2025': float(request.form['annual_gw_allocation_domestic']),
#             'Stage of Ground Water Extraction (%)': float(request.form['stage_of_gw_extraction'])
#         }
#         input_data = pd.DataFrame([data])

#         # Load and preprocess the dataset
#         df = pd.read_csv('uploads/Forecasting_Dataset.csv')
#         df = df.drop(columns=['S.no.'])  # Assuming 'S.no.' is not needed

#         # Handling missing values
#         # Numeric columns: fill with median
#         numeric_cols = df.select_dtypes(include=[np.number])
#         df[numeric_cols.columns] = numeric_cols.fillna(numeric_cols.median())
        
#         # Categorical columns: handle separately if needed
#         categorical_cols = df.select_dtypes(include=['object'])
#         for col in categorical_cols:
#             df[col] = df[col].fillna('Unknown')  # Or use another method like mode
        
#         # Encoding categorical variables
#         label_encoders = {}
#         for col in categorical_cols.columns:
#             label_encoders[col] = LabelEncoder()
#             df[col] = label_encoders[col].fit_transform(df[col])
#             if col in input_data:
#                 input_data[col] = label_encoders[col].transform(input_data[col])

#         # Splitting data
#         X = df.drop(columns=['Net Ground Water Availability for future use'])
#         y = df['Net Ground Water Availability for future use']
#         X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

#         # Standardize features
#         scaler = StandardScaler()
#         X_train_scaled = scaler.fit_transform(X_train)
#         X_test_scaled = scaler.transform(X_test)  # This line is actually unnecessary in this context

#         # Prediction model
#         rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
#         rf_model.fit(X_train_scaled, y_train)

#         # Make prediction for the input data
#         input_data_scaled = scaler.transform(input_data)  # Transform input data
#         prediction = rf_model.predict(input_data_scaled)

#         # Render prediction result to the frontend
#         return render_template('prediction.html', prediction=prediction[0])

#     # If the request is GET, show the prediction form
#     return render_template('prediction.html')
@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    if request.method == 'POST':
        try:
            # Extract input values from the form
            data = {
                'Name of State': request.form['state'],
                'Name of District': request.form['district'],
                'Recharge from rainfall During Monsoon Season': float(request.form['rainfall_monsoon']),
                'Recharge from other sources During Monsoon Season': float(request.form['other_sources_monsoon']),
                'Recharge from rainfall During Non Monsoon Season': float(request.form['rainfall_non_monsoon']),
                'Recharge from other sources During Non Monsoon Season': float(request.form['other_sources_non_monsoon']),
                'Total Annual Ground Water Recharge': float(request.form['total_annual_recharge']),
                'Total Natural Discharges': float(request.form['total_natural_discharge']),
                'Annual Extractable Ground Water Resource': float(request.form['extractable_gw']),
                'Current Annual Ground Water Extraction For Irrigation': float(request.form['current_annual_extraction_irrigation']),
                'Current Annual Ground Water Extraction For Domestic & Industrial Use': float(request.form['current_annual_extraction_domestic']),
                'Total Current Annual Ground Water Extraction': float(request.form['Total_Current_Annual_Ground_Water_Extraction']),
                'Annual GW Allocation for Domestic Use as on 2025': float(request.form['annual_gw_allocation_domestic']),
                'Stage of Ground Water Extraction (%)': float(request.form['stage_of_gw_extraction'])
            }
            input_data = pd.DataFrame([data])

            # Load and preprocess the dataset
            df = pd.read_csv('uploads/Forecasting_Dataset.csv')
            df = df.drop(columns=['S.no.'], errors='ignore')

            # Handle missing values
            numeric_cols = df.select_dtypes(include=[np.number])
            df[numeric_cols.columns] = numeric_cols.fillna(numeric_cols.median())
            categorical_cols = df.select_dtypes(include=['object'])
            for col in categorical_cols:
                df[col] = df[col].fillna('Unknown')

            # Encode categorical variables
            label_encoders = {}
            for col in categorical_cols.columns:
                label_encoders[col] = LabelEncoder()
                df[col] = label_encoders[col].fit_transform(df[col])
                if col in input_data:
                    input_data[col] = label_encoders[col].transform(input_data[col])

            # Split data
            X = df.drop(columns=['Net Ground Water Availability for future use'])
            y = df['Net Ground Water Availability for future use']
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            # Standardize features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)

            # Train model
            rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
            rf_model.fit(X_train_scaled, y_train)

            # Make prediction
            input_data_scaled = scaler.transform(input_data)
            prediction = rf_model.predict(input_data_scaled)[0]

            # Load GeoJSON files
            try:
                states_gdf = gpd.read_file('static/geojson/india_state.geojson')
                districts_gdf = gpd.read_file('static/geojson/india_district.geojson')
            except Exception as e:
                return render_template('prediction.html', error=f"Error loading GeoJSON files: {str(e)}")

            # Create a Folium map centered on India with OpenStreetMap tiles
            m = folium.Map(location=[20.5937, 78.9629], zoom_start=5, tiles="OpenStreetMap")

            # Normalize prediction for color scaling
            max_gw = 1000000  # Adjust based on your data's range
            norm_prediction = min(max(prediction / max_gw, 0), 1)

            # Define color scale
            def get_color(value):
                if value < 0.3:
                    return '#ff0000'  # Red for low availability
                elif value < 0.6:
                    return '#ffa500'  # Orange for medium
                else:
                    return '#008000'  # Green for high availability

            # Highlight the selected state
            state_name = data['Name of State']
            district_name = data['Name of District']
            warning = None

            state_feature = states_gdf[states_gdf['NAME_1'].str.upper() == state_name.upper()]
            if not state_feature.empty:
                folium.GeoJson(
                    state_feature,
                    style_function=lambda x: {
                        'fillColor': get_color(norm_prediction),
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.3
                    },
                    tooltip=f"{state_name}: {prediction:.2f} m³/year"
                ).add_to(m)
            else:
                logger.warning(f"State not found in GeoJSON: {state_name}")
                warning = f"State '{state_name}' not found in map data. Showing prediction without map highlight."

            # Highlight the selected district (skip if district == state, indicating no district data)
            if district_name.upper() != state_name.upper():
                district_feature = districts_gdf[
                    (districts_gdf['NAME_2'].str.upper() == district_name.upper()) &
                    (districts_gdf['NAME_1'].str.upper() == state_name.upper())
                ]
                if not district_feature.empty:
                    folium.GeoJson(
                        district_feature,
                        style_function=lambda x: {
                            'fillColor': get_color(norm_prediction),
                            'color': 'black',
                            'weight': 2,
                            'fillOpacity': 0.7
                        },
                        tooltip=f"{district_name}, {state_name}: {prediction:.2f} m³/year"
                    ).add_to(m)
                else:
                    logger.warning(f"District not found in GeoJSON: {district_name}, {state_name}")
                    warning = warning or f"District '{district_name}' not found in map data. Showing state highlight only."

            # Save the map to a temporary HTML file
            map_path = 'static/map.html'
            m.save(map_path)

            # Render the template with prediction, map, and warning (if any)
            return render_template('prediction.html', prediction=prediction, map_path=map_path, warning=warning)

        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return render_template('prediction.html', error=f"Error processing prediction: {str(e)}")

    return render_template('prediction.html')


if __name__ == '__main__':
    app.run(debug=True)
