import os
from resources.category import *


def load_bill_into_list_zfb(input_file):
    header = None
    contents = []
    result_list = []
    with open(input_file) as file:
        for line in file:
            if line.startswith('交易号'):
                header = [h.strip() for h in line.split(',')[:-1]]
            elif line.startswith('2019') or line.startswith('202'):
                contents.append([item.strip() for item in line.split(',')[:-1]])
            else:
                # print('-------------invalid line---------------', line)
                pass
    for item in contents:
        result_list.append(dict(zip(header, item)))
    # return result_list
    for item in result_list:
        if item['交易对方'].startswith('友宝售货机'):
            item['交易对方'] = '友宝售货机'
    return [item for item in result_list if item['交易状态'] == '交易成功' and \
                                            item['收/支'] == '支出' and \
                                            item['交易对方'] not in free_charge_counterparty_zfb]


def load_category():
    result_dict = {}
    for cat1, cat2_and_counterparty in counterparty_category.items():
        for cat2, counterparties in cat2_and_counterparty.items():
            for counterparty in counterparties:
                result_dict[counterparty] = {'category1': cat1, 'category2': cat2}
    return result_dict


def add_bill_category_zfb(bill_list):
    category_dict = load_category()
    for item in bill_list:
        if item['交易对方'] in category_dict:
            item['类别1'] = category_dict[item['交易对方']]['category1']
            item['类别2'] = category_dict[item['交易对方']]['category2']
        elif item['交易来源地'] == '淘宝':
            item['类别1'] = '网购'
            item['类别2'] = '淘宝天猫'
        else:
            item['类别1'] = '未分类消费'
            item['类别2'] = '未分类消费'


def write_bill_as_csv(bill_list, filename):
    new_header = [
        '交易创建时间', '交易对方', '商品名称', '类别1', '类别2', '金额（元）', '交易状态', '收/支',
        '类型', '交易号', '商家订单号', '付款时间', '最近修改时间', '交易来源地', '服务费（元）', '成功退款（元）', '备注', '资金状态',
    ]

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w') as file:
        file.write(','.join(new_header) + '\n')
        for item in bill_list:
            new_value = [item[h] for h in new_header]
            file.write(','.join(new_value) + '\n')

def load_bill_into_list_wx(input_file):
    header = None
    contents = []
    result_list = []
    with open(input_file, encoding='utf8') as file:
        for line in file:
            if line.startswith('交易时间'):
                header = [h.strip() for h in line.split(',')[:-1]]
            elif line.startswith('20') and len(line.split(',')[0]) == 19:
                contents.append([item.strip() for item in line.split(',')[:-1]])
            else:
                # print('-------------invalid line---------------', line)
                pass
    for item in contents:
        result_list.append(dict(zip(header, item)))
    # for item in result_list:
    #     if item['交易对方'].startswith('友宝售货机'):
    #         item['交易对方'] = '友宝售货机'
    valid_trade = {'商户消费', '微信红包', '扫二维码付款', '群收款', '转账', '转账到银行卡', '零钱提现'}
    return [item for item in result_list if item['交易类型'] in valid_trade and item['收/支'] == '支出' and item['交易对方'] not in free_charge_counterparty_wx]

def add_bill_category_wx(bill_list):
    category_dict = load_category()
    for item in bill_list:
        if item['交易对方'] in category_dict:
            item['类别1'] = category_dict[item['交易对方']]['category1']
            item['类别2'] = category_dict[item['交易对方']]['category2']
        elif item['交易来源地'] == '淘宝':
            item['类别1'] = '网购'
            item['类别2'] = '淘宝天猫'
        else:
            item['类别1'] = '未分类消费'
            item['类别2'] = '未分类消费'

if __name__ == '__main__':
    print('start...')
    # input_file_zfb = '../bills/支付宝/zfb_gfl_20190101_20191020.csv'
    # bill_list_zfb = load_bill_into_list_zfb(input_file_zfb)
    # # print(len(bill_list_zfb), bill_list_zfb)
    # add_bill_category_zfb(bill_list_zfb)
    # # print(len(bill_list_zfb), bill_list_zfb)
    # write_bill_as_csv(bill_list_zfb, '../output/支付宝/' + os.path.basename(input_file_zfb))

    input_file_wx = '../bills/微信/微信支付账单(20190101-20190401)/微信支付账单(20190101-20190401).csv'
    bill_list_wx = load_bill_into_list_wx(input_file_wx)
    print(len(bill_list_wx), bill_list_wx)
    add_bill_category_wx(bill_list_wx)
    print('done!!!')