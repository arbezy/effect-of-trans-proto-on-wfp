import os
import sys

# tcp parser:
for f in os.listdir(sys.argv[1]):
    fpath = os.path.join(sys.argv[1], f)
    print(f"parsing {f}!")
    os.system("tshark -nn -T fields -E separator=/t  -e frame.time_epoch"
              " -e ip.src -e ip.dst -e udp.srcport -e udp.dstport -e tcp.srcport -e tcp.dstport"
              " -e ip.proto -e ip.len -e ip.hdr_len -e tcp.hdr_len -e data.len"
              " -e frame.len -e tcp.time_delta -e tcp.time_relative"
              " -e tcp.seq  -e tcp.ack "
              " -e tcp.window_size_value -e _ws.expert.message -e tls.change_cipher_spec"
              " -r  {0} > {0}.csv".format(fpath))
    print(f"{f} parsed!")
    
# add syn into
# also can just remove acks from captured traffic

# # udp (quic!) parser
# for f in os.listdir(sys.argv[1]):
#     fpath = os.path.join(sys.argv[1], f)
#     print(f"parsing {f}!")
#     os.system("tshark -nn -T fields -E seperator=/t aggregator=f -e frame.time.epoch"
#               " -e ip.src -e ip.dst -e udp.srcport -e udp.dstport"
#               " -e tcp.srcport -e tcp.dstport"
#               " -e ip.proto -e -ip.len -e ip.hdr_len"
#               " -e frame.len -e udp.time_delta -e udp.time_relative"
#               " -e udp.stream -e _ws.expert.message -e tls.change_cipher_spec -e quic.handshake_payload"
#               "-r {0} > {0}.csv".format(fpath))
#     print(f"{f} parsed!")

# client hello
    
# this error occurs sometimes, need to record for which pcaps and exclude?
#  ** (tshark:88649) 16:57:20.772431 [Epan WARNING] -- Dissector bug, protocol TLS, in packet 19: ./epan/dissectors/packet-tls-utils.c:6412: failed assertion "offset <= offset_end"
    