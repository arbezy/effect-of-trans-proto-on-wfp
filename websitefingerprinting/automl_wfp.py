from autogluon.tabular import TabularDataset, TabularPredictor
import pandas as pd

def main():
    predictors = []
    for h_version in ['h2', 'h3']:
        print(h_version, '!!')
        labels, streams = get_simple_wfp_data(h_version, 200)
        # recombine labels and streams
        streams.insert(0, 'domain', labels)

        tab_data = TabularDataset(streams)
        predictor = TabularPredictor(label='domain').fit(tab_data)
        predictors.append(predictor)
        
    print('\n')
    print('HTTP2 LEADERBOARD:')
    predictor[0].leaderboard()
    print('\nHTTP3 LEADERBOARD:')
    predictor[1].leaderboard()

def get_transfer_wfp_data(h_version: str, k: int):
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        d_df = df[df['0'] == d]
        new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, 8:]
    return labels, streams

def get_simple_wfp_data(h_version: str, k: int):
    df = pd.read_csv(f"D:/traffic-features/" + h_version + "_traffic_features_" + str(k) + ".csv")
    df = df.sort_values(['0'])

    domains = df['0'].unique()
    new_df = pd.DataFrame(columns=df.columns)
    
    for d in domains:
        if d != "ustc":
            d_df = df[df['0'] == d]
            new_df = pd.concat([new_df, d_df[:100]])
        
    labels = new_df['0']
    streams = new_df.drop(df.columns[[0,1]], axis=1).iloc[:, :8]
    #print(streams)
    return labels, streams

main()
