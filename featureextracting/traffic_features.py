"""Feature extractor for quic and tcp traffic used to train a website fingerprinting model
by ANDREW ELLISON
"""

# ignores pandas warnings about df.append becoming deprecated soon... 
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import numpy as np
import os
import sys
from statistics import mean

# NOTE: THERE is an ambiguity about how they use k in the paper, here i use it in all my features to limit them to the first k packets, but they might not do this in the paper, should mention this in report


# k = Number of packets to use when extracting features, i.e. k=40 == use the first 40 packets.

# NEED TO SUPPLY THIS PROGRAM WITH TWO ARGUMENTS (DIRECTORY, 'quic'/'tcp')

def main():  
    for k in range(200, 201, 5):
        no_of_cols = 1 + 8 + ((1460)*2) + (k*2) + (1*7)
        trace_df = pd.DataFrame(columns=list(range(no_of_cols)))
        # counter is just to keep track of progress
        counter = 1
        # read every parsed pcap file in a directory, and extract features from it, then return a feature file for all the pcaps (and a given value of k)
        for f in os.listdir(sys.argv[1]):
            if f.endswith('.csv'):
                fname = os.path.join(sys.argv[1], f)
                current_capture = pd.read_csv(f"{fname}", sep='\t')
                print(f"{k}:{counter}->{f}:")
                
                # Label and filter traffic dataframes
                # the handshake removal function is optional
                if is_quic:
                    print("IS QUIC")
                    current_capture = label_quic_dataframe(current_capture)
                    current_capture = filter_out_irrelevant_pkts_quic(current_capture)
                    current_capture = remove_quic_handshake(current_capture)
                else:
                    print("IS NOT QUIC")
                    current_capture = label_tcp_dataframe(current_capture)
                    current_capture = filter_out_irrelevant_pkts_tcp(current_capture)
                    current_capture = remove_tcp_handshake(current_capture)
                    
                simple = simple_features(current_capture, k)
                # k = the number of packets to use in relevant transfer features = 40 (early traffic scenario)
                t_features = transfer_features(current_capture, simple, k)
                
                # combine simple and transfer features and save with the domain name, to act as a label for the sklearn models
                simple_values = list(simple.values())
                trace_features = simple_values + t_features
                domain = [f.split('_')[1].split('.')[0]]
                row = domain + trace_features
                trace_df.loc[len(trace_df)] = row
                counter += 1
                
        # Save transfer features as .csv
        save_fname = f'D:/h3_traffic_features_{k}.csv' if is_quic else f'D:/h2_traffic_features_{k}.csv'
        trace_df.to_csv(save_fname)
        print(f"saved as {save_fname}\n")

            
def is_df_empty(df: pd.DataFrame):
    if df.empty:
        print("DF IS EMPTY")
    else:
        print("DF IS NOT EMPTY")
        
        
def filter_out_irrelevant_pkts_quic(df: pd.DataFrame) -> pd.DataFrame:
    # checking source ports are equal to my caddy server source port
    df1 = df[df['dst_port'] == 2020]
    #df1.head(5)
    df2 = df[df['src_port'] == 2020]
    #df2.head(5)
    # NOTE: append is deprecated in later versions of pandas I think, alternative is to use concat
    df1 = df1.append(df2, ignore_index=False)
    df1 = df1.sort_values(by=['seq_num'])
    return df1

def filter_out_irrelevant_pkts_tcp(df: pd.DataFrame) -> pd.DataFrame:
    df1 = df[df['dst_port'] == 2020]
    df2 = df[df['src_port'] == 2020]
    df1 = df1.append(df2, ignore_index=False)
    df1 = df1.sort_values(by=['seq_num'])
    # removing udp packets
    return df1[df1['proto'] != 17]


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

