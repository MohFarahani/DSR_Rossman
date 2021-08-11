import pandas as pd
import numpy as np
import sys
import pickle
import xgboost


PATH_STORE = 'modified_store.csv'
PATH_MODEL = 'xgb.pickle.dat'

def metric(preds, actuals):
    preds = preds.reshape(-1)
    actuals = actuals.reshape(-1)
    assert preds.shape == actuals.shape
    return 100 * np.linalg.norm((actuals - preds) / actuals) / np.sqrt(preds.shape[0])

def evaluate(path_X_csv,path_y_csv):
    train = pd.read_csv(path_X_csv)
    y_real = pd.read_csv(path_y_csv)

    if 'Open' in train.columns:
        mask_open = train['Open']==1
        train = train[mask_open]
        y_real = y_real[mask_open]
    y_predict = predict(train)
    RMSPE = metric(y_predict, y_real)
    print("RMSPE: ",RMSPE)
    return RMSPE

def clean(df):
    if 'StateHoliday' in df.columns:
        df.loc[df['StateHoliday']==0,'StateHoliday']='0'
        df.loc[df['StateHoliday']=='0','StateHoliday']='0'

def fillna(df):
    def fillna_mean(df,columns):
        for col in columns:
            if col in df.columns:
                mean_value = int(df[col].mean())
                df.loc[:,col].fillna(value=mean_value,inplace=True)
        return df

    def fillna_most(df,columns):
        for col in columns:
            if col in df.columns:
                most_value = df[col].value_counts().idxmax()
                df.loc[:,col].fillna(value=most_value,inplace=True)
        return df
    columns_mean = ['DayOfWeek','Customers']
    df = fillna_mean(df,columns_mean)

    columns_most = ['Promo','SchoolHoliday','StateHoliday']
    df = fillna_most(df,columns_most)
    return df

def encoding(df):
    pass

def new_features(df):
    pass


def predict(train):
    store = pd.read_csv(PATH_STORE)
    train = clean(train)
    train = fillna(train)
    train_full = pd.merge(train,store, on='Store', how='inner')
    train_full = encoding(train_full)
    train_full = new_features(train_full)
    drop_columns_list = ['Store','Customer','Date','Open']
    train_full.drop(columns=drop_columns_list,inplace=True, error='ignore')
    train_full.dropna(inplace=True)
    xgb = pickle.load(open(PATH_MODEL, "rb"))
    return xgb.predict(train)

if __name__ == "__main__":
    path_X_csv,path_y_csv = sys.argv[1] , sys.argv[2]
    RMSPE = evaluate(path_X_csv,path_y_csv)