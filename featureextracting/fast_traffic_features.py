print("efficient extract features")

# modified feature extraction code, new additions:
#         - calculates all features in a single loop
#         - multithreaded to calculate features for multiple values of k simultaneously



# ignores pandas warnings about df.append becoming deprecated soon... 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import os
import sys
from statistics import mean

import math

import multiprocessing

from time import sleep

def main():
    # change this to match computer cores for max speeeeeed
    # N_THREADS is a bit misleading, as this actually uses multiprocessing, "N_THREADS" is left over from a previous threaded implementation
    N_THREADS = 8
    # Divide the range of values amongst the processes
    val_range = range(40, 205, 5)
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

    # init all processes, with their own range of values to extract features for
    threads = []
    for i in range(N_THREADS):
        thread_range = val_range[chunk_sizes_cumulative[i] : chunk_sizes_cumulative[i+1]]
        start_ind = thread_range[0]
        end_ind = thread_range[-1]
        threads.append(multiprocessing.Process(target=main_thread, args=(start_ind, end_ind)))
    
    # start all processes, with a 5 second pause between each
    for t in threads:
        t.start()
        sleep(5)
    
    # join all processes (when they have finished executing)
    for t in threads:
        t.join()
        
    print("threads joined")
    
# each process/thread is given a subrange of the total range of values to extract features for
# processes should only read the parsed traffic files and write their own feature files so should not interfere with each other
def main_thread(start: int, stop: int):
    print(f"thread for {start}->{stop} started")
    # extract features for the subrange of k values
    for k in range(start, stop+5, 5):
        no_of_cols = 1 + 8 + ((1460)*2) + (k*2) + (1*7)
        trace_df = pd.DataFrame(columns=list(range(no_of_cols)))
        counter = 1
        for f in os.listdir(sys.argv[1]):
            # now that multiple threads run at once, it is easier to keep track of progress with less clutter, so at every 1000 files a process gives a head up
            if counter % 1000 == 0:
                print(f"thread({start},{stop}) has reached {counter}")

            if f.endswith('.csv'):
                fname = os.path.join(sys.argv[1], f)
                current_capture = pd.read_csv(f"{fname}", sep='\t', dtype={18: str})
                
                # handshake removal is optional, label and filter are NOT.
                if is_quic:
                    current_capture = label_quic_dataframe(current_capture)
                    current_capture = filter_out_irrelevant_pkts_quic(current_capture)
                    #current_capture = remove_quic_handshake(current_capture)
                else:
                    current_capture = label_tcp_dataframe(current_capture)
                    current_capture = filter_out_irrelevant_pkts_tcp(current_capture)
                    #current_capture = remove_tcp_handshake(current_capture)
                
                # get both simple and transfer features
                combined_features = get_features(current_capture, k)
                
                domain = [f.split('_')[1].split('.')[0]]
                row = domain + combined_features
                trace_df.loc[len(trace_df)] = row
                counter += 1
                
        # Save transfer features as .csv
        save_fname = f'D:/h3_traffic_features_{k}.csv' if is_quic else f'D:/h2_traffic_features_{k}.csv'
        trace_df.to_csv(save_fname)
        print(f"saved as {save_fname}\n")
        
