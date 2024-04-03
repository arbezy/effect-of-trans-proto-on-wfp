print("efficient extract simple features")

# modified fast features, now takes no args, and extracts both http2, and http3 in the same run
# ONLY CALCULATES SIMPLE FEATURES
# have also removed uses of df.append as it is deprecated
# NOTE: now directory needs to be specified manually


import pandas as pd
import numpy as np
import os
import sys
from statistics import mean

import math

import multiprocessing

from time import sleep
# should make this multi process not thread!!!

def main():
    # change this to match computer cores for max speeeeeed
    N_THREADS = 8
    val_range = range(5, 45, 5)
    n = len(val_range)
    chunk_size = math.floor(n / N_THREADS)
    left_over = n % N_THREADS
    chunk_sizes = [chunk_size for _ in range(N_THREADS)]
    chunk_sizes[-1] += left_over
    chunk_sizes_cumulative = np.cumsum(chunk_sizes)
    chunk_sizes_cumulative = np.flip(chunk_sizes_cumulative)
    chunk_sizes_cumulative = np.append(chunk_sizes_cumulative, [0])
    chunk_sizes_cumulative = np.flip(chunk_sizes_cumulative)
    print(chunk_sizes_cumulative)


    for is_quic in [False, True]:

        threads = []
        for i in range(N_THREADS):
            thread_range = val_range[chunk_sizes_cumulative[i] : chunk_sizes_cumulative[i+1]]
            start_ind = thread_range[0]
            end_ind = thread_range[-1]
            threads.append(multiprocessing.Process(target=main_thread, args=(start_ind, end_ind, is_quic)))
        
        for t in threads:
            t.start()
            sleep(5)
            
        for t in threads:
            t.join()
            
        print("threads joined")
    
def main_thread(start: int, stop: int, is_quic: bool):
    print(f"thread for {start}->{stop} started")
    for k in range(start, stop+5, 5):
        no_of_cols = 1 + 8
        trace_df = pd.DataFrame(columns=list(range(no_of_cols)))
        counter = 1
        # SPECIFY DIRECTORYs HERE
        if is_quic:
            direc = "D:/FINALQUICRESULTS/finalparsedh3results/parsed-h3-results"
        else:
            direc = "D:/FINALH2RESULTS/FINALPARSEDH2/parsed-h2-results"

        for f in os.listdir(direc):
            if counter % 1000 == 0:
                print(f"thread({start},{stop}) has reached {counter}")
            if f.endswith('.csv'):
                fname = os.path.join(direc, f)
                current_capture = pd.read_csv(f"{fname}", sep='\t', dtype={18: str})
                #print(f"{k}:{counter}->{f}:")
                
                if is_quic:
                    #print("IS QUIC")
                    current_capture = label_quic_dataframe(current_capture)
                    current_capture = filter_out_irrelevant_pkts_quic(current_capture)
                    current_capture = remove_quic_handshake(current_capture)
                else:
                    #print("IS NOT QUIC")
                    current_capture = label_tcp_dataframe(current_capture)
                    current_capture = filter_out_irrelevant_pkts_tcp(current_capture)
                    current_capture = remove_tcp_handshake(current_capture)
                    
                simple_features = get_features(current_capture, k)
                
                domain = [f.split('_')[1].split('.')[0]]
                row = domain + simple_features
                trace_df.loc[len(trace_df)] = row
                counter += 1
                
        # Save transfer features as .csv
        save_fname = f'D:/traffic_features_wo_handshake/h3_traffic_features_{k}.csv' if is_quic else f'D:/traffic_features_wo_handshake/h2_traffic_features_{k}.csv'
        trace_df.to_csv(save_fname)
        print(f"saved as {save_fname}\n")
        
