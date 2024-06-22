import dash
import dash_auth
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import pickle
import requests
import hashlib

# Define the URL to your model on GitHub
model_url = "https://github.com/OBAUDE95/House-Price-Prediction/raw/a27c5cdeba10f459e39b56df949e9da2550c5ee2/random_forest_model.pkl"

# Download the model file
response = requests.get(model_url)

if response.status_code == 200:
    loaded_model, loaded_columns = pickle.loads(response.content)
else:
    raise Exception("Failed to download the model file.")

# Define the house title mapping
title_mapping = {
    'Block of Flats': 0,
    'Detached Bungalow': 1,
    'Detached Duplex': 2,
    'Semi Detached Bungalow': 3,
    'Semi Detached Duplex': 4,
    'Terraced Bungalow': 5,
    'Terraced Duplexes': 6
}

# Reverse the mapping for radio button labels
title_mapping_reversed = {v: k for k, v in title_mapping.items()}

# Initialize the Dash app with a dark theme
app = dash.Dash(external_stylesheets=[dbc.themes.DARKLY])
server = app.server

# Define authentication credentials
# Custom authorization function


def authorization_function(username, password):
    salt = 'mypassword'  # Use a more secure salt in a real application
    salted_message = password + salt  # Concatenate password with salt
    # Hash the concatenated string
    hashed_password = hashlib.sha256(salted_message.encode()).hexdigest()

    # This is the stored hashed password for demonstration (hash of "world" + salt "mypassword")
    stored_hashed_password = "8dc75eb0460c9c6851fe58311bac43c7f2f424595c8afdb6561cab8ee1e65113"

    # Check if the hashed password matches the stored hashed password
    if str(hashed_password) == stored_hashed_password:
        return True
    else:
        return False


# Set up BasicAuth with the custom authorization function
auth = dash_auth.BasicAuth(
    app,
    auth_func=authorization_function,
    secret_key="Developer"
)

# Define the layout of the app using Bootstrap components
app.layout = dbc.Container([
    html.H1("Model Interface", className='mb-4 mt-5 text-center text-white'),
    html.P(
        "Welcome to the Ajah House Price Prediction Dashboard! "
        "Enter the details of the house below and click 'Submit' to get a predicted price. "
        "Use the buttons to select the type of house, and fill in the number of bedrooms, bathrooms, toilets, and parking spaces. "
        "This tool uses a machine learning model trained on real estate data to provide you with an estimate.",
        className='text-center text-white'
    ),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Label("Bedrooms:", width=4, className='text-white'),
                dbc.Col(dbc.Input(id='bedrooms',
                        type='number', value=2.0), width=8),
            ], className='mb-3'),
            dbc.Row([
                dbc.Label("Bathrooms:", width=4, className='text-white'),
                dbc.Col(dbc.Input(id='bathrooms',
                        type='number', value=2.0), width=8),
            ], className='mb-3'),
            dbc.Row([
                dbc.Label("Toilets:", width=4, className='text-white'),
                dbc.Col(dbc.Input(id='toilets', type='number', value=2.0), width=8),
            ], className='mb-3'),
            dbc.Row([
                dbc.Label("Parking Space:", width=4, className='text-white'),
                dbc.Col(dbc.Input(id='parking_space',
                        type='number', value=2.0), width=8),
            ], className='mb-3'),
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.Label("House Type:", className='text-white'),
                        dbc.RadioItems(
                            id='title',
                            options=[{'label': v, 'value': k}
                                     for k, v in title_mapping_reversed.items()],
                            value=6,  # Default value
                            className='text-white'
                        ),
                    ]), width=8, className='mb-3'
                ),
            ]),
            dbc.Row([
                dbc.Col(dbc.Button('Submit', id='submit-val', n_clicks=0,
                        color='primary'), width={"size": 6, "offset": 3}),
            ])
        ], width=6)  # Adjust width as needed
    ], justify='center'),
    html.Div(id='output-container-button', className='text-center text-white')
], className='py-5')

# Define callback to update output based on input


@app.callback(
    Output('output-container-button', 'children'),
    [Input('submit-val', 'n_clicks')],
    [State('bedrooms', 'value'),
     State('bathrooms', 'value'),
     State('toilets', 'value'),
     State('parking_space', 'value'),
     State('title', 'value')]
)
def update_output(n_clicks, bedrooms, bathrooms, toilets, parking_space, title):
    if n_clicks > 0:  # Only predict after the button is clicked
        # Create a DataFrame for prediction
        new_data = pd.DataFrame({
            'bedrooms': [bedrooms],
            'bathrooms': [bathrooms],
            'toilets': [toilets],
            'parking_space': [parking_space],
            'title': [title]
        })

        # Ensure that the new data contains the same columns as the training data
        new_data = new_data[loaded_columns]

        # Use the loaded model to make predictions
        prediction = loaded_model.predict(new_data)

        return html.H4(f'Prediction: #{prediction[0]:,.2f}', className='text-primary mt-4')

    return ''  # Return an empty string if button not clicked


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
