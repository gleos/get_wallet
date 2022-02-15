from curses import raw
from hmac import trans_36
import solana
from solana.rpc.api import Client
import pygsheets
import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
from sqlalchemy import func

def get_wlt(rpc, casino, oldwlt):
    solana_client = Client(rpc)
    result  = solana_client.get_signatures_for_address(casino)
    print('len:', len(result['result']))
    transactions = []
    # I use `[:5]` to display only first 5 values
    for number, item in enumerate(result['result'], 1):
        transactions.append(item['signature'])
    test = transactions#[:5]
    wallets=[]

    for tx in test:
        info = solana_client.get_confirmed_transaction(tx)
        wlt = info['result']['transaction']['message']['accountKeys'][1]
        if wlt != casino:
            if wlt not in oldwlt:
                wallets.append(wlt)
        else:
            a = info['result']['transaction']['message']['accountKeys'][0]
            if a not in oldwlt:
                wallets.append(a)


    # print(wallets)
    #wallets_sol= {}

    for i in wallets:
        a = float(solana_client.get_balance(i)['result']['value'])
        if (a != 0.0) and (a != 2268960.0) and (a != 2827172.0):
            oldwlt[i]=a/1000000000
    #return wallets_sol

#     print("yapas

def update_wooksheet(sheet,list_wlt):
    #out_wlt_sol = pd.DataFrame.from_dict(wallets_sol)
    id = "1i8857PlnUt227gFVxogx4d4xa586-C_rmLbeFj1GgXA"
    #sheet.values.batchUpdate(spreadsheetID=id,body=wallets_sol)
    sheet.update('A:B', list(list_wlt.items()))


for i in range(1,2000000):
    print("Parsing ",i)
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    # add credentials to the account
    creds = ServiceAccountCredentials.from_json_keyfile_name('/Users/gregoire/Downloads/get_wallet/erudite-bonbon-340016-c17d1f364404.json', scope)
    # authorize the clientsheet 
    client = gspread.authorize(creds)
    sheet = client.open('wallets_list')
    sheet_instance = sheet.get_worksheet(0)
    adrs = sheet_instance.col_values(1)
    raw_balance = sheet_instance.col_values(2)
    balance = [float(i.replace(',','.')) for i in raw_balance]

    list_wlts = dict(zip(adrs, balance))
    len_old_list = len(list_wlts)

    RPC = 'https://solana-mainnet.phantom.tech'
    casino = 'bankgQRjUPrTeesV8WT49Am35pNDnWFqkzeKWnAT6YE' #hippo
    casino2 = 'DLq9BPETifWi56sxmW29FVCYGhpJSupq9v6uC5cYxgQA' #dcf
    casino3 = 'FLjvtVy9yL5Ut7GxhHCZr1fihhuPmy9bqcJzrZ8vVFfn' #plinko
    casino4 = 'D1CEzFxTzYBtJPUsqn44YKeEt46MdzjnqXr4gG9pD6Co' #dice

    get_wlt(RPC,casino, list_wlts)
    get_wlt(RPC,casino2, list_wlts)
    get_wlt(RPC,casino3, list_wlts)
    get_wlt(RPC,casino4, list_wlts)

    update_wooksheet(sheet_instance, list_wlts)
    
    print("+",len(list_wlts)-len_old_list, " nouveaux wallets")
    
