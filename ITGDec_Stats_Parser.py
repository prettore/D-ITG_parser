##################################################
## script to parse ITG summary logs, and network
# metrics in a time function to CSV
##################################################
## Author: Paulo H. L. Rettore
## Status: close
## Date: 01/07/2020
##################################################
import os
import csv
from datetime import datetime
import argparse
import pandas as pd

#create folder
def creatingFolders(dataFolder):
    if (os.path.isdir(dataFolder) == False):
        os.makedirs(dataFolder)

# ITGDec parser
def parser_itg(folder,inFileSummary,inFileMetrics,outFileName,expRound):

    file_ = open(folder+inFileSummary, 'r')
    raw_data = file_.readlines()
    file_.close()

    if(raw_data[2] != 'Empty log file\n'):
        csv_columns = ['timestamp', 'ip_from', 'ip_to', 'flows', 'total_time_s', 'total_packets', 'min_delay_s',
                       'max_delay_s', 'avg_delay_s', 'sd_delay_s', 'avg_jitter_s', 'bytes_received', 'avg_bitrate_kb',
                       'avg_packetrate_pkts', 'packet_dropped', 'packet_dropped_pct', 'avg_loss_burst_pkt']

        csv_line = [datetime.now(tz=None),
                    raw_data[4].split()[1],  # ip from
                    raw_data[5].split()[1],  # ip to
                    raw_data[24].split()[4],  # number of flows
                    raw_data[25].split()[3],  # total time
                    raw_data[26].split()[3],  # total of packets
                    raw_data[27].split()[3],  # minimum delay
                    raw_data[28].split()[3],  # maximum delay
                    raw_data[29].split()[3],  # avg delay
                    raw_data[31].split()[4],  # delay sd
                    raw_data[30].split()[3],  # avg jitter
                    raw_data[32].split()[3],  # bytes received
                    raw_data[33].split()[3],  # avg bitrate
                    raw_data[34].split()[4],  # avg packet rate per sec
                    raw_data[35].split()[3],  # packet dropped
                    raw_data[35].split()[4].replace('(', ''),  # packet dropped percentage
                    raw_data[36].split()[4]]  # avg packet rate per sec

        # save dictionary in csv file
        if os.path.isfile(folder + outFileName):
            with open(folder + outFileName, "a") as fp:
                wr = csv.writer(fp, delimiter=',')
                wr.writerow(csv_line)

            df = pd.read_csv(folder + inFileMetrics, sep='\s+', header=None)
            df['round'] = expRound
            df.to_csv(folder + outFileName.replace(".csv", "_metrics.csv"), mode='a',header=False, index=False)
        else:  # create header if there is no one
            with open(folder + outFileName, "a") as fp:
                wr = csv.writer(fp, delimiter=',')
                wr.writerow(csv_columns)
                wr.writerow(csv_line)

            df = pd.read_csv(folder + inFileMetrics, sep='\s+', header=None)
            column_header = ['time', 'bitrate', 'delay', 'jitter', 'packet_loss','round']
            df['round'] = expRound
            df.to_csv(folder + outFileName.replace(".csv", "_metrics.csv"), mode='a', header=column_header, index=False)
    else:
        print("FAIL TO LOG THE DATA...")


    os.system("sudo rm " + folder + inFileSummary)
    os.system("sudo rm " + folder + inFileMetrics)

if __name__ == '__main__':

    path = os.path.dirname(os.path.abspath(__file__))
    creatingFolders(path+'/data/statistics/')

    parser = argparse.ArgumentParser(description="D-ITG parser!")
    parser.add_argument("-i", "--inputFile", help="ITG receiver file as input. Ex.: fileName.log", type=str, required=True)
    parser.add_argument("-o", "--outputFile", help="The file name that you wish to write data into. Ex.: fileName.csv", type=str, required=True)
    parser.add_argument("-t", "--time", help="SMA. Averaged time in seconds", type=str, default='1')
    parser.add_argument("-r", "--expRound",
                        help="The experiment round. Used to compute standard error and confidence interval", type=str,
                        default='0')
    args = parser.parse_args()
    if args.inputFile and args.outputFile:

        av_time = int(float(str(args.time)) * 1000)

        exportITG_file = 'ITGDec ' + path + '/' + str(args.inputFile) + ' -v > ' + path + '/data/statistics/result_temp.txt'
        os.system(exportITG_file)
        exportITG_file = 'ITGDec ' + path + '/' + str(args.inputFile)  + ' -c ' + str(av_time)
        os.system(exportITG_file)

        os.system("sudo rm " + path+'/'+str(args.inputFile))

        os.system("mv " + path + '/combined_stats.dat ' + path + '/data/statistics')
        parser_itg(path + '/data/statistics/', 'result_temp.txt', 'combined_stats.dat', str(args.outputFile),str(args.expRound))

    else:
        print("Exiting of D-ITG parser! There are no enough arguments")
