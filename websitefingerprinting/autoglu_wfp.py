from autogluon.tabular import TabularDataset, TabularPredictor
import pandas as pd

from sklearn.model_selection import train_test_split

def main():
    predictors = []
    for h_vers in ['h2', 'h3']:
        print(h_vers, '!!')
        labels, streams = get_simple_wfp_data(h_vers, 200)
        streams.insert(0, 'domain', labels)

        train_stream, test_stream = train_test_split(streams, test_size=0.3, random_state=42)

        tab_data = TabularDataset(train_stream)
        predictor = TabularPredictor(label='domain').fit(tab_data)

        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        print(h_vers)
        predictor.leaderboard(test_stream)
        print('\n')
        y_test = test_stream['domain']
        y_pred = predictor.predict(test_stream)
        predictor.evaluate_predictions(y_true=y_test, y_pred=y_pred, auxiliary_metrics=True)
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

def get_simple_wfp_data(h_version:str, k:int):
    df = pd.read_csv("D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    #df = df.sort_values['0']

    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)

    for d in domains:
        d_df = df[df['0'] == d]
        new_df = pd.concat([new_df, d_df[:100]])

    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, :8]
    return labels, streams

main()