# NOTE: data len could be a bit misleading as it is the packet length not the data length.
def label_quic_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(e=pd.Series(range(1, len(df)+1)).values)
    df.columns = ["time_frame_epoch", "src_ip", "dst_ip", "src_port", "dst_port", "src_port(TCP)", "dst_port(TCP)", "proto", "ip_len", "ip_hdr_len", "udp_len", "data_len", "time_delta", "time_relative", "udp_stream", "expert_msg", "change_cipher_spec", "seq_num"]
    return df
        
def label_tcp_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.assign(e=pd.Series(range(1, len(df)+1)).values)
    df.columns =["time_frame_epoch", "src_ip", "dst_ip", "src_port_udp", "dst_port_udp", "src_port", "dst_port", "proto", "ip_len", "ip_hdr_len", "tcp_hdr_len", "notworking_data_len", "data_len", "time_delta", "time_relative", "tcp_seq", "tcp_ack", "tcp_win_size", "expert_msg", "change_cipher_spec", "seq_num"]
    return df


    
# SIMPLE FEATURES:

def simple_features(capture_df: pd.DataFrame, k: int):
    simple_features_results = {s1+s2:0 for s1 in ["positive", "negative"] for s2 in ["tiny", "small", "medium", "large"]}
    i = 0
    for index, row in capture_df.iterrows():
        if i < k:
            src_port = int(row.src_port)
            dst_port = int(row.dst_port)
            pkt_size = int(row.data_len)
            # server port is 2020
            if src_port == 2020:
                simple_features_results["negative"+get_pkt_size_classification(pkt_size)] += 1
            elif dst_port == 2020:
                simple_features_results["positive"+get_pkt_size_classification(pkt_size)] += 1
            else:
                print("Neither the src or dst ip matched the client or server IP (but that's ok)")
        i += 1
    return simple_features_results
        
        
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



# ADVANCED FEATURES:
def transfer_features(df: pd.DataFrame, simple_features, k: int):
    # TODO: Could combine this upper and lower code to make a but more concise
    
    unique_pkt_size = unique_packet_size(df, k) # 1460d
    #print(f"unique pkt size = {len(unique_pkt_size)}dim")
    pkt_size_counts = pkt_size_count(df, k) # 1460d
    #print(f"pkt size counts = {len(pkt_size_counts)}dim")
    ordered_pkt_lengths = packet_order(df, k) # kd
    #print(f"ordered pkt lengths = {len(ordered_pkt_lengths)}dim")
    ita_time = interarrival_time(df, k) # kd
    #print(f"ita time = {len(ita_time)}dim")
    negative_pkts = neg_pkts(simple_features) # 1d
    cum_sum = cumulative_size(df, k) # 1d
    cum_sum_w_direction = cumulative_size_w_direction(df, k) # 1d
    bursts, max_burst, mean_burst = burst_features(df, k) # 1d, 1d, 1d
    ttl_trans_time = total_transmission_time(df, k) # 1d
    
    trace_transfer_features = []
    trace_transfer_features += unique_pkt_size
    trace_transfer_features += pkt_size_counts
    trace_transfer_features += ordered_pkt_lengths
    trace_transfer_features += ita_time
    trace_transfer_features += [negative_pkts]
    trace_transfer_features += [cum_sum]
    trace_transfer_features += [cum_sum_w_direction]
    trace_transfer_features += [bursts, max_burst, mean_burst]
    trace_transfer_features += [ttl_trans_time]
    
    return trace_transfer_features
    

"""this feature statistics whether the packet 𝑡 of
length 𝑙 is in the traffic 𝑇 . Specifically, define Length(𝑡) as a func-
tion that calculates the length of packet 𝑡, if 𝑙 ∈ {Length(𝑡𝑖)|𝑡𝑖 ∈
𝑇 }, 𝑙-th dimension of this feature is set to 1, otherwise, is set to
0. This feature is a 1460-dimension vector (packet length range
from 54 to 1514).

replaced this range with 56 -> 1894 which is my actual range of pkt lengths, meaning it is a 1838-dimension vector
"""
def unique_packet_size(df: pd.DataFrame, k:int):
    smallest_pkt_size = 56
    largest_pkt_size = 1516
    unique_packet_sizes = [0 for i in range((largest_pkt_size - smallest_pkt_size) + 1)]
    i = 0
    for index, row in df.iterrows():
        if i < k:
            pkt_size = row['data_len']
            if pkt_size <= 1516:
                unique_packet_sizes[int(pkt_size)-smallest_pkt_size] = 1
        i += 1
    return unique_packet_sizes[1:]
    
        