def remove_quic_handshake(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    #print("removing quic handshake")
    i=0
    indexes_to_drop = []
    while df.iloc[i].dst_port == 2020:
        indexes_to_drop.append(i)
        i += 1
    #print(indexes_to_drop)
    df = df.drop(index=indexes_to_drop)
    return df

def remove_tcp_handshake(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    #print("remove tcp / tls1.2 handshake")
    i=0
    indexes_to_drop = []
    while df.iloc[i].tcp_seq == 1 or df.iloc[i].tcp_ack == 1:
        indexes_to_drop.append(i)
        i += 1
    # should generally be larger than the quic handshake
    #print(indexes_to_drop)
    df = df.drop(index=indexes_to_drop)
    return df

def filter_out_irrelevant_pkts_quic(df: pd.DataFrame) -> pd.DataFrame:
    # checking if traffic has come from / gone to my server, using the port number
    # Would be more rigorous to use the IP address
    df1 = df[df['dst_port'] == 2020]
    df1.head(5)
    df2 = df[df['src_port'] == 2020]
    df2.head(5)
    df1 = pd.concat([df1, df2], ignore_index=False)
    df1 = df1.sort_values(by=['seq_num'])
    return df1

def filter_out_irrelevant_pkts_tcp(df: pd.DataFrame) -> pd.DataFrame:
    df1 = df[df['dst_port'] == 2020]
    df2 = df[df['src_port'] == 2020]
    df1 = pd.concat([df1, df2], ignore_index=False)
    df1 = df1.sort_values(by=['seq_num'])
    return df1[df1['proto'] != 17]

# NOTE: data len could be a bit misleading as it is the packet length not the data length.
def label_quic_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # data_length, pkt_length, arrival_time
    df = df.assign(e=pd.Series(range(1, len(df)+1)).values)
    df.columns = ["time_frame_epoch", "src_ip", "dst_ip", "src_port", "dst_port", "src_port(TCP)", "dst_port(TCP)", "proto", "ip_len", "ip_hdr_len", "udp_len", "data_len", "time_delta", "time_relative", "udp_stream", "expert_msg", "change_cipher_spec", "seq_num"]
    return df
        
# TODO: need to change this to the correct columns
def label_tcp_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(e=pd.Series(range(1, len(df)+1)).values)
    # NOTE: outdated col headers!
    df.columns =["time_frame_epoch", "src_ip", "dst_ip", "src_port_udp", "dst_port_udp", "src_port", "dst_port", "proto", "ip_len", "ip_hdr_len", "tcp_hdr_len", "notworking_data_len", "data_len", "time_delta", "time_relative", "tcp_seq", "tcp_ack", "tcp_win_size", "expert_msg", "change_cipher_spec", "seq_num"]
    return df

def get_features(capture_df: pd.DataFrame, k: int):
    simple_features = {s1+s2:0 for s1 in ["positive", "negative"] for s2 in ["tiny", "small", "medium", "large"]}

    i = 0
    for index, row in capture_df[:k].iterrows():
        # SIMPLE FEATURES
        src_port = int(row.src_port)
        dst_port = int(row.dst_port)
        pkt_size = int(row.data_len)
        # server port is 2020
        if src_port == 2020:
            simple_features["negative"+get_pkt_size_classification(pkt_size)] += 1
        elif dst_port == 2020:
            simple_features["positive"+get_pkt_size_classification(pkt_size)] += 1
        else:
            print("Neither the src or dst ip matched the client or server IP (but that's ok)")
            
    return list(simple_features.values())
    
    
def get_pkt_size_classification(pkt_size: bytes) -> str:
    # unit == bytes
    # TODO: write critique of paper that they used less than when they meant less than or equal to
    # TODO: also discuss in report whether this size distribution makes sense
    if pkt_size < 80:
        return "tiny"
    elif 80 <= pkt_size and pkt_size < 160:
        return "small"
    elif 160 <= pkt_size and pkt_size < 1280:
        return "medium"
    elif 1280 <= pkt_size:
        return "large"
    else:
        raise Exception("hmmm invalid pkt size, that's weird")

        
# is_quic = False
# if sys.argv[2] == "quic":
#     is_quic = True  

if __name__ == '__main__':
    main()
