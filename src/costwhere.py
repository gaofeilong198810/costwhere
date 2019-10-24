import os
import json

from src.category import *


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
    return [item for item in result_list if
            item['交易状态'] == '交易成功' and
            item['收/支'] == '支出' and
            item['交易对方'] not in free_charge_counterparty]


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
            item['类别1'] = '餐饮日用'
            item['类别2'] = '未分类消费'


def write_bill_as_csv_zfb(bill_list, filename):
    new_header = [
        '交易创建时间', '类别1', '类别2', '交易对方', '商品名称', '金额（元）', '交易状态', '收/支',
        '类型', '交易号', '商家订单号', '付款时间', '最近修改时间', '交易来源地', '服务费（元）', '成功退款（元）', '备注', '资金状态',
    ]

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w') as file:
        file.write(','.join(new_header) + '\n')
        for item in bill_list:
            new_value = [item[h] for h in new_header]
            file.write(','.join(new_value) + '\n')


def load_bill_into_list_wx(input_dir):
    header = None
    contents = []
    result_list = []
    input_files = [root + '/' + files[0] for root, dirs, files in os.walk(input_dir) if len(files) != 0]
    for input_file in input_files:
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
    for item in result_list:
        item['商品'] = item['商品'].strip('"')
        item['金额(元)'] = item['金额(元)'].strip('¥')
    valid_trade = {'商户消费', '微信红包', '扫二维码付款', '群收款', '转账', '转账到银行卡', '零钱提现'}
    return [item for item in result_list if
            item['交易类型'] in valid_trade and
            item['收/支'] == '支出' and
            item['当前状态'] == '支付成功' and
            item['交易对方'] not in free_charge_counterparty]


def add_bill_category_wx(bill_list):
    category_dict = load_category()
    for item in bill_list:
        if item['交易对方'] in category_dict:
            item['类别1'] = category_dict[item['交易对方']]['category1']
            item['类别2'] = category_dict[item['交易对方']]['category2']
        else:
            item['类别1'] = '餐饮日用'
            item['类别2'] = '未分类消费'
        if item['交易对方'] == '/':
            item['类别1'] = '红包'
            item['类别2'] = '红包'


def write_bill_as_csv_wx(bill_list, filename):
    new_header = [
        '交易时间', '类别1', '类别2', '交易对方', '商品', '金额(元)', '当前状态', '收/支', '支付方式', '交易类型', '交易单号', '商户单号'
    ]

    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w', encoding='gb18030') as file:
        file.write(','.join(new_header) + '\n')
        for item in bill_list:
            new_value = [item[h] for h in new_header]
            file.write(','.join(new_value) + '\n')


def merge_bill_list(bill_list_zfb, bill_list_wx):
    bill_list_all = []
    new_header = ['交易时间', '类别1', '类别2', '交易对方', '商品', '金额', '支付方式']
    for item in bill_list_zfb:
        common_header = ['交易创建时间', '类别1', '类别2', '交易对方', '商品名称', '金额（元）']
        bill_in_common_header = [item[header] for header in common_header]
        bill_dict = dict(zip(new_header, bill_in_common_header))
        bill_dict['支付方式'] = '支付宝'
        bill_list_all.append(bill_dict)
    for item in bill_list_wx:
        common_header = ['交易时间', '类别1', '类别2', '交易对方', '商品', '金额(元)']
        bill_in_common_header = [item[header] for header in common_header]
        bill_dict = dict(zip(new_header, bill_in_common_header))
        bill_dict['支付方式'] = '微信'
        bill_list_all.append(bill_dict)
    return bill_list_all


def write_bill_as_csv_all(bill_list, filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))

    with open(filename, 'w', encoding='gb18030') as file:
        file.write(','.join(bill_list[0].keys()) + '\n')
        for item in bill_list:
            file.write(','.join(item.values()) + '\n')

if __name__ == '__main__':
    print('start...')
    # 支付宝
    input_file_zfb = '../bills/支付宝/支付宝_高飞龙_20190101_20191020.csv'
    bill_list_zfb = load_bill_into_list_zfb(input_file_zfb)
    # print(len(bill_list_zfb), bill_list_zfb)
    # print(print(json.dumps(bill_list_zfb, indent=2, ensure_ascii=False)))
    add_bill_category_zfb(bill_list_zfb)
    # print(len(bill_list_zfb), bill_list_zfb)
    # print(print(json.dumps(bill_list_zfb, indent=2, ensure_ascii=False)))
    write_bill_as_csv_zfb(bill_list_zfb, '../output/支付宝/' + os.path.basename(input_file_zfb))

    # 微信
    input_file_wx = '../bills/微信/高飞龙_微信_20190101_20191021'
    bill_list_wx = load_bill_into_list_wx(input_file_wx)
    # print(len(bill_list_wx), bill_list_wx)
    # print(print(json.dumps(bill_list_wx, indent=2, ensure_ascii=False)))
    add_bill_category_wx(bill_list_wx)
    # print(len(bill_list_wx), bill_list_wx)
    # print(print(json.dumps(bill_list_wx, indent=2, ensure_ascii=False)))
    write_bill_as_csv_wx(bill_list_wx, '../output/微信/高飞龙_微信_20190101_20191021.csv')

    # 合并
    bill_list_all = merge_bill_list(bill_list_zfb, bill_list_wx)
    write_bill_as_csv_all(bill_list_all, '../output/全部/高飞龙_全部_20190101_20191020.csv')
    # print(bill_list_all)
    print('done!!!')