"""packet size count: this feature statistics the number of packet 𝑡 of
length 𝑙 in the traffic 𝑇 . Specifically, if 𝑙 ∈ {Length(𝑡𝑖)|𝑡𝑖 ∈ 𝑇 }, 𝑙-th
dimension of this feature is set to Card({𝑡𝑖|𝑡𝑖 ∈ 𝑇 , Length(𝑡𝑖) = 𝑙}).
This feature is a 1460-dimension vector.
"""
def pkt_size_count(df: pd.DataFrame, k: int):
    # TODO: change pkt size range
    smallest_pkt_size = 56
    largest_pkt_size = 1516
    unique_packet_sizes = [0 for i in range((largest_pkt_size) - smallest_pkt_size + 1)]
    i = 0
    for index, row in df.iterrows():
        if i < k:
            pkt_size = row['data_len']
            if pkt_size <= 1516:
                unique_packet_sizes[pkt_size-smallest_pkt_size] += 1
        i += 1
    return unique_packet_sizes[1:]

"""packet order: this feature records the packets length in order
of packet position. Specifically, the 𝑖-th dimension of this feature
is set to Length(𝑡𝑖), where 𝑡𝑖 is the 𝑖-th packet in traffic 𝑇 . This
feature is a 𝑘-dimension vector.
"""
def packet_order(df: pd.DataFrame, k: int):
    packet_lengths_in_order = []
    i = 0
    for index, row in df.iterrows():
        if i < k:
            pkt_size = row['data_len']
            packet_lengths_in_order.append(pkt_size)
        i += 1
    if len(packet_lengths_in_order) < k:
        return list(np.pad(np.array(packet_lengths_in_order), (0, k-len(packet_lengths_in_order))))
    else:
        return packet_lengths_in_order
    

"""inter-arrival time: this feature statistics arrival interval of ad-
jacent packets in order of packet position. Specifically, define
Time(𝑡) as a function that fetch the arrival time of a packet, let
𝑡0 be the 2-nd Client Hello packet for GQUIC, the last Handshake
packet for IQUIC, and the Change Cipher Spec packet for HTTPS,
then 𝑙-th dimension of this feature is set to (Time(𝑡𝑖) − Time(𝑡𝑖−1)),
where 𝑡𝑖, 𝑡𝑖−1 ∈ 𝑇 . This feature is a 𝑘-dimension vector.
"""
def interarrival_time(df: pd.DataFrame, k: int):
    time_deltas = np.array(df['time_delta'])
    
    if len(time_deltas) >= k:
        return list(time_deltas[:k])
    else:
        temp = np.pad(time_deltas, (0, k-len(time_deltas)), mode='edge')
        return list(temp)

"""negative packets: this feature statistics the number of packet 𝑡
in negative direction in traffic 𝑇 . This 1-dimension feature is set
to Card({(𝑡𝑗 , 𝑑𝑗 )|𝑑𝑗 = negative}).
"""
def neg_pkts(simple_features):
    return (simple_features["negativetiny"] + simple_features["negativesmall"] + simple_features["negativemedium"] + simple_features["negativelarge"])