def remove_quic_handshake(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    print("removing quic handshake")
    i=0
    indexes_to_drop = []
    while df.iloc[i].dst_port == 2020:
        indexes_to_drop.append(i)
        i += 1
    print(indexes_to_drop)
    df = df.drop(index=indexes_to_drop)
    return df

def remove_tcp_handshake(df: pd.DataFrame):
    df = df.reset_index(drop=True)
    print("remove tcp / tls1.2 handshake")
    i=0
    indexes_to_drop = []
    while df.iloc[i].tcp_seq == 1 or df.iloc[i].tcp_ack == 1:
        indexes_to_drop.append(i)
        i += 1
    # should generally be larger than the quic handshake
    print(indexes_to_drop)
    df = df.drop(index=indexes_to_drop)
    return df

def filter_out_irrelevant_pkts_quic(df: pd.DataFrame) -> pd.DataFrame:
    # checking source ports or ip addresses
    df1 = df[df['dst_port'] == 2020]
    df1.head(5)
    df2 = df[df['src_port'] == 2020]
    df2.head(5)
    df1 = df1.append(df2, ignore_index=False)
    df1 = df1.sort_values(by=['seq_num'])
    return df1

def filter_out_irrelevant_pkts_tcp(df: pd.DataFrame) -> pd.DataFrame:
    df1 = df[df['dst_port'] == 2020]
    df2 = df[df['src_port'] == 2020]
    df1 = df1.append(df2, ignore_index=False)
    df1 = df1.sort_values(by=['seq_num'])
    return df1[df1['proto'] != 17]

# NOTE: data len could be a bit misleading as it is the packet length not the data length.
def label_quic_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # data_length, pkt_length, arrival_time
    df = df.assign(e=pd.Series(range(1, len(df)+1)).values)
    df.columns = ["time_frame_epoch", "src_ip", "dst_ip", "src_port", "dst_port", "src_port(TCP)", "dst_port(TCP)", "proto", "ip_len", "ip_hdr_len", "udp_len", "data_len", "time_delta", "time_relative", "udp_stream", "expert_msg", "change_cipher_spec", "seq_num"]
    return df
        
def label_tcp_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(e=pd.Series(range(1, len(df)+1)).values)
    df.columns =["time_frame_epoch", "src_ip", "dst_ip", "src_port_udp", "dst_port_udp", "src_port", "dst_port", "proto", "ip_len", "ip_hdr_len", "tcp_hdr_len", "notworking_data_len", "data_len", "time_delta", "time_relative", "tcp_seq", "tcp_ack", "tcp_win_size", "expert_msg", "change_cipher_spec", "seq_num"]
    return df

# have collected the functions for every feature into one function, so that they can all be calculated at the same time.
def get_features(capture_df: pd.DataFrame, k: int):
    simple_features = {s1+s2:0 for s1 in ["positive", "negative"] for s2 in ["tiny", "small", "medium", "large"]}
    smallest_pkt_size = 56
    largest_pkt_size = 1516
    unique_packet_sizes = [0 for i in range((largest_pkt_size - smallest_pkt_size) + 1)]
    packet_size_count = [0 for i in range((largest_pkt_size) - smallest_pkt_size + 1)]
    packet_lengths_in_order = []
    time_deltas = []
    total_size = 0
    total_size_w_direction = 0
    # to calculate burst features need an initial direction ()
    first_pkt = capture_df.iloc[0]
    if first_pkt.dst_port == 2020:
        previous_direction = 'forward'
        current_direction = 'forward'
    else:
        previous_direction = 'backward'
        current_direction = 'backward'
    
    curr_burst = []
    burst_sizes = []

    i = 0
    for index, row in capture_df[:k+20].iterrows():
        if i < k:
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
            
            # TRANSFER FEATURES
            pkt_size = row['data_len']
            if pkt_size <= 1516:
                # unique packet sizes:
                unique_packet_sizes[int(pkt_size)-smallest_pkt_size] = 1
                # packet size counts:
                packet_size_count[pkt_size-smallest_pkt_size] += 1
                # total size:
                total_size += pkt_size
                # total size with direction:
                if src_port == 2020:
                    # from the server so -ve
                    total_size_w_direction -= pkt_size
                elif dst_port == 2020:
                    # to the server so +ve
                    total_size_w_direction += pkt_size
                    
            # packets lengths in arrival order:
            packet_lengths_in_order.append(pkt_size)
            # change in time between packets:
            time_deltas.append(row['time_delta'])
            
            # burst features:
            if int(row.dst_port) == 2020:
                previous_direction = current_direction
                current_direction = 'forward'
            elif int(row.src_port) == 2020:
                previous_direction = current_direction
                current_direction = 'backward'
            if current_direction == previous_direction:
                curr_burst.append(row.data_len)
            else:
                burst_sizes.append(sum(curr_burst))
                curr_burst = [row.data_len]
        i += 1
    
    # negative packets:
    neg_pkts = (simple_features["negativetiny"] + simple_features["negativesmall"] + simple_features["negativemedium"] + simple_features["negativelarge"])
    
    # total transmission time:
    if len(capture_df) >= k:
        final_elem = capture_df.iloc[k-1]
    else:
        final_elem = capture_df.iloc[-1]
    
    # bursts:
    burst_sizes.append(sum(curr_burst))
    
    # combine features into one list, padding where there is not k packets in a trace
    trace_features = []
    trace_features += list(simple_features.values())
    trace_features += unique_packet_sizes[1:]
    trace_features += packet_size_count[1:]
    if len(packet_lengths_in_order) < k:
        trace_features += list(np.pad(np.array(packet_lengths_in_order), (0, k-len(packet_lengths_in_order))))
    else:
        trace_features += packet_lengths_in_order
    if len(time_deltas) >= k:
        trace_features += list(time_deltas[:k])
    else:
        temp = np.pad(time_deltas, (0, k-len(time_deltas)), mode='edge')
        trace_features += list(temp)
    trace_features += [neg_pkts]
    trace_features += [total_size]
    trace_features += [total_size_w_direction]
    trace_features += [len(burst_sizes), max(burst_sizes), mean(burst_sizes)]
    trace_features += [final_elem.time_relative]
    
    return trace_features
    
    
def get_pkt_size_classification(pkt_size: bytes) -> str:
    # unit == bytes
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

# if quic arg is given, then use the quic related functions
is_quic = False
if sys.argv[2] == "quic":
    is_quic = True  

if __name__ == '__main__':
    main()
