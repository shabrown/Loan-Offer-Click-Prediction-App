from flask import Flask, render_template, request
import pickle
import numpy as np
import pandas as pd


model = pickle.load(open('gbc_model.sav', 'rb'))

app = Flask(__name__)

lender_id_map = {"237": 0.33940774487471526,
                 "240": 0.36676646706586824,
                 "262": 0.5020408163265306,
                 "311": 0.05555555555555555,
                 "321": 0.15782122905027932,
                 "327": 0.5084745762711864,
                 "363": 0.476593625498008,
                 "383": 0.9303921568627451,
                 "386": 0.2246376811594203,
                 "389": 0.30068337129840544,
                 "417": 0.27154046997389036,
                 "457": 0.3245997088791849,
                 "473": 0.0,
                 "621": 0.3575233022636485,
                 "641": 0.1875,
                 "939": 0.6772151898734177,
                 "1103": 0.3955484896661367,
                 "1506": 0.41509433962264153,
                 "1737": 0.25902335456475584,
                 "1777": 0.063194761687224,
                 "1828": 0.6666666666666666,
                 "1992": 0.297165991902834,
                 "2034": 0.6775510204081633,
                 "2093": 0.22794117647058823,
                 "2108": 0.6221122112211221,
                 "2139": 0.96}

credit_map = {'None': 0.35714285714285715,
              'excellent': 0.3110181311018131,
              'fair': 0.35626179074154696,
              'good': 0.3495387683869359,
              'limited': 0.8363636363636363,
              'poor': 0.3083325076785891,
              'unknown': 0.4}

loan_purpose_map = {'auto': 0.5976627712854758,
                    'auto_purchase': 0.5714285714285714,
                    'auto_refinance': 0.4,
                    'baby': 0.4888888888888889,
                    'boat': 0.22807017543859648,
                    'business': 0.5384615384615384,
                    'car_repair': 0.625,
                    'cosmetic': 1.0,
                    'credit_card_refi': 0.3524945770065076,
                    'debt_consolidation': 0.2785820443661584,
                    'emergency': 0.5384615384615384,
                    'green': 0.5555555555555556,
                    'home_improvement': 0.451966473243069,
                    'home_purchase': 1.0,
                    'household_expenses': 0.8051282051282052,
                    'large_purchases': 0.5099009900990099,
                    'life_event': 1.0,
                    'medical_dental': 0.5628865979381443,
                    'motorcycle': 1.0,
                    'moving_relocation': 0.6091549295774648,
                    'other': 0.32434232434232435,
                    'special_occasion': 0.5285714285714286,
                    'student_loan': 0.7307692307692307,
                    'taxes': 0.5588235294117647,
                    'unknown': 0.55,
                    'vacation': 0.6616541353383458,
                    'wedding': 0.5747126436781609}

def preprocess_data(df):
    df['lender_id'] = df['lender_id'].map(lender_id_map)
    df['credit'] = df['credit'].map(credit_map)
    df['loan_purpose'] = df['loan_purpose'].map(loan_purpose_map)
    return df


def create_dataframe(temp_df):

    temp_df = pd.DataFrame(temp_df, columns=['requested', 'loan_purpose',
                                             'credit', 'annual_income',
                                             'apr', 'lender_id'])

    temp_df = temp_df[['apr', 'lender_id', 'requested', 'loan_purpose',
                       'credit', 'annual_income']]

    return temp_df


@app.route('/')
@app.route('/home')
def index():
    return render_template('home.html')


@app.route('/predict', methods=['POST'])
def home():
    apr = request.form['apr']
    lender_id = request.form['lender_id']
    requested = request.form['requested']
    loan_purpose = request.form['loan_purpose']
    credit = request.form['credit']
    annual_income = request.form['annual_income']
    arr = np.array([[apr, lender_id, requested, loan_purpose, credit, annual_income]])
    temp_df = pd.DataFrame(arr, columns=['apr', 'lender_id', 'requested', 'loan_purpose',\
                                         'credit', 'annual_income'])
    temp_df = preprocess_data(temp_df)

    prediction = model.predict_proba(temp_df)
    output = f"{prediction[0][1]:.2f}"

    if output > str(0.5):
        return render_template('after.html',
                               pred='This offer is likely to be clicked!\nProbability is {}'.format(output))
    else:
        return render_template('after.html',
                               pred='This offer is NOT likely to be clicked!\
                               \n Probability of getting clicked is {}'.format(output))

@app.route('/test')
def test():
    return render_template('test.html')


@app.route('/test2', methods=['POST'])

def test2():
    requested = request.form['requested']
    loan_purpose = request.form['loan_purpose']
    credit = request.form['credit']
    annual_income = np.float(request.form['annual_income'])
    apr = request.form['apr']
    lender_id = request.form['lender_id']
    apr2 = request.form['apr2']
    lender_id2 = request.form['lender_id2']
    lead_arr = np.array([[requested, loan_purpose, credit, annual_income]])
    offer_1 = np.array([[apr, str(lender_id)]])
    offer_2 = np.array([[apr2, str(lender_id2)]])
    temp_1 = np.concatenate((lead_arr, offer_1), axis=1)
    temp_1 = create_dataframe(temp_1)
    temp_1 = preprocess_data(temp_1)
    temp_2 = np.concatenate((lead_arr, offer_2), axis=1)
    temp_2 = create_dataframe(temp_2)
    temp_2 = preprocess_data(temp_2)

    prediction_1 = model.predict_proba(temp_1)
    output_1 = f"{prediction_1[0][1]:.2f}"

    prediction_2 = model.predict_proba(temp_2)
    output_2 = f"{prediction_2[0][1]:.2f}"

    if output_1 > str(0.5) and output_2 > str(0.5):
        return render_template('test_after.html',
                               pred_1='This offer is likely to be clicked!\nProbability is {}'.format(output_1),
                               pred_2='This offer is likely to be clicked!\nProbability is {}'.format(output_2))

    elif output_1 <= str(0.5) and output_2 <= str(0.5):
        return render_template('test_after.html',
                               pred_1='This offer is NOT likely to be clicked!\
                               \n Probability of getting clicked is {}'.format(output_1),
                               pred_2='This offer is NOT likely to be clicked!\
                               \n Probability of getting clicked is {}'.format(output_2))

    else:
        return render_template('test_after.html',
                               pred_1= 'Probability is {}'.format(output_1),
                               pred_2= 'Probability is {}'.format(output_2))
if __name__ == "__main__":
    app.run(debug=True)