"""cumulative size: this feature statistics the cumulative size of
packets in traffic 𝑇 . This 1-dimension feature is set to ∑{𝑇𝑝, 𝑇𝑛},
where 𝑇𝑝 = {Length((𝑡𝑖, 𝑑𝑖))|𝑡𝑖 ∈ 𝑇 , 𝑑𝑖 = positive}, 𝑇𝑛 =
{Length((𝑡𝑖, 𝑑𝑖))|𝑡𝑖 ∈ 𝑇 , 𝑑𝑖 = negative}.

THIS IS SUPER MISLEADING IN THE PAPER, CUMULATIVE SIZE IS JUST TOTAL SIZE AS IT IS 1 DIMENSION i.e. THE SUM
"""
def cumulative_size(df: pd.DataFrame, k:int):
    # This would return the cumulative sum as a k-dim feature, except it is not actually cumulative bc of their strange def.
    return df['data_len'][:k].sum()

"""cumulative size with direction: this feature statistics the cu-
mulative size of packets in traffic 𝑇 , but the impact of packet
direction 𝑑 is considered. This 1-dimension feature is set to
∑{𝑇𝑝, 𝑇𝑛}, where 𝑇𝑝 = {Length((𝑡𝑖, 𝑑𝑖))|𝑡𝑖 ∈ 𝑇 , 𝑑𝑖 = positive}, 𝑇𝑛 =
{−Length((𝑡𝑖, 𝑑𝑖))|𝑡𝑖 ∈ 𝑇 , 𝑑𝑖 = negative}.
"""
def cumulative_size_w_direction(df: pd.DataFrame, k: int):
    cumulative_sum = 0
    i = 0
    for index, row in df.iterrows():
        if i < k:
            src_port = int(row.src_port)
            dst_port = int(row.dst_port)
            if src_port == 2020:
                # from the server so -ve
                cumulative_sum -= row.data_len
            elif dst_port == 2020:
                # to the server so +ve
                cumulative_sum += row.data_len
        i += 1
    return cumulative_sum

"""bursts numbers/maximal length/mean length: burst is define
as the consecutive packets between two packets sent in the oppo-
site direction [33]. Bursts numbers, bursts maximal length, and
bursts mean length is the statistical features based on burst in the
traffic 𝑇
"""
""" OK that description is a bit shite, the one from the paper they reference is better...
https://www.scopus.com/record/display.uri?eid=2-s2.0-84878355718&origin=inward
in that original paper they just use burst size not all this extra stuff. 

On a serious note it doesn't make sense to use these extra 2 features as the max is already available in the list and the mean is already implicitly available...
"""
def burst_features(df: pd.DataFrame, k:int):
    first_pkt = df.iloc[0]
    if first_pkt.dst_port == 2020:
        previous_direction = 'forward'
        current_direction = 'forward'
    else:
        previous_direction = 'backward'
        current_direction = 'backward'
    
    curr_burst = []
    burst_sizes = []
    i = 0
    for index, row in df.iterrows():
        if i < k:
            if int(row.dst_port) == 2020:
                previous_direction = current_direction
                current_direction = 'forward'
                #print('->')
            elif int(row.src_port) == 2020:
                previous_direction = current_direction
                current_direction = 'backward'
                #print('<-')
                
            if current_direction == previous_direction:
                curr_burst.append(row.data_len)
            else:
                burst_sizes.append(sum(curr_burst))
                curr_burst = [row.data_len]
        i += 1

    burst_sizes.append(sum(curr_burst))
    return (len(burst_sizes), max(burst_sizes), mean(burst_sizes))

"""total transmission time: this feature statistics the total trans-
mission time of traffic 𝑇 . This 1-dimension feature is set to
∑{Time(𝑡𝑖) − Time(𝑡𝑖−1)|𝑡𝑖 ∈ 𝑇 , 𝑖 > 1}
"""
def total_transmission_time(df: pd.DataFrame, k:int):
    # think here I can just get the time stamp of the final packet
    if len(df) >= k:
        final_elem = df.iloc[k-1]
    else:
        final_elem = df.iloc[-1]
    return final_elem.time_relative




# NOTE: Whether it is quic or not is signalled via the cmd line, the code doesn't work this out itself :)
is_quic = False
if sys.argv[2] == "quic":
    is_quic = True  
